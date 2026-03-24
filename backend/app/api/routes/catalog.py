from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import SuiteType, UserRole
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.qa import (
    EnvironmentCreate,
    EnvironmentRead,
    FixtureSetCreate,
    FixtureSetRead,
    ProjectCreate,
    ProjectRead,
    ScheduleRead,
    ScheduleUpdateRequest,
    SuiteCreate,
    SuiteRead,
)
from app.services.catalog import CatalogService


router = APIRouter()


@router.get("/projects", response_model=ListResponse[ProjectRead])
async def list_projects(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[ProjectRead]:
    items = await CatalogService(session).list_projects()
    return ListResponse(items=[ProjectRead.model_validate(item) for item in items], total=len(items))


@router.post("/projects", response_model=ProjectRead)
async def create_project(
    payload: ProjectCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> ProjectRead:
    project = await CatalogService(session).create_project(payload, actor)
    await session.commit()
    return ProjectRead.model_validate(project)


@router.get("/environments", response_model=ListResponse[EnvironmentRead])
async def list_environments(
    project_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[EnvironmentRead]:
    items = await CatalogService(session).list_environments(project_id=project_id)
    return ListResponse(items=[EnvironmentRead.model_validate(item) for item in items], total=len(items))


@router.post("/environments", response_model=EnvironmentRead)
async def create_environment(
    payload: EnvironmentCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> EnvironmentRead:
    environment = await CatalogService(session).create_environment(payload, actor)
    await session.commit()
    return EnvironmentRead.model_validate(environment)


@router.get("/fixtures", response_model=ListResponse[FixtureSetRead])
async def list_fixture_sets(
    project_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[FixtureSetRead]:
    items = await CatalogService(session).list_fixture_sets(project_id=project_id)
    return ListResponse(items=[FixtureSetRead.model_validate(item) for item in items], total=len(items))


@router.post("/fixtures", response_model=FixtureSetRead)
async def create_fixture_set(
    payload: FixtureSetCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> FixtureSetRead:
    fixture_set = await CatalogService(session).create_fixture_set(payload, actor)
    await session.commit()
    return FixtureSetRead.model_validate(fixture_set)


@router.get("/suites", response_model=ListResponse[SuiteRead])
async def list_suites(
    project_id: str | None = Query(default=None),
    suite_type: SuiteType | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[SuiteRead]:
    items = await CatalogService(session).list_suites(project_id=project_id, suite_type=suite_type)
    return ListResponse(items=[SuiteRead.model_validate(item) for item in items], total=len(items))


@router.post("/suites", response_model=SuiteRead)
async def create_suite(
    payload: SuiteCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> SuiteRead:
    suite = await CatalogService(session).create_suite(payload, actor)
    await session.commit()
    return SuiteRead.model_validate(suite)


@router.get("/schedules", response_model=ListResponse[ScheduleRead])
async def list_schedules(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[ScheduleRead]:
    items = await CatalogService(session).list_schedules()
    return ListResponse(items=[ScheduleRead.model_validate(item) for item in items], total=len(items))


@router.patch("/schedules/{schedule_id}", response_model=ScheduleRead)
async def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdateRequest,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.QA_ENGINEER)),
) -> ScheduleRead:
    schedule = await CatalogService(session).update_schedule(schedule_id, payload, actor)
    await session.commit()
    return ScheduleRead.model_validate(schedule)
