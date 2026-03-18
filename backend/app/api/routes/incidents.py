from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.core.errors import ApiError
from app.db.session import get_session
from app.models.enums import IncidentStatus, SeverityLevel, UserRole
from app.models.user import User
from app.repositories.incidents import IncidentRepository
from app.schemas.common import ListResponse
from app.schemas.incidents import IncidentNoteCreate, IncidentNoteRead, IncidentRead, IncidentUpdate
from app.services.audit import AuditService
from app.services.incidents import IncidentService


router = APIRouter()


@router.get("", response_model=ListResponse[IncidentRead])
async def list_incidents(
    session: AsyncSession = Depends(get_session),
    service_id: str | None = None,
    severity: SeverityLevel | None = None,
    status: IncidentStatus | None = None,
    environment: str | None = None,
) -> ListResponse[IncidentRead]:
    items = await IncidentRepository(session).list_filtered(
        service_id=service_id,
        severity=severity,
        status=status,
        environment=environment,
    )
    return ListResponse(items=[IncidentRead.model_validate(item) for item in items], total=len(items))


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: str, session: AsyncSession = Depends(get_session)) -> IncidentRead:
    incident = await IncidentRepository(session).get(incident_id)
    if not incident:
        raise ApiError("incident_not_found", "Incident not found", status_code=404)
    return IncidentRead.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentRead)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> IncidentRead:
    repository = IncidentRepository(session)
    incident = await repository.get(incident_id)
    if not incident:
        raise ApiError("incident_not_found", "Incident not found", status_code=404)
    updated = await IncidentService(session).update_incident(incident, **payload.model_dump(exclude_unset=True))
    await AuditService(session).record(
        action="incident.updated",
        resource_type="incident",
        resource_id=incident_id,
        actor=actor,
        message=f"{actor.full_name} updated incident {incident_id}",
    )
    await session.commit()
    refreshed = await repository.get(incident_id)
    return IncidentRead.model_validate(refreshed)


@router.post("/{incident_id}/notes", response_model=IncidentNoteRead)
async def add_incident_note(
    incident_id: str,
    payload: IncidentNoteCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(get_current_user),
) -> IncidentNoteRead:
    repository = IncidentRepository(session)
    incident = await repository.get(incident_id)
    if not incident:
        raise ApiError("incident_not_found", "Incident not found", status_code=404)
    note = await IncidentService(session).add_note(incident, actor, payload.content)
    await AuditService(session).record(
        action="incident.note_added",
        resource_type="incident",
        resource_id=incident_id,
        actor=actor,
        message=f"{actor.full_name} added a note to incident {incident_id}",
    )
    await session.commit()
    refreshed = await repository.get(incident_id)
    latest_note = sorted(refreshed.notes, key=lambda item: item.created_at)[-1]
    return IncidentNoteRead.model_validate(latest_note)

