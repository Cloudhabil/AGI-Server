"""Development agent simulator for local testing."""

import asyncio

from .redis_bus import publish, subscribe


async def agent_echo(node_id: str) -> None:
    """Echo chat agent that streams tokens back."""

    ch_in = f"chat:{node_id}:in"
    ch_out = f"chat:{node_id}:out"
    async for payload in subscribe(ch_in):
        t = payload.get("type")
        if t == "seed":
            await publish(
                ch_out,
                {"type": "message", "role": "system", "text": f"seeded: {payload.get('text', '')}"},
            )
        elif t == "send":
            text = payload.get("text", "")
            for tok in text.split():
                await asyncio.sleep(0.02)
                await publish(ch_out, {"type": "token", "text": tok})
            await publish(
                ch_out,
                {"type": "message", "role": "assistant", "text": f"Echo: {text}"},
            )


async def agent_logs(node_id: str) -> None:
    """Periodic log publisher."""

    i = 0
    while True:
        await asyncio.sleep(0.6)
        i += 1
        await publish(
            f"logs:{node_id}",
            {
                "type": "log",
                "level": ["INFO", "DEBUG", "WARN"][i % 3],
                "node_id": node_id,
                "line": f"{node_id} heartbeat {i}",
            },
        )


async def main() -> None:
    await asyncio.gather(
        agent_echo("agent-1"),
        agent_echo("agent-2"),
        agent_logs("agent-1"),
        agent_logs("agent-2"),
    )


if __name__ == "__main__":
    asyncio.run(main())
