# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/probe/command_probe.py — utilise `python3`
(toujours present dans l'environnement de test) et un nom de binaire
improbable, jamais de dependance a un outil tiers specifique."""
from __future__ import annotations

import sys

from omega_log.infrastructure.probe.command_probe import CommandProbe


def test_check_presence_of_known_binary() -> None:
    probe = CommandProbe()
    assert probe.check_presence("python3") or probe.check_presence("python")


def test_check_presence_of_unknown_binary() -> None:
    probe = CommandProbe()
    assert not probe.check_presence("this-binary-does-not-exist-omega-log")


def test_probe_command_missing_binary_shape() -> None:
    probe = CommandProbe()
    result = probe.probe_command("this-binary-does-not-exist-omega-log")
    assert result == {"present": False, "functional": False, "path": None, "message": result["message"]}
    assert "not found" in result["message"]


def test_probe_command_present_without_test_command() -> None:
    probe = CommandProbe()
    binary = "python3" if probe.check_presence("python3") else sys.executable
    result = probe.probe_command(binary)
    assert result["present"] is True
    assert result["functional"] is True
