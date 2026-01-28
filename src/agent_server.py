import os
import threading
import asyncio
import contextlib
from pathlib import Path
import logging
import traceback
import json
import hmac
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, List, Tuple
import base64
import hashlib
import uuid
import shlex
import subprocess
import time
from urllib.parse import urlparse

from fastapi import FastAPI, Request, Response, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel

from observability import setup as setup_observability

from models.backend import make_client
from core.kb import add_entry, ingest_hierarchical_text
from core.bus_client import BusClient
from plugins.profile.points import award_points, get_rankings
from plugins.profile.badges import assign_badge
from integrations.social_hooks import init_cron, shutdown
from integrations import social_hooks
from core import error_summary
from hnet.dynamic_chunker import DynamicChunker
import math


# --- Shell connector configuration ---
# Hard-coded allowlist of shell commands usable via the "shell_command" connector.
# Keep this list minimal and only include commands that are safe for your environment.
CONNECTOR_SHELL_ALLOW = {"echo"}

# --- Lifespan Manager (replaces on_event) ---


_heartbeat_task: asyncio.Task[Any] | None = None


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handles application startup and shutdown events."""
    print("Agent server is waking up...")
    load_and_register_model()
    # Start heartbeat loop
    global _heartbeat_task
    try:
        loop = asyncio.get_event_loop()
        _heartbeat_task = loop.create_task(_heartbeat_loop())
    except Exception:
        _heartbeat_task = None
    try:
        yield
    finally:
        if bus:
            await bus.stop()
        if _heartbeat_task:
            _heartbeat_task.cancel()
            with contextlib.suppress(BaseException):
                await _heartbeat_task
        print("Agent server is shutting down.")
        shutdown()


# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)

# CORS: allow origins from env (comma-separated), default localhost:5173
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Optionally serve built SPA if configured
spa_dist = os.environ.get("SERVE_SPA_DIST")
if spa_dist:
    try:
        spa_path = Path(spa_dist)
        app.mount("/", StaticFiles(directory=spa_path, html=True), name="spa")

        @app.get("/{full_path:path}")
        async def spa_catch_all(full_path: str) -> FileResponse:
            index_file = spa_path / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            raise HTTPException(status_code=404, detail="index.html not found")
    except Exception:
        logger.warning("Failed to mount SPA from SERVE_SPA_DIST=%s", spa_dist)

setup_observability("agent-server", app)

# --- Environment and Configuration ---
role = os.environ.get("ROLE", "AGENT")
config_model = os.environ.get("MODEL_KIND", "ollama")
config_endpoint = os.environ.get("MODEL_ENDPOINT", "http://localhost:11434")
config_model_name = os.environ.get("MODEL_NAME", "llama3.1")
prompt_file = os.environ.get("PROMPT_FILE", "prompts/AGENT.md")
BUS_URL = os.environ.get("BUS_URL")
BUS_TOKEN = os.environ.get("BUS_TOKEN")
if BUS_URL and not BUS_TOKEN:
    raise RuntimeError("Missing required environment variables: BUS_TOKEN")

# --- Global State ---
llm: Any | None = None
system_prompt: str = ""
bus: BusClient | None = (
    BusClient(BUS_URL, role, lambda msg: add_entry(kind=f"bus:{role}", data=msg), token=BUS_TOKEN)
    if BUS_URL
    else None
)
if bus is not None:
    b = bus
    threading.Thread(target=lambda: asyncio.run(b.run_forever()), daemon=True).start()


# --- Dev JWT/session utilities ---


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _jwt_secret() -> str:
    return os.environ.get("DEV_JWT_SECRET", os.environ.get("AGENT_SHARED_SECRET", "devjwtsecret"))


def _sign_token(payload: Dict[str, Any], *, exp_s: int = 3600, kind: str = "session") -> str:
    body = dict(payload)
    body["exp"] = int(time.time()) + exp_s
    body["kind"] = kind
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    msg = _b64url(raw)
    sig = hmac.new(_jwt_secret().encode("utf-8"), msg.encode("ascii"), hashlib.sha256).digest()
    return msg + "." + _b64url(sig)


def _verify_token(token: str, *, expect_kind: str | None = None) -> Dict[str, Any]:
    try:
        msg, sig = token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid token")
    want = hmac.new(_jwt_secret().encode("utf-8"), msg.encode("ascii"), hashlib.sha256).digest()
    got = _b64url_decode(sig)
    if not hmac.compare_digest(want, got):
        raise HTTPException(status_code=401, detail="invalid signature")
    body: Dict[str, Any] = json.loads(_b64url_decode(msg))
    if int(body.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="expired token")
    if expect_kind and body.get("kind") != expect_kind:
        raise HTTPException(status_code=401, detail="wrong token kind")
    return body


# In-memory agents registry (prep for real discovery)
AGENTS: Dict[str, Dict[str, Any]] = {
    "orchestrator": {"id": "orchestrator", "name": "Orchestrator", "status": "running"},
    "agent-1": {"id": "agent-1", "name": "Agent 1", "status": "stopped"},
    "agent-2": {"id": "agent-2", "name": "Agent 2", "status": "stopped"},
}
AGENTS_SEQ = 0
AGENTS_LOCK = threading.Lock()


def _notify_agents_changed() -> None:
    global AGENTS_SEQ
    with AGENTS_LOCK:
        AGENTS_SEQ += 1


async def _heartbeat_loop() -> None:
    """Emit periodic heartbeats and update lastSeen for agents."""
    while True:
        try:
            now = time.time()
            for k, v in list(AGENTS.items()):
                v["lastSeen"] = now
                add_entry(kind="agent_heartbeat", data={"id": v.get("id", k), "ts": now})
                if bus is not None:
                    try:
                        payload = json.dumps({"id": v.get("id", k), "ts": now})
                        await bus.publish("heartbeat", payload)
                    except Exception:
                        logger.exception("Failed to publish heartbeat to bus")
            _notify_agents_changed()
        except Exception:
            pass
        await asyncio.sleep(max(3, int(os.environ.get("HEARTBEAT_INTERVAL_S", "10"))))


# --- Pydantic Models ---


class Message(BaseModel):
    text: str


class BusMessage(BaseModel):
    topic: str
    data: Dict[str, Any]


class History(BaseModel):
    messages: List[Dict[str, str]]


# --- Core Functions ---


def load_and_register_model() -> None:
    """Loads the LLM and system prompt from config."""
    global llm, system_prompt
    llm = make_client(kind=config_model, endpoint=config_endpoint, model=config_model_name)
    prompt_path = Path(prompt_file)
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        logger.warning("Prompt file not found at %s", prompt_file)


# --- Middleware for Authentication ---
@app.middleware("http")
async def secret_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Validate Authorization header against a shared secret."""

    # Read secret at request time so env changes are picked up
    shared_secret = os.environ.get("AGENT_SHARED_SECRET")
    if not shared_secret:
        logger.warning("AGENT_SHARED_SECRET is not set")
        return JSONResponse(status_code=401, content={"detail": "Missing AGENT_SHARED_SECRET"})

    # Accept Bearer shared secret or signed token, cookie session, or query param (dev SSE)
    authed = False
    auth_header = request.headers.get("authorization")
    if auth_header:
        parts = auth_header.split(None, 1)
        scheme = parts[0].lower() if parts else ""
        bearer = parts[1] if len(parts) == 2 else ""
        if scheme == "bearer" and bearer:
            if hmac.compare_digest(bearer, shared_secret):
                authed = True
            else:
                try:
                    _ = _verify_token(bearer)
                    authed = True
                except HTTPException:
                    authed = False
    if not authed:
        cookie = request.cookies.get("session")
        if cookie:
            try:
                _ = _verify_token(cookie)
                authed = True
            except HTTPException:
                authed = False
    if not authed:
        q_token = request.query_params.get("token")
        q_sse = request.query_params.get("sse")
        if q_token and hmac.compare_digest(q_token, shared_secret):
            authed = True
        elif q_sse:
            try:
                _ = _verify_token(q_sse, expect_kind="sse")
                authed = True
            except HTTPException:
                authed = False
    if not authed:
        data = {"path": str(request.url.path)}
        if auth_header:
            data["masked_token"] = "***"
        add_entry(kind="auth_failure", data=data)
        status = 401 if not auth_header else 403
        detail = "Unauthorized" if status == 401 else "Forbidden"
        return JSONResponse(status_code=status, content={"detail": detail})

    return await call_next(request)


