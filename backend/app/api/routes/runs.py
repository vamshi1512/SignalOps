from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import RunStatus, TriggerType, UserRole
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.execution import ManualRunRequest, TestRunDetail, TestRunRead
from app.services.execution import ExecutionService


router = APIRouter()


@router.get("/runs", response_model=ListResponse[TestRunRead])
async def list_runs(
    limit: int = Query(default=40, ge=1, le=100),
    suite_id: str | None = Query(default=None),
    status: RunStatus | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[TestRunRead]:
    items = await ExecutionService(session).list_runs(limit=limit, suite_id=suite_id, status=status)
    return ListResponse(items=[TestRunRead.model_validate(item) for item in items], total=len(items))


@router.get("/runs/{run_id}", response_model=TestRunDetail)
async def get_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> TestRunDetail:
    item = await ExecutionService(session).get_run(run_id)
    return TestRunDetail.model_validate(item)


@router.post("/suites/{suite_id}/runs", response_model=TestRunRead)
async def launch_suite_run(
    suite_id: str,
    payload: ManualRunRequest,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> TestRunRead:
    service = ExecutionService(session)
    run = await service.create_run_for_suite(
        suite_id,
        trigger_type=TriggerType.MANUAL,
        actor=actor,
        environment_id=payload.environment_id,
        fixture_set_id=payload.fixture_set_id,
        parallel_workers=payload.parallel_workers,
    )
    await session.commit()
    await service.dispatch_run(run.id)
    item = await ExecutionService(session).get_run(run.id)
    return TestRunRead.model_validate(item)
