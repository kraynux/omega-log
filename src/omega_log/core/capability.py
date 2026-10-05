# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Core capability model.

Defines the Capability dataclass, which represents a single system
capability with its status, reason, and metadata. Porte verbatim depuis
omega-fire (core/capability.py)."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from omega_log.core.enums import CapabilityStatus


@dataclass
class Capability:
    """A single system capability."""
    id: str
    status: CapabilityStatus
    reason: str = ""
    detail: dict[str, Any] | None = None
    last_checked: datetime = field(default_factory=datetime.now)
    category: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        return self.status == CapabilityStatus.AVAILABLE

    def is_degraded(self) -> bool:
        return self.status == CapabilityStatus.DEGRADED

    def is_missing(self) -> bool:
        return self.status == CapabilityStatus.MISSING

    def is_disqualified(self) -> bool:
        return self.status == CapabilityStatus.DISQUALIFIED

    def is_usable(self, allow_degraded: bool = False) -> bool:
        if self.status == CapabilityStatus.AVAILABLE:
            return True
        return bool(allow_degraded and self.status == CapabilityStatus.DEGRADED)

    def update_status(
        self,
        status: CapabilityStatus,
        reason: str = "",
        detail: dict[str, Any] | None = None,
    ) -> None:
        self.status = status
        self.reason = reason
        if detail is not None:
            self.detail = detail
        self.last_checked = datetime.now()

    def mark_available(self, reason: str = "") -> None:
        self.update_status(CapabilityStatus.AVAILABLE, reason)

    def mark_degraded(self, reason: str, detail: dict[str, Any] | None = None) -> None:
        self.update_status(CapabilityStatus.DEGRADED, reason, detail)

    def mark_missing(self, reason: str = "") -> None:
        self.update_status(CapabilityStatus.MISSING, reason)

    def mark_disqualified(self, reason: str, detail: dict[str, Any] | None = None) -> None:
        self.update_status(CapabilityStatus.DISQUALIFIED, reason, detail)

    def age_seconds(self, now: datetime | None = None) -> float:
        if now is None:
            now = datetime.now()
        delta = now - self.last_checked
        return delta.total_seconds()

    def is_stale(self, max_age_seconds: int = 300) -> bool:
        return self.age_seconds() > max_age_seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "reason": self.reason,
            "detail": self.detail,
            "last_checked": self.last_checked.isoformat(),
            "category": self.category,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        status_str = self.status.value.upper()
        if self.reason:
            return f"{self.id}: {status_str} ({self.reason})"
        return f"{self.id}: {status_str}"


def create_capability(
    capability_id: str,
    status: CapabilityStatus = CapabilityStatus.AVAILABLE,
    reason: str = "",
    detail: dict[str, Any] | None = None,
    category: str | None = None,
) -> Capability:
    return Capability(id=capability_id, status=status, reason=reason, detail=detail, category=category)
