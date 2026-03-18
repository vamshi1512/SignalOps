from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.core.errors import ApiError
from app.db.session import get_session
from app.models.enums import SeverityLevel, UserRole
from app.schemas.common import ListResponse
from app.schemas.logs import LogEventRead, LogIngestRequest, LogIngestResponse
from app.services.ingestion import LogIngestionService
from app.repositories.logs import LogRepository


router = APIRouter()


@router.get("", response_model=ListResponse[LogEventRead])
async def list_logs(
    session: AsyncSession = Depends(get_session),
    service_id: str | None = None,
    severity: SeverityLevel | None = None,
    environment: str | None = None,
    status: str | None = Query(default=None, description="Use 'anomalous' to show anomaly hits"),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> ListResponse[LogEventRead]:
    items = await LogRepository(session).list_filtered(
        service_id=service_id,
        severity=severity,
        environment=environment,
        status=status,
        start_at=start_at,
        end_at=end_at,
    )
    return ListResponse(items=[LogEventRead.model_validate(item) for item in items], total=len(items))


@router.post("", response_model=LogIngestResponse)
async def ingest_log(
    payload: LogIngestRequest,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.SRE)),
) -> LogIngestResponse:
    try:
        log, incident_id, alert_ids = await LogIngestionService(session).ingest(**payload.model_dump())
    except ValueError as exc:
        raise ApiError("unknown_service", str(exc), status_code=404) from exc
    await session.commit()
    refreshed = await LogRepository(session).get(log.id)
    return LogIngestResponse(log=LogEventRead.model_validate(refreshed), incident_id=incident_id, alert_ids=alert_ids)
