import asyncio
import json
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: Set[WebSocket] = set()
event_queue: asyncio.Queue = asyncio.Queue()


@app.websocket("/ui")
async def ui_ws(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            msg = await event_queue.get()
            await ws.send_text(json.dumps(msg))
    except WebSocketDisconnect:
        clients.discard(ws)


class AgentInitPayload(BaseModel):
    agent_id: str
    cfg: dict
    initial_task: str


@app.post("/agents")
async def create_agent(payload: AgentInitPayload):
    await emit_bus_event("ui", payload.agent_id, size=len(payload.initial_task))
    return {"status": "ok"}


async def emit_bus_event(source: str, target: str, size: int = 1, payloadType: str = "task"):
    await event_queue.put(
        {
            "type": "bus.event",
            "source": source,
            "target": target,
            "size": size,
            "payloadType": payloadType,
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
