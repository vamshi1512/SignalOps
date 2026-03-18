from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.core.errors import ApiError
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.service import Service
from app.schemas.common import ListResponse
from app.schemas.services import ServiceCreate, ServiceRead
from app.services.dashboard import DashboardService
from app.repositories.services import ServiceRepository


router = APIRouter()


@router.get("", response_model=ListResponse[ServiceRead])
async def list_services(session: AsyncSession = Depends(get_session)) -> ListResponse[ServiceRead]:
    dashboard = await DashboardService(session).overview()
    return ListResponse(items=dashboard.services, total=len(dashboard.services))


@router.post("", response_model=ServiceRead)
async def create_service(
    payload: ServiceCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> ServiceRead:
    repository = ServiceRepository(session)
    if await repository.get_by_slug(payload.slug):
        raise ApiError("duplicate_service", f"Service slug '{payload.slug}' already exists", status_code=409)
    service = Service(**payload.model_dump())
    await repository.add(service)
    await session.commit()
    await session.refresh(service)
    return ServiceRead.model_validate(service)