# --- API Endpoints ---


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "role": role}


@app.post("/wake")
async def wake_up() -> Dict[str, str]:
    if bus is not None:
        logger.info("Bus client active for role %s", role)
        init_cron()
    return {"status": "awake", "role": role}


@app.post("/chat")
async def chat_endpoint(message: Message) -> Dict[str, str]:
    """Simple chat endpoint for direct interaction."""
    assert llm is not None
    chunker = DynamicChunker()
    outputs: List[str] = []
    for chunk in chunker.chunk(message.text):
        outputs.append(llm.chat(system_prompt, chunk))
    response = "\n".join(outputs)
    add_entry(kind=f"{role} chat", data={"in": message.text, "out": response})
    award_points(role, "chat")
    return {"response": response}


@app.post("/chat_history")
async def chat_history_endpoint(history: History) -> Dict[str, str]:
    """Chat endpoint that takes conversational history."""
    assert llm is not None
    chunker = DynamicChunker()
    expanded: List[Dict[str, str]] = []
    convo_lines: List[str] = []
    for msg in history.messages:
        text = msg.get("content", "")
        role_name = msg.get("role", "user")
        convo_lines.append(f"{role_name}: {text}")
        for part in chunker.chunk(text):
            expanded.append({"role": role_name, "content": part})
    # Persist hierarchical summaries of the full conversation
    conversation_log = "\n".join(convo_lines)
    ingest_hierarchical_text(
        conversation_log,
        lambda t: llm.chat(system_prompt, f"Summarize:\n{t}"),
        meta={"kind": f"{role} chat"},
    )
    response = llm.chat_history(expanded)
    add_entry(kind=f"{role} chat history", data={"in": history.messages, "out": response})
    award_points(role, "chat_history")
    return {"response": response}


