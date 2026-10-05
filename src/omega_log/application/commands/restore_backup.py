# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Restore backup command — ADAPTE depuis omega-fire (application/
commands/restore_backup.py) : la version source distingue une branche
"logs" (fusion = ajout avec separateur) d'une branche "blocklist/exports"
(fusion = dedoublonnage par IP, specifique au pare-feu) — seule la
premiere a un sens pour LOG, la seconde est entierement retiree plutot
que laissee morte dans le code.

Mode "overwrite" : une sauvegarde de securite du fichier cible est
creee automatiquement avant l'ecrasement (comme la version source).
Mode "append" : le contenu extrait est ajoute a la fin du fichier
cible avec un separateur horodate, sans dedoublonnage (comportement
attendu pour des logs, contrairement a une liste d'IP).

Elevation sudo ponctuelle (plan §5.1, 2026-10-03) AJOUTEE sur
PermissionError lors de l'ECRITURE vers `target_file` (la LECTURE de
l'archive extraite, elle, ne pose jamais ce probleme : `temp_dir` nous
appartient toujours). Meme signal PermissionRequiredError que les
autres use cases si `runner` n'est pas fourni."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from omega_log.infrastructure.exceptions import StorageError
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.privileged.privileged_file_ops import (
    append_file_privileged,
    overwrite_file_privileged,
    stage_protected_copy_privileged,
)
from omega_log.ports.persistence import BackupInfo, PersistencePort
from omega_log.ports.process_runner_port import ProcessRunnerPort


@dataclass
class RestoreBackupRequest:
    backup_path: str
    target_dir: str
    mode: str = "append"  # "append" | "overwrite"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.backup_path:
            errors.append("backup_path must not be empty")
        elif not Path(self.backup_path).exists():
            errors.append(f"Backup file not found: {self.backup_path}")
        if self.mode not in ("append", "overwrite"):
            errors.append(f"Invalid mode: {self.mode}")
        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0


@dataclass
class RestoreBackupResult:
    success: bool
    message: str
    target_file: Path | None = None
    safety_backup_path: Path | None = None


class RestoreBackupCommand:
    def __init__(
        self, persistence_port: PersistencePort, temp_dir: Path, backup_dir: Path,
        elevated_tmp_dir: Path | None = None,
    ):
        self._port = persistence_port
        self._temp_dir = temp_dir
        self._backup_dir = backup_dir
        self._elevated_tmp_dir = elevated_tmp_dir

    def execute(self, request: RestoreBackupRequest, *, runner: ProcessRunnerPort | None = None) -> RestoreBackupResult:
        errors = request.validate()
        if errors:
            return RestoreBackupResult(success=False, message="; ".join(errors))

        backup_path = Path(request.backup_path)
        target_dir = Path(request.target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        backup = BackupInfo(
            path=backup_path,
            created_at=datetime.fromtimestamp(backup_path.stat().st_mtime),
            size_bytes=backup_path.stat().st_size,
            components=[],
        )

        try:
            self._port.restore_backup(backup, dest_dir=self._temp_dir)
        except StorageError as e:
            return RestoreBackupResult(success=False, message=f"Echec de l'extraction : {e}")

        extracted_files = list(self._temp_dir.glob("*"))
        if not extracted_files:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            return RestoreBackupResult(success=False, message="L'archive extraite est vide.")

        extracted_file = extracted_files[0]
        target_file = target_dir / extracted_file.name
        safety_backup_path = None
        target_protected = target_file.exists() and not os.access(target_file, os.R_OK | os.W_OK)

        if target_protected and runner is None:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            raise PermissionRequiredError(str(target_file))

        try:
            if request.mode == "overwrite":
                if target_file.exists():
                    safety_source = target_file
                    staged_safety_copy: Path | None = None
                    if target_protected:
                        if self._elevated_tmp_dir is None:
                            return RestoreBackupResult(success=False, message="Elevation non configuree pour cette commande.")
                        self._elevated_tmp_dir.mkdir(parents=True, exist_ok=True)
                        stage_result = stage_protected_copy_privileged(runner, target_file, self._elevated_tmp_dir)
                        if not stage_result.success:
                            return RestoreBackupResult(success=False, message=f"Elevation impossible : {stage_result.message}")
                        staged_safety_copy = Path(stage_result.content)
                        safety_source = staged_safety_copy
                    try:
                        safety_info = self._port.create_backup(
                            backup_dir=self._backup_dir,
                            source_paths=[safety_source],
                            components=["safety_auto"],
                            metadata={"reason": "Sauvegarde automatique avant ecrasement"},
                        )
                        safety_backup_path = safety_info.path
                    finally:
                        if staged_safety_copy is not None:
                            staged_safety_copy.unlink(missing_ok=True)

                if target_protected:
                    priv_result = overwrite_file_privileged(
                        runner, str(target_file), extracted_file.read_text(encoding="utf-8", errors="ignore"),
                    )
                    if not priv_result.success:
                        return RestoreBackupResult(success=False, message=f"Ecriture privilegiee impossible : {priv_result.message}")
                else:
                    shutil.copy2(extracted_file, target_file)
                summary = "Remplacement complet (ecrasement)"
            else:
                if target_file.exists():
                    content = extracted_file.read_text(encoding="utf-8", errors="ignore")
                    separator = (
                        f"\n\n# --- Restauration ajoutee le "
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} "
                        f"(depuis {backup_path.name}) ---\n"
                    )
                    if target_protected:
                        priv_result = append_file_privileged(runner, str(target_file), separator + content)
                        if not priv_result.success:
                            return RestoreBackupResult(success=False, message=f"Ecriture privilegiee impossible : {priv_result.message}")
                    else:
                        with target_file.open("a", encoding="utf-8") as dst:
                            dst.write(separator + content)
                    summary = "Fusion incrementale (ajout en fin de fichier)"
                else:
                    shutil.copy2(extracted_file, target_file)
                    summary = "Fusion incrementale (fichier cible cree)"
        except OSError as e:
            return RestoreBackupResult(success=False, message=f"Echec de la restauration : {e}")
        finally:
            shutil.rmtree(self._temp_dir, ignore_errors=True)

        return RestoreBackupResult(
            success=True,
            message=f"Restauration effectuee avec succes : {summary}.",
            target_file=target_file,
            safety_backup_path=safety_backup_path,
        )
