# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de core/capability_registry.py."""
from __future__ import annotations

import pytest

from omega_log.core.capability import create_capability
from omega_log.core.capability_registry import CapabilityRegistry
from omega_log.core.enums import CapabilityStatus
from omega_log.core.exceptions import CapabilityNotFoundError, RegistryError


def test_register_and_get() -> None:
    registry = CapabilityRegistry()
    registry.register(create_capability("lnav", status=CapabilityStatus.AVAILABLE))
    assert registry.is_registered("lnav")
    assert registry.get("lnav").status == CapabilityStatus.AVAILABLE


def test_register_duplicate_raises() -> None:
    registry = CapabilityRegistry()
    registry.register(create_capability("lnav"))
    with pytest.raises(RegistryError):
        registry.register(create_capability("lnav"))


def test_get_or_raise_missing_capability() -> None:
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityNotFoundError):
        registry.get_or_raise("missing")


def test_is_available_respects_degraded_flag() -> None:
    registry = CapabilityRegistry()
    registry.register(create_capability("nginx", status=CapabilityStatus.DEGRADED))
    assert not registry.is_available("nginx")
    assert registry.is_available("nginx", allow_degraded=True)


def test_list_by_category() -> None:
    registry = CapabilityRegistry()
    registry.register(create_capability("nginx", category="web"))
    registry.register(create_capability("mysqld", category="databases"))
    web_caps = registry.list_by_category("web")
    assert [c.id for c in web_caps] == ["nginx"]


def test_get_summary_counts_by_status() -> None:
    registry = CapabilityRegistry()
    registry.register(create_capability("a", status=CapabilityStatus.AVAILABLE))
    registry.register(create_capability("b", status=CapabilityStatus.MISSING))
    summary = registry.get_summary()
    assert summary["total"] == 2
    assert summary["available"] == 1
    assert summary["missing"] == 1