# --- API Router (/api) ---

api = APIRouter(prefix="/api")


@api.get("/health")
async def api_health() -> Dict[str, Any]:
    """Aggregated health of this service and optional bus server."""
    status: Dict[str, Any] = {"backend": {"ok": True, "role": role}}
    if BUS_URL:
        import httpx

        try:
            headers = {"Authorization": f"Bearer {BUS_TOKEN}"} if BUS_TOKEN else {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{BUS_URL}/health", headers=headers)
            status["bus"] = {"ok": r.status_code == 200}
        except Exception as e:  # pragma: no cover - network issues
            status["bus"] = {"ok": False, "error": str(e)}
    return status


class Agent(BaseModel):
    id: str
    name: str
    status: str
    model: str | None = None
    lastSeen: float | None = None


def _default_agents() -> List[Agent]:
    return [Agent(**v) for v in AGENTS.values()]


@api.get("/agents")
async def list_agents() -> Dict[str, Any]:
    """Return known agents and their status (stub, to be backed by real discovery)."""
    return {"items": [a.model_dump() for a in _default_agents()]}


@api.post("/agents/{agent_id}/{action}")
async def agent_action(request: Request, agent_id: str, action: str) -> Dict[str, Any]:
    _require_role(request, {"operator", "admin"})
    if action not in {"start", "stop", "wake"}:
        raise HTTPException(status_code=400, detail="invalid action")
    # If bus is configured, publish control message
    if bus is not None:
        try:
            payload = json.dumps({"target": agent_id, "action": action})
            await bus.publish("control", payload)
        except Exception:
            logger.exception("Failed to publish control message to bus")
    # Special-case self wake
    if action == "wake" and agent_id in {role, "orchestrator"}:
        await wake_up()
    # Update in-memory status
    if agent_id in AGENTS:
        if action == "start":
            AGENTS[agent_id]["status"] = "running"
        elif action == "stop":
            AGENTS[agent_id]["status"] = "stopped"
        _notify_agents_changed()
    return {"status": "accepted", "agent": agent_id, "action": action}


@api.post("/chat")
async def api_chat(message: Message) -> Dict[str, str]:
    return await chat_endpoint(message)


@api.post("/chat_history")
async def api_chat_history(history: History) -> Dict[str, str]:
    return await chat_history_endpoint(history)


# Mount API router
app.include_router(api)

# Compatibility routes for existing frontend helpers (/api/nodes/*)


@api.post("/nodes/{node_id}/start")
async def nodes_start(request: Request, node_id: str) -> Dict[str, Any]:
    return await agent_action(request, node_id, "start")


@api.post("/nodes/{node_id}/stop")
async def nodes_stop(request: Request, node_id: str) -> Dict[str, Any]:
    return await agent_action(request, node_id, "stop")


@api.get("/nodes/{node_id}/config")
async def nodes_get_config(node_id: str) -> Dict[str, Any]:
    # Placeholder: fetch real config per node/agent
    return {"id": node_id, "config": {}}


@api.put("/nodes/{node_id}/config")
async def nodes_put_config(node_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder: persist config; for now just echo
    add_entry(kind="config_update", data={"node": node_id, "config": body})
    return {"status": "ok"}


# --- KB & Uploads ---


@api.get("/kb/recent")
async def kb_recent(limit: int = 20) -> Dict[str, Any]:
    from core.kb import last as kb_last

    items = []
    for row in kb_last(max(1, min(200, limit))):
        try:
            payload = json.loads(row.get("data", "{}"))
        except Exception:
            payload = {"raw": row.get("data")}
        items.append({"id": row["id"], "kind": row["kind"], "data": payload, "ts": row["ts"]})
    return {"items": items}


@api.get("/kb/search")
async def kb_search(q: str) -> Dict[str, Any]:
    from core.kb import search as kb_search_impl

    results = []
    for row in kb_search_impl(q):
        try:
            payload = json.loads(row.get("data", "{}"))
        except Exception:
            payload = {"raw": row.get("data")}
        results.append({"id": row["id"], "kind": row["kind"], "data": payload})
    return {"items": results}


@api.get("/kb/{entry_id}")
async def kb_get(entry_id: int) -> Dict[str, Any]:
    from core.kb import get as kb_get_impl

    row = kb_get_impl(entry_id)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    try:
        payload = json.loads(row.get("data", "{}"))
    except Exception:
        payload = {"raw": row.get("data")}
    return {"id": row["id"], "kind": row["kind"], "data": payload, "ts": row["ts"]}


@api.post("/kb/semantic_search")
async def kb_semantic_search(body: Dict[str, Any]) -> Dict[str, Any]:
    query = str(body.get("query", "")).strip()
    k = int(body.get("k", 5))
    if not query:
        return {"items": []}
    # Try embeddings if available
    try:
        from integrations.openvino_embedder import get_embeddings

        q_vec = get_embeddings(query)
        from core.kb import last as kb_last

        cands: List[tuple[float, Dict[str, Any], Dict[str, Any]]] = []
        for row in kb_last(800):
            try:
                data = json.loads(row.get("data", "{}"))
            except Exception:
                continue
            emb = data.get("embedding")
            if not emb:
                continue
            num = sum(float(a) * float(b) for a, b in zip(q_vec, emb))
            den1 = math.sqrt(sum(float(a) * float(a) for a in q_vec))
            den2 = math.sqrt(sum(float(b) * float(b) for b in emb))
            score = num / (den1 * den2 + 1e-9)
            cands.append((score, row, data))
        cands.sort(key=lambda x: x[0], reverse=True)
        out = [
            {"id": r["id"], "kind": r["kind"], "score": float(s), "data": d, "ts": r["ts"]}
            for s, r, d in cands[: max(1, min(50, k))]
        ]
        return {"items": out}
    except Exception:
        pass
    # Fallback: FTS
    from core.kb import search as kb_search_impl

    results = []
    for row in kb_search_impl(query)[: max(1, min(50, k))]:
        try:
            payload = json.loads(row.get("data", "{}"))
        except Exception:
            payload = {"raw": row.get("data")}
        results.append({"id": row["id"], "kind": row["kind"], "score": 0.0, "data": payload})
    return {"items": results}


@api.post("/uploads")
async def upload_file(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    _require_role(request, {"operator", "admin"})
    """Accept a single file and ingest into KB (best-effort text)."""
    content = await file.read()
    name = file.filename or "upload.bin"
    text: str | None = None
    try:
        text = content.decode("utf-8")
    except Exception:
        # fallback: ignore binary ingestion; store meta only
        text = None
    add_entry(kind="upload", name=name, size=len(content), mimetype=file.content_type)

    if text and llm is not None:
        try:
            ingest_hierarchical_text(text, lambda t: llm.chat(system_prompt, f"Summarize:\n{t}"), meta={"name": name})
        except Exception:
            # store plain text chunked
            ingest_hierarchical_text(text, lambda t: t[:2000], meta={"name": name})
    elif text:
        ingest_hierarchical_text(text, lambda t: t[:2000], meta={"name": name})

    return {"status": "ok", "name": name, "bytes": len(content)}


@api.post("/files/upload")
async def upload_files_compat(request: Request, files: list[UploadFile] = File(...)) -> Dict[str, Any]:
    _require_role(request, {"operator", "admin"})
    """Compatibility: accept multiple files under 'files' (as OrchestratorUI uses)."""
    total = 0
    for f in files:
        content = await f.read()
        total += len(content)
        try:
            txt = content.decode("utf-8")
        except Exception:
            txt = None
        add_entry(kind="upload", name=f.filename, size=len(content), mimetype=f.content_type)
        if txt:
            if llm is not None:
                try:
                    ingest_hierarchical_text(txt, lambda t: llm.chat(system_prompt, f"Summarize:\n{t}"), meta={"name": f.filename})
                except Exception:
                    ingest_hierarchical_text(txt, lambda t: t[:2000], meta={"name": f.filename})
            else:
                ingest_hierarchical_text(txt, lambda t: t[:2000], meta={"name": f.filename})
    return {"status": "ok", "files": len(files), "bytes": total}


# --- SSE Streams ---


def _sse_event(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@api.get("/logs/sse")
async def logs_sse(
    kinds: str | None = None,
    interval_ms: int = 1000,
    run_id: str | None = None,
    last_id: int = 0,
) -> StreamingResponse:
    """Server-Sent Events stream of recent log-like KB entries.

    Filters by comma-separated kinds if provided, e.g. kinds=bus_message,kb_summary
    """
    from core.kb import last as kb_last

    kinds_set = set([k.strip() for k in (kinds or "").split(",") if k.strip()])
    start_id = int(last_id) if last_id else 0

    async def gen() -> AsyncIterator[str]:
        nonlocal start_id
        while True:
            try:
                rows = kb_last(50)
                rows.sort(key=lambda r: r["id"])  # oldest first
                for row in rows:
                    rid = int(row["id"])
                    if rid <= start_id:
                        continue
                    if kinds_set and row.get("kind") not in kinds_set:
                        continue
                    try:
                        payload = json.loads(row.get("data", "{}"))
                    except Exception:
                        payload = {"raw": row.get("data")}
                    if run_id and payload.get("run_id") != run_id:
                        continue
                    yield _sse_event({"id": rid, "kind": row.get("kind"), "data": payload, "ts": row.get("ts")})
                    start_id = rid
            except Exception:
                # swallow and continue
                pass
            await asyncio.sleep(max(0.1, interval_ms / 1000))

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)


@api.get("/agents/sse")
async def agents_sse(interval_ms: int = 1000) -> StreamingResponse:
    """SSE stream of agents snapshot when changed."""
    last_seq = -1

    async def gen() -> AsyncIterator[str]:
        nonlocal last_seq
        yield _sse_event({"items": list(AGENTS.values())})
        last_seq = AGENTS_SEQ
        while True:
            if AGENTS_SEQ != last_seq:
                yield _sse_event({"items": list(AGENTS.values())})
                last_seq = AGENTS_SEQ
            await asyncio.sleep(max(0.1, interval_ms / 1000))

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)


@api.get("/bus/sse")
async def bus_sse(
    topic: str | None = None,
    interval_ms: int = 1000,
    last_id: int = 0,
) -> StreamingResponse:
    """SSE stream of bus_message KB entries, optionally filtered by topic."""
    from core.kb import last as kb_last

    start_id = int(last_id) if last_id else 0

    async def gen() -> AsyncIterator[str]:
        nonlocal start_id
        while True:
            try:
                rows = kb_last(50)
                rows.sort(key=lambda r: r["id"])  # oldest first
                for row in rows:
                    rid = int(row["id"])
                    if rid <= start_id:
                        continue
                    if row.get("kind") != "bus_message":
                        continue
                    try:
                        payload = json.loads(row.get("data", "{}"))
                    except Exception:
                        payload = {"raw": row.get("data")}
                    if topic and payload.get("topic") != topic:
                        continue
                    yield _sse_event({"id": rid, **payload, "ts": row.get("ts")})
                    start_id = rid
            except Exception:
                pass
            await asyncio.sleep(max(0.1, interval_ms / 1000))

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)


# --- Bus helpers (no SSE) ---


@api.post("/bus/publish")
async def bus_publish(request: Request, topic: str = Form(...), payload: str = Form("{}")) -> Dict[str, Any]:
    _require_role(request, {"operator", "admin"})
    """Publish a message to the configured bus via BusClient (if available)."""
    if not bus:
        raise HTTPException(status_code=400, detail="bus not configured")
    try:
        data = json.loads(payload)
    except Exception:
        data = {"text": payload}
    try:
        await bus.publish(topic, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    add_entry(kind="bus_publish", topic=topic, payload=data)
    return {"status": "ok"}


@api.get("/bus/tail")
async def bus_tail(topic: str | None = None, limit: int = 50) -> Dict[str, Any]:
    """Return recent bus messages from KB entries for quick UI tailing."""
    from core.kb import last as kb_last

    items = []
    for row in kb_last(max(1, min(200, limit * 2))):
        if row.get("kind") == "bus_message":
            try:
                payload = json.loads(row.get("data", "{}"))
            except Exception:
                payload = {"raw": row.get("data")}
            if topic and payload.get("topic") != topic:
                continue
            items.append({"id": row["id"], **payload, "ts": row["ts"]})
            if len(items) >= limit:
                break
    return {"items": items}


# --- Connectors (Phase 5 preparation) ---


CONNECTORS: List[Dict[str, Any]] = [
    {
        "key": "http_request",
        "name": "HTTP Request",
        "params": {"method": "GET", "url": "https://example.org"},
        "schema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"},
                "url": {"type": "string", "default": "https://example.org"},
                "headers": {"type": "object", "default": {}},
                "data": {"type": "string", "default": ""},
            },
            "required": ["method", "url"],
        },
    },
    {
        "key": "shell_command",
        "name": "Shell Command",
        "params": {"cmd": "echo hello"},
        "schema": {
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "default": "echo hello"},
            },
            "required": ["cmd"],
        },
    },
]


