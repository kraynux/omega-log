# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Probe results. Structured result types for probe operations. Porte
depuis omega-fire (infrastructure/probe/results.py) — trimme a
CommandProbeResult/ServiceProbeResult/ScanResult (pas KernelProbeResult,
LOG ne sonde pas de modules noyau)."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandProbeResult:
    """Result type for command probe operations."""
    present: bool
    functional: bool
    path: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"present": self.present, "functional": self.functional, "path": self.path, "message": self.message}


@dataclass
class ServiceProbeResult:
    """Result type for service probe operations."""
    available: bool
    exists: bool
    active: bool
    enabled: bool
    state: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "exists": self.exists,
            "active": self.active,
            "enabled": self.enabled,
            "state": self.state,
            "message": self.message,
        }


@dataclass
class ScanResult:
    """Result type for complete system scan."""
    capabilities_registered: int
    capabilities_available: int
    capabilities_degraded: int
    capabilities_missing: int
    capabilities_disqualified: int
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capabilities_registered": self.capabilities_registered,
            "capabilities_available": self.capabilities_available,
            "capabilities_degraded": self.capabilities_degraded,
            "capabilities_missing": self.capabilities_missing,
            "capabilities_disqualified": self.capabilities_disqualified,
            "errors": self.errors,
        }

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
