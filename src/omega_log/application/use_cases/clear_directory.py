# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use case Options (plan_omega_log.md §7) : vider le contenu d'un
dossier applicatif a plat (exports/ ou screenshots/, jamais un dossier
de logs scannes) — supprime les fichiers qu'il contient, conserve le
dossier lui-meme. Jamais d'elevation sudo necessaire ici : ces dossiers
vivent sous var_dir, toujours possedes par l'utilisateur courant
(infrastructure/config/paths.py), contrairement aux logs de /var/log."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ClearDirectoryResult:
    deleted_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors


def clear_directory(directory: Path) -> ClearDirectoryResult:
    """Supprime chaque FICHIER directement sous `directory` (jamais les
    sous-dossiers — exports/screenshots sont plats par construction,
    aucun sous-dossier attendu ; un sous-dossier presente serait ignore
    plutot que supprime recursivement sans confirmation explicite).
    Dossier absent : rien a faire, pas une erreur (jamais encore
    utilise)."""
    if not directory.is_dir():
        return ClearDirectoryResult()

    deleted = 0
    errors: list[str] = []
    for entry in directory.iterdir():
        if entry.is_dir():
            continue
        try:
            entry.unlink()
            deleted += 1
        except OSError as exc:
            errors.append(f"{entry.name} : {exc}")
    return ClearDirectoryResult(deleted_count=deleted, errors=errors)