@api.get("/connectors")
async def list_connectors() -> Dict[str, Any]:
    return {"items": CONNECTORS}


@api.post("/connectors/run")
async def run_connector(request: Request, body: Dict[str, Any]) -> Dict[str, Any]:
    _require_role(request, {"operator", "admin"})
    key = body.get("key")
    params = body.get("params", {})
    if not key:
        raise HTTPException(status_code=400, detail="missing key")
    run_id = str(uuid.uuid4())
    started_ts = time.time()
    add_entry(kind="connector_run", run_id=run_id, data={"key": key, "params": params, "ts": started_ts})

    try:
        if key == "shell_command":
            result = _run_shell_command(run_id, params)
        elif key == "http_request":
            result = await _run_http_request(run_id, params)
        else:
            raise HTTPException(status_code=400, detail=f"unknown connector: {key}")
        add_entry(kind="connector_done", run_id=run_id, data={"key": key, "ok": True, "result": result, "ts": time.time()})
        return {"status": "ok", "key": key, "run_id": run_id, "result": result}
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover - safety
        add_entry(kind="connector_done", run_id=run_id, data={"key": key, "ok": False, "error": str(e), "ts": time.time()})
        raise HTTPException(status_code=500, detail=str(e))


def _conn_log(run_id: str, message: str, kind: str = "connector_log") -> None:
    add_entry(kind=kind, run_id=run_id, data={"message": message, "ts": time.time()})


