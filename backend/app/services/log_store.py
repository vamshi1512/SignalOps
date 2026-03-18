from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SeverityLevel
from app.models.log_event import LogEvent
from app.models.service import Service
from app.repositories.logs import LogRepository
from app.utils.incidenting import fingerprint


class LogStorageBackend(ABC):
    @abstractmethod
    async def ingest(
        self,
        *,
        service: Service,
        severity: SeverityLevel,
        message: str,
        source: str,
        tags: list[str],
        metadata: dict[str, Any],
        occurred_at: datetime | None,
    ) -> LogEvent:
        raise NotImplementedError


class PostgresLogStorage(LogStorageBackend):
    def __init__(self, session: AsyncSession) -> None:
        self.repository = LogRepository(session)

    async def ingest(
        self,
        *,
        service: Service,
        severity: SeverityLevel,
        message: str,
        source: str,
        tags: list[str],
        metadata: dict[str, Any],
        occurred_at: datetime | None,
    ) -> LogEvent:
        event = LogEvent(
            service_id=service.id,
            severity=severity,
            message=message,
            source=source,
            tags=tags,
            event_metadata=metadata,
            occurred_at=occurred_at,
            fingerprint=fingerprint(service.slug, message),
        )
        return await self.repository.add(event)
