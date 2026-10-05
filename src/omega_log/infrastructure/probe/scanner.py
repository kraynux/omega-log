# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""System scanner.

Orchestrates service detection and populates the capability registry —
etape 1 de scan_logs (plan_omega_log.md §4). Adapte depuis omega-fire
(infrastructure/probe/scanner.py) : `_scan_backends`/`_scan_fail2ban`/
`_scan_conntrack`/`_scan_service_manager` sont specifiques au pare-feu de
FIRE (nftables/iptables/conntrack) et delibrement PAS portes — seul
`_scan_known_services()` (pgrep sur KNOWN_SERVICES) a un equivalent
reel ici, complete par `_scan_systemd_unit_services()` (NEUF, pour
omega-serv et tout futur service detecte par unite systemd plutot que
par nom de process)."""
from __future__ import annotations

import subprocess

from omega_log.core.capability_registry import CapabilityRegistry
from omega_log.core.enums import CapabilityStatus
from omega_log.infrastructure.probe.capability_mapper import CapabilityMapper
from omega_log.infrastructure.probe.known_services import KNOWN_SERVICES, SYSTEMD_UNIT_SERVICES
from omega_log.infrastructure.probe.systemd_unit_probe import SystemdUnitProbe


class SystemScanner:
    """Orchestre la detection de services et peuple le registre de
    capacites — seule etape portee depuis FIRE qui a un sens pour LOG."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry
        self._mapper = CapabilityMapper()
        self._systemd_probe = SystemdUnitProbe()

    def scan(self) -> dict:
        """Retourne {capabilities_registered, capabilities_available,
        capabilities_degraded, capabilities_missing,
        capabilities_disqualified, errors}."""
        errors: list[str] = []
        registered = 0

        try:
            registered += self._scan_known_services()
        except Exception as e:  # noqa: BLE001 - un probe en echec ne doit jamais arreter le scan
            errors.append(f"Known services scan failed: {e}")

        try:
            registered += self._scan_systemd_unit_services()
        except Exception as e:  # noqa: BLE001
            errors.append(f"Systemd unit scan failed: {e}")

        counts = {status: 0 for status in CapabilityStatus}
        for cap in self._registry.list_all():
            counts[cap.status] += 1

        return {
            "capabilities_registered": registered,
            "capabilities_available": counts[CapabilityStatus.AVAILABLE],
            "capabilities_degraded": counts[CapabilityStatus.DEGRADED],
            "capabilities_missing": counts[CapabilityStatus.MISSING],
            "capabilities_disqualified": counts[CapabilityStatus.DISQUALIFIED],
            "errors": errors,
        }

    def _scan_known_services(self) -> int:
        """Sonde chaque service connu via `pgrep -x` (meme mecanisme
        qu'omega-fire)."""
        registered_count = 0

        for category, process_names in KNOWN_SERVICES.items():
            for process_name in process_names:
                cap_id = process_name
                try:
                    result = subprocess.run(
                        ["pgrep", "-x", process_name], capture_output=True, timeout=2, check=False,
                    )
                    present = result.returncode == 0
                except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                    present = False

                probe_result = {
                    "present": present,
                    "functional": present,
                    "path": None,
                    "message": "Processus detecte" if present else "Processus non detecte",
                }
                capability = self._mapper.map_command_probe_result(cap_id, probe_result, category=category)

                if self._registry.is_registered(cap_id):
                    self._registry.update(capability)
                else:
                    self._registry.register(capability)
                registered_count += 1

        return registered_count

    def _scan_systemd_unit_services(self) -> int:
        """Sonde chaque service de SYSTEMD_UNIT_SERVICES via `systemctl`
        plutot que `pgrep` (voir known_services.py et annuaire §2/§15)."""
        registered_count = 0

        for cap_id, unit_name in SYSTEMD_UNIT_SERVICES.items():
            probe_result = self._systemd_probe.probe_unit(unit_name)
            capability = self._mapper.map_service_probe_result(cap_id, probe_result, category="omega")

            if self._registry.is_registered(cap_id):
                self._registry.update(capability)
            else:
                self._registry.register(capability)
            registered_count += 1

        return registered_count

    def rescan(self) -> dict:
        self._registry.clear()
        return self.scan()
