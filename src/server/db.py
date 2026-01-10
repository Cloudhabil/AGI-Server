"""Async PostgreSQL connection pooling and helpers for node storage."""

from typing import Any, Dict, Optional, cast

import asyncpg
from fastapi import HTTPException

from .config import settings


pool: Optional[asyncpg.Pool] = None


async def init_db() -> None:
    """Initialise the global asyncpg pool and ensure schema exists."""

    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=30,
            statement_cache_size=1000,
        )
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_seeds (
                  id SERIAL PRIMARY KEY,
                  node_id TEXT NOT NULL,
                  text TEXT NOT NULL,
                  meta JSONB,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS nodes (
                  id TEXT PRIMARY KEY,
                  status TEXT NOT NULL,
                  config JSONB NOT NULL DEFAULT '{}'::jsonb
                );
                """
            )
            for node_id, status in [
                ("orchestrator", "running"),
                ("agent-1", "stopped"),
                ("agent-2", "stopped"),
            ]:
                await conn.execute(
                    """
                    INSERT INTO nodes (id, status, config)
                    VALUES ($1, $2, '{}'::jsonb)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    node_id,
                    status,
                )


async def close_db() -> None:
    """Close the global database pool."""

    global pool
    if pool is not None:
        await pool.close()
        pool = None


async def ping_db() -> bool:
    """Check database connectivity."""

    if pool is None:
        return False
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except (asyncpg.PostgresError, OSError):
        return False


async def list_nodes() -> list[Dict[str, Any]]:
    """Return all nodes stored in the database."""

    if pool is None:
        raise HTTPException(status_code=503, detail="Database not initialised")
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, status, config FROM nodes ORDER BY id")
        return [dict(r) for r in rows]


async def get_node(node_id: str) -> Dict[str, Any]:
    """Return a single node or raise 404."""

    if pool is None:
        raise HTTPException(status_code=503, detail="Database not initialised")
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, status, config FROM nodes WHERE id=$1",
            node_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
        return dict(row)


async def set_node_status(node_id: str, status: str) -> Dict[str, Any]:
    """Update the status of a node and return the updated row."""

    if pool is None:
        raise HTTPException(status_code=503, detail="Database not initialised")
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE nodes SET status=$2 WHERE id=$1 RETURNING id, status, config",
            node_id,
            status,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
        return dict(row)


async def get_node_config(node_id: str) -> Dict[str, Any]:
    """Return the config JSON for a node."""

    if pool is None:
        raise HTTPException(status_code=503, detail="Database not initialised")
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT config FROM nodes WHERE id=$1",
            node_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
        return cast(Dict[str, Any], row["config"])


async def update_node_config(node_id: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Replace the config JSON for a node and return the updated row."""

    if pool is None:
        raise HTTPException(status_code=503, detail="Database not initialised")
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE nodes SET config=$2 WHERE id=$1 RETURNING id, status, config",
            node_id,
            cfg,
        )
        if row is None:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
        return dict(row)
