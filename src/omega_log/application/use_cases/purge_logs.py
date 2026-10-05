# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use cases Purger (plan_omega_log.md §3/§7) :

- purge_log_content() : vide le CONTENU d'un log sans le supprimer —
  troncature EN PLACE (meme inode, memes permissions/proprietaire),
  jamais une suppression+recreation. C'est precisement le sens de
  "recreation NON ABSOLUE selon logiciel maitre" du plan : un logiciel
  qui ecrit encore dans ce fichier garde son descripteur ouvert sur le
  MEME inode apres une troncature, alors qu'une suppression+recreation
  casserait ce descripteur. Si le fichier n'existe pas (purge "doit
  exister mais ne l'est plus"), il est RECREE avec la correction de
  permissions deja documentee (plan §5, precedent FileLineLogger
  d'omega-serv) — seul ce cas de secours cree un nouvel inode.

- delete_log_files() : supprime completement un ou plusieurs fichiers
  (pas de recreation) — toujours precede d'une confirmation cote ecran,
  jamais appele seul depuis un bouton sans ConfirmScreen.

`runner` optionnel sur les deux fonctions (AJOUTE 2026-10-03, plan
§5.1, elevation sudo ponctuelle) : si check_path_writable() refuse ET
qu'un `runner` est fourni, retombe sur une troncature/suppression
privilegiee (infrastructure/privileged/privileged_file_ops.py) au lieu
de refuser directement — sans lui, le refus de check_path_writable()
reste tel quel (aucune PermissionRequiredError ici : contrairement aux
lectures, l'absence d'ecriture est deja detectee EN AMONT par
check_path_writable(), pas rattrapee apres une exception)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from omega_log.application.guards.permission_guard import check_path_writable
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.privileged.privileged_file_ops import (
    delete_file_privileged,
    truncate_file_privileged,
)

if TYPE_CHECKING:
    from omega_log.ports.process_runner_port import ProcessRunnerPort

_RECREATED_FILE_MODE = 0o664
"""Groupe inscriptible, meme raisonnement que FileLineLogger d'omega-serv
(plan §5) : un fichier recree par l'utilisateur courant (umask 022 ->
644 par defaut) deviendrait illisible en ecriture par le service tiers
qui l'attend, dans un seul sens difficile a diagnostiquer apres coup."""


@dataclass
class PurgeContentResult:
    success: bool
    message: str
    recreated: bool = False


def purge_log_content(path: str, *, runner: ProcessRunnerPort | None = None) -> PurgeContentResult:
    target = Path(path)
    check = check_path_writable(path)
    if not check.writable:
        if target.exists():
            if runner is None:
                raise PermissionRequiredError(path)
            priv_result = truncate_file_privileged(runner, path)
            if not priv_result.success:
                return PurgeContentResult(success=False, message=f"Troncature privilegiee impossible : {priv_result.message}")
            return PurgeContentResult(success=True, message=f"Contenu vide (fichier conserve) : {path}")
        return PurgeContentResult(success=False, message=check.reason)

    if target.exists():
        try:
            with target.open("r+b") as f:
                f.truncate(0)
        except OSError as exc:
            return PurgeContentResult(success=False, message=f"Troncature impossible : {exc}")
        return PurgeContentResult(success=True, message=f"Contenu vide (fichier conserve) : {path}")

    try:
        target.touch()
        os.chmod(target, _RECREATED_FILE_MODE)
    except OSError as exc:
        return PurgeContentResult(success=False, message=f"Recreation impossible : {exc}")
    return PurgeContentResult(success=True, message=f"Fichier recree vide (etait absent) : {path}", recreated=True)


@dataclass
class DeleteFilesResult:
    deleted: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors


def delete_log_files(paths: list[str], *, runner: ProcessRunnerPort | None = None) -> DeleteFilesResult:
    deleted: list[str] = []
    errors: list[str] = []
    for path in paths:
        check = check_path_writable(path)
        if not check.writable:
            if Path(path).exists():
                if runner is None:
                    raise PermissionRequiredError(path)
                priv_result = delete_file_privileged(runner, path)
                if priv_result.success:
                    deleted.append(path)
                else:
                    errors.append(f"{path} : {priv_result.message}")
                continue
            errors.append(f"{path} : {check.reason}")
            continue
        try:
            Path(path).unlink(missing_ok=True)
            deleted.append(path)
        except OSError as exc:
            errors.append(f"{path} : {exc}")
    return DeleteFilesResult(deleted=deleted, errors=errors)