# --- Dev Auth endpoints (Phase 6) ---


class DevLogin(BaseModel):
    username: str
    role: str = "admin"
    password: str | None = None


@api.post("/auth/login")
async def dev_login(resp: Response, body: DevLogin) -> Dict[str, Any]:
    expected = os.environ.get("DEV_LOGIN_PASSWORD", os.environ.get("AGENT_SHARED_SECRET"))
    if expected and body.password and not hmac.compare_digest(body.password, expected):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = _sign_token({"sub": body.username, "role": body.role}, exp_s=3600, kind="session")
    resp.set_cookie("session", token, httponly=True, samesite="lax")
    return {"token": token, "role": body.role}


@api.post("/auth/sse_token")
async def dev_sse_token() -> Dict[str, Any]:
    token = _sign_token({"purpose": "sse"}, exp_s=300, kind="sse")
    return {"sse": token, "exp_s": 300}


def _validate_shell_args(args: List[str]) -> None:
    """
    Validate shell connector arguments to reduce risk from untrusted input.

    Ensures arguments are non-empty printable strings without control characters,
    and enforces simple length limits to avoid abuse.
    """
    # Limit the number of arguments to a reasonable amount.
    max_args = 32
    if len(args) > max_args:
        raise HTTPException(status_code=400, detail="too many command arguments")

    # Limit length of each argument and total combined length.
    max_arg_len = 512
    max_total_len = 4096
    total_len = 0

    for a in args:
        if not isinstance(a, str):
            raise HTTPException(status_code=400, detail="invalid command arguments")
        if not a:
            raise HTTPException(status_code=400, detail="empty argument not allowed")
        # Reject arguments containing non-printable characters, including newlines and NULs.
        if not a.isprintable() or any(ch in a for ch in ("\n", "\r", "\x00")):
            raise HTTPException(status_code=400, detail="invalid characters in command arguments")
        if len(a) > max_arg_len:
            raise HTTPException(status_code=400, detail="command argument too long")
        total_len += len(a)
        if total_len > max_total_len:
            raise HTTPException(status_code=400, detail="command line too long")


