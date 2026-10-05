# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/privileged/privileged_file_ops.py — verifie
la construction exacte des commandes sudo via un FakeProcessRunner
(jamais de vrai sudo/mot de passe dans les tests automatises, voir
plan_omega_log.md §5.1, Phase 9)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from omega_log.infrastructure.privileged.privileged_file_ops import (
    append_file_privileged,
    delete_file_privileged,
    overwrite_file_privileged,
    read_file_privileged,
    read_new_bytes_privileged,
    stage_protected_copy_privileged,
    truncate_file_privileged,
)
from omega_log.ports.process_runner_port import ProcessResult


@dataclass
class FakeProcessRunner:
    """Capture les commandes recues, retourne des resultats scriptes —
    jamais de sous-processus reel."""
    canned: ProcessResult = field(default_factory=lambda: ProcessResult(returncode=0, stdout="", stderr=""))
    calls: list[list[str]] = field(default_factory=list)
    input_texts: list[str | None] = field(default_factory=list)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        self.input_texts.append(input_text)
        return self.canned

    def run_interactive(self, args: list[str]) -> int:
        self.calls.append(args)
        return 0


def test_read_file_privileged_uses_sudo_cat() -> None:
    runner = FakeProcessRunner(canned=ProcessResult(returncode=0, stdout="contenu\n", stderr=""))
    result = read_file_privileged(runner, "/var/log/fail2ban.log")
    assert result.success
    assert result.content == "contenu\n"
    assert runner.calls == [["sudo", "cat", "/var/log/fail2ban.log"]]


def test_read_file_privileged_failure_message() -> None:
    runner = FakeProcessRunner(canned=ProcessResult(returncode=1, stdout="", stderr="cat: permission denied\n"))
    result = read_file_privileged(runner, "/var/log/x")
    assert not result.success
    assert "permission denied" in result.message


def test_read_new_bytes_privileged_uses_sudo_tail_with_one_indexed_offset() -> None:
    runner = FakeProcessRunner(canned=ProcessResult(returncode=0, stdout="nouvelle ligne\n", stderr=""))
    result = read_new_bytes_privileged(runner, "/var/log/x", offset=100)
    assert result.success
    assert runner.calls == [["sudo", "tail", "-c", "+101", "/var/log/x"]]


def test_read_new_bytes_privileged_falls_back_to_full_read_at_offset_zero() -> None:
    runner = FakeProcessRunner(canned=ProcessResult(returncode=0, stdout="tout\n", stderr=""))
    result = read_new_bytes_privileged(runner, "/var/log/x", offset=0)
    assert result.success
    assert runner.calls == [["sudo", "cat", "/var/log/x"]]


def test_truncate_file_privileged_uses_sudo_truncate_in_place() -> None:
    runner = FakeProcessRunner()
    result = truncate_file_privileged(runner, "/var/log/x")
    assert result.success
    assert runner.calls == [["sudo", "truncate", "-s", "0", "/var/log/x"]]


def test_delete_file_privileged_uses_sudo_rm() -> None:
    runner = FakeProcessRunner()
    result = delete_file_privileged(runner, "/var/log/x")
    assert result.success
    assert runner.calls == [["sudo", "rm", "-f", "/var/log/x"]]


def test_overwrite_file_privileged_stages_then_sudo_cp(tmp_path: Path) -> None:
    runner = FakeProcessRunner()
    target = str(tmp_path / "target.log")
    result = overwrite_file_privileged(runner, target, "nouveau contenu")
    assert result.success
    assert len(runner.calls) == 1
    cmd = runner.calls[0]
    assert cmd[0:2] == ["sudo", "cp"]
    assert cmd[-1] == target
    # le fichier temporaire est nettoye apres l'appel (succes ou echec)
    tmp_name = cmd[-2]
    assert not Path(tmp_name).exists()


def test_append_file_privileged_uses_sudo_tee_dash_a() -> None:
    runner = FakeProcessRunner()
    result = append_file_privileged(runner, "/var/log/x", "ligne ajoutee\n")
    assert result.success
    assert runner.calls == [["sudo", "tee", "-a", "--", "/var/log/x"]]
    assert runner.input_texts == ["ligne ajoutee\n"]


def test_stage_protected_copy_privileged_copies_then_chowns(tmp_path: Path) -> None:
    runner = FakeProcessRunner()
    dest_dir = tmp_path / "elevated_tmp"
    dest_dir.mkdir()
    (dest_dir / "fail2ban.log").write_text("simule la copie sudo pour ce test")

    result = stage_protected_copy_privileged(runner, Path("/var/log/fail2ban.log"), dest_dir)

    assert result.success
    assert result.content == str(dest_dir / "fail2ban.log")
    assert len(runner.calls) == 2
    assert runner.calls[0][0:2] == ["sudo", "cp"]
    assert runner.calls[1][0:2] == ["sudo", "chown"]


def test_stage_protected_copy_privileged_cleans_up_on_chown_failure(tmp_path: Path) -> None:
    class FailingChownRunner(FakeProcessRunner):
        def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
            self.calls.append(args)
            if args[1] == "chown":
                return ProcessResult(returncode=1, stdout="", stderr="chown: operation not permitted")
            return ProcessResult(returncode=0, stdout="", stderr="")

    runner = FailingChownRunner()
    dest_dir = tmp_path / "elevated_tmp"
    dest_dir.mkdir()
    (dest_dir / "fail2ban.log").write_text("x")

    result = stage_protected_copy_privileged(runner, Path("/var/log/fail2ban.log"), dest_dir)

    assert not result.success
    assert not (dest_dir / "fail2ban.log").exists()
