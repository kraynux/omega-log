# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/purge_logs.py — troncature en place
(inode preserve) vs recreation (permissions corrigees), plan_omega_log.md §5.
Tests d'elevation sudo ponctuelle (§5.1, Phase 9) a la fin du fichier."""
from __future__ import annotations

import stat
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from omega_log.application.use_cases.purge_logs import delete_log_files, purge_log_content
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.ports.process_runner_port import ProcessResult


def test_purge_content_truncates_in_place_preserving_inode(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("some content\n")
    inode_before = log_path.stat().st_ino

    result = purge_log_content(str(log_path))

    assert result.success
    assert not result.recreated
    assert log_path.stat().st_size == 0
    assert log_path.stat().st_ino == inode_before


def test_purge_content_recreates_missing_file_with_group_writable_mode(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.log"

    result = purge_log_content(str(missing_path))

    assert result.success
    assert result.recreated
    assert missing_path.exists()
    mode = stat.S_IMODE(missing_path.stat().st_mode)
    assert mode == 0o664


def test_delete_log_files_removes_files(tmp_path: Path) -> None:
    a = tmp_path / "a.log"
    b = tmp_path / "b.log"
    a.write_text("x")
    b.write_text("x")

    result = delete_log_files([str(a), str(b)])

    assert result.success
    assert not a.exists()
    assert not b.exists()
    assert set(result.deleted) == {str(a), str(b)}


@dataclass
class _FakeProcessRunner:
    calls: list[list[str]] = field(default_factory=list)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        return ProcessResult(returncode=0, stdout="", stderr="")

    def run_interactive(self, args: list[str]) -> int:  # pragma: no cover - non utilise ici
        self.calls.append(args)
        return 0


def test_purge_content_without_runner_raises_permission_required(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("content")
    log_path.chmod(0o444)  # pas inscriptible, mais existe (check_path_writable echoue)
    try:
        with pytest.raises(PermissionRequiredError):
            purge_log_content(str(log_path))
    finally:
        log_path.chmod(0o644)


def test_purge_content_falls_back_to_privileged_truncate(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("content")
    log_path.chmod(0o444)
    try:
        runner = _FakeProcessRunner()
        result = purge_log_content(str(log_path), runner=runner)
    finally:
        log_path.chmod(0o644)
    assert result.success
    assert runner.calls == [["sudo", "truncate", "-s", "0", str(log_path)]]


def test_delete_log_files_without_runner_raises_permission_required(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("content")
    log_path.chmod(0o444)
    try:
        with pytest.raises(PermissionRequiredError):
            delete_log_files([str(log_path)])
    finally:
        log_path.chmod(0o644)


def test_delete_log_files_falls_back_to_privileged_delete(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("content")
    log_path.chmod(0o444)
    runner = _FakeProcessRunner()
    try:
        result = delete_log_files([str(log_path)], runner=runner)
    finally:
        log_path.chmod(0o644) if log_path.exists() else None
    assert result.success
    assert runner.calls == [["sudo", "rm", "-f", str(log_path)]]
