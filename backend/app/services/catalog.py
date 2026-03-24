from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models.enums import SuiteType
from app.models.qa import Environment, FixtureSet, Project, RunSchedule, TestRun, TestSuite
from app.models.user import User
from app.schemas.qa import EnvironmentCreate, FixtureSetCreate, ProjectCreate, ScheduleUpdateRequest, SuiteCreate
from app.services.audit import AuditService
from app.services.serializers import (
    serialize_environment,
    serialize_fixture_set,
    serialize_project,
    serialize_schedule,
    serialize_suite,
)


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audit = AuditService(session)

    async def list_projects(self) -> list[dict]:
        result = await self.session.execute(select(Project).order_by(Project.name))
        return [serialize_project(project) for project in result.scalars().all()]

    async def create_project(self, payload: ProjectCreate, actor: User) -> dict:
        project = Project(**payload.model_dump())
        self.session.add(project)
        await self.session.flush()
        await self.audit.record(
            action="project.created",
            resource_type="project",
            resource_id=project.id,
            message=f"Created project {project.name}",
            actor=actor,
            details={"slug": project.slug},
        )
        return serialize_project(project)

    async def list_environments(self, project_id: str | None = None) -> list[dict]:
        query = select(Environment).order_by(Environment.name).options(selectinload(Environment.project))
        if project_id:
            query = query.where(Environment.project_id == project_id)
        result = await self.session.execute(query)
        return [serialize_environment(environment) for environment in result.scalars().all()]

    async def create_environment(self, payload: EnvironmentCreate, actor: User) -> dict:
        await self._get_project(payload.project_id)
        if payload.is_default:
            await self._clear_default_environment(payload.project_id)
        environment = Environment(**payload.model_dump())
        self.session.add(environment)
        await self.session.flush()
        await self.audit.record(
            action="environment.created",
            resource_type="environment",
            resource_id=environment.id,
            message=f"Registered environment {environment.name}",
            actor=actor,
            details={"kind": environment.kind.value},
        )
        return serialize_environment(environment)

    async def list_fixture_sets(self, project_id: str | None = None) -> list[dict]:
        query = select(FixtureSet).order_by(FixtureSet.name)
        if project_id:
            query = query.where(FixtureSet.project_id == project_id)
        result = await self.session.execute(query)
        return [serialize_fixture_set(fixture_set) for fixture_set in result.scalars().all()]

    async def create_fixture_set(self, payload: FixtureSetCreate, actor: User) -> dict:
        await self._get_project(payload.project_id)
        fixture_set = FixtureSet(**payload.model_dump())
        self.session.add(fixture_set)
        await self.session.flush()
        await self.audit.record(
            action="fixture_set.created",
            resource_type="fixture_set",
            resource_id=fixture_set.id,
            message=f"Created fixture set {fixture_set.name}",
            actor=actor,
            details={"project_id": fixture_set.project_id},
        )
        return serialize_fixture_set(fixture_set)

    async def list_suites(self, project_id: str | None = None, suite_type: SuiteType | None = None) -> list[dict]:
        query = (
            select(TestSuite)
            .options(
                selectinload(TestSuite.project),
                selectinload(TestSuite.default_environment),
                selectinload(TestSuite.default_fixture_set),
                selectinload(TestSuite.test_cases),
                selectinload(TestSuite.schedules).selectinload(RunSchedule.environment),
                selectinload(TestSuite.runs),
            )
            .order_by(TestSuite.name)
        )
        if project_id:
            query = query.where(TestSuite.project_id == project_id)
        if suite_type:
            query = query.where(TestSuite.suite_type == suite_type)

        result = await self.session.execute(query)
        suites = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        for suite in result.scalars().all():
            recent_runs = [
                run
                for run in suite.runs
                if self._as_utc(run.started_at or run.created_at) >= cutoff
            ]
            latest_run = max(suite.runs, key=lambda run: self._as_utc(run.started_at or run.created_at), default=None)
            total_assertions = sum(run.total_count for run in recent_runs) or 0
            passing_assertions = sum(run.pass_count + run.skip_count for run in recent_runs)
            pass_rate = (passing_assertions / total_assertions * 100) if total_assertions else 100.0
            flaky_cases = sum(1 for test_case in suite.test_cases if "flaky" in test_case.deterministic_profile)
            suites.append(
                serialize_suite(
                    suite,
                    latest_run_status=latest_run.status if latest_run else None,
                    last_run_at=self._as_utc(latest_run.started_at) if latest_run and latest_run.started_at else None,
                    pass_rate_14d=round(pass_rate, 1),
                    flaky_cases=flaky_cases,
                )
            )
        return suites

    async def create_suite(self, payload: SuiteCreate, actor: User) -> dict:
        project = await self._get_project(payload.project_id)
        if payload.default_environment_id:
            await self._get_environment(payload.default_environment_id, project_id=project.id)
        if payload.default_fixture_set_id:
            await self._get_fixture_set(payload.default_fixture_set_id, project_id=project.id)
        suite = TestSuite(**payload.model_dump())
        self.session.add(suite)
        await self.session.flush()
        suite = await self._get_suite(suite.id)
        await self.audit.record(
            action="suite.created",
            resource_type="suite",
            resource_id=suite.id,
            message=f"Created suite {suite.name}",
            actor=actor,
            details={"suite_type": suite.suite_type.value},
        )
        return serialize_suite(suite)

    async def list_schedules(self) -> list[dict]:
        result = await self.session.execute(
            select(RunSchedule)
            .options(selectinload(RunSchedule.environment), selectinload(RunSchedule.suite))
            .order_by(RunSchedule.next_run_at)
        )
        return [serialize_schedule(schedule) for schedule in result.scalars().all()]

    async def update_schedule(self, schedule_id: str, payload: ScheduleUpdateRequest, actor: User) -> dict:
        schedule = await self._get_schedule(schedule_id)
        updates = payload.model_dump(exclude_unset=True)
        if "next_run_at" in updates and updates["next_run_at"] is not None:
            updates["next_run_at"] = self._as_utc(updates["next_run_at"])
        for field, value in updates.items():
            setattr(schedule, field, value)
        await self.session.flush()
        await self.audit.record(
            action="schedule.updated",
            resource_type="schedule",
            resource_id=schedule.id,
            message=f"Updated schedule {schedule.name}",
            actor=actor,
            details={key: str(value) for key, value in updates.items()},
        )
        return serialize_schedule(schedule)

    async def _get_project(self, project_id: str) -> Project:
        project = await self.session.get(Project, project_id)
        if not project:
            raise ApiError("project_not_found", "Project was not found", status_code=404)
        return project

    async def _get_environment(self, environment_id: str, *, project_id: str | None = None) -> Environment:
        environment = await self.session.get(Environment, environment_id)
        if not environment:
            raise ApiError("environment_not_found", "Environment was not found", status_code=404)
        if project_id and environment.project_id != project_id:
            raise ApiError(
                "environment_project_mismatch",
                "Environment does not belong to the selected project",
                status_code=400,
            )
        return environment

    async def _get_fixture_set(self, fixture_set_id: str, *, project_id: str | None = None) -> FixtureSet:
        fixture_set = await self.session.get(FixtureSet, fixture_set_id)
        if not fixture_set:
            raise ApiError("fixture_set_not_found", "Fixture set was not found", status_code=404)
        if project_id and fixture_set.project_id != project_id:
            raise ApiError(
                "fixture_project_mismatch",
                "Fixture set does not belong to the selected project",
                status_code=400,
            )
        return fixture_set

    async def _get_schedule(self, schedule_id: str) -> RunSchedule:
        schedule = await self.session.get(RunSchedule, schedule_id)
        if not schedule:
            raise ApiError("schedule_not_found", "Schedule was not found", status_code=404)
        return schedule

    async def _get_suite(self, suite_id: str) -> TestSuite:
        result = await self.session.execute(
            select(TestSuite)
            .where(TestSuite.id == suite_id)
            .options(
                selectinload(TestSuite.project),
                selectinload(TestSuite.default_environment),
                selectinload(TestSuite.default_fixture_set),
                selectinload(TestSuite.test_cases),
                selectinload(TestSuite.schedules).selectinload(RunSchedule.environment),
                selectinload(TestSuite.runs),
            )
        )
        suite = result.scalar_one_or_none()
        if not suite:
            raise ApiError("suite_not_found", "Suite was not found", status_code=404)
        return suite

    async def _clear_default_environment(self, project_id: str) -> None:
        result = await self.session.execute(select(Environment).where(Environment.project_id == project_id, Environment.is_default.is_(True)))
        for environment in result.scalars().all():
            environment.is_default = False

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
