# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Core capability registry.

Defines the CapabilityRegistry class, the central registry for all
system capabilities. Single source of truth for what is available on
the target machine. Porte verbatim depuis omega-fire
(core/capability_registry.py)."""

from omega_log.core.capability import Capability
from omega_log.core.enums import CapabilityStatus
from omega_log.core.exceptions import CapabilityNotFoundError, InvalidCapabilityError, RegistryError


class CapabilityRegistry:
    """Central registry for system capabilities."""

    def __init__(self):
        self._capabilities: dict[str, Capability] = {}
        self._initialized: bool = False

    def register(self, capability: Capability) -> None:
        if not capability.id:
            raise InvalidCapabilityError("Capability ID cannot be empty", capability_id=capability.id)

        if capability.id in self._capabilities:
            raise RegistryError(
                f"Capability '{capability.id}' is already registered",
                capability_id=capability.id,
                operation="register",
            )

        self._capabilities[capability.id] = capability
        self._initialized = True

    def update(self, capability: Capability) -> None:
        if not capability.id:
            raise InvalidCapabilityError("Capability ID cannot be empty", capability_id=capability.id)

        if capability.id not in self._capabilities:
            raise CapabilityNotFoundError(capability.id)

        self._capabilities[capability.id] = capability

    def get(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    def get_or_raise(self, capability_id: str) -> Capability:
        capability = self.get(capability_id)
        if capability is None:
            raise CapabilityNotFoundError(capability_id)
        return capability

    def is_available(self, capability_id: str, allow_degraded: bool = False) -> bool:
        capability = self.get(capability_id)
        if capability is None:
            return False
        return capability.is_usable(allow_degraded)

    def is_registered(self, capability_id: str) -> bool:
        return capability_id in self._capabilities

    def invalidate(self, capability_id: str, reason: str = "") -> None:
        self.get_or_raise(capability_id).mark_missing(reason)

    def mark_degraded(self, capability_id: str, reason: str, detail: dict | None = None) -> None:
        self.get_or_raise(capability_id).mark_degraded(reason, detail)

    def mark_disqualified(self, capability_id: str, reason: str, detail: dict | None = None) -> None:
        self.get_or_raise(capability_id).mark_disqualified(reason, detail)

    def mark_available(self, capability_id: str, reason: str = "") -> None:
        self.get_or_raise(capability_id).mark_available(reason)

    def list_all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def list_by_status(self, status: CapabilityStatus) -> list[Capability]:
        return [c for c in self._capabilities.values() if c.status == status]

    def list_by_category(self, category: str) -> list[Capability]:
        """Ajoute depuis omega-fire : utile pour LOG, qui groupe les
        capacites par categorie annuaire (web, databases, mail, dns,
        security, ...) — absent de la version source car FIRE n'avait
        pas besoin de filtrer par categorie dans son registre."""
        return [c for c in self._capabilities.values() if c.category == category]

    def list_available(self, include_degraded: bool = False) -> list[Capability]:
        return [c for c in self._capabilities.values() if c.is_usable(allow_degraded=include_degraded)]

    def list_missing(self) -> list[Capability]:
        return self.list_by_status(CapabilityStatus.MISSING)

    def list_degraded(self) -> list[Capability]:
        return self.list_by_status(CapabilityStatus.DEGRADED)

    def list_disqualified(self) -> list[Capability]:
        return self.list_by_status(CapabilityStatus.DISQUALIFIED)

    def count(self) -> int:
        return len(self._capabilities)

    def count_by_status(self, status: CapabilityStatus) -> int:
        return len(self.list_by_status(status))

    def clear(self) -> None:
        self._capabilities.clear()
        self._initialized = False

    def is_initialized(self) -> bool:
        return self._initialized

    def get_summary(self) -> dict:
        return {
            "total": self.count(),
            "available": self.count_by_status(CapabilityStatus.AVAILABLE),
            "degraded": self.count_by_status(CapabilityStatus.DEGRADED),
            "missing": self.count_by_status(CapabilityStatus.MISSING),
            "disqualified": self.count_by_status(CapabilityStatus.DISQUALIFIED),
            "initialized": self._initialized,
        }

    def to_dict(self) -> dict[str, dict]:
        return {cap_id: cap.to_dict() for cap_id, cap in self._capabilities.items()}

    def __str__(self) -> str:
        summary = self.get_summary()
        return (
            f"CapabilityRegistry({summary['total']} capabilities: "
            f"{summary['available']} available, "
            f"{summary['degraded']} degraded, "
            f"{summary['missing']} missing, "
            f"{summary['disqualified']} disqualified)"
        )

    def __contains__(self, capability_id: str) -> bool:
        return self.is_registered(capability_id)

    def __len__(self) -> int:
        return self.count()