def _run_shell_command(run_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # Use a hard-coded allowlist of commands. See CONNECTOR_SHELL_ALLOW above.
    allow = {c.lower() for c in CONNECTOR_SHELL_ALLOW}
    cmd_param = params.get("cmd")
    if not cmd_param:
        raise HTTPException(status_code=400, detail="missing cmd")

    # Require explicit list of arguments to avoid free-form shell-style parsing.
    if isinstance(cmd_param, list):
        args = [str(x) for x in cmd_param]
    else:
        raise HTTPException(status_code=400, detail="invalid cmd; expected list of arguments")

    if not args:
        raise HTTPException(status_code=400, detail="empty cmd")

    base = args[0].lower()
    if base not in allow:
        raise HTTPException(status_code=403, detail=f"command not allowed: {base}")

    # Validate arguments before executing the command.
    _validate_shell_args(args)

    timeout = int(os.environ.get("CONNECTOR_SHELL_TIMEOUT", "20"))
    _conn_log(run_id, f"exec: {' '.join(args)}")
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        start = time.time()
        output_lines: List[str] = []
        assert proc.stdout is not None
        while True:
            line = proc.stdout.readline()
            if line:
                output_lines.append(line.rstrip())
                _conn_log(run_id, line.rstrip())
            if proc.poll() is not None:
                break
            if time.time() - start > timeout:
                proc.kill()
                _conn_log(run_id, f"timeout after {timeout}s", kind="connector_error")
                raise HTTPException(status_code=408, detail="command timeout")
        rc = proc.returncode
        _conn_log(run_id, f"exit code: {rc}")
        return {"rc": rc, "lines": output_lines[-100:]}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"command not found: {base}")


