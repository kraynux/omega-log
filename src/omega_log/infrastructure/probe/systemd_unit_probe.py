# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Systemd unit probe.

NEUF (pas de precedent dans la suite) : contrairement a nginx/apache/etc.
(binaire nomme distinctement, `pgrep` suffit), certains services visés
par le Registre se lancent sous un nom de process generique (ex.
`python -m omega_serv ... serve`, voir plan_omega_log.md §4 et l'annuaire
§2/§15 — omega-serv est le premier cas reel verifie sur la machine de
reference). `pgrep` seul ne les distingue pas d'un autre process du meme
interpreteur ; la detection fiable passe par l'unite systemd elle-meme.

Volontairement MINIMAL : ne porte PAS la couche d'abstraction multi-init
(systemd/openrc/runit) d'omega-fire — LOG n'a besoin, pour l'instant, que
de verifier des unites systemd nommees explicitement (voir
known_services.py::SYSTEMD_UNIT_SERVICES), pas de detecter quel
gestionnaire de services tourne sur la machine. A etendre le jour ou un
besoin reel runit/openrc se presente, pas avant (YAGNI)."""
from __future__ import annotations

import subprocess


class SystemdUnitProbe:
    """Interroge `systemctl` pour une unite nommee explicitement."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self._timeout = timeout_seconds

    def _systemctl(self, *args: str) -> tuple[int, str]:
        try:
            result = subprocess.run(
                ["systemctl", *args],
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,
            )
            return result.returncode, result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return 1, ""

    def probe_unit(self, unit_name: str) -> dict:
        """Retourne la meme forme que ServiceProbe.check_service_status()
        de FIRE (available/exists/active/enabled/state/message), pour que
        capability_mapper.map_service_probe_result() reste inchange."""
        returncode, _ = self._systemctl("cat", unit_name)
        if returncode != 0:
            return {
                "available": True,
                "exists": False,
                "active": False,
                "enabled": False,
                "state": "not_found",
                "message": f"Unite systemd '{unit_name}' introuvable",
            }

        _, active_state = self._systemctl("is-active", unit_name)
        _, enabled_state = self._systemctl("is-enabled", unit_name)
        active = active_state == "active"
        enabled = enabled_state == "enabled"

        return {
            "available": True,
            "exists": True,
            "active": active,
            "enabled": enabled,
            "state": active_state or "unknown",
            "message": f"Unite '{unit_name}' : {active_state or 'unknown'} ({enabled_state or 'unknown'} au demarrage)",
        }
