# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine absolue des exceptions du projet, et exceptions transverses de
core/ (registre de capacites). Meme patron que le reste de la suite
omega- (D-007) : chaque couche a sa propre racine, toutes derivees de
celle-ci — un `except OmegaLogError` generique attrape donc toute erreur
du projet. Les classes du registre sont portees depuis omega-fire
(core/exceptions.py), seul le sous-ensemble reellement utilise par
core/capability_registry.py (pas AuditError, specifique au systeme
d'audit de FIRE, absent de LOG)."""
from __future__ import annotations

from typing import Any


class OmegaLogError(Exception):
    """Racine absolue des erreurs omega-log."""


class ConfigurationError(OmegaLogError):
    """Configuration invalide ou incomplete (chemins, variables d'environnement)."""


class CoreError(OmegaLogError):
    """Racine des erreurs de la couche core/ (registre de capacites, etc.).

    Contexte entre PARENTHESES dans __str__, jamais entre crochets — bug
    reel deja rencontre et corrige chez omega-fire/omega-check : des
    crochets dans un message affiche via `App.notify()` sont interpretes
    comme une balise de style Rich/Textual (`textual.markup.MarkupError`,
    crash reproductible avec des messages systeme natifs comme
    "[Errno 2] No such file or directory")."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class RegistryError(CoreError):
    """Le registre de capacites ne peut pas enregistrer/mettre a jour une
    capacite, ou est dans un etat incoherent."""

    def __init__(
        self,
        message: str,
        capability_id: str | None = None,
        operation: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, context)
        self.capability_id = capability_id
        self.operation = operation
        if capability_id:
            self.context["capability_id"] = capability_id
        if operation:
            self.context["operation"] = operation


class InvalidCapabilityError(RegistryError):
    """Une capacite est invalide ou malformee (ID vide, champs manquants)."""

    def __init__(
        self,
        message: str,
        capability_id: str | None = None,
        reason: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, capability_id=capability_id, context=context)
        self.reason = reason
        if reason:
            self.context["reason"] = reason


class CapabilityNotFoundError(RegistryError):
    """Une capacite demandee n'est pas (encore) enregistree dans le registre."""

    def __init__(self, capability_id: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(
            f"Capability '{capability_id}' not found in registry",
            capability_id=capability_id,
            context=context,
        )


class RegistryStateError(RegistryError):
    """Le registre est accede dans un etat invalide (avant initialisation,
    transition d'etat incorrecte)."""

    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        expected_state: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.current_state = current_state
        self.expected_state = expected_state
        if current_state:
            self.context["current_state"] = current_state
        if expected_state:
            self.context["expected_state"] = expected_state
