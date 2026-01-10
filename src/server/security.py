"""Authentication helpers for the FastAPI backend."""

from fastapi import (
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def validate_token(token: str = Depends(oauth2_scheme)) -> None:
    """Ensure the provided Bearer token matches the configured token."""

    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validate_ws_token(ws: WebSocket, token: str | None = Query(None)) -> None:
    """Validate token for WebSocket connections."""

    if token != settings.API_TOKEN:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
