"""FastAPI backend providing chat and log streaming services."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict
import logging
import traceback
import redis
from prometheus_client import Counter

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

from core import error_summary
from integrations import social_hooks

from .config import settings
from . import db
from .db import close_db, init_db, ping_db
from .models import NodeConfig, SeedBody
from .redis_bus import get_redis, publish, psubscribe, subscribe
from .security import validate_token, validate_ws_token

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

REDIS_READYZ_FAILURES = Counter(
    "redis_readyz_failure_total",
    "Count of redis readiness check failures",
    ["reason"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()


app = FastAPI(title="Cloudhabil CLI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

# Node data is stored in the database; helper functions are in ``server.db``.


@app.get("/healthz")
async def healthz() -> Dict[str, bool]:
    return {"ok": True}


@app.get("/readyz")
async def readyz() -> Dict[str, bool]:
    db_ok = await ping_db()
    try:
        redis_ok = bool(await get_redis().ping())
    except redis.exceptions.ConnectionError as exc:
        logger.error("Redis connection error during readyz: %s", exc)
        REDIS_READYZ_FAILURES.labels(reason="connection_error").inc()
        redis_ok = False
    except redis.exceptions.TimeoutError as exc:
        logger.error("Redis timeout error during readyz: %s", exc)
        REDIS_READYZ_FAILURES.labels(reason="timeout_error").inc()
        redis_ok = False
    if not (db_ok and redis_ok):
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"db": db_ok, "redis": redis_ok}


@app.get("/api/nodes", dependencies=[Depends(validate_token)])
async def nodes_list() -> list[Dict[str, Any]]:
    return await db.list_nodes()


@app.post("/api/nodes/{node_id}/start", dependencies=[Depends(validate_token)])
async def node_start(node_id: str) -> Dict[str, Any]:
    n = await db.set_node_status(node_id, "running")
    await publish(
        f"logs:{node_id}",
        {"type": "log", "level": "INFO", "node_id": node_id, "line": f"{node_id} started"},
    )
    return {"ok": True, "id": n["id"], "status": n["status"]}


@app.post("/api/nodes/{node_id}/stop", dependencies=[Depends(validate_token)])
async def node_stop(node_id: str) -> Dict[str, Any]:
    n = await db.set_node_status(node_id, "stopped")
    await publish(
        f"logs:{node_id}",
        {"type": "log", "level": "INFO", "node_id": node_id, "line": f"{node_id} stopped"},
    )
    return {"ok": True, "id": n["id"], "status": n["status"]}


@app.get("/api/nodes/{node_id}/config", dependencies=[Depends(validate_token)])
async def node_get_config(node_id: str) -> Dict[str, Any]:
    return await db.get_node_config(node_id)


@app.put("/api/nodes/{node_id}/config", dependencies=[Depends(validate_token)])
async def node_put_config(node_id: str, cfg: NodeConfig) -> Dict[str, Any]:
    n = await db.update_node_config(node_id, cfg.model_dump())
    return {"ok": True, "id": node_id, "config": n["config"]}


@app.post("/api/files/upload", dependencies=[Depends(validate_token)])
async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    os.makedirs(".uploads", exist_ok=True)
    safe_name = Path(file.filename or "upload.bin").name
    allowed_extensions = {
        ".txt",
        ".md",
        ".json",
        ".csv",
        ".bin",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
    }
    if allowed_extensions and Path(safe_name).suffix.lower() not in allowed_extensions:
        await file.close()
        raise HTTPException(status_code=400, detail="File extension not allowed")
    path = os.path.join(".uploads", safe_name)
    if file.size is not None and file.size > MAX_UPLOAD_SIZE:
        await file.close()
        raise HTTPException(status_code=413, detail="File too large")
    size = 0
    try:
        with open(path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="File too large")
                f.write(chunk)
    except HTTPException:
        if os.path.exists(path):
            os.remove(path)
        raise
    finally:
        await file.close()
    return {"ok": True, "filename": file.filename}


@app.post("/api/actions/sesamawake", dependencies=[Depends(validate_token)])
async def sesamawake() -> Dict[str, bool]:
    events = [
        ("pipeline:configure_services", {"action": "configure_services"}),
        ("pipeline:ticket", {"action": "ticket"}),
        ("pipeline:slack_summary", {"action": "slack_summary"}),
        ("pipeline:kpi_update", {"action": "kpi_update"}),
    ]
    for channel, payload in events:
        await publish(channel, payload)
        await publish(
            "logs:sesamawake",
            {
                "type": "log",
                "level": "INFO",
                "action": payload["action"],
                "line": f"{payload['action']} triggered",
            },
        )
    return {"ok": True}


@app.post("/api/chat/{node_id}/seed", dependencies=[Depends(validate_token)])
async def chat_seed(node_id: str, body: SeedBody) -> Dict[str, Any]:
    if not await ping_db():
        raise HTTPException(status_code=503, detail="Database unavailable")
    pool = db.pool
    assert pool is not None
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO chat_seeds(node_id, text, meta) VALUES($1, $2, $3)",
            node_id,
            body.text,
            json.dumps(body.meta or {}),
        )
    await publish(
        f"chat:{node_id}:in",
        {"type": "seed", "text": body.text, "meta": body.meta or {}, "node_id": node_id},
    )
    return {"ok": True, "node_id": node_id, "ack": body.text}


@app.websocket("/ws/chat/{node_id}", dependencies=[Depends(validate_ws_token)])
async def ws_chat(ws: WebSocket, node_id: str) -> None:
    await ws.accept()
    alive = True

    async def pinger() -> None:
        while alive:
            await asyncio.sleep(15)
            try:
                await ws.send_json({"type": "ping", "ts": asyncio.get_event_loop().time()})
            except Exception:
                break

    ping_task = asyncio.create_task(pinger())

    async def forwarder() -> None:
        async for payload in subscribe(f"chat:{node_id}:out"):
            await ws.send_json(payload)

    fwd_task = asyncio.create_task(forwarder())
    try:
        await ws.send_json({"type": "hello", "node_id": node_id, "protocol": 1})
        while True:
            raw = await ws.receive_text()
            try:
                obj = json.loads(raw)
            except Exception:
                obj = {"type": "send", "text": raw}
            if obj.get("type") == "ping":
                await ws.send_json({"type": "pong"})
                continue
            await publish(f"chat:{node_id}:in", obj)
    except WebSocketDisconnect:
        pass
    finally:
        alive = False
        ping_task.cancel()
        fwd_task.cancel()


@app.websocket("/ws/logs/{node_id}", dependencies=[Depends(validate_ws_token)])
async def ws_logs_node(ws: WebSocket, node_id: str) -> None:
    await ws.accept()
    node = await db.get_node(node_id)
    await ws.send_json({"type": "status", "node_id": node_id, "status": node["status"]})
    try:
        async for payload in subscribe(f"logs:{node_id}"):
            await ws.send_json(payload)
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/logs", dependencies=[Depends(validate_ws_token)])
async def ws_logs_global(ws: WebSocket) -> None:
    await ws.accept()
    try:
        async for _, payload in psubscribe("logs:*"):
            await ws.send_json(payload)
    except WebSocketDisconnect:
        pass




@app.exception_handler(Exception)
async def _unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """Summarize and notify on uncaught exceptions."""
    trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    summary = error_summary.summarize(trace)
    social_hooks.notify_error(summary)
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
