# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sauvegardes planifiees executees (portees d'omega-serv 2.6.0, 2026-11-07)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from omega_log.application.use_cases import rotation_automation as ra
from omega_log.domain.logs.rotation_schedule import (
    build_rotation_cron_line,
    build_rotation_service_unit,
    is_due,
    next_run,
    rotation_cron_marker,
    without_marked_line,
)
from omega_log.infrastructure.storage.rotation_automation_store import RotationAutomationStore
from omega_log.ports.process_runner_port import ProcessResult

_NOW = datetime(2026, 11, 7, 3, 45, tzinfo=timezone.utc)


def test_due_after_interval_and_unreadable_never_due() -> None:
    created = {"path": "/x", "days_interval": 7, "created_at": (_NOW - timedelta(days=8)).isoformat()}
    assert is_due(created, _NOW)
    assert next_run(created) == _NOW - timedelta(days=1)
    assert not is_due({"path": "/x", "days_interval": 7, "last_run_at": _NOW.isoformat()}, _NOW)
    assert not is_due({"path": "/x"}, _NOW)


def test_units_and_cron_line_carry_the_var_dir() -> None:
    unit = build_rotation_service_unit(python_executable="/v/bin/python", var_dir="/home/u/var", user="u")
    assert "User=u" in unit and "Environment=OMEGA_LOG_VAR_DIR=/home/u/var" in unit
    assert "-m omega_log rotate run-automations" in unit
    line = build_rotation_cron_line(python_executable="/v/bin/python", var_dir="/home/u/var", user="u")
    assert line.startswith("45 3 * * * OMEGA_LOG_VAR_DIR=/home/u/var ") and line.endswith(rotation_cron_marker("u"))
    assert without_marked_line(f"0 1 * * * other\n{line}\n", "u") == ["0 1 * * * other"]


def test_run_due_automations_records_result(tmp_path: Path) -> None:
    store = RotationAutomationStore(tmp_path / "a.json")
    old = (_NOW - timedelta(days=2)).isoformat()
    store.add({"path": "/ok.log", "days_interval": 1, "created_at": old})
    store.add({"path": "/protege.log", "days_interval": 1, "created_at": old})
    store.add({"path": "/pas-du.log", "days_interval": 30, "created_at": old})
    runs = ra.run_due_automations(store, _NOW, lambda path: (path == "/ok.log", "fait" if path == "/ok.log" else "refus"))
    assert [(run.path, run.success) for run in runs] == [("/ok.log", True), ("/protege.log", False)]
    saved = store.list_all()
    assert saved[0]["last_run_at"] == _NOW.isoformat() and saved[0]["last_success"] is True
    assert saved[1]["last_success"] is False and "last_run_at" not in saved[1]
    assert "last_result" not in saved[2]


class _Crontab:
    def __init__(self, content: str = "", missing: bool = False) -> None:
        self.content, self.missing, self.calls = content, missing, []

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        if self.missing:
            return ProcessResult(127, "", "")
        if args == ["crontab", "-l"]:
            return ProcessResult(0, self.content, "")
        if args == ["crontab", "-"]:
            self.content = input_text or ""
            return ProcessResult(0, "", "")
        return ProcessResult(1, "", "inattendu")

    def run_interactive(self, args: list[str]) -> int:
        return 0


def test_crontab_install_status_remove(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ra, "uses_systemd", lambda: False)
    runner = _Crontab("0 1 * * * autre\n")
    result = ra.install_rotation_schedule("u", tmp_path, "/v/bin/python", runner)
    assert result.success and result.mechanism == "cron"
    assert "autre" in runner.content and rotation_cron_marker("u") in runner.content
    assert ra.rotation_schedule_status("u", runner).success
    assert ra.remove_rotation_schedule("u", runner).success
    assert rotation_cron_marker("u") not in runner.content and "autre" in runner.content


def test_without_crontab_shows_manual_instructions(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ra, "uses_systemd", lambda: False)
    result = ra.install_rotation_schedule("u", tmp_path, "/v/bin/python", _Crontab(missing=True))
    assert result.mechanism == "manual" and not result.success and "crontab" in result.message
