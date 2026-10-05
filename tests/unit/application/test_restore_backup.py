# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/commands/restore_backup.py — couverture de base
(absente avant Phase 9) + elevation sudo ponctuelle (plan §5.1) sur
l'ECRITURE vers une cible protegee, dans les deux modes (overwrite/append)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from omega_log.application.commands.restore_backup import RestoreBackupCommand, RestoreBackupRequest
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.storage.files.archive_store import ArchiveStore
from omega_log.infrastructure.storage.files.persistence_adapter import FileBackupAdapter
from omega_log.ports.process_runner_port import ProcessResult

_ORIGINAL_CONTENT = "ligne originale\n"


def _make_backup(tmp_path: Path, backup_dir: Path, content: str = _ORIGINAL_CONTENT) -> str:
    source = tmp_path / "source.log"
    source.write_text(content)
    port = FileBackupAdapter(ArchiveStore(backup_dir))
    info = port.create_backup(backup_dir=backup_dir, source_paths=[source], components=["logs"])
    return str(info.path)


@dataclass
class _FakeRunner:
    """Simule `sudo cp`/`sudo chown`/`sudo tee -a` en levant temporairement
    la permission Unix du fichier cible pour ecrire/copier — c'est
    exactement ce que ferait un VRAI sudo (root ignore les bits de mode),
    jamais une simple ecriture Python qui, elle, resterait soumise aux
    memes permissions que le reste du process de test."""
    calls: list[tuple[list[str], str | None]] = field(default_factory=list)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append((args, input_text))
        if args[0:2] == ["sudo", "cp"]:
            src, dest = Path(args[-2]), Path(args[-1])
            if not os.access(src, os.R_OK):
                os.chmod(src, 0o644)
            if dest.exists() and not os.access(dest, os.W_OK):
                os.chmod(dest, 0o644)
            dest.write_bytes(src.read_bytes())
            return ProcessResult(returncode=0, stdout="", stderr="")
        if args[0:2] == ["sudo", "chown"]:
            return ProcessResult(returncode=0, stdout="", stderr="")
        if args[0:3] == ["sudo", "tee", "-a"]:
            target = Path(args[-1])
            os.chmod(target, 0o644)
            with target.open("a", encoding="utf-8") as f:
                f.write(input_text or "")
            return ProcessResult(returncode=0, stdout="", stderr="")
        return ProcessResult(returncode=1, stdout="", stderr="commande inattendue")

    def run_interactive(self, args: list[str]) -> int:  # pragma: no cover - non utilise ici
        self.calls.append((args, None))
        return 0


def test_restore_overwrite_normal_target(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_path = _make_backup(tmp_path, backup_dir)
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "source.log"
    target_file.write_text("sera ecrase")

    command = RestoreBackupCommand(
        FileBackupAdapter(ArchiveStore(backup_dir)), tmp_path / "restore_temp", backup_dir,
    )
    result = command.execute(RestoreBackupRequest(backup_path=backup_path, target_dir=str(target_dir), mode="overwrite"))

    assert result.success
    assert target_file.read_text() == _ORIGINAL_CONTENT
    assert result.safety_backup_path is not None and result.safety_backup_path.exists()


def test_restore_overwrite_protected_target_without_runner_raises(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_path = _make_backup(tmp_path, backup_dir)
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "source.log"
    target_file.write_text("protege")
    target_file.chmod(0)

    command = RestoreBackupCommand(
        FileBackupAdapter(ArchiveStore(backup_dir)), tmp_path / "restore_temp", backup_dir,
    )
    try:
        with pytest.raises(PermissionRequiredError):
            command.execute(RestoreBackupRequest(backup_path=backup_path, target_dir=str(target_dir), mode="overwrite"))
    finally:
        target_file.chmod(0o644)


def test_restore_overwrite_protected_target_falls_back_to_privileged_write(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_path = _make_backup(tmp_path, backup_dir)
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "source.log"
    target_file.write_text("protege")
    target_file.chmod(0)

    elevated_tmp_dir = tmp_path / "elevated_tmp"
    command = RestoreBackupCommand(
        FileBackupAdapter(ArchiveStore(backup_dir)), tmp_path / "restore_temp", backup_dir, elevated_tmp_dir,
    )
    runner = _FakeRunner()
    result = command.execute(
        RestoreBackupRequest(backup_path=backup_path, target_dir=str(target_dir), mode="overwrite"), runner=runner,
    )

    assert result.success
    assert target_file.read_text() == _ORIGINAL_CONTENT
    # sauvegarde de securite ET ecrasement final passent tous les deux par sudo cp
    assert sum(1 for args, _ in runner.calls if args[0:2] == ["sudo", "cp"]) >= 2
    assert not (elevated_tmp_dir / "source.log").exists()


def test_restore_append_protected_target_falls_back_to_privileged_write(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_path = _make_backup(tmp_path, backup_dir, content="nouvelle ligne\n")
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "source.log"
    target_file.write_text("ligne existante\n")
    target_file.chmod(0)

    command = RestoreBackupCommand(
        FileBackupAdapter(ArchiveStore(backup_dir)), tmp_path / "restore_temp", backup_dir, tmp_path / "elevated_tmp",
    )
    runner = _FakeRunner()
    result = command.execute(
        RestoreBackupRequest(backup_path=backup_path, target_dir=str(target_dir), mode="append"), runner=runner,
    )

    assert result.success
    content = target_file.read_text()
    assert "ligne existante" in content
    assert "nouvelle ligne" in content
    assert any(args[0:3] == ["sudo", "tee", "-a"] for args, _ in runner.calls)
