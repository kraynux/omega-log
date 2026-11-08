# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrats de la declaration anonyme (repris d'omega-serv, sans le journal d'envois quotidiens
de son service : omega-log n'envoie qu'une fois, depuis l'ecran)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from omega_log.domain.declaration.model import Declaration


@dataclass(frozen=True)
class SendOutcome:
    ok: bool
    reason: str = ""
    """Vide si ok ; sinon « unreachable » (reseau, DNS, delai depasse, certificat) ou « http-<code> »."""


@dataclass(frozen=True)
class StoredDeclaration:
    declaration: Declaration
    declared_at: datetime


class DeclarationSenderPort(Protocol):
    def send(self, payload: dict[str, object]) -> SendOutcome:
        """POST HTTPS vers la reception. Ne leve jamais : un echec est un SendOutcome."""
        ...


class DeclarationStorePort(Protocol):
    def load(self) -> StoredDeclaration | None: ...

    def save(self, stored: StoredDeclaration) -> None: ...

    def delete(self) -> None:
        """Efface la declaration (retrait). Jamais d'erreur si absente."""
        ...
