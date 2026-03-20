from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.audit import AuditEntryRead
from app.schemas.common import ListResponse
from app.services.audit import AuditService
from app.services.serializers import serialize_audit


router = APIRouter()


@router.get("", response_model=ListResponse[AuditEntryRead])
async def list_audit(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
) -> ListResponse[AuditEntryRead]:
    entries = await AuditService(session).list_entries()
    payload = [AuditEntryRead.model_validate(serialize_audit(entry)) for entry in entries]
    return ListResponse(items=payload, total=len(payload))
