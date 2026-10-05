# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Garde de permissions par action — plan_omega_log.md §5.1.

ADAPTE depuis omega-fire (application/pipeline/guards/permission_guard.py),
PAS porte verbatim : la version source verifie "suis-je root ?"
(os.getuid() == 0) de maniere generique, independamment du fichier cible
— correct pour des operations pare-feu (toujours root ou rien). LOG a
deja tranche differemment (plan §5.1) : preferer la delegation par
groupe (ex. le groupe dedie `omega-serv` deja verifie sur la machine de
reference) a l'execution en root. La verification pertinente ici n'est
donc pas "suis-je root" mais "puis-je ecrire CE fichier precis" — ce que
cette version controle reellement, avant l'action plutot qu'en rattrapant
l'exception apres coup."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PermissionCheckResult:
    writable: bool
    reason: str = ""


def check_path_writable(path: str) -> PermissionCheckResult:
    """Verifie si `path` (ou son dossier parent, si le fichier n'existe
    pas encore) est reellement inscriptible par l'utilisateur courant —
    appele AVANT toute tentative d'ecriture/suppression/troncature,
    jamais seulement en rattrapage d'une PermissionError."""
    target = Path(path)
    check_target = target if target.exists() else target.parent

    if not check_target.exists():
        return PermissionCheckResult(
            writable=False, reason=f"Dossier introuvable : {check_target}",
        )

    if os.access(check_target, os.W_OK):
        return PermissionCheckResult(writable=True)

    return PermissionCheckResult(
        writable=False,
        reason=(
            f"Permission d'ecriture refusee sur {check_target}. "
            "Ajoutez votre utilisateur au groupe proprietaire si possible, "
            "ou relancez cette action avec les droits necessaires (sudo)."
        ),
    )
