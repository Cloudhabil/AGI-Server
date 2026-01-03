import asyncio
import json
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from skills.conscience.memory.skill import MemoryStore, MemorySkill
from skills.base import SkillCategory, SkillContext
from alpha import AlphaAgent


REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "skills" / "conscience" / "memory" / "store" / "memories.db"
TEMPLATES_DIR = REPO_ROOT / "templates"
STATIC_DIR = REPO_ROOT / "static"
PAUSE_FLAG = REPO_ROOT / "runs" / "heartbeat.pause"
SKILL_INDEXER = REPO_ROOT / "skills" / "system" / "skill-indexer" / "scripts" / "index_skills.py"

app = FastAPI(title="Cognitive Interface", version="1.0.0")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
memory_store = MemoryStore(DB_PATH)

# Lazy-loaded skills
_memory_skill: Optional[MemorySkill] = None
_mindset_skill = None
_self_skill = None
_skill_context = SkillContext(agent_role="ui")

# Alpha agent runtime
_alpha_lock = threading.Lock()
_alpha_thread: Optional[threading.Thread] = None
_alpha_stop: Optional[threading.Event] = None
_alpha_agent: Optional[AlphaAgent] = None
_alpha_config = {"mode": "propose", "interval_s": 300, "max_memory": 20000}
_alpha_last_error: Optional[str] = None

# =============================================================================
# TRAINING / NEURAL HUD STATE
# =============================================================================
_training_lock = threading.Lock()
_training_session: Optional[Dict[str, Any]] = None
_gradient_history: List[Dict[str, Any]] = []
_checkpoints: List[Dict[str, Any]] = []
_adapters: List[Dict[str, Any]] = []
_audit_logs: List[Dict[str, Any]] = []
_audit_enabled: bool = False
_gradient_monitor = None

def _get_gradient_monitor():
    """Lazy-load GradientMonitor from micro_tune_auditor."""
    global _gradient_monitor
    if _gradient_monitor is None:
        try:
            from micro_tune_auditor import GradientMonitor
            import torch
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _gradient_monitor = GradientMonitor(device)
        except Exception as e:
            print(f"[Training] Could not init GradientMonitor: {e}")
    return _gradient_monitor

def _get_device_info() -> Dict[str, Any]:
    """Get GPU device information."""
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return {
                "available": True,
                "name": name,
                "memory_gb": round(memory, 2),
                "is_rtx_4070": "4070" in name
            }
    except:
        pass
    return {"available": False, "name": "CPU", "memory_gb": 0, "is_rtx_4070": False}

def _log_audit(action: str, actor: str = "system", severity: str = "info", **details):
    """Add entry to audit log."""
    global _audit_logs
    import uuid
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": actor,
        "action": action,
        "severity": severity,
        "details": details
    }
    _audit_logs.append(entry)
    # Keep last 1000 entries
    if len(_audit_logs) > 1000:
        _audit_logs = _audit_logs[-1000:]
    return entry

def _get_memory_skill() -> MemorySkill:
    global _memory_skill
    if _memory_skill is None:
        _memory_skill = MemorySkill(use_mshr=True)
    return _memory_skill

def _get_mindset_skill():
    global _mindset_skill
    if _mindset_skill is None:
        try:
            from skills.conscience.mindset.skill import MindsetSkill
            _mindset_skill = MindsetSkill()
        except ImportError:
            pass
    return _mindset_skill

def _get_self_skill():
    global _self_skill
    if _self_skill is None:
        try:
            from skills.conscience.self.skill import SelfSkill
            _self_skill = SelfSkill()
        except ImportError:
            pass
    return _self_skill

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
clients = set()

# Request models
class ChatRequest(BaseModel):
    message: str

class FixEmbeddingRequest(BaseModel):
    memory_id: Optional[str] = None
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# =============================================================================
# TRAINING / NEURAL HUD MODELS
# =============================================================================

class GradientMetric(BaseModel):
    """Single gradient measurement for Neural HUD."""
    step: int
    timestamp: str
    gradient_norm: float
    learning_rate: float = 0.0001
    memory_usage_mb: float = 0.0
    is_clipped: bool = False


class DeviceInfo(BaseModel):
    """GPU/Device information."""
    available: bool
    name: str = "Unknown"
    memory_gb: float = 0.0
    is_rtx_4070: bool = False


class TrainingSessionConfig(BaseModel):
    """Configuration for training session."""
    name: str = "default"
    target_module: str = "attn"
    learning_rate: float = 0.0001
    max_steps: int = 1000
    gradient_clip: float = 1.0


class TrainingSession(BaseModel):
    """Active training session state."""
    session_id: str
    name: str
    status: str = "idle"  # idle, initializing, training, validating, completed, failed
    current_step: int = 0
    total_steps: int = 1000
    current_loss: float = 0.0
    gradient_history: List[GradientMetric] = []
    logs: List[str] = []
    created_at: str = ""
    config: Optional[TrainingSessionConfig] = None


class Checkpoint(BaseModel):
    """Training checkpoint."""
    id: str
    name: str
    step: int
    val_loss: float
    created_at: str
    path: str
    is_active: bool = False


class Adapter(BaseModel):
    """LoRA adapter model."""
    id: str
    name: str
    base_model: str
    rank: int = 16
    alpha: float = 32.0
    is_active: bool = False
    version: int = 1
    created_at: str = ""
    path: str = ""


class AuditLogEntry(BaseModel):
    """Audit log entry."""
    id: str
    timestamp: str
    actor: str = "system"  # system, user, auto-tuner
    action: str
    severity: str = "info"  # info, warning, critical
    details: Dict[str, Any] = {}


class CorrectionPayload(BaseModel):
    """Feedback/correction for tuning."""
    session_id: str
    prompt: str
    model_output: str
    user_correction: str
    rating: int = 1  # 1 or -1

class MemoryRequest(BaseModel):
    content: str
    memory_type: str = "semantic"
    importance: float = 0.5

class ReflectRequest(BaseModel):
    topic: str

class AnalyzeRequest(BaseModel):
    problem: str
    pattern: str = "balanced"

class GoalPriority(BaseModel):
    id: str
    priority: float

class GoalsReorderRequest(BaseModel):
    goals: List[GoalPriority]


class AlphaConfigRequest(BaseModel):
    mode: Optional[str] = None
    interval_s: Optional[int] = None
    max_memory: Optional[int] = None


class AlphaMessageRequest(BaseModel):
    message: str


