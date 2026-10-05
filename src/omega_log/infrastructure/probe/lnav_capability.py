# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Detection de la presence/fonctionnalite du binaire `lnav` — patron
CapabilityRegistry d'omega-fire reoriente (plan_omega_log.md §4, point
2) : `lnav` est une dependance systeme externe (binaire C/C++), jamais
un paquet Python, donc jamais dans pyproject.toml/requirements.txt —
verifiee au runtime comme fail2ban/nftables le sont deja chez FIRE."""
from __future__ import annotations

from omega_log.core.capability import Capability
from omega_log.infrastructure.probe.capability_mapper import CapabilityMapper
from omega_log.infrastructure.probe.command_probe import CommandProbe

_CAPABILITY_ID = "lnav"


def probe_lnav() -> Capability:
    probe = CommandProbe()
    result = probe.probe_command("lnav", test_command=["lnav", "-V"])
    return CapabilityMapper().map_command_probe_result(_CAPABILITY_ID, result, category="viewer")
