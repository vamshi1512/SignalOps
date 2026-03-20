from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.common import MessageResponse
from app.services.demo import DEMO_ACCOUNTS


router = APIRouter()


@router.get("/health")
async def healthcheck(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    _ = session
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "demo_mode": settings.demo_mode,
        "websocket_clients": len(request.app.state.websocket_manager._connections),
    }


@router.get("/demo-accounts")
async def demo_accounts() -> list[dict]:
    return [
        {"email": email, "full_name": name, "title": title, "password": password, "role": role.value}
        for email, name, title, password, role in DEMO_ACCOUNTS
    ]
