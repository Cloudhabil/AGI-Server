# API Reference

## Bus Client

```python
import asyncio
from core.bus_client import BusClient

async def handler(message):
    print(message)

client = BusClient("http://127.0.0.1:8081", topic="events", handler=handler, token="secret")
asyncio.run(client.publish("events", "hello"))
```

## Knowledge Base

```python
from core import kb

kb.add_entry(kind="note", text="refactor auth", meta={"source": "manual"})
kb.ingest_text("long document text", meta={"source": "docs"})
recent = kb.last(10)
results = kb.search("auth")
```

Additional modules are documented inline with docstrings.

## FastAPI apps and lifespan

Both `server/main.py` and `bus_server.py` define `FastAPI` apps with a `lifespan`
context to manage startup/shutdown (DB pool, Redis). You can mount them into a
parent app, and resources will be acquired/released correctly:

```python
from fastapi import FastAPI
from server.main import app as backend_app
from bus_server import app as bus_app

app = FastAPI()
app.mount("/api", backend_app)
app.mount("/bus", bus_app)
```

Run with `uvicorn module:app` or integrate into your ASGI stack.
