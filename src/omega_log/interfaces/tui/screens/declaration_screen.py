# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Aide -> Contact et support -> Se declarer utilisateur, repris d'omega-serv (2026-11-06) et
simplifie : pas de choix du mode (« une seule fois » seulement, decision utilisateur). Continent et
pays facultatifs (deux listes independantes, chacune avec « Autre »), puis le message EXACT qui sera
envoye, mis a jour a chaque choix. L'envoi tourne dans un fil : l'ecran ne se fige jamais (5 s au plus)."""
from __future__ import annotations

import json
from datetime import datetime
from functools import cache
from importlib import resources
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Select, Static

from omega_log.application.use_cases.declaration import DeclareResult, declare, preview_payload
from omega_log.domain.declaration.countries import COUNTRY_CODES
from omega_log.domain.declaration.model import OTHER, RECEPTION_URL
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_CONTINENT_LABELS = (
    ("AF", _("Afrique")),
    ("AN", _("Antarctique")),
    ("AS", _("Asie")),
    ("EU", _("Europe")),
    ("NA", _("Amérique du Nord")),
    ("OC", _("Océanie")),
    ("SA", _("Amérique du Sud")),
)
_LANGUAGE = "fr"
"""Langue des noms de pays ; suivra la langue de l'interface au lot traduction."""


def local_date(value: datetime | None) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M") if value is not None else "-"


@cache
def _country_names() -> dict[str, dict[str, str]]:
    data = resources.files("omega_log.domain.declaration").joinpath("country_names.json").read_text(encoding="utf-8")
    names = json.loads(data)["names"]
    return names if isinstance(names, dict) else {}


def country_options(language_code: str = _LANGUAGE) -> list[tuple[str, str]]:
    """(libelle, code) tries par nom ; « Autre » en dernier."""
    names = _country_names()
    table = names.get(language_code) or names.get("fr") or {}
    options = sorted(((table.get(code, code), code) for code in COUNTRY_CODES), key=lambda item: item[0].casefold())
    return [*options, (_("Autre (non référencé)"), OTHER)]


def continent_options() -> list[tuple[str, str]]:
    return [*((label, code) for code, label in _CONTINENT_LABELS), (_("Autre (non référencé)"), OTHER)]


class DeclarationScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._existing = container.declaration_store.load()

    def compose(self) -> ComposeResult:
        existing = self._existing.declaration if self._existing is not None else None
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            with Center():
                yield Static(_("SE DÉCLARER UTILISATEUR (ANONYME)"), classes="omega-title")
            yield Static(_("Une déclaration volontaire et anonyme : elle sert uniquement à "
                           "compter les utilisateurs d'omega-log et, si vous le souhaitez, "
                           "leur continent ou leur pays. Une clé tirée au hasard est créée "
                           "pour cette installation ; elle n'a aucun lien avec vous ni avec "
                           "votre machine. Envoi : une seule fois, maintenant."), classes="omega-hint")

            yield Static(_("Continent (facultatif)"), classes="omega-subtitle")
            yield Select(continent_options(), value=existing.continent if existing and existing.continent else Select.NULL,
                         allow_blank=True, prompt=_("Non précisé"), id="declaration-continent")
            yield Static(_("Pays (facultatif)"), classes="omega-subtitle")
            yield Select(country_options(), value=existing.country if existing and existing.country else Select.NULL,
                         allow_blank=True, prompt=_("Non précisé"), id="declaration-country")

            yield Static(_("Message envoyé"), classes="omega-subtitle")
            yield Static("", id="declaration-preview")
            yield Static(_("Destination : {RECEPTION_URL}").format(RECEPTION_URL=RECEPTION_URL), classes="omega-hint")
            yield Static(_("Jamais envoyés : votre nom, le nom de la machine, vos logs."), classes="omega-hint")
            yield Static(_("Votre adresse IP n'est pas enregistrée dans les déclarations. "
                           "Comme pour toute visite d'un site, elle passe par les contrôles de "
                           "sécurité et le journal technique du serveur de réception."), classes="omega-hint")
            yield Static(_("Vous pouvez retirer votre déclaration à tout moment depuis Contact "
                           "et support."),
                         classes="omega-hint")
            yield Static("", id="declaration-error", classes="omega-hint")
        with Center(), Horizontal(classes="omega-actions omega-fixed-actions"):
            with Container(classes="omega-btn-frame"):
                yield Button(_("Envoyer"), id="send", variant="primary")
            with Container(classes="omega-btn-frame"):
                yield Button(_("Annuler"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._update_preview()

    def _value(self, widget_id: str) -> str:
        value = self.query_one(f"#{widget_id}", Select).value
        return "" if value is Select.NULL or value is None else str(value)

    def on_select_changed(self, _event: Select.Changed) -> None:
        self._update_preview()

    def _update_preview(self) -> None:
        payload = preview_payload(self._container.declaration_store, self._container.app_version,
                                  self._value("declaration-continent"), self._value("declaration-country"))
        if self._existing is None:
            payload["cle"] = _("<clé tirée au hasard à l'envoi>")
        self.query_one("#declaration-preview", Static).update(json.dumps(payload, ensure_ascii=False))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "send":
            self._send()

    def _send(self) -> None:
        continent, country = self._value("declaration-continent"), self._value("declaration-country")
        container = self._container
        self.query_one("#send", Button).disabled = True
        self.query_one("#declaration-error", Static).update(_("Envoi en cours..."))

        def run() -> None:
            result = declare(container.declaration_store, container.declaration_sender, container.app_version,
                             continent, country)
            self.app.call_from_thread(self._finish, result)

        self.run_worker(run, thread=True, exclusive=True)

    def _finish(self, result: DeclareResult) -> None:
        if result.ok:
            self.app.notify(_("Merci ! Vous êtes déclaré utilisateur anonyme."))
            self.dismiss()
            return
        self.query_one("#send", Button).disabled = False
        self.query_one("#declaration-error", Static).update(
            _("Réception injoignable : rien n'a été enregistré, réessayez plus tard."))
