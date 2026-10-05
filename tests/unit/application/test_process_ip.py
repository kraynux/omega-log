# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/process_ip.py."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from omega_log.application.use_cases.process_ip import (
    compute_top_ips_for_paths,
    count_ip_occurrences,
    remove_ip_from_file,
)
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.ports.process_runner_port import ProcessResult

_LOG_CONTENT = (
    '10.0.0.1 - - [10/Oct/2026:10:00:00] "GET / HTTP/1.1" 200 100\n'
    '10.0.0.2 - - [10/Oct/2026:10:00:01] "GET / HTTP/1.1" 200 100\n'
    '10.0.0.1 - - [10/Oct/2026:10:00:02] "GET /x HTTP/1.1" 404 50\n'
)


def test_compute_top_ips_for_paths(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    top = compute_top_ips_for_paths([str(log_path)], n=5)
    assert top[0].ip == "10.0.0.1"
    assert top[0].count == 2


def test_count_ip_occurrences(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)
    assert count_ip_occurrences(str(log_path), "10.0.0.1") == 2
    assert count_ip_occurrences(str(log_path), "10.0.0.9") == 0


def test_count_ip_occurrences_rejects_invalid_ip(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)
    assert count_ip_occurrences(str(log_path), "not-an-ip") == 0


def test_remove_ip_from_file_rewrites_content(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    result = remove_ip_from_file(str(log_path), "10.0.0.1")
    assert result.success
    assert result.occurrences == 2

    remaining = log_path.read_text().splitlines()
    assert len(remaining) == 1
    assert "10.0.0.2" in remaining[0]
    assert not any(line for line in remaining if "10.0.0.1" in line)


def test_remove_ip_from_file_no_occurrences(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)
    result = remove_ip_from_file(str(log_path), "10.0.0.9")
    assert result.success
    assert result.occurrences == 0


def test_remove_ip_from_file_invalid_ip(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)
    result = remove_ip_from_file(str(log_path), "not-an-ip")
    assert not result.success


def test_remove_ip_from_file_missing_file(tmp_path: Path) -> None:
    result = remove_ip_from_file(str(tmp_path / "missing.log"), "10.0.0.1")
    assert not result.success


@dataclass
class _FakeProcessRunner:
    """Simule un sudo deja authentifie — jamais de vrai sous-processus
    (plan_omega_log.md §5.1, Phase 9)."""
    canned_stdout: str = ""
    calls: list[list[str]] = field(default_factory=list)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        return ProcessResult(returncode=0, stdout=self.canned_stdout, stderr="")

    def run_interactive(self, args: list[str]) -> int:  # pragma: no cover - non utilise ici
        self.calls.append(args)
        return 0


def test_count_ip_occurrences_without_runner_raises_permission_required(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text(_LOG_CONTENT)
    log_path.chmod(0)
    try:
        with pytest.raises(PermissionRequiredError):
            count_ip_occurrences(str(log_path), "10.0.0.1")
    finally:
        log_path.chmod(0o644)


def test_count_ip_occurrences_falls_back_to_privileged_read(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("placeholder")
    log_path.chmod(0)
    try:
        runner = _FakeProcessRunner(canned_stdout=_LOG_CONTENT)
        count = count_ip_occurrences(str(log_path), "10.0.0.1", runner=runner)
    finally:
        log_path.chmod(0o644)
    assert count == 2
    assert runner.calls == [["sudo", "cat", str(log_path)]]


def test_remove_ip_from_file_without_runner_raises_permission_required(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text(_LOG_CONTENT)
    log_path.chmod(0)
    try:
        with pytest.raises(PermissionRequiredError):
            remove_ip_from_file(str(log_path), "10.0.0.1")
    finally:
        log_path.chmod(0o644)


def test_remove_ip_from_file_falls_back_to_privileged_write(tmp_path: Path) -> None:
    # Simule /var/log : le DOSSIER n'est pas inscriptible par nous (donc
    # meme l'ecriture atomique via fichier temporaire voisin echoue, pas
    # seulement l'ouverture directe du fichier cible) — sans ca,
    # os.replace() ne verifie que les permissions du DOSSIER, jamais
    # celles du fichier cible lui-meme, et reussirait a tort dans ce test.
    subdir = tmp_path / "protected_dir"
    subdir.mkdir()
    log_path = subdir / "protected.log"
    log_path.write_text("placeholder")
    log_path.chmod(0)
    subdir.chmod(0o555)
    try:
        runner = _FakeProcessRunner(canned_stdout=_LOG_CONTENT)
        result = remove_ip_from_file(str(log_path), "10.0.0.1", runner=runner)
    finally:
        subdir.chmod(0o755)
        log_path.chmod(0o644)
    assert result.success
    assert result.occurrences == 2
    # lecture privilegiee (sudo cat) puis ecriture privilegiee (sudo cp, l'ecriture
    # Python directe sur la cible ayant elle-meme echoue en PermissionError)
    assert runner.calls[0] == ["sudo", "cat", str(log_path)]
    assert runner.calls[1][0:2] == ["sudo", "cp"]
    assert runner.calls[1][-1] == str(log_path)
