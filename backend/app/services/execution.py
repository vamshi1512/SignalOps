from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.errors import ApiError
from app.models.enums import EnvironmentStatus, ResultStatus, RunStatus, TriggerType
from app.models.qa import Environment, FixtureSet, RunSchedule, TestCase, TestResult, TestRun, TestSuite
from app.models.user import User
from app.services.audit import AuditService
from app.services.notifications import NotificationService
from app.services.serializers import serialize_run


class ExecutionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.audit = AuditService(session)
        self.notifications = NotificationService(session)
        self.artifact_root = Path(self.settings.artifact_root)

    async def list_runs(
        self,
        *,
        limit: int = 40,
        suite_id: str | None = None,
        status: RunStatus | None = None,
    ) -> list[dict]:
        query = (
            select(TestRun)
            .options(
                selectinload(TestRun.project),
                selectinload(TestRun.suite),
                selectinload(TestRun.environment),
                selectinload(TestRun.fixture_set),
                selectinload(TestRun.schedule).selectinload(RunSchedule.environment),
                selectinload(TestRun.triggered_by),
            )
            .order_by(TestRun.created_at.desc())
            .limit(limit)
        )
        if suite_id:
            query = query.where(TestRun.suite_id == suite_id)
        if status:
            query = query.where(TestRun.status == status)
        result = await self.session.execute(query)
        return [serialize_run(run) for run in result.scalars().all()]

    async def get_run(self, run_id: str) -> dict:
        run = await self._load_run(run_id, include_results=True)
        return serialize_run(run, include_results=True)

    async def create_run_for_suite(
        self,
        suite_id: str,
        *,
        trigger_type: TriggerType,
        actor: User | None = None,
        environment_id: str | None = None,
        fixture_set_id: str | None = None,
        schedule_id: str | None = None,
        parallel_workers: int | None = None,
        created_at: datetime | None = None,
    ) -> TestRun:
        suite = await self._load_suite(suite_id)
        environment = await self._resolve_environment(suite, environment_id)
        fixture_set = await self._resolve_fixture_set(suite, fixture_set_id)
        ordinal = await self._next_suite_ordinal(suite.id)

        run = TestRun(
            project_id=suite.project_id,
            suite_id=suite.id,
            environment_id=environment.id,
            fixture_set_id=fixture_set.id if fixture_set else None,
            schedule_id=schedule_id,
            triggered_by_user_id=actor.id if actor else None,
            trigger_type=trigger_type,
            status=RunStatus.QUEUED,
            requested_parallel_workers=parallel_workers or suite.parallel_workers,
            summary={
                "ordinal": ordinal,
                "suite_type": suite.suite_type.value,
                "source_command": suite.command,
                "repo_path": suite.repo_path,
                "branch": suite.project.default_branch,
                "fixture_profile": fixture_set.name if fixture_set else "default",
                "target_environment": environment.slug,
            },
            runtime_metadata={
                "runner": "deterministic-simulator",
                "project_slug": suite.project.slug,
                "release_ring": environment.variables.get("RELEASE_RING", "demo"),
                "schedule_id": schedule_id,
            },
        )
        if created_at:
            run.created_at = created_at
            run.updated_at = created_at
        self.session.add(run)
        await self.session.flush()

        await self.audit.record(
            action="run.queued",
            resource_type="run",
            resource_id=run.id,
            message=f"Queued {suite.name} for {environment.name}",
            actor=actor,
            details={"trigger_type": trigger_type.value},
        )
        return run

    async def dispatch_run(self, run_id: str) -> None:
        if self.settings.celery_eager:
            await self.execute_run(run_id)
            await self.session.commit()
            return
        from app.tasks.jobs import execute_run_task

        execute_run_task.delay(run_id)

    async def execute_run(self, run_id: str, *, started_at: datetime | None = None) -> TestRun:
        run = await self._load_run(run_id, include_results=True)
        run.results.clear()
        run.notifications.clear()
        start_time = started_at or datetime.now(timezone.utc)
        run.started_at = start_time
        run.status = RunStatus.RUNNING
        ordinal = int(run.summary.get("ordinal", 1))

        offset_ms = 0
        results: list[TestResult] = []
        for test_case in run.suite.test_cases:
            status, is_flaky, retry_count = self._resolve_status(test_case, run.environment, ordinal)
            duration_ms = self._resolve_duration(test_case, ordinal, run.environment)
            case_started_at = start_time + timedelta(milliseconds=offset_ms)
            case_finished_at = case_started_at + timedelta(milliseconds=duration_ms)
            request_details = self._build_request_details(test_case, run.environment)
            response_details = self._build_response_details(test_case, run.environment, status)
            error_message = self._build_error_message(test_case, status)
            stack_trace = self._build_stack_trace(test_case, status)
            logs = self._build_logs(test_case, run.environment, status, duration_ms)
            attachments = self._write_attachments(
                run=run,
                test_case=test_case,
                status=status,
                request_details=request_details,
                response_details=response_details,
                logs=logs,
                error_message=error_message,
            )
            result = TestResult(
                run_id=run.id,
                suite_id=run.suite_id,
                test_case_id=test_case.id,
                run=run,
                test_case=test_case,
                name=test_case.name,
                module_name=test_case.module_name,
                status=status,
                retry_count=retry_count,
                is_flaky=is_flaky,
                duration_ms=duration_ms,
                started_at=case_started_at,
                finished_at=case_finished_at,
                error_message=error_message,
                stack_trace=stack_trace,
                logs=logs,
                request_details=request_details,
                response_details=response_details,
                attachments=attachments,
            )
            results.append(result)
            offset_ms += duration_ms + 250

        self.session.add_all(results)
        await self.session.flush()

        run.total_count = len(results)
        run.pass_count = sum(1 for result in results if result.status == ResultStatus.PASSED)
        run.fail_count = sum(1 for result in results if result.status == ResultStatus.FAILED)
        run.skip_count = sum(1 for result in results if result.status == ResultStatus.SKIPPED)
        run.flaky_count = sum(1 for result in results if result.is_flaky or result.status == ResultStatus.FLAKY)
        run.finished_at = results[-1].finished_at if results else start_time
        run.duration_ms = max(int((run.finished_at - start_time).total_seconds() * 1000), 0)
        run.runtime_metadata = {
            **run.runtime_metadata,
            "environment_kind": run.environment.kind.value,
            "alerted": run.fail_count > 0,
        }
        run.status = self._resolve_run_status(run)
        run.environment.last_checked_at = run.finished_at
        run.environment.status = EnvironmentStatus.DEGRADED if run.fail_count else EnvironmentStatus.HEALTHY
        run.environment.health_summary = (
            f"{run.fail_count} failing results and {run.flaky_count} flaky indicators in the latest run"
            if run.fail_count
            else "Latest automation pass completed without detected regressions."
        )

        if run.fail_count:
            await self.notifications.notify_failed_run(run)

        await self.audit.record(
            action="run.completed",
            resource_type="run",
            resource_id=run.id,
            message=f"Completed {run.suite.name} with status {run.status.value}",
            actor=run.triggered_by,
            details={
                "pass_count": run.pass_count,
                "fail_count": run.fail_count,
                "flaky_count": run.flaky_count,
            },
        )
        await self.session.flush()
        return run

    async def schedule_due_runs(self) -> list[str]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(RunSchedule)
            .where(RunSchedule.active.is_(True), RunSchedule.next_run_at <= now)
            .options(selectinload(RunSchedule.environment), selectinload(RunSchedule.suite))
            .order_by(RunSchedule.next_run_at)
        )
        schedules = list(result.scalars().all())
        run_ids: list[str] = []
        for schedule in schedules:
            run = await self.create_run_for_suite(
                schedule.suite_id,
                trigger_type=TriggerType.SCHEDULED,
                environment_id=schedule.environment_id,
                schedule_id=schedule.id,
                parallel_workers=schedule.parallel_workers,
                created_at=schedule.next_run_at - timedelta(seconds=5),
            )
            schedule.last_run_at = schedule.next_run_at
            schedule.next_run_at = schedule.next_run_at + timedelta(minutes=schedule.cadence_minutes)
            run_ids.append(run.id)
        return run_ids

    async def _load_suite(self, suite_id: str) -> TestSuite:
        result = await self.session.execute(
            select(TestSuite)
            .where(TestSuite.id == suite_id)
            .options(
                selectinload(TestSuite.project),
                selectinload(TestSuite.default_environment),
                selectinload(TestSuite.default_fixture_set),
                selectinload(TestSuite.test_cases),
            )
        )
        suite = result.scalar_one_or_none()
        if not suite:
            raise ApiError("suite_not_found", "Suite was not found", status_code=404)
        return suite

    async def _load_run(self, run_id: str, *, include_results: bool) -> TestRun:
        options = [
            selectinload(TestRun.project),
            selectinload(TestRun.suite).selectinload(TestSuite.test_cases),
            selectinload(TestRun.environment),
            selectinload(TestRun.fixture_set),
            selectinload(TestRun.schedule).selectinload(RunSchedule.environment),
            selectinload(TestRun.triggered_by),
            selectinload(TestRun.notifications),
        ]
        if include_results:
            options.append(selectinload(TestRun.results))
        result = await self.session.execute(select(TestRun).where(TestRun.id == run_id).options(*options))
        run = result.scalar_one_or_none()
        if not run:
            raise ApiError("run_not_found", "Run was not found", status_code=404)
        return run

    async def _resolve_environment(self, suite: TestSuite, environment_id: str | None) -> Environment:
        selected_id = environment_id or suite.default_environment_id
        if not selected_id:
            raise ApiError("environment_required", "Suite does not have a default environment", status_code=400)
        environment = await self.session.get(Environment, selected_id)
        if not environment:
            raise ApiError("environment_not_found", "Environment was not found", status_code=404)
        if environment.project_id != suite.project_id:
            raise ApiError(
                "environment_project_mismatch",
                "Environment must belong to the suite project",
                status_code=400,
            )
        return environment

    async def _resolve_fixture_set(self, suite: TestSuite, fixture_set_id: str | None) -> FixtureSet | None:
        selected_id = fixture_set_id or suite.default_fixture_set_id
        if not selected_id:
            return None
        fixture_set = await self.session.get(FixtureSet, selected_id)
        if not fixture_set:
            raise ApiError("fixture_set_not_found", "Fixture set was not found", status_code=404)
        if fixture_set.project_id != suite.project_id:
            raise ApiError(
                "fixture_project_mismatch",
                "Fixture set must belong to the suite project",
                status_code=400,
            )
        return fixture_set

    async def _next_suite_ordinal(self, suite_id: str) -> int:
        result = await self.session.execute(select(func.count(TestRun.id)).where(TestRun.suite_id == suite_id))
        return int(result.scalar_one() or 0) + 1

    def _resolve_status(self, test_case: TestCase, environment: Environment, ordinal: int) -> tuple[ResultStatus, bool, int]:
        profile = test_case.deterministic_profile
        if profile == "stable":
            return ResultStatus.PASSED, False, 0
        if profile == "flaky":
            if ordinal % 5 == 0:
                return ResultStatus.FAILED, True, 1
            if ordinal % 3 == 0:
                return ResultStatus.FLAKY, True, 1
            return ResultStatus.PASSED, False, 0
        if profile == "staging-risk":
            if environment.kind.value in {"qa", "staging"} and ordinal % 4 == 0:
                return ResultStatus.FAILED, False, 0
            return ResultStatus.PASSED, False, 0
        if profile == "contract-drift":
            if environment.kind.value in {"prod_like", "mock"} and ordinal % 6 == 0:
                return ResultStatus.FAILED, False, 0
            return ResultStatus.PASSED, False, 0
        if profile == "ui-visual":
            if ordinal % 4 == 0:
                return ResultStatus.FAILED, False, 0
            return ResultStatus.PASSED, False, 0
        if profile == "slow-burn":
            if ordinal % 7 == 0:
                return ResultStatus.FAILED, False, 0
            return ResultStatus.PASSED, False, 0
        return ResultStatus.PASSED, False, 0

    def _resolve_duration(self, test_case: TestCase, ordinal: int, environment: Environment) -> int:
        environment_factor = {
            "qa": 40,
            "staging": 80,
            "prod_like": 55,
            "mock": 25,
        }[environment.kind.value]
        fluctuation = (ordinal % 5) * 35 + (len(test_case.module_name) % 5) * 20
        if test_case.deterministic_profile == "slow-burn":
            fluctuation += 220
        return test_case.baseline_duration_ms + environment_factor + fluctuation

    def _resolve_run_status(self, run: TestRun) -> RunStatus:
        if run.fail_count:
            return RunStatus.FAILED
        if run.flaky_count:
            return RunStatus.PARTIAL
        return RunStatus.PASSED

    def _build_request_details(self, test_case: TestCase, environment: Environment) -> dict:
        if test_case.tags and "ui" in test_case.tags:
            return {}
        endpoint = {
            "session": "/target-api/auth/session",
            "payment": "/target-api/payments/authorize",
            "orders": "/target-api/orders/CHK-1007",
            "identity": "/target-api/identity/permissions",
        }
        path = endpoint.get(test_case.module_name.split(".")[0], "/target-api/health")
        method = "GET" if "read" in test_case.name.lower() or "sync" in test_case.name.lower() else "POST"
        return {
            "method": method,
            "url": f"{environment.api_base_url}{path}",
            "headers": {"x-suite-case": test_case.key, "x-env": environment.slug},
            "body": {"fixture_profile": test_case.fixture_overrides or "default"},
        }

    def _build_response_details(self, test_case: TestCase, environment: Environment, status: ResultStatus) -> dict:
        if test_case.tags and "ui" in test_case.tags:
            return {}
        code = 200 if status in {ResultStatus.PASSED, ResultStatus.FLAKY} else 503
        payload = {
            "result": "ok" if code == 200 else "error",
            "module": test_case.module_name,
            "environment": environment.slug,
            "case": test_case.key,
        }
        if code != 200:
            payload["failure_hint"] = "Synthetic upstream dependency returned unstable data."
        return {"status_code": code, "json": payload}

    def _build_error_message(self, test_case: TestCase, status: ResultStatus) -> str:
        if status not in {ResultStatus.FAILED, ResultStatus.FLAKY}:
            return ""
        if "ui" in test_case.tags:
            return f"Locator assertion failed for {test_case.name.lower()}."
        return f"Assertion mismatch detected in {test_case.module_name}."

    def _build_stack_trace(self, test_case: TestCase, status: ResultStatus) -> str:
        if status not in {ResultStatus.FAILED, ResultStatus.FLAKY}:
            return ""
        if "ui" in test_case.tags:
            return (
                "Error: locator assertion failed\n"
                f"  at {test_case.automation_ref}\n"
                "  at expect(locator).toHaveText(...)"
            )
        return (
            "AssertionError: response contract mismatch\n"
            f"  at {test_case.automation_ref}\n"
            "  expected status_code == 200"
        )

    def _build_logs(self, test_case: TestCase, environment: Environment, status: ResultStatus, duration_ms: int) -> str:
        outcome = "passed"
        if status == ResultStatus.FAILED:
            outcome = "failed"
        if status == ResultStatus.FLAKY:
            outcome = "recovered-after-retry"
        return (
            f"[runner] executing {test_case.automation_ref}\n"
            f"[env] {environment.slug}\n"
            f"[duration] {duration_ms}ms\n"
            f"[outcome] {outcome}\n"
            f"[module] {test_case.module_name}"
        )

    def _write_attachments(
        self,
        *,
        run: TestRun,
        test_case: TestCase,
        status: ResultStatus,
        request_details: dict,
        response_details: dict,
        logs: str,
        error_message: str,
    ) -> list[dict]:
        attachments: list[dict] = []
        if status not in {ResultStatus.FAILED, ResultStatus.FLAKY}:
            return attachments

        run_dir = self.artifact_root / run.id
        run_dir.mkdir(parents=True, exist_ok=True)
        safe_key = test_case.key.replace("/", "-").replace(":", "-")
        if "ui" in test_case.tags:
            svg_name = f"{safe_key}-failure.svg"
            svg_path = run_dir / svg_name
            svg_path.write_text(self._build_failure_svg(run, test_case, error_message), encoding="utf-8")
            attachments.append({"label": "Failure screenshot", "type": "image", "url": f"/artifacts/{run.id}/{svg_name}"})
        else:
            request_name = f"{safe_key}-request.json"
            response_name = f"{safe_key}-response.json"
            (run_dir / request_name).write_text(json.dumps(request_details, indent=2), encoding="utf-8")
            (run_dir / response_name).write_text(json.dumps(response_details, indent=2), encoding="utf-8")
            attachments.append({"label": "Request payload", "type": "json", "url": f"/artifacts/{run.id}/{request_name}"})
            attachments.append({"label": "Response payload", "type": "json", "url": f"/artifacts/{run.id}/{response_name}"})

        log_name = f"{safe_key}-runner.log"
        (run_dir / log_name).write_text(logs, encoding="utf-8")
        attachments.append({"label": "Runner log", "type": "text", "url": f"/artifacts/{run.id}/{log_name}"})
        return attachments

    def _build_failure_svg(self, run: TestRun, test_case: TestCase, error_message: str) -> str:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#0f172a"/>
  <rect x="48" y="48" width="1184" height="624" rx="32" fill="#111827" stroke="#334155" stroke-width="2"/>
  <text x="88" y="110" fill="#f8fafc" font-size="30" font-family="IBM Plex Sans, sans-serif">TestForge Failure Snapshot</text>
  <text x="88" y="154" fill="#94a3b8" font-size="18" font-family="IBM Plex Sans, sans-serif">{run.suite.name} / {run.environment.name}</text>
  <rect x="88" y="196" width="1104" height="104" rx="20" fill="#1e293b"/>
  <text x="120" y="250" fill="#38bdf8" font-size="22" font-family="IBM Plex Mono, monospace">{test_case.name}</text>
  <text x="120" y="286" fill="#e2e8f0" font-size="18" font-family="IBM Plex Sans, sans-serif">{error_message or "Visual diff threshold exceeded."}</text>
  <rect x="88" y="336" width="1104" height="280" rx="28" fill="#020617" stroke="#1e293b" stroke-width="2"/>
  <text x="120" y="392" fill="#e2e8f0" font-size="20" font-family="IBM Plex Mono, monospace">data-testid=checkout-summary</text>
  <text x="120" y="438" fill="#fda4af" font-size="18" font-family="IBM Plex Mono, monospace">Expected total: SEK 99.00</text>
  <text x="120" y="472" fill="#fecaca" font-size="18" font-family="IBM Plex Mono, monospace">Actual total:   SEK 104.00</text>
  <text x="120" y="526" fill="#94a3b8" font-size="16" font-family="IBM Plex Sans, sans-serif">Synthetic screenshot generated by the deterministic UI artifact pipeline.</text>
  <text x="120" y="570" fill="#64748b" font-size="16" font-family="IBM Plex Mono, monospace">Run {run.id}</text>
</svg>
"""
