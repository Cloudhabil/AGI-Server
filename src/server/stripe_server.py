import os
import asyncio
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Request
import stripe
from stripe.error import SignatureVerificationError  # type: ignore[attr-defined]

from core.kb import add_entry

app = FastAPI()
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BUS_URL = os.environ.get("BUS_URL", "http://127.0.0.1:7088")
BUS_TOKEN = os.environ.get("BUS_TOKEN", "")

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/stripe/webhook")
async def webhook(request: Request) -> Dict[str, str]:
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not sig:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    try:
        event: Any = stripe.Webhook.construct_event(
            payload, sig, WEBHOOK_SECRET
        )  # type: ignore[no-untyped-call]
    except SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    add_entry(kind="stripe_event", type=event.get("type"))
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                f"{BUS_URL}/publish",
                headers={"Authorization": f"Bearer {BUS_TOKEN}"},
                json={"topic": role, "data": {"stripe_event": event.get("type")}},
            )
            for role in ["CFO", "COO", "CEO", "CMO", "CPO"]
        ]
        await asyncio.gather(*tasks)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "stripe_server:app",
        host=os.environ.get("STRIPE_BIND", "0.0.0.0"),
        port=int(os.environ.get("STRIPE_PORT", 7077)),
    )
