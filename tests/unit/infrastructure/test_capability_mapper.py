# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/probe/capability_mapper.py."""
from __future__ import annotations

from omega_log.core.enums import CapabilityStatus
from omega_log.infrastructure.probe.capability_mapper import CapabilityMapper


def test_map_command_probe_missing_binary() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_command_probe_result("lnav", {"present": False, "functional": False, "path": None, "message": ""})
    assert cap.status == CapabilityStatus.MISSING


def test_map_command_probe_present_but_not_functional() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_command_probe_result(
        "lnav", {"present": True, "functional": False, "path": "/usr/bin/lnav", "message": "broken"},
    )
    assert cap.status == CapabilityStatus.DISQUALIFIED


def test_map_command_probe_available() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_command_probe_result(
        "lnav", {"present": True, "functional": True, "path": "/usr/bin/lnav", "message": "ok"},
    )
    assert cap.status == CapabilityStatus.AVAILABLE


def test_map_service_probe_no_manager() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_service_probe_result(
        "omega-serv", {"available": False, "exists": False, "active": False, "enabled": False, "state": "", "message": ""},
    )
    assert cap.status == CapabilityStatus.MISSING


def test_map_service_probe_installed_but_inactive() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_service_probe_result(
        "omega-serv",
        {"available": True, "exists": True, "active": False, "enabled": True, "state": "inactive", "message": ""},
    )
    assert cap.status == CapabilityStatus.DEGRADED


def test_map_service_probe_active() -> None:
    mapper = CapabilityMapper()
    cap = mapper.map_service_probe_result(
        "omega-serv",
        {"available": True, "exists": True, "active": True, "enabled": True, "state": "active", "message": ""},
    )
    assert cap.status == CapabilityStatus.AVAILABLE
