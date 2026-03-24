from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.schemas.audit import AuditRead
from app.schemas.common import ListResponse
from app.services.serializers import serialize_audit_entry


router = APIRouter()


@router.get("", response_model=ListResponse[AuditRead])
async def list_audit(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[AuditRead]:
    items = await AuditRepository(session).list_recent()
    return ListResponse(
        items=[AuditRead.model_validate(serialize_audit_entry(item)) for item in items],
        total=len(items),
    )
