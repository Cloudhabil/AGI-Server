r"""FastAPI message bus backed by Redis Streams with bearer token authentication.

All requests must supply an ``Authorization: Bearer`` header whose token
matches the ``BUS_TOKEN`` environment variable. Requests with an invalid
token return ``401 Unauthorized``.
"""

import os
import json
import logging
import traceback
import re
from typing import Any, AsyncIterator, Dict

from fastapi import FastAPI, Depends, HTTPException, Request, status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import redis.asyncio as aioredis

from core.kb import add_entry
from observability import setup as setup_observability
from core import error_summary
from integrations import social_hooks

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        # Ensure Redis is closed on shutdown
        await redis.close()


app = FastAPI(lifespan=lifespan)
setup_observability("bus-server", app)
logger = logging.getLogger(__name__)

redis = aioredis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)  # type: ignore[no-untyped-call]

required_env = ["BUS_TOKEN"]
missing = [v for v in required_env if not os.environ.get(v)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


security = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> bool:
    token = os.environ.get("BUS_TOKEN")
    if not token or credentials.credentials != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return True


class PublishReq(BaseModel):
    topic: str
    data: Dict[str, Any]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/shutdown")
async def shutdown(_: bool = Depends(verify_token)) -> Dict[str, str]:
    await redis.close()
    return {"status": "shutting down"}


@app.post("/publish")
async def publish(req: PublishReq, _: bool = Depends(verify_token)) -> Dict[str, str]:
    if not re.fullmatch(r"\w+", req.topic):
        raise HTTPException(status_code=400, detail="Invalid topic name")
    stream = f"bus:{req.topic}"
    await redis.xadd(stream, {"data": json.dumps(req.data)})
    add_entry(kind="bus_message", topic=req.topic, payload=req.data)
    return {"status": "ok"}


@app.get("/get")
async def get(
    topic: str, group: str, consumer: str, _: bool = Depends(verify_token)
) -> Dict[str, Any]:
    if not re.fullmatch(r"\w+", topic):
        raise HTTPException(status_code=400, detail="Invalid topic name")
    stream = f"bus:{topic}"
    try:
        await redis.xgroup_create(stream, group, id="0", mkstream=True)
    except aioredis.ResponseError as exc:  # pragma: no cover - group exists
        if "BUSYGROUP" not in str(exc):
            raise
    while True:
        resp = await redis.xreadgroup(group, consumer, {stream: ">"}, count=1, block=15000)
        if resp:
            _, messages = resp[0]
            msg_id, fields = messages[0]
            await redis.xack(stream, group, msg_id)
            data = json.loads(fields.get("data", "{}"))
            return {"topic": topic, "data": data}


@app.exception_handler(Exception)
async def _unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    summary = error_summary.summarize(trace)
    social_hooks.notify_error(summary)
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("bus_server:app", host="0.0.0.0", port=7088)
