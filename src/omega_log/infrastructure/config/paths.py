# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Resolution des chemins runtime (var/), la seule source de verite pour
ces chemins. Meme patron que le reste de la suite omega- (plan_omega_log.md
§5) : tout doit vivre par defaut dans le dossier de l'application (`./var`),
rien dans le filesystem utilisateur (`~/.config`, `~/.omega_log/`) sauf
choix explicite (override via `$OMEGA_LOG_VAR_DIR`).

Distinct des chemins de LOGS SCANNES (`/var/log`, dossiers personnalises) :
ce module ne resout QUE le var_dir applicatif de LOG lui-meme (favoris,
settings, bibliotheque) — voir plan_omega_log.md §5 et l'annuaire pour les
chemins de logs serveur."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAR_DIRNAME = "var"
ENV_VAR_DIR = "OMEGA_LOG_VAR_DIR"


def resolve_var_dir() -> Path:
    """Racine des fichiers runtime : `$OMEGA_LOG_VAR_DIR` si defini,
    sinon `./var` relatif au repertoire courant d'execution."""
    override = os.environ.get(ENV_VAR_DIR)
    if override:
        return Path(override)
    return Path.cwd() / DEFAULT_VAR_DIRNAME


def default_settings_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "settings.json"


def default_library_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "library.json"


def default_favorites_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "favorites.json"


def default_backup_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "backups"


def default_restore_temp_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "restore_temp"


def default_exports_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "exports"


def default_screenshots_dir(var_dir: Path | None = None) -> Path:
    """Sans ce chemin explicite, `App.deliver_screenshot()` ecrirait par
    defaut dans le dossier Telechargements de l'utilisateur, jamais dans
    var/ — piege deja documente et corrige cote omega-check/omega-stress."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "screenshots"


def default_elevated_tmp_dir(var_dir: Path | None = None) -> Path:
    """Scratch dir QUE NOUS POSSEDONS, utilise comme relais pour
    l'elevation sudo ponctuelle (plan §5.1, 2026-10-03) : un fichier
    protege de /var/log est copie ici (`sudo cp` + `sudo chown`) avant
    d'etre traite normalement par un code qui n'a, lui, jamais besoin de
    privileges (ArchiveStore/tarfile notamment). Jamais le dossier
    restore_temp_dir existant : usage distinct (celui-la recoit le
    CONTENU extrait d'une archive, pas une copie temporaire d'un
    original protege)."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "elevated_tmp"