async def _run_http_request(run_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    import httpx

    method = str(params.get("method", "GET")).upper()
    url = str(params.get("url", "")).strip()
    data = params.get("data")
    headers = params.get("headers", {})
    if method not in {"GET", "POST"}:
        raise HTTPException(status_code=400, detail="method not allowed")
    if not url:
        raise HTTPException(status_code=400, detail="missing url")
    pr = urlparse(url)
    if pr.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="invalid scheme")
    allowed_hosts = {h.strip().lower() for h in os.environ.get("ALLOWED_HTTP_HOSTS", "example.org,localhost,127.0.0.1").split(",") if h.strip()}
    if pr.hostname and pr.hostname.lower() not in allowed_hosts:
        raise HTTPException(status_code=403, detail=f"host not allowed: {pr.hostname}")
    _conn_log(run_id, f"http {method} {url}")
    timeout = httpx.Timeout(10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, headers=headers, data=data)
    _conn_log(run_id, f"status {resp.status_code}")
    snippet = resp.text[:2000] if resp.text else ""
    add_entry(kind="http_response", run_id=run_id, data={"url": url, "status": resp.status_code, "body_snippet": snippet})
    return {"status": resp.status_code, "length": len(resp.content)}


@app.post("/publish")
async def publish_to_bus(message: BusMessage) -> JSONResponse:
    """Endpoint to publish a message to the bus."""
    if not bus:
        return JSONResponse(status_code=503, content={"detail": "Message bus not configured"})
    await bus.publish(message.topic, json.dumps(message.data))
    return JSONResponse(content={"status": "published", "topic": message.topic})


