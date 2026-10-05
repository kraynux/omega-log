# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/privileged/elevation.py."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_log.infrastructure.privileged.elevation import (
    PermissionRequiredError,
    authenticate_sudo,
    running_as_root,
)


@dataclass
class FakeProcessRunner:
    interactive_returncode: int = 0
    calls: list[list[str]] = field(default_factory=list)

    def run(self, args, input_text=None, timeout=None):  # pragma: no cover - non utilise ici
        raise NotImplementedError

    def run_interactive(self, args: list[str]) -> int:
        self.calls.append(args)
        return self.interactive_returncode


def test_running_as_root_false_for_this_test_process() -> None:
    # Les tests ne tournent jamais en root dans cette suite (voir CI/dev local).
    assert running_as_root() is False


def test_authenticate_sudo_success_calls_sudo_dash_v() -> None:
    runner = FakeProcessRunner(interactive_returncode=0)
    result = authenticate_sudo(runner)
    assert result.success
    assert runner.calls == [["sudo", "-v"]]


def test_authenticate_sudo_failure_reports_message() -> None:
    runner = FakeProcessRunner(interactive_returncode=1)
    result = authenticate_sudo(runner)
    assert not result.success
    assert result.message


def test_permission_required_error_carries_path() -> None:
    exc = PermissionRequiredError("/var/log/fail2ban.log")
    assert exc.path == "/var/log/fail2ban.log"
    assert "/var/log/fail2ban.log" in str(exc)
