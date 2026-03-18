from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.audit import AuditRepository
from app.schemas.audit import AuditRead
from app.schemas.common import ListResponse


router = APIRouter()


@router.get("", response_model=ListResponse[AuditRead])
async def list_audit(session: AsyncSession = Depends(get_session)) -> ListResponse[AuditRead]:
    items = await AuditRepository(session).list_recent()
    return ListResponse(items=[AuditRead.model_validate(item) for item in items], total=len(items))

