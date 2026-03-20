from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_user_from_token
from app.db.session import get_session, get_session_factory
from app.models.user import User


router = APIRouter()


@router.get("/status")
async def simulator_status(_: User = Depends(get_current_user)) -> dict:
    return {"status": "running"}


@router.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with get_session_factory()() as session:
        try:
            await get_user_from_token(token, session)
        except Exception:  # noqa: BLE001
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    manager = websocket.app.state.websocket_manager
    await manager.connect(websocket)
    await websocket.send_json({"type": "connected"})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
