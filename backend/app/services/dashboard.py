from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.qa import Environment, RunSchedule, TestRun
from app.services.catalog import CatalogService
from app.services.serializers import serialize_run


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def overview(self) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=14)
        run_result = await self.session.execute(
            select(TestRun)
            .where(TestRun.created_at >= since)
            .options(
                selectinload(TestRun.project),
                selectinload(TestRun.suite),
                selectinload(TestRun.environment),
                selectinload(TestRun.fixture_set),
                selectinload(TestRun.schedule).selectinload(RunSchedule.environment),
                selectinload(TestRun.triggered_by),
                selectinload(TestRun.results),
            )
            .order_by(TestRun.created_at.desc())
        )
        runs = list(run_result.scalars().all())
        environment_result = await self.session.execute(
            select(Environment).options(selectinload(Environment.project)).order_by(Environment.name)
        )
        environments = list(environment_result.scalars().all())
        suites = await CatalogService(self.session).list_suites()

        current_week_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        current_week = [run for run in runs if self._as_utc(run.created_at) >= current_week_cutoff]
        prior_week = [run for run in runs if since <= self._as_utc(run.created_at) < current_week_cutoff]

        def aggregate_pass_rate(target_runs: list[TestRun]) -> float:
            total = sum(run.total_count for run in target_runs)
            passed = sum(run.pass_count + run.skip_count for run in target_runs)
            return round((passed / total * 100) if total else 100.0, 1)

        def avg_duration_minutes(target_runs: list[TestRun]) -> float:
            return round((mean([run.duration_ms for run in target_runs]) / 60000) if target_runs else 0.0, 1)

        current_pass_rate = aggregate_pass_rate(current_week)
        prior_pass_rate = aggregate_pass_rate(prior_week)
        current_failure_count = sum(run.fail_count for run in current_week)
        prior_failure_count = sum(run.fail_count for run in prior_week)
        current_flaky = sum(run.flaky_count for run in current_week)
        prior_flaky = sum(run.flaky_count for run in prior_week)
        current_duration = avg_duration_minutes(current_week)
        prior_duration = avg_duration_minutes(prior_week)
        schedule_coverage = round((sum(1 for suite in suites if suite["schedules"]) / len(suites) * 100) if suites else 0.0, 1)

        metrics = [
            {"label": "Pass rate", "value": current_pass_rate, "delta": current_pass_rate - prior_pass_rate, "suffix": "%"},
            {"label": "Failures", "value": float(current_failure_count), "delta": float(current_failure_count - prior_failure_count), "suffix": ""},
            {"label": "Avg duration", "value": current_duration, "delta": current_duration - prior_duration, "suffix": "m"},
            {"label": "Flaky hits", "value": float(current_flaky), "delta": float(current_flaky - prior_flaky), "suffix": ""},
            {"label": "Schedule coverage", "value": schedule_coverage, "delta": 0.0, "suffix": "%"},
        ]

        grouped_runs: dict[str, list[TestRun]] = defaultdict(list)
        for run in runs:
            day_bucket = self._as_utc(run.created_at).date().isoformat()
            grouped_runs[day_bucket].append(run)

        pass_rate_trend = []
        duration_trend = []
        flaky_trend = []
        for day in sorted(grouped_runs):
            day_runs = grouped_runs[day]
            timestamp = datetime.fromisoformat(f"{day}T00:00:00+00:00")
            pass_rate_trend.append({"timestamp": timestamp, "value": aggregate_pass_rate(day_runs)})
            duration_trend.append({"timestamp": timestamp, "value": avg_duration_minutes(day_runs)})
            flaky_trend.append({"timestamp": timestamp, "value": float(sum(run.flaky_count for run in day_runs))})

        failure_counter = Counter(
            result.module_name
            for run in runs
            for result in run.results
            if result.status.value == "failed"
        )
        failures_by_module = [
            {"module_name": module_name, "failures": failures}
            for module_name, failures in failure_counter.most_common(6)
        ]

        recent_runs = [serialize_run(run) for run in runs[:8]]
        latest_run_by_suite: dict[str, TestRun] = {}
        for run in runs:
            latest_run_by_suite.setdefault(run.suite_id, run)

        risk_candidates = [
            suite
            for suite in suites
            if suite["pass_rate_14d"] < 100
            or suite["flaky_cases"] > 0
            or (
                latest_run_by_suite.get(suite["id"]) is not None
                and latest_run_by_suite[suite["id"]].fail_count > 0
            )
        ]
        if not risk_candidates:
            risk_candidates = suites
        suites_at_risk = [
            {
                "id": suite["id"],
                "name": suite["name"],
                "suite_type": suite["suite_type"],
                "owner": suite["owner"],
                "latest_status": suite["latest_run_status"],
                "pass_rate_14d": suite["pass_rate_14d"],
                "flaky_cases": suite["flaky_cases"],
                "failing_results": latest_run_by_suite.get(suite["id"]).fail_count if latest_run_by_suite.get(suite["id"]) else 0,
                "environment_name": suite["default_environment"]["name"] if suite["default_environment"] else None,
            }
            for suite in sorted(risk_candidates, key=lambda item: (item["pass_rate_14d"], -item["flaky_cases"]))[:6]
        ]

        environment_badges = [
            {
                "id": environment.id,
                "name": environment.name,
                "kind": environment.kind,
                "status": environment.status,
                "project_name": environment.project.name,
                "last_checked_at": environment.last_checked_at,
            }
            for environment in environments
        ]

        return {
            "metrics": metrics,
            "pass_rate_trend": pass_rate_trend,
            "duration_trend": duration_trend,
            "flaky_trend": flaky_trend,
            "failures_by_module": failures_by_module,
            "recent_runs": recent_runs,
            "suites_at_risk": suites_at_risk,
            "environments": environment_badges,
        }

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
