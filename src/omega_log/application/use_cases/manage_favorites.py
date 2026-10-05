# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use cases Favoris (plan_omega_log.md §3) — adapte de
ManageLiveTailPinsCommand (omega-fire) : meme principe (nom -> chemins),
mais source = Bibliotheque LOG (pas de pins/historique separes a ce
stade), et ajoute la regle de validation propre a LOG (plan §5) :
1 log -> les 3 viewers ; 2+ logs -> lnav uniquement. Un favori qui
violerait cette regle est refuse a la creation, jamais silencieusement
tronque."""
from __future__ import annotations

from dataclasses import dataclass

from omega_log.domain.entities.favorite import Favorite
from omega_log.domain.value_objects.viewer_type import ViewerType, allowed_viewers
from omega_log.ports.favorite_repository import FavoriteRepository


@dataclass
class CreateFavoriteResult:
    success: bool
    message: str = ""


def list_favorites(repository: FavoriteRepository) -> list[Favorite]:
    return repository.list_all()


def create_favorite(
    repository: FavoriteRepository, *, name: str, paths: list[str], viewer: ViewerType
) -> CreateFavoriteResult:
    if not name.strip():
        return CreateFavoriteResult(success=False, message="Nom requis.")
    if not paths:
        return CreateFavoriteResult(success=False, message="Au moins un log est requis.")
    if viewer not in allowed_viewers(len(paths)):
        return CreateFavoriteResult(
            success=False,
            message=f"{len(paths)} log(s) selectionne(s) : seul {allowed_viewers(len(paths))[-1].value} est compatible.",
        )

    repository.add(Favorite(name=name.strip(), paths=tuple(paths), viewer=viewer))
    return CreateFavoriteResult(success=True, message=f"Favori '{name}' enregistre.")


def remove_favorite(repository: FavoriteRepository, name: str) -> None:
    repository.remove(name)
