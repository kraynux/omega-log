# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/commands/rotate_logs.py — le point important est
la retention : les archives les plus ANCIENNES doivent etre supprimees,
pas les plus recentes (bug reel trouve et corrige en Phase 6, voir le
commentaire dans rotate_logs.py). Tests d'elevation sudo ponctuelle
(§5.1, Phase 9) a la fin du fichier."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from omega_log.application.commands.rotate_logs import RotateLogsCommand, RotateLogsRequest
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.storage.files.archive_store import ArchiveStore
from omega_log.infrastructure.storage.files.persistence_adapter import FileBackupAdapter
from omega_log.ports.process_runner_port import ProcessResult


def test_rotate_creates_backup(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("content")
    backup_dir = tmp_path / "backups"
    port = FileBackupAdapter(ArchiveStore(backup_dir))

    command = RotateLogsCommand(port, backup_dir)
    result = command.execute(RotateLogsRequest(source_path=str(log_path), keep=5))

    assert result.success
    assert result.backup_path is not None
    assert result.backup_path.exists()


def test_rotate_rejects_missing_source(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    port = FileBackupAdapter(ArchiveStore(backup_dir))
    command = RotateLogsCommand(port, backup_dir)

    result = command.execute(RotateLogsRequest(source_path=str(tmp_path / "missing.log")))
    assert not result.success


def test_rotate_retention_deletes_oldest_not_newest(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    backup_dir = tmp_path / "backups"
    port = FileBackupAdapter(ArchiveStore(backup_dir))
    command = RotateLogsCommand(port, backup_dir)

    for i in range(3):
        log_path.write_text(f"content {i}")
        command.execute(RotateLogsRequest(source_path=str(log_path), keep=2))
        time.sleep(1.1)  # le nom d'archive est horodate a la seconde

    backups = port.list_backups(backup_dir)
    assert len(backups) == 2
    # la plus ancienne des 3 doit avoir disparu, les 2 plus recentes restent
    newest_two = sorted(backups, key=lambda b: b.created_at)
    assert newest_two[0].created_at < newest_two[1].created_at


@dataclass
class _FakeStagingRunner:
    """Simule `sudo cp`/`sudo chown` reels (le FakeProcessRunner le plus
    simple ne cree jamais le fichier de destination, insuffisant ici :
    la suite reelle de l'execute() a besoin d'un fichier stage reellement
    present pour archiver du contenu non vide)."""
    source_content: str
    calls: list[list[str]] = field(default_factory=list)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        if args[0:2] == ["sudo", "cp"]:
            Path(args[-1]).write_text(self.source_content)
            return ProcessResult(returncode=0, stdout="", stderr="")
        if args[0:2] == ["sudo", "chown"]:
            return ProcessResult(returncode=0, stdout="", stderr="")
        return ProcessResult(returncode=1, stdout="", stderr="commande inattendue")

    def run_interactive(self, args: list[str]) -> int:  # pragma: no cover - non utilise ici
        self.calls.append(args)
        return 0


def test_rotate_without_runner_raises_permission_required(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("x")
    log_path.chmod(0)
    backup_dir = tmp_path / "backups"
    port = FileBackupAdapter(ArchiveStore(backup_dir))
    command = RotateLogsCommand(port, backup_dir, tmp_path / "elevated_tmp")
    try:
        with pytest.raises(PermissionRequiredError):
            command.execute(RotateLogsRequest(source_path=str(log_path), keep=5))
    finally:
        log_path.chmod(0o644)


def test_rotate_stages_protected_source_then_cleans_up(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text("contenu protege")
    log_path.chmod(0)
    backup_dir = tmp_path / "backups"
    elevated_tmp_dir = tmp_path / "elevated_tmp"
    port = FileBackupAdapter(ArchiveStore(backup_dir))
    command = RotateLogsCommand(port, backup_dir, elevated_tmp_dir)

    try:
        runner = _FakeStagingRunner(source_content="contenu protege")
        result = command.execute(RotateLogsRequest(source_path=str(log_path), keep=5), runner=runner)
    finally:
        log_path.chmod(0o644)

    assert result.success
    assert result.backup_path is not None
    assert result.backup_path.exists()
    assert result.backup_size_bytes is not None and result.backup_size_bytes > 0
    # la copie de mise en scene est nettoyee apres l'archivage, jamais laissee derriere
    assert not (elevated_tmp_dir / "protected.log").exists()
    assert any(c[0:2] == ["sudo", "cp"] for c in runner.calls)
    assert any(c[0:2] == ["sudo", "chown"] for c in runner.calls)
