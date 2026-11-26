# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Etat d'acces d'un log : lisible, protege ou absent (demande 2026-11-26 : /var/log/lighttpd/access.log).

Un log range dans un dossier ferme a votre compte (`/var/log/lighttpd/`, droits 750) fait echouer meme `stat()`
avec une PermissionError ; `Path.exists()`/`is_file()` la transforment en « absent ». Tous les modules (Bibliotheque,
Registre, viewers, Statistiques, Voir et Traiter IP, Rotate, Purger, Sante des logs, lnav) passent donc par ici
au lieu de `exists()` : un log protege n'est plus jamais pris pour un log absent.

Quand sudo a deja ete accorde dans cette session (`elevation_active()`), la taille et la date d'un log protege sont
lues avec `sudo -n stat` : jamais d'invite de mot de passe ici (`-n`), et jamais de `sudo` tente avant qu'une
authentification ait eu lieu (une tentative refusee laisserait une ligne d'echec dans le journal d'authentification)."""
from __future__ import annotations

import os
import stat as stat_module
from dataclasses import dataclass
from enum import Enum

from omega_log.infrastructure.privileged.elevation import elevation_active
from omega_log.infrastructure.process.subprocess_runner import SubprocessRunner
from omega_log.ports.process_runner_port import ProcessRunnerPort

_TIMEOUT_SECONDS = 10
_DEFAULT_RUNNER = SubprocessRunner()


class Access(Enum):
    READABLE = "readable"
    PROTECTED = "protected"
    """Existe (ou dossier ferme : existence verifiable seulement avec sudo) mais illisible par votre compte."""
    MISSING = "missing"


@dataclass(frozen=True, slots=True)
class FileAccess:
    access: Access
    exists: bool
    """True si l'existence est CONSTATEE ; False pour un absent, ou un protege pas encore verifie avec sudo."""
    size: int | None = None
    modified_at: float | None = None
    mode: int | None = None
    device: int | None = None
    regular: bool = True

    @property
    def protected(self) -> bool:
        return self.access is Access.PROTECTED

    @property
    def may_exist(self) -> bool:
        """Existe, ou peut exister derriere un dossier ferme : a ouvrir avec sudo, jamais a declarer absent."""
        return self.access is not Access.MISSING


def privileged_stat(path: str, runner: ProcessRunnerPort | None = None) -> FileAccess | None:
    """`sudo -n stat` d'un chemin protege. None si sudo n'est pas accorde (ou plus : cache expire) ;
    FileAccess(MISSING) si sudo voit que le chemin n'existe pas."""
    if not elevation_active():
        return None
    result = (runner or _DEFAULT_RUNNER).run(
        ["sudo", "-n", "env", "LC_ALL=C", "stat", "-L", "-c", "%s %Y %a %d %F", "--", path], timeout=_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        error = (result.stderr or "").lower()
        if "no such file" in error or "not a directory" in error:
            return FileAccess(Access.MISSING, exists=False)
        return None  # mot de passe redemande (cache sudo expire) ou refus : etat inconnu
    try:
        size, mtime, mode, device, kind = (result.stdout or "").strip().split(" ", 4)
        return FileAccess(Access.PROTECTED, exists=True, size=int(size), modified_at=float(mtime),
                          mode=int(mode, 8), device=int(device), regular=kind.startswith("regular"))
    except ValueError:
        return None


def probe_file(path: str, runner: ProcessRunnerPort | None = None) -> FileAccess:
    """Etat reel d'un chemin, sans jamais demander de mot de passe."""
    try:
        info = os.stat(path)
    except PermissionError:  # dossier ferme : seul sudo peut voir le fichier
        return privileged_stat(path, runner) or FileAccess(Access.PROTECTED, exists=False)
    except OSError:
        return FileAccess(Access.MISSING, exists=False)
    readable = os.access(path, os.R_OK)
    return FileAccess(
        Access.READABLE if readable else Access.PROTECTED, exists=True, size=info.st_size,
        modified_at=info.st_mtime, mode=stat_module.S_IMODE(info.st_mode), device=info.st_dev,
        regular=stat_module.S_ISREG(info.st_mode),
    )


def may_exist(path: str) -> bool:
    """Remplace `Path(path).exists()` pour un log : True aussi derriere un dossier ferme (sudo decidera)."""
    return probe_file(path).may_exist


def file_size(path: str, runner: ProcessRunnerPort | None = None) -> int | None:
    """Taille actuelle ; avec sudo si le log est protege et sudo accorde. None si inconnue."""
    return probe_file(path, runner).size
