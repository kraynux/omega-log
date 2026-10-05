# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Rotate logs command — porte depuis omega-fire (application/commands/
rotate_logs.py) : cree une archive compressee d'un fichier log choisi,
puis applique la limite de retention (en supprimant les archives
excedentaires les plus anciennes) via domain/logs/rotation.py
(compute_rotations_to_delete, deja porte Phase 2). Aucun I/O tarfile
direct ici (delegue au port persistence).

Elevation sudo ponctuelle (plan §5.1, 2026-10-03) AJOUTEE : si la source
n'est pas lisible par l'utilisateur courant, une copie privilegiee est
d'abord mise en scene dans `elevated_tmp_dir` (que NOUS possedons) via
stage_protected_copy_privileged (sudo cp + chown), et c'est CETTE COPIE
qui est passee au port persistence — jamais le port lui-meme mis au
courant de l'elevation (ArchiveStore/tarfile reste pur I/O, sans aucun
privilege). Meme signal PermissionRequiredError que les autres use
cases si `runner` n'est pas fourni."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from omega_log.domain.logs.rotation import compute_rotations_to_delete
from omega_log.infrastructure.exceptions import StorageError
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.privileged.privileged_file_ops import stage_protected_copy_privileged
from omega_log.ports.persistence import PersistencePort
from omega_log.ports.process_runner_port import ProcessRunnerPort


@dataclass
class RotateLogsRequest:
    source_path: str
    reason: str | None = None
    keep: int = 7

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_path:
            errors.append("source_path must not be empty")
        elif not Path(self.source_path).exists():
            errors.append(f"Source file not found: {self.source_path}")
        if self.keep < 1:
            errors.append("Keep must be at least 1")
        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0


@dataclass
class RotateLogsResult:
    success: bool
    message: str
    backup_path: Path | None = None
    backup_size_bytes: int | None = None
    deleted_count: int = 0


class RotateLogsCommand:
    """Use case : cree un backup compresse d'un fichier log, puis
    applique la limite de retention en supprimant les archives
    excedentaires les plus anciennes."""

    def __init__(self, persistence_port: PersistencePort, backup_dir: Path, elevated_tmp_dir: Path | None = None):
        self._port = persistence_port
        self._backup_dir = backup_dir
        self._elevated_tmp_dir = elevated_tmp_dir

    def execute(self, request: RotateLogsRequest, *, runner: ProcessRunnerPort | None = None) -> RotateLogsResult:
        errors = request.validate()
        if errors:
            return RotateLogsResult(success=False, message="; ".join(errors))

        source = Path(request.source_path)
        staged_copy: Path | None = None
        actual_source = source

        if not os.access(source, os.R_OK):
            if runner is None:
                raise PermissionRequiredError(str(source))
            if self._elevated_tmp_dir is None:
                return RotateLogsResult(success=False, message="Elevation non configuree pour cette commande.")
            self._elevated_tmp_dir.mkdir(parents=True, exist_ok=True)
            stage_result = stage_protected_copy_privileged(runner, source, self._elevated_tmp_dir)
            if not stage_result.success:
                return RotateLogsResult(success=False, message=f"Elevation impossible : {stage_result.message}")
            staged_copy = Path(stage_result.content)
            actual_source = staged_copy

        try:
            backup_info = self._port.create_backup(
                backup_dir=self._backup_dir,
                source_paths=[actual_source],
                components=["logs"],
                metadata={"reason": request.reason or ""},
            )
        except StorageError as e:
            return RotateLogsResult(success=False, message=f"Erreur technique lors de la sauvegarde : {e}")
        finally:
            if staged_copy is not None:
                staged_copy.unlink(missing_ok=True)

        try:
            existing_backups = self._port.list_backups(self._backup_dir)
        except StorageError as e:
            return RotateLogsResult(
                success=True,
                message=(
                    f"Sauvegarde creee avec succes, mais la purge des anciennes archives a echoue : {e}"
                ),
                backup_path=backup_info.path,
                backup_size_bytes=backup_info.size_bytes,
            )

        # compute_rotations_to_delete() presume une liste triee PLUS
        # ANCIEN D'ABORD (voir sa docstring) — list_backups() du port
        # retourne le plus RECENT d'abord (pour l'affichage), tri
        # explicitement inverse ici avant l'appel. Omis par erreur dans
        # la version source omega-fire (meme mesange constate dans ce
        # code : la liste y est passee telle quelle, non re-triee) —
        # corrige ici plutot que reproduit, aurait sinon supprime les
        # archives les plus RECENTES au lieu des plus anciennes.
        oldest_first_names = [b.path.name for b in sorted(existing_backups, key=lambda b: b.created_at)]
        names_to_delete = compute_rotations_to_delete(existing_rotations=oldest_first_names, max_rotations=request.keep)

        backups_by_name = {b.path.name: b for b in existing_backups}
        deleted_count = 0
        for name in names_to_delete:
            backup = backups_by_name.get(name)
            if backup:
                self._port.delete_backup(backup)
                deleted_count += 1

        return RotateLogsResult(
            success=True,
            message=f"Sauvegarde creee avec succes : {backup_info.path.name}",
            backup_path=backup_info.path,
            backup_size_bytes=backup_info.size_bytes,
            deleted_count=deleted_count,
        )
