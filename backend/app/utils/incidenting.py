from __future__ import annotations

import re
from typing import Any


_numbers = re.compile(r"\b\d+\b")
_hex = re.compile(r"0x[0-9a-fA-F]+")
_whitespace = re.compile(r"\s+")


def normalize_message(message: str) -> str:
    normalized = message.lower().strip()
    normalized = _hex.sub("<hex>", normalized)
    normalized = _numbers.sub("<num>", normalized)
    normalized = _whitespace.sub(" ", normalized)
    return normalized[:160]


def fingerprint(service_slug: str, message: str) -> str:
    return f"{service_slug}:{normalize_message(message)}"


def root_cause_hint(message: str, metadata: dict[str, Any]) -> str:
    if "timeout" in message.lower():
        return "Upstream timeout pattern detected. Check downstream dependency saturation and connection pool usage."
    if "unauthorized" in message.lower() or metadata.get("status_code") == "401":
        return "Auth failures are clustering. Verify token issuer drift and credential rotation state."
    if "database" in message.lower() or "postgres" in message.lower():
        return "Database path implicated. Inspect query latency, locks, and connection churn."
    if "queue" in message.lower():
        return "Worker backlog signature detected. Inspect queue depth and consumer throughput."
    return "Repeated error fingerprint detected. Compare deployment changes, shared tags, and the most recent critical logs."