@app.get("/rankings")
async def get_rankings_endpoint() -> List[Tuple[str, int]]:
    """Returns the current point rankings."""
    return get_rankings()


@app.post("/assign_badge")
async def assign_badge_endpoint(user_id: str, badge_name: str) -> Dict[str, str]:
    """Assigns a badge to a user."""
    assign_badge(user_id, badge_name)
    return {"status": "badge assigned"}


@app.exception_handler(Exception)
async def _unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    summary = error_summary.summarize(trace)
    social_hooks.notify_error(summary)
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# --- RBAC (Phase 6 Prep) ---


def _rbac_mode() -> str:
    return os.environ.get("RBAC_MODE", "disabled").lower()  # disabled|log|enforce


def _get_user_role(request: Request) -> str:
    role = request.headers.get("x-user-role") or ""
    if role:
        return role.lower()
    # Future: parse JWT from Authorization header for role claims
    return "viewer"


def _require_role(request: Request, allowed: set[str]) -> None:
    mode = _rbac_mode()
    if mode == "disabled":
        return
    role = _get_user_role(request)
    ok = role in allowed or role == "admin"
    if ok:
        return
    detail = {"detail": "forbidden", "role": role, "allowed": sorted(list(allowed))}
    add_entry(kind="rbac_denied", data=detail)
    if mode == "log":
        logger.warning("RBAC denied (log mode): %s", detail)
        return
    raise HTTPException(status_code=403, detail=detail)
