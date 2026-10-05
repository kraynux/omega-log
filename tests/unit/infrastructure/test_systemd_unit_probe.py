# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/probe/systemd_unit_probe.py — `systemctl` est
mocke pour rester deterministe (pas de dependance a l'etat systemd reel
de la machine qui execute les tests, contrairement au scan manuel reel
documente dans le plan)."""
from __future__ import annotations

import subprocess
from unittest.mock import patch

from omega_log.infrastructure.probe.systemd_unit_probe import SystemdUnitProbe


def _completed(returncode: int, stdout: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_probe_unit_not_found() -> None:
    probe = SystemdUnitProbe()
    with patch("subprocess.run", return_value=_completed(1)):
        result = probe.probe_unit("unknown.service")
    assert result == {
        "available": True, "exists": False, "active": False, "enabled": False,
        "state": "not_found", "message": "Unite systemd 'unknown.service' introuvable",
    }


def test_probe_unit_active_and_enabled() -> None:
    probe = SystemdUnitProbe()
    responses = [_completed(0), _completed(0, "active\n"), _completed(0, "enabled\n")]
    with patch("subprocess.run", side_effect=responses):
        result = probe.probe_unit("omega-serv.service")
    assert result["exists"] is True
    assert result["active"] is True
    assert result["enabled"] is True
    assert result["state"] == "active"


def test_probe_unit_installed_but_inactive() -> None:
    probe = SystemdUnitProbe()
    responses = [_completed(0), _completed(0, "inactive\n"), _completed(0, "disabled\n")]
    with patch("subprocess.run", side_effect=responses):
        result = probe.probe_unit("stopped.service")
    assert result["exists"] is True
    assert result["active"] is False
    assert result["enabled"] is False
