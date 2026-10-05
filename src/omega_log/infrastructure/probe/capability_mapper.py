# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Capability mapper.

Transforms raw probe results into Capability objects. Porte depuis
omega-fire (infrastructure/probe/capability_mapper.py) — trimme a
map_command_probe_result/map_service_probe_result (pas de
map_kernel_probe_result, LOG ne sonde pas de modules noyau)."""
from typing import Any

from omega_log.core.capability import Capability, create_capability
from omega_log.core.enums import CapabilityStatus


class CapabilityMapper:
    """Maps probe results to Capability objects."""

    def map_command_probe_result(
        self, capability_id: str, probe_result: dict[str, Any], category: str = "backend",
    ) -> Capability:
        present = probe_result.get("present", False)
        functional = probe_result.get("functional", False)
        path = probe_result.get("path")
        message = probe_result.get("message", "")

        if not present:
            return create_capability(
                capability_id=capability_id,
                status=CapabilityStatus.MISSING,
                reason=f"Composant non installe : {message}" if message else "Binaire introuvable sur le systeme",
                detail={"path": path, "message": message},
                category=category,
            )

        if not functional:
            return create_capability(
                capability_id=capability_id,
                status=CapabilityStatus.DISQUALIFIED,
                reason=f"Binaire present mais non fonctionnel : {message}",
                detail={"path": path, "message": message},
                category=category,
            )

        return create_capability(
            capability_id=capability_id,
            status=CapabilityStatus.AVAILABLE,
            reason=f"Binaire operationnel ({path})",
            detail={"path": path, "message": message},
            category=category,
        )

    def map_service_probe_result(
        self, capability_id: str, probe_result: dict[str, Any], category: str = "service",
    ) -> Capability:
        available = probe_result.get("available", False)
        exists = probe_result.get("exists", False)
        active = probe_result.get("active", False)
        enabled = probe_result.get("enabled", False)
        state = probe_result.get("state", "unknown")
        message = probe_result.get("message", "")

        if not available:
            return create_capability(
                capability_id=capability_id,
                status=CapabilityStatus.MISSING,
                reason=f"Gestionnaire de services indisponible : {message}",
                detail={"state": state, "message": message},
                category=category,
            )

        if not exists:
            return create_capability(
                capability_id=capability_id,
                status=CapabilityStatus.MISSING,
                reason=f"Service non installe sur le systeme ({message})" if message else "Service introuvable",
                detail={"state": state, "message": message},
                category=category,
            )

        if not active:
            return create_capability(
                capability_id=capability_id,
                status=CapabilityStatus.DEGRADED,
                reason=f"Service installe mais INACTIF (arrete) : {message}",
                detail={"state": state, "active": active, "enabled": enabled, "message": message},
                category=category,
            )

        return create_capability(
            capability_id=capability_id,
            status=CapabilityStatus.AVAILABLE,
            reason=f"Service actif : {message}",
            detail={"state": state, "active": active, "enabled": enabled, "message": message},
            category=category,
        )