def _get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_skill_dir(file_path: str) -> Path:
    raw_path = Path(file_path)
    abs_path = raw_path if raw_path.is_absolute() else (REPO_ROOT / raw_path)
    abs_path = abs_path.resolve()

    if abs_path.suffix:
        skill_dir = abs_path.with_suffix("")
    else:
        skill_dir = abs_path

    skills_root = (REPO_ROOT / "skills").resolve()
    if not _is_relative_to(skill_dir, skills_root):
        raise ValueError("Skill path must be within repo skills directory.")

    return skill_dir


def _refresh_skill_index() -> None:
    if not SKILL_INDEXER.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(SKILL_INDEXER)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        print(f"Skill index refresh failed: {exc}")


@app.on_event("startup")
async def refresh_index_on_startup() -> None:
    _refresh_skill_index()


def _alpha_status() -> Dict[str, Any]:
    with _alpha_lock:
        running = _alpha_thread is not None and _alpha_thread.is_alive()
        status = _alpha_agent.status() if _alpha_agent else {}
        return {
            "running": running,
            "config": _alpha_config,
            "status": status,
            "last_error": _alpha_last_error,
        }


def _alpha_start(config: AlphaConfigRequest) -> Dict[str, Any]:
    global _alpha_thread, _alpha_stop, _alpha_agent, _alpha_last_error
    with _alpha_lock:
        if _alpha_thread and _alpha_thread.is_alive():
            if config.mode or config.interval_s or config.max_memory:
                _alpha_config.update({k: v for k, v in config.dict().items() if v is not None})
                if _alpha_agent:
                    _alpha_agent.update_config(
                        _alpha_config.get("mode"),
                        _alpha_config.get("interval_s"),
                        _alpha_config.get("max_memory"),
                    )
            return _alpha_status()

        _alpha_config.update({k: v for k, v in config.dict().items() if v is not None})
        _alpha_stop = threading.Event()
        _alpha_agent = AlphaAgent(
            interval_s=_alpha_config.get("interval_s"),
            mode=_alpha_config.get("mode", "propose"),
            max_memory=_alpha_config.get("max_memory"),
        )
        _alpha_thread = threading.Thread(
            target=_alpha_agent.start, args=(_alpha_stop,), daemon=True
        )
        _alpha_thread.start()
        _alpha_last_error = None
        return _alpha_status()


def _alpha_stop_agent() -> Dict[str, Any]:
    with _alpha_lock:
        if _alpha_stop:
            _alpha_stop.set()
        return _alpha_status()


def _alpha_run_once() -> Dict[str, Any]:
    global _alpha_agent
    with _alpha_lock:
        if _alpha_agent is None:
            _alpha_agent = AlphaAgent(
                interval_s=_alpha_config.get("interval_s"),
                mode=_alpha_config.get("mode", "propose"),
                max_memory=_alpha_config.get("max_memory"),
            )
        return _alpha_agent.run_once()


@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request) -> HTMLResponse:
    conn = _get_db_connection()

    identity_rows = conn.execute("SELECT key, value FROM identity").fetchall()
    identity = {row["key"]: row["value"] for row in identity_rows}

    memory_rows = conn.execute(
        """
        SELECT id, content, memory_type, timestamp, importance, context
        FROM memories
        ORDER BY timestamp DESC
        LIMIT 15
        """
    ).fetchall()

    memories = [
        {
            "id": row["id"],
            "content": row["content"],
            "memory_type": row["memory_type"],
            "timestamp": row["timestamp"],
            "importance": row["importance"],
            "context": row["context"],
        }
        for row in memory_rows
    ]

    goals = conn.execute(
        """
        SELECT objective, status, priority
        FROM goals
        WHERE status != 'completed'
        ORDER BY priority DESC
        """
    ).fetchall()

    learned_rows = conn.execute(
        """
        SELECT content, timestamp
        FROM memories
        WHERE content LIKE 'Learned skill created:%'
           OR content LIKE 'Extracted skill requirement from task:%'
        ORDER BY timestamp DESC
        LIMIT 25
        """
    ).fetchall()

    conn.close()

    # Get registered skills from the registry
    registered_skills = []
    try:
        from skills.loader import SkillLoader
        from skills.registry import get_registry
        loader = SkillLoader()
        loader.scan_all(lazy=True)  # Light scan - no code loading
        registry = get_registry()
        skill_metas = registry.list_skills()
        skill_metas_sorted = sorted(skill_metas, key=lambda m: m.id)
        for meta in skill_metas_sorted:
            registered_skills.append({
                "id": meta.id,
                "name": meta.name,
                "category": meta.category.value if hasattr(meta.category, 'value') else str(meta.category),
                "level": meta.level.value if hasattr(meta.level, 'value') else str(meta.level),
            })
    except Exception as e:
        print(f"Failed to load skills: {e}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "name": identity.get("name", "Unknown Agent"),
            "purpose": identity.get("purpose", "No defined purpose"),
            "memories": memories,
            "goals": goals,
            "learned_skills": learned_rows,
            "registered_skills": registered_skills,
        },
    )


@app.get("/stream")
async def stream_memories() -> StreamingResponse:
    async def event_generator():
        last_ts = None
        while True:
            conn = _get_db_connection()
            if last_ts:
                rows = conn.execute(
                    """
                    SELECT id, content, memory_type, timestamp, importance, context
                    FROM memories
                    WHERE timestamp > ?
                    ORDER BY timestamp ASC
                    LIMIT 50
                    """,
                    (last_ts,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, content, memory_type, timestamp, importance, context
                    FROM memories
                    ORDER BY timestamp DESC
                    LIMIT 20
                    """
                ).fetchall()[::-1]
            conn.close()

            if rows:
                last_ts = rows[-1]["timestamp"]
                payload = [
                    {
                        "id": row["id"],
                        "content": row["content"],
                        "memory_type": row["memory_type"],
                        "timestamp": row["timestamp"],
                        "importance": row["importance"],
                        "context": row["context"],
                    }
                    for row in rows
                ]
                yield f"data: {json.dumps(payload)}\n\n"

            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.websocket("/ws")
async def websocket_memories(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        last_ts = None
        while True:
            conn = _get_db_connection()
            if last_ts:
                rows = conn.execute(
                    """
                    SELECT id, content, memory_type, timestamp, importance, context
                    FROM memories
                    WHERE timestamp > ?
                    ORDER BY timestamp ASC
                    LIMIT 50
                    """,
                    (last_ts,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, content, memory_type, timestamp, importance, context
                    FROM memories
                    ORDER BY timestamp DESC
                    LIMIT 20
                    """
                ).fetchall()[::-1]
            conn.close()

            if rows:
                last_ts = rows[-1]["timestamp"]
                payload = [
                    {
                        "id": row["id"],
                        "content": row["content"],
                        "memory_type": row["memory_type"],
                        "timestamp": row["timestamp"],
                        "importance": row["importance"],
                        "context": row["context"],
                    }
                    for row in rows
                ]
                await websocket.send_text(json.dumps(payload))

            await asyncio.sleep(2)
    except WebSocketDisconnect:
        clients.discard(websocket)


@app.post("/goal")
async def add_goal(objective: str = Form(...)) -> RedirectResponse:
    memory_store.create_goal(
        objective=objective,
        origin="user_ui",
        priority=0.8,
    )
    return RedirectResponse(url="/", status_code=303)


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port, log_level="error")


