"""Redis PubSub bridge utilities."""

import json
from typing import Any, AsyncIterator, Dict, Tuple

import redis.asyncio as aioredis

from .config import settings


_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return a singleton Redis client."""

    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)  # type: ignore[no-untyped-call]
    return _redis


async def publish(channel: str, payload: Dict[str, Any]) -> None:
    """Publish JSON payload to a Redis channel."""

    r = get_redis()
    await r.publish(channel, json.dumps(payload))


async def subscribe(channel: str) -> AsyncIterator[Dict[str, Any]]:
    """Subscribe to a Redis channel yielding decoded JSON payloads."""

    r = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for msg in pubsub.listen():
            if msg and msg.get("type") == "message":
                data = msg.get("data")
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    yield {"type": "raw", "data": data}
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


async def psubscribe(pattern: str) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
    """Pattern subscribe yielding channel name and decoded payload."""

    r = get_redis()
    pubsub = r.pubsub()
    await pubsub.psubscribe(pattern)
    try:
        async for msg in pubsub.listen():
            if msg and msg.get("type") == "pmessage":
                ch = msg.get("channel")
                data = msg.get("data")
                try:
                    yield ch, json.loads(data)
                except json.JSONDecodeError:
                    yield ch, {"type": "raw", "data": data}
    finally:
        await pubsub.punsubscribe(pattern)
        await pubsub.close()
