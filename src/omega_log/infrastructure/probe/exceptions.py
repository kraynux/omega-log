# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Probe exceptions. Technical exceptions specific to the probe
subsystem. Porte depuis omega-fire (infrastructure/probe/exceptions.py)
— trimme a ce qui est reellement leve par LOG (pas de
CapabilityMappingError, jamais levee par capability_mapper.py)."""
from omega_log.core.exceptions import CoreError


class ProbeError(CoreError):
    """Base exception for probe operations."""
    def __init__(self, message: str, probe_name: str | None = None, context: dict | None = None):
        super().__init__(message, context)
        self.probe_name = probe_name
        if probe_name:
            self.context["probe_name"] = probe_name


class ProbeExecutionError(ProbeError):
    """Raised when a probe fails to execute."""
    def __init__(self, probe_name: str, reason: str, context: dict | None = None):
        super().__init__(
            f"Probe '{probe_name}' execution failed: {reason}",
            probe_name=probe_name,
            context={**(context or {}), "reason": reason},
        )
        self.reason = reason


class ScannerError(ProbeError):
    """Raised when the scanner encounters a critical error."""
    def __init__(
        self,
        reason: str,
        probes_completed: int = 0,
        probes_failed: int = 0,
        context: dict | None = None,
    ):
        super().__init__(
            f"Scanner failed: {reason}",
            probe_name="scanner",
            context={
                **(context or {}),
                "reason": reason,
                "probes_completed": probes_completed,
                "probes_failed": probes_failed,
            },
        )
        self.reason = reason
        self.probes_completed = probes_completed
        self.probes_failed = probes_failed