@app.post("/execute")
async def execute_generator() -> RedirectResponse:
    from skills.loader import SkillLoader
    from skills.registry import get_registry
    from skills.base import SkillContext

    SkillLoader().scan_all(lazy=False)
    reg = get_registry()
    reg.execute_skill(
        "system/intelligent-generator",
        {"action": "verify"},
        SkillContext(agent_role="ui"),
    )
    return RedirectResponse(url="/", status_code=303)


@app.post("/chat")
async def post_chat(message: str = Form(...)) -> RedirectResponse:
    conn = _get_db_connection()
    conn.execute(
        """
        INSERT INTO memories (id, content, memory_type, importance, timestamp, context)
        VALUES (hex(randomblob(16)), ?, 'episodic', ?, datetime('now'), ?)
        """,
        (message, 0.4, "{\"source\":\"ui_chat\"}"),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/status")
async def api_status() -> JSONResponse:
    """Get system status including compute devices."""
    import subprocess

    # Check Ollama models
    ollama_models = []
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[1:]:
                if line.strip():
                    parts = line.split()
                    if parts:
                        ollama_models.append(parts[0])
    except Exception:
        pass

    # Check GPU
    gpu_info = {"available": False, "name": "N/A", "memory": "N/A"}
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info = {
                "available": True,
                "name": torch.cuda.get_device_name(0),
                "memory": f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB",
            }
    except Exception:
        pass

    # Check NPU
    npu_info = {"available": False}
    try:
        from core.npu_utils import has_npu
        npu_info["available"] = has_npu()
    except Exception:
        pass

    # Memory stats
    conn = _get_db_connection()
    memory_counts = {}
    current_stage = "UNKNOWN"
    try:
        rows = conn.execute(
            "SELECT memory_type, COUNT(*) as cnt FROM memories GROUP BY memory_type"
        ).fetchall()
        memory_counts = {row["memory_type"]: row["cnt"] for row in rows}

        stage_row = conn.execute(
            """
            SELECT context
            FROM memories
            WHERE content LIKE 'Heartbeat #%'
            ORDER BY timestamp DESC
            LIMIT 1
            """
        ).fetchone()
        if stage_row and stage_row["context"]:
            try:
                ctx = json.loads(stage_row["context"])
                current_stage = ctx.get("observations_summary", {}).get("stage", ctx.get("stage", "UNKNOWN"))
            except json.JSONDecodeError:
                current_stage = "UNKNOWN"
    except Exception:
        pass
    conn.close()

    return JSONResponse({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "compute": {
            "gpu": gpu_info,
            "npu": npu_info,
            "models": ollama_models,
        },
        "memory": {
            "total": sum(memory_counts.values()),
            "by_type": memory_counts,
        }
        ,
        "control_plane": {
            "stage": current_stage,
        }
        ,
        "heartbeat": {
            "paused": PAUSE_FLAG.exists(),
        }
    })


@app.get("/api/memories")
async def api_memories(
    memory_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> JSONResponse:
    """Get memories with optional filtering."""
    conn = _get_db_connection()

    if memory_type:
        rows = conn.execute(
            """
            SELECT id, content, memory_type, timestamp, importance, context
            FROM memories
            WHERE memory_type = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (memory_type, limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, content, memory_type, timestamp, importance, context
            FROM memories
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    conn.close()

    memories = [
        {
            "id": row["id"],
            "content": row["content"],
            "memory_type": row["memory_type"],
            "timestamp": row["timestamp"],
            "importance": row["importance"],
            "context": json.loads(row["context"]) if row["context"] else {},
        }
        for row in rows
    ]

    return JSONResponse({"memories": memories, "count": len(memories)})


@app.post("/api/memories/recall")
async def api_recall(request: Request) -> JSONResponse:
    """Semantic memory recall using MSHR."""
    body = await request.json()
    query = body.get("query", "")
    memory_types = body.get("memory_types")
    limit = body.get("limit", 5)

    skill = _get_memory_skill()
    result = skill.execute({
        "capability": "recall",
        "query": query,
        "memory_types": memory_types,
        "limit": limit,
    }, _skill_context)

    if result.success:
        return JSONResponse(result.output)
    return JSONResponse({"error": result.error}, status_code=500)


@app.post("/api/memories/store")
async def api_store_memory(req: MemoryRequest) -> JSONResponse:
    """Store a new memory."""
    skill = _get_memory_skill()
    result = skill.execute({
        "capability": "experience",
        "content": req.content,
        "memory_type": req.memory_type,
        "importance": req.importance,
    }, _skill_context)

    if result.success:
        return JSONResponse({"success": True, "memory_id": result.output.get("memory_id")})
    return JSONResponse({"error": result.error}, status_code=500)


@app.get("/api/memories/stats")
async def api_memory_stats() -> JSONResponse:
    """Get detailed memory statistics."""
    skill = _get_memory_skill()
    stats = skill.store.get_stats()

    # Get MSHR index stats if available
    mshr_stats = {}
    if skill._mshr:
        for mt, idx in skill._mshr.indexes.items():
            mshr_stats[mt.value] = {
                "count": len(idx.ids),
                "threshold": idx.config.similarity_threshold,
            }

    return JSONResponse({
        "stats": stats,
        "mshr": mshr_stats,
    })


@app.post("/api/memories/mshr/rebuild")
async def api_mshr_rebuild() -> JSONResponse:
    """Rebuild MSHR indexes from stored memories."""
    skill = _get_memory_skill()
    success = skill.rebuild_mshr()
    if not success:
        return JSONResponse({"success": False, "error": "MSHR rebuild failed"}, status_code=500)
    stats = skill._mshr.get_stats() if skill._mshr else {}
    return JSONResponse({"success": True, "mshr": stats})


@app.post("/api/fix/embedding_model")
async def api_fix_embedding_model(req: FixEmbeddingRequest) -> JSONResponse:
    """Force a rebuild of the embedding indexes to fix dimension mismatches."""
    skill = _get_memory_skill()
    success = skill.rebuild_mshr()
    if success:
        try:
            skill.execute({
                "capability": "experience",
                "content": "Embedding model rebuild executed via force fix.",
                "memory_type": "procedural",
                "importance": 0.6,
                "context": {
                    "source": "api/fix/embedding_model",
                    "memory_id": req.memory_id,
                    "context": req.context or {},
                },
            }, _skill_context)
        except Exception:
            pass
        stats = skill._mshr.get_stats() if skill._mshr else {}
        return JSONResponse({
            "success": True,
            "message": "Embedding indexes rebuilt.",
            "mshr": stats,
        })
    return JSONResponse({"success": False, "error": "Embedding rebuild failed"}, status_code=500)


@app.post("/api/mindset/analyze")
async def api_analyze(req: AnalyzeRequest) -> JSONResponse:
    """Analyze a problem using MindsetSkill."""
    skill = _get_mindset_skill()
    if not skill:
        return JSONResponse({"error": "MindsetSkill not available"}, status_code=503)

    result = skill.execute({
        "capability": "analyze",
        "problem": req.problem,
        "pattern": req.pattern,
        "store_reasoning": False,
    }, _skill_context)

    if result.success:
        return JSONResponse(result.output)
    return JSONResponse({"error": result.error}, status_code=500)


@app.post("/api/self/reflect")
async def api_reflect(req: ReflectRequest) -> JSONResponse:
    """Self-reflection using SelfSkill."""
    skill = _get_self_skill()
    if not skill:
        return JSONResponse({"error": "SelfSkill not available"}, status_code=503)

    result = skill.execute({
        "capability": "reflect",
        "topic": req.topic,
        "store": False,
    }, _skill_context)

    if result.success:
        return JSONResponse(result.output)
    return JSONResponse({"error": result.error}, status_code=500)


@app.get("/api/self/identity")
async def api_identity() -> JSONResponse:
    """Get identity information."""
    conn = _get_db_connection()

    try:
        identity_rows = conn.execute("SELECT key, value FROM identity").fetchall()
        identity = {row["key"]: row["value"] for row in identity_rows}
    except Exception:
        identity = {"name": "Cognitive Agent", "purpose": "Autonomous cognition"}

    conn.close()
    return JSONResponse(identity)


@app.get("/api/goals")
async def api_goals(status: Optional[str] = None) -> JSONResponse:
    """Get goals with optional status filter."""
    conn = _get_db_connection()

    if status:
        rows = conn.execute(
            "SELECT * FROM goals WHERE status = ? ORDER BY priority DESC",
            (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM goals ORDER BY priority DESC"
        ).fetchall()

    conn.close()

    goals = [dict(row) for row in rows]
    return JSONResponse({"goals": goals})


@app.post("/api/goals/reorder")
async def api_goals_reorder(req: GoalsReorderRequest) -> JSONResponse:
    """Update goal priorities based on drag-and-drop order."""
    conn = _get_db_connection()
    updates = [(goal.priority, goal.id) for goal in req.goals]
    conn.executemany("UPDATE goals SET priority = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()
    return JSONResponse({"updated": len(updates)})


@app.post("/api/chat")
async def api_chat(req: ChatRequest) -> JSONResponse:
    """Return a full chat response using local LLMs."""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen3:latest",
                    "prompt": req.message,
                    "stream": False,
                    "keep_alive": -1,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return JSONResponse({"reply": data.get("response", "")})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/chat/stream")
async def api_chat_stream(req: ChatRequest) -> StreamingResponse:
    """Stream a chat response using GPIA orchestrator with multi-model routing."""
    import httpx
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # Thread pool for running sync GPIA code
    executor = ThreadPoolExecutor(max_workers=1)

    async def generate():
        try:
            # Phase 1: Initialize GPIA
            yield f"data: {json.dumps({'phase': 'init', 'text': '🧠 GPIA Initializing...\n'})}\n\n"

            from gpia import GPIA

            def run_gpia_sync():
                """Run GPIA synchronously in thread."""
                gpia = GPIA(verbose=False)
                return gpia.run(req.message)

            # Phase 2: Understanding (stream progress)
            yield f"data: {json.dumps({'phase': 'understand', 'text': '📊 Analyzing task intent...\n'})}\n\n"
            await asyncio.sleep(0.1)  # Allow UI to update

            # Phase 3: Execute GPIA in thread pool
            yield f"data: {json.dumps({'phase': 'execute', 'text': '⚡ Executing with PASS Protocol...\n'})}\n\n"

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, run_gpia_sync)

            # Phase 4: Stream results
            yield f"data: {json.dumps({'phase': 'result', 'model': 'GPIA'})}\n\n"

            # Skills used
            if result.skills_used:
                skills_text = f"**Skills:** {', '.join(result.skills_used[:5])}\n\n"
                yield f"data: {json.dumps({'text': skills_text})}\n\n"

            # Parse response - extract actual content from JSON if present
            response_text = result.response or ""

            # Try to extract from JSON wrapper
            if response_text.strip().startswith('{'):
                try:
                    parsed = json.loads(response_text)
                    if isinstance(parsed, dict):
                        # Try multiple possible keys
                        response_text = (
                            parsed.get('output') or
                            parsed.get('response') or
                            parsed.get('text') or
                            parsed.get('content') or
                            str(parsed)
                        )
                except json.JSONDecodeError:
                    # Try partial JSON extraction
                    import re
                    match = re.search(r'"output"\s*:\s*"([^"]*)"', response_text)
                    if match:
                        response_text = match.group(1)

            # Handle empty responses
            if not response_text or response_text.strip() in ['', '{}', 'null']:
                response_text = "*No response generated. The model may need more context or the query was too abstract.*"

            # Stream response in chunks
            chunk_size = 80
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                yield f"data: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0.015)

            # Metadata footer
            metadata = f"\n\n---\n*{result.execution_time:.2f}s | PASS: {result.pass_count} | Assists: {result.assist_count}*"
            yield f"data: {json.dumps({'text': metadata})}\n\n"

            yield f"data: {json.dumps({'done': True, 'success': result.success})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'text': f'❌ Error: {str(e)}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/heartbeat")
async def api_heartbeat() -> JSONResponse:
    """Get last heartbeat info from memories."""
    conn = _get_db_connection()

    rows = conn.execute(
        """
        SELECT content, timestamp, importance, context
        FROM memories
        WHERE content LIKE '%Heartbeat%'
        ORDER BY timestamp DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    heartbeats = [
        {
            "content": row["content"],
            "timestamp": row["timestamp"],
            "importance": row["importance"],
            "context": json.loads(row["context"]) if row["context"] else {},
        }
        for row in rows
    ]

    return JSONResponse({"heartbeats": heartbeats})


@app.get("/api/skills")
async def api_skills() -> JSONResponse:
    """Get all registered skills."""
    skills = []
    try:
        from skills.loader import SkillLoader
        from skills.registry import get_registry
        loader = SkillLoader()
        loader.scan_all(lazy=True)
        registry = get_registry()
        skill_metas = registry.list_skills()
        # Sort by skill ID
        skill_metas_sorted = sorted(skill_metas, key=lambda m: m.id)
        for meta in skill_metas_sorted:
            skills.append({
                "id": meta.id,
                "name": meta.name,
                "description": meta.description,
                "category": meta.category.value if hasattr(meta.category, 'value') else str(meta.category),
                "level": meta.level.value if hasattr(meta.level, 'value') else str(meta.level),
                "tags": meta.tags if hasattr(meta, 'tags') else [],
            })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"skills": skills, "count": len(skills)})


class SkillFromMemoryRequest(BaseModel):
    memory_id: Optional[str] = None
    content: str
    context: Optional[Dict[str, Any]] = None
    name: str
    description: str
    file_path: str


@app.post("/api/skills/create-from-memory")
async def api_create_skill_from_memory(req: SkillFromMemoryRequest) -> JSONResponse:
    """Create a new skill template from a memory item."""
    try:
        skill_dir = _resolve_skill_dir(req.file_path)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    if skill_dir.exists():
        return JSONResponse({"error": f"Skill directory already exists: {skill_dir}"}, status_code=400)

    skills_root = (REPO_ROOT / "skills").resolve()
    skill_id = str(skill_dir.relative_to(skills_root)).replace("\\", "/")
    skill_name = req.name.strip() or skill_id.replace("/", " ").replace("_", " ").title()
    description = req.description.strip() or req.content.strip()[:200]

    try:
        from skills.loader import SkillLoader

        loader = SkillLoader()
        loader.create_skill_template(
            directory=skill_dir,
            skill_id=skill_id,
            name=skill_name,
            description=description,
            category=SkillCategory.CODE,
        )

        readme_path = skill_dir / "README.md"
        memory_notes = (
            "\n\n## Source Memory\n\n"
            f"Memory ID: {req.memory_id or 'n/a'}\n\n"
            f"{req.content}\n"
        )
        readme_path.write_text(readme_path.read_text(encoding="utf-8") + memory_notes, encoding="utf-8")

        try:
            memory_skill = _get_memory_skill()
            memory_skill.execute({
                "capability": "experience",
                "content": f"Learned skill created: {skill_id}",
                "memory_type": "procedural",
                "importance": 0.7,
                "context": {
                    "source": "api/skills/create-from-memory",
                    "skill_id": skill_id,
                    "skill_path": str(skill_dir),
                },
            }, _skill_context)
        except Exception:
            pass

        _refresh_skill_index()

        return JSONResponse({
            "success": True,
            "skill_id": skill_id,
            "skill_path": str(skill_dir),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/alpha/status")
async def api_alpha_status() -> JSONResponse:
    return JSONResponse(_alpha_status())


@app.post("/api/alpha/start")
async def api_alpha_start(req: AlphaConfigRequest) -> JSONResponse:
    return JSONResponse(_alpha_start(req))


@app.post("/api/alpha/stop")
async def api_alpha_stop() -> JSONResponse:
    return JSONResponse(_alpha_stop_agent())


@app.post("/api/alpha/once")
async def api_alpha_once() -> JSONResponse:
    return JSONResponse(_alpha_run_once())


@app.post("/api/alpha/config")
async def api_alpha_config(req: AlphaConfigRequest) -> JSONResponse:
    return JSONResponse(_alpha_start(req))


@app.post("/api/alpha/message")
async def api_alpha_message(req: AlphaMessageRequest) -> JSONResponse:
    if _alpha_agent:
        _alpha_agent.handle_message(req.message)
    else:
        memory_skill = _get_memory_skill()
        memory_skill.execute({
            "capability": "experience",
            "content": f"Alpha message: {req.message}",
            "memory_type": "semantic",
            "importance": 0.6,
            "context": {"source": "alpha_message"},
        }, _skill_context)
    return JSONResponse({"success": True})


@app.get("/api/control/pause")
async def api_pause_status() -> JSONResponse:
    """Get heartbeat pause status."""
    return JSONResponse({"paused": PAUSE_FLAG.exists()})


@app.post("/api/control/pause")
async def api_pause() -> JSONResponse:
    """Pause the heartbeat loop by creating a flag file."""
    PAUSE_FLAG.parent.mkdir(parents=True, exist_ok=True)
    PAUSE_FLAG.write_text("paused", encoding="utf-8")
    return JSONResponse({"paused": True})


@app.post("/api/control/resume")
async def api_resume() -> JSONResponse:
    """Resume the heartbeat loop by removing the flag file."""
    if PAUSE_FLAG.exists():
        PAUSE_FLAG.unlink()
    return JSONResponse({"paused": False})


# ============================================================================
# WORKFLOW API - Autonomous Task Management with User Control
# ============================================================================

def _get_workflow_skill():
    """Lazy load the TaskWorkflowSkill."""
    try:
        from skills.system.task_workflow.skill import TaskWorkflowSkill
        return TaskWorkflowSkill()
    except ImportError:
        # Try alternate import path
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "task_workflow",
            Path(__file__).parent / "skills" / "system" / "task-workflow" / "skill.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.TaskWorkflowSkill()


@app.get("/api/workflows")
async def api_list_workflows(status: Optional[str] = None) -> JSONResponse:
    """List all workflows, optionally filtered by status."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "list",
            "status": status,
        }, SkillContext())

        if result.success:
            _refresh_skill_index()
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows")
async def api_create_workflow(request: Request) -> JSONResponse:
    """Create a new workflow from a goal or task list."""
    try:
        from skills.base import SkillContext
        body = await request.json()
        skill = _get_workflow_skill()

        result = skill.execute({
            "capability": "create",
            "goal": body.get("goal"),
            "tasks": body.get("tasks", []),
            "name": body.get("name"),
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output, status_code=201)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/workflows/{workflow_id}")
async def api_get_workflow(workflow_id: str) -> JSONResponse:
    """Get a specific workflow by ID."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "status",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/execute")
async def api_execute_workflow(workflow_id: str) -> JSONResponse:
    """Execute a workflow (queue it for processing)."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "execute",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/pause")
async def api_pause_workflow(workflow_id: str) -> JSONResponse:
    """Pause a running workflow."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "pause",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/resume")
async def api_resume_workflow(workflow_id: str) -> JSONResponse:
    """Resume a paused workflow."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "resume",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/cancel")
async def api_cancel_workflow(workflow_id: str) -> JSONResponse:
    """Cancel a workflow."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "cancel",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.patch("/api/workflows/{workflow_id}")
async def api_adapt_workflow(workflow_id: str, request: Request) -> JSONResponse:
    """Modify a workflow (add/remove/update tasks)."""
    try:
        from skills.base import SkillContext
        body = await request.json()
        skill = _get_workflow_skill()

        result = skill.execute({
            "capability": "adapt",
            "workflow_id": workflow_id,
            "modifications": body,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/workflows/{workflow_id}/autocomplete")
async def api_workflow_autocomplete(workflow_id: str) -> JSONResponse:
    """Get AI suggestions for next steps."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "autocomplete",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/tasks/{task_id}/approve")
async def api_approve_task(workflow_id: str, task_id: str) -> JSONResponse:
    """Approve a task waiting for user approval."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "approve",
            "workflow_id": workflow_id,
            "task_id": task_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/tasks/{task_id}/reject")
async def api_reject_task(workflow_id: str, task_id: str) -> JSONResponse:
    """Reject a task waiting for approval."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "reject",
            "workflow_id": workflow_id,
            "task_id": task_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/workflows/{workflow_id}/tasks/{task_id}/retry")
async def api_retry_task(workflow_id: str, task_id: str) -> JSONResponse:
    """Retry a failed task."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "retry",
            "workflow_id": workflow_id,
            "task_id": task_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.delete("/api/workflows/{workflow_id}")
async def api_delete_workflow(workflow_id: str) -> JSONResponse:
    """Delete a workflow."""
    try:
        from skills.base import SkillContext
        skill = _get_workflow_skill()
        result = skill.execute({
            "capability": "delete",
            "workflow_id": workflow_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# =============================================================================
# Model Reasoning Traces API
# =============================================================================

@app.get("/api/reasoning/latest")
async def api_latest_reasoning() -> JSONResponse:
    """Get latest reasoning traces from heartbeats for live display."""
    try:
        conn = _get_db_connection()
        rows = conn.execute("""
            SELECT id, content, memory_type, importance, context, timestamp
            FROM memories
            WHERE context LIKE '%model_trace%'
            ORDER BY timestamp DESC
            LIMIT 20
        """).fetchall()
        conn.close()

        traces = []
        for row in rows:
            try:
                ctx = json.loads(row["context"]) if row["context"] else {}
                model_trace = ctx.get("model_trace", {})

                # Extract analysis chain
                analysis_steps = model_trace.get("analysis", [])
                decision_steps = model_trace.get("decision", [])

                # Only include if there are actual traces
                if analysis_steps or decision_steps:
                    traces.append({
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "cycle": ctx.get("cycle", 0),
                        "duration_s": ctx.get("duration_s", 0),
                        "analysis": [
                            {
                                "model": step.get("model", "Unknown"),
                                "role": step.get("role", ""),
                                "thought": step.get("thought", "")[:500],
                                "duration_ms": step.get("duration_ms", 0),
                            }
                            for step in analysis_steps
                        ],
                        "decision": [
                            {
                                "model": step.get("model", "Unknown"),
                                "role": step.get("role", ""),
                                "thought": step.get("thought", "")[:500],
                                "duration_ms": step.get("duration_ms", 0),
                            }
                            for step in decision_steps
                        ],
                        "observations": ctx.get("observations_summary", {}),
                        "action": ctx.get("action", {}),
                    })
            except Exception:
                continue

        return JSONResponse({"traces": traces, "count": len(traces)})
    except Exception as e:
        return JSONResponse({"error": str(e), "traces": []}, status_code=500)


@app.get("/api/reasoning/stream")
async def api_reasoning_stream() -> StreamingResponse:
    """Stream reasoning traces as SSE for real-time display."""
    async def generate():
        last_id = ""
        while True:
            try:
                conn = _get_db_connection()
                rows = conn.execute("""
                    SELECT id, content, context, timestamp
                    FROM memories
                    WHERE context LIKE '%model_trace%'
                    ORDER BY timestamp DESC
                    LIMIT 5
                """).fetchall()
                conn.close()

                for row in rows:
                    if row["id"] != last_id:
                        last_id = row["id"]
                        ctx = json.loads(row["context"]) if row["context"] else {}
                        model_trace = ctx.get("model_trace", {})

                        if model_trace.get("analysis") or model_trace.get("decision"):
                            data = {
                                "id": row["id"],
                                "timestamp": row["timestamp"],
                                "cycle": ctx.get("cycle", 0),
                                "analysis": model_trace.get("analysis", []),
                                "decision": model_trace.get("decision", []),
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                            break

                await asyncio.sleep(3)
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(5)

    return StreamingResponse(generate(), media_type="text/event-stream")


# =============================================================================
# CI/CD Pipeline API
# =============================================================================

_cicd_skill = None

def _get_cicd_skill():
    global _cicd_skill
    if _cicd_skill is None:
        try:
            # Import using importlib due to hyphen in directory name
            import importlib
            cicd_module = importlib.import_module("skills.automation.cicd-pipeline.skill")
            _cicd_skill = cicd_module.CICDPipelineSkill()
        except Exception as e:
            print(f"CICDPipelineSkill not available: {e}")
    return _cicd_skill


class PipelineRunRequest(BaseModel):
    target: str = "."
    stages: Optional[List[str]] = None
    environment: str = "dev"


class SkillCreateRequest(BaseModel):
    id: str
    name: str
    description: str
    capabilities: List[str] = []
    category: str = "automation"


@app.get("/api/cicd/status")
async def api_cicd_status() -> JSONResponse:
    """Get CI/CD pipeline status."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "status",
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"status": "error", "error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/cicd/history")
async def api_cicd_history() -> JSONResponse:
    """Get pipeline run history."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "history",
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"runs": [], "error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/run")
async def api_cicd_run(request: PipelineRunRequest) -> JSONResponse:
    """Run a CI/CD pipeline."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "run",
            "target": request.target,
            "stages": request.stages,
            "environment": request.environment,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/validate")
async def api_cicd_validate(target: str = ".") -> JSONResponse:
    """Run validation stage (lint, type check)."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "validate",
            "target": target,
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/analyze")
async def api_cicd_analyze(target: str = ".") -> JSONResponse:
    """Run deep analysis stage (DeepSeek reasoning)."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "analyze",
            "target": target,
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/test")
async def api_cicd_test(target: str = ".") -> JSONResponse:
    """Run tests."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "test",
            "target": target,
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/build")
async def api_cicd_build(target: str = ".", environment: str = "dev") -> JSONResponse:
    """Build Docker image."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "build",
            "target": target,
            "environment": environment,
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/improve")
async def api_cicd_improve(target: str = ".") -> JSONResponse:
    """Generate AI improvements (Qwen3)."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "improve",
            "target": target,
        }, SkillContext())

        return JSONResponse(result.output if result.success else {"error": result.error})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/improve-skill/{skill_id:path}")
async def api_cicd_improve_skill(skill_id: str) -> JSONResponse:
    """Improve a specific skill using multi-model reasoning."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "improve_skill",
            "target": skill_id,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/create-skill")
async def api_cicd_create_skill(request: SkillCreateRequest) -> JSONResponse:
    """Create a new skill from specification."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "create_skill",
            "skill_spec": {
                "id": request.id,
                "name": request.name,
                "description": request.description,
                "capabilities": request.capabilities,
                "category": request.category,
            },
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cicd/deploy")
async def api_cicd_deploy(environment: str = "dev") -> JSONResponse:
    """Deploy to environment."""
    try:
        skill = _get_cicd_skill()
        if not skill:
            return JSONResponse({"error": "CI/CD skill not available"}, status_code=503)

        result = skill.execute({
            "capability": "deploy",
            "environment": environment,
        }, SkillContext())

        if result.success:
            return JSONResponse(result.output)
        return JSONResponse({"error": result.error}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# =============================================================================
# TRAINING / NEURAL HUD API ENDPOINTS
# =============================================================================

@app.get("/api/training/status")
async def api_training_status() -> JSONResponse:
    """Get training system status and device info."""
    device = _get_device_info()
    session = _training_session
    return JSONResponse({
        "device": device,
        "active": session is not None and session.get("status") == "training",
        "session_id": session.get("session_id") if session else None,
        "status": session.get("status") if session else "idle"
    })


@app.get("/api/training/gradients")
async def api_training_gradients(limit: int = 100) -> JSONResponse:
    """Get gradient history for Neural HUD visualization."""
    global _gradient_history
    # Return most recent gradients
    history = _gradient_history[-limit:] if _gradient_history else []
    return JSONResponse({"gradients": history, "count": len(history)})


@app.post("/api/training/session/start")
async def api_training_session_start(config: TrainingSessionConfig) -> JSONResponse:
    """Start a new training session."""
    global _training_session, _gradient_history
    import uuid

    with _training_lock:
        if _training_session and _training_session.get("status") == "training":
            return JSONResponse({"error": "Training session already active"}, status_code=409)

        session_id = str(uuid.uuid4())[:12]
        _training_session = {
            "session_id": session_id,
            "name": config.name,
            "status": "initializing",
            "current_step": 0,
            "total_steps": config.max_steps,
            "current_loss": 0.0,
            "config": config.dict(),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "logs": ["Session initialized"]
        }
        _gradient_history = []  # Reset history for new session

        _log_audit("training_session_started", actor="user", session_id=session_id, config=config.dict())

    return JSONResponse({"session_id": session_id, "status": "initializing"})


@app.get("/api/training/session/{session_id}")
async def api_training_session_get(session_id: str) -> JSONResponse:
    """Get training session details."""
    if not _training_session or _training_session.get("session_id") != session_id:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    return JSONResponse(_training_session)


@app.post("/api/training/session/{session_id}/stop")
async def api_training_session_stop(session_id: str) -> JSONResponse:
    """Stop a training session."""
    global _training_session

    with _training_lock:
        if not _training_session or _training_session.get("session_id") != session_id:
            return JSONResponse({"error": "Session not found"}, status_code=404)

        _training_session["status"] = "stopped"
        _training_session["logs"].append("Session stopped by user")
        _log_audit("training_session_stopped", actor="user", session_id=session_id)

    return JSONResponse({"status": "stopped"})


@app.post("/api/training/gradient")
async def api_training_gradient_record(metric: GradientMetric) -> JSONResponse:
    """Record a gradient measurement (called by training loop)."""
    global _gradient_history

    entry = metric.dict()
    _gradient_history.append(entry)

    # Keep last 10000 samples
    if len(_gradient_history) > 10000:
        _gradient_history = _gradient_history[-10000:]

    # Update session if active
    if _training_session:
        _training_session["current_step"] = metric.step

    return JSONResponse({"recorded": True})


@app.get("/api/training/stream")
async def api_training_stream(request: Request):
    """SSE stream for real-time training metrics."""
    async def event_generator():
        last_count = 0
        while True:
            if await request.is_disconnected():
                break

            current_count = len(_gradient_history)
            if current_count > last_count:
                # Send new gradients
                new_gradients = _gradient_history[last_count:]
                for g in new_gradients:
                    yield f"data: {json.dumps(g)}\n\n"
                last_count = current_count

            # Also send session status
            if _training_session:
                status = {
                    "type": "status",
                    "session_id": _training_session.get("session_id"),
                    "status": _training_session.get("status"),
                    "step": _training_session.get("current_step", 0),
                    "loss": _training_session.get("current_loss", 0)
                }
                yield f"data: {json.dumps(status)}\n\n"

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# =============================================================================
# CHECKPOINT API ENDPOINTS
# =============================================================================

@app.get("/api/training/checkpoints")
async def api_training_checkpoints() -> JSONResponse:
    """List all checkpoints."""
    return JSONResponse({"checkpoints": _checkpoints})


@app.post("/api/training/checkpoints")
async def api_training_checkpoint_create(name: str = "checkpoint") -> JSONResponse:
    """Save a new checkpoint."""
    global _checkpoints
    import uuid

    step = _training_session.get("current_step", 0) if _training_session else 0
    loss = _training_session.get("current_loss", 0) if _training_session else 0

    checkpoint = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "step": step,
        "val_loss": loss,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "path": f"checkpoints/{name}_{step}.pt",
        "is_active": False
    }
    _checkpoints.append(checkpoint)
    _log_audit("checkpoint_created", checkpoint_id=checkpoint["id"], step=step)

    return JSONResponse(checkpoint)


@app.post("/api/training/checkpoints/{checkpoint_id}/load")
async def api_training_checkpoint_load(checkpoint_id: str) -> JSONResponse:
    """Load a checkpoint."""
    global _checkpoints

    for cp in _checkpoints:
        if cp["id"] == checkpoint_id:
            # Deactivate all, activate this one
            for c in _checkpoints:
                c["is_active"] = False
            cp["is_active"] = True
            _log_audit("checkpoint_loaded", checkpoint_id=checkpoint_id)
            return JSONResponse({"loaded": True, "checkpoint": cp})

    return JSONResponse({"error": "Checkpoint not found"}, status_code=404)


# =============================================================================
# ADAPTER API ENDPOINTS
# =============================================================================

@app.get("/api/adapters")
async def api_adapters_list() -> JSONResponse:
    """List all LoRA adapters."""
    return JSONResponse({"adapters": _adapters})


@app.post("/api/adapters")
async def api_adapter_create(adapter: Adapter) -> JSONResponse:
    """Register a new adapter."""
    global _adapters

    adapter_dict = adapter.dict()
    adapter_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    _adapters.append(adapter_dict)
    _log_audit("adapter_created", adapter_id=adapter.id, name=adapter.name)

    return JSONResponse(adapter_dict)


@app.get("/api/adapters/{adapter_id}")
async def api_adapter_get(adapter_id: str) -> JSONResponse:
    """Get adapter details."""
    for adapter in _adapters:
        if adapter["id"] == adapter_id:
            return JSONResponse(adapter)
    return JSONResponse({"error": "Adapter not found"}, status_code=404)


@app.post("/api/adapters/{adapter_id}/activate")
async def api_adapter_activate(adapter_id: str) -> JSONResponse:
    """Activate an adapter (hot-swap into model)."""
    global _adapters

    for adapter in _adapters:
        if adapter["id"] == adapter_id:
            # Deactivate all, activate this one
            for a in _adapters:
                a["is_active"] = False
            adapter["is_active"] = True
            _log_audit("adapter_activated", adapter_id=adapter_id, severity="warning")
            return JSONResponse({"activated": True, "adapter": adapter})

    return JSONResponse({"error": "Adapter not found"}, status_code=404)


@app.post("/api/adapters/{adapter_id}/deactivate")
async def api_adapter_deactivate(adapter_id: str) -> JSONResponse:
    """Deactivate an adapter."""
    global _adapters

    for adapter in _adapters:
        if adapter["id"] == adapter_id:
            adapter["is_active"] = False
            _log_audit("adapter_deactivated", adapter_id=adapter_id)
            return JSONResponse({"deactivated": True})

    return JSONResponse({"error": "Adapter not found"}, status_code=404)


@app.get("/api/adapters/{adapter_id}/versions")
async def api_adapter_versions(adapter_id: str) -> JSONResponse:
    """Get version history for an adapter."""
    # For now, return mock version history
    versions = [
        {"version": 1, "created_at": "2025-12-30T10:00:00Z", "changes": "Initial version"},
    ]
    return JSONResponse({"adapter_id": adapter_id, "versions": versions})


@app.post("/api/adapters/{adapter_id}/rollback")
async def api_adapter_rollback(adapter_id: str, target_version: int = 1) -> JSONResponse:
    """Rollback adapter to previous version."""
    _log_audit("adapter_rollback", adapter_id=adapter_id, target_version=target_version, severity="warning")
    return JSONResponse({"rolled_back": True, "version": target_version})


@app.delete("/api/adapters/{adapter_id}")
async def api_adapter_delete(adapter_id: str) -> JSONResponse:
    """Delete an adapter."""
    global _adapters

    _adapters = [a for a in _adapters if a["id"] != adapter_id]
    _log_audit("adapter_deleted", adapter_id=adapter_id, severity="warning")

    return JSONResponse({"deleted": True})


# =============================================================================
# AUDIT API ENDPOINTS
# =============================================================================

@app.get("/api/audit/status")
async def api_audit_status() -> JSONResponse:
    """Get audit mode status."""
    return JSONResponse({
        "enabled": _audit_enabled,
        "log_count": len(_audit_logs),
        "last_entry": _audit_logs[-1] if _audit_logs else None
    })


@app.post("/api/audit/enable")
async def api_audit_enable() -> JSONResponse:
    """Enable enhanced audit mode."""
    global _audit_enabled
    _audit_enabled = True
    _log_audit("audit_mode_enabled", actor="user", severity="info")
    return JSONResponse({"enabled": True})


@app.post("/api/audit/disable")
async def api_audit_disable() -> JSONResponse:
    """Disable audit mode."""
    global _audit_enabled
    _log_audit("audit_mode_disabled", actor="user", severity="warning")
    _audit_enabled = False
    return JSONResponse({"enabled": False})


@app.get("/api/audit/logs")
async def api_audit_logs(
    limit: int = 100,
    severity: Optional[str] = None,
    actor: Optional[str] = None
) -> JSONResponse:
    """Get audit logs with optional filtering."""
    logs = _audit_logs

    if severity:
        logs = [l for l in logs if l.get("severity") == severity]
    if actor:
        logs = [l for l in logs if l.get("actor") == actor]

    return JSONResponse({"logs": logs[-limit:], "total": len(logs)})


@app.get("/api/audit/stream")
async def api_audit_stream(request: Request):
    """SSE stream for real-time audit events."""
    async def event_generator():
        last_count = len(_audit_logs)
        while True:
            if await request.is_disconnected():
                break

            current_count = len(_audit_logs)
            if current_count > last_count:
                new_logs = _audit_logs[last_count:]
                for log in new_logs:
                    yield f"data: {json.dumps(log)}\n\n"
                last_count = current_count

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/audit/report")
async def api_audit_report_generate() -> JSONResponse:
    """Generate compliance report from audit logs."""
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "period_start": _audit_logs[0]["timestamp"] if _audit_logs else None,
        "period_end": _audit_logs[-1]["timestamp"] if _audit_logs else None,
        "total_events": len(_audit_logs),
        "by_severity": {
            "info": len([l for l in _audit_logs if l.get("severity") == "info"]),
            "warning": len([l for l in _audit_logs if l.get("severity") == "warning"]),
            "critical": len([l for l in _audit_logs if l.get("severity") == "critical"]),
        },
        "by_actor": {},
        "compliance_status": "COMPLIANT" if not any(l.get("severity") == "critical" for l in _audit_logs) else "REQUIRES_REVIEW"
    }

    # Count by actor
    for log in _audit_logs:
        actor = log.get("actor", "unknown")
        report["by_actor"][actor] = report["by_actor"].get(actor, 0) + 1

    return JSONResponse(report)


# =============================================================================
# TUNING / FEEDBACK API ENDPOINTS
# =============================================================================

@app.post("/api/training/feedback")
async def api_training_feedback(correction: CorrectionPayload) -> JSONResponse:
    """Submit a correction/feedback for tuning."""
    # Store as preference pair for future DPO training
    feedback = {
        "id": str(datetime.now().timestamp()),
        "session_id": correction.session_id,
        "prompt": correction.prompt,
        "rejected": correction.model_output,
        "chosen": correction.user_correction,
        "rating": correction.rating,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    # Store in memory system for persistence
    try:
        mem = _get_memory_skill()
        if mem:
            mem.execute({
                "capability": "experience",
                "content": f"Correction feedback: {correction.prompt[:100]}... -> {correction.user_correction[:100]}...",
                "memory_type": "semantic",
                "importance": 0.9,
                "metadata": {"type": "correction", "feedback": feedback}
            }, _skill_context)
    except Exception as e:
        print(f"[Feedback] Could not store in memory: {e}")

    _log_audit("feedback_submitted", actor="user", session_id=correction.session_id)

    return JSONResponse({"stored": True, "feedback_id": feedback["id"]})


if __name__ == "__main__":
    start_server()
