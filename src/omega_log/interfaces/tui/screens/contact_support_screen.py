# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Aide -> Contact et support, repris d'omega-serv (2026-11-06) : payer un cafe (PayPal), se declarer
utilisateur anonyme (une seule fois, omega-log n'a ni serveur ni instance), contacter le support (mail
et formulaire du site, aucun formulaire ici). Les adresses sont toujours affichees en clair : sans
session graphique (SSH), le navigateur ne s'ouvre pas et l'utilisateur les recopie."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Button, Footer, Header, Static

from omega_log.application.use_cases.check_updates import check_for_update
from omega_log.application.use_cases.declaration import WithdrawResult, withdraw
from omega_log.domain.updates.release_check import UpdateCheck, UpdateStatus
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.screens.declaration_screen import DeclarationScreen, local_date
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

PAYPAL_URL = "https://paypal.me/kraynux"
SUPPORT_MAIL = "kraynux@proton.me"
CONTACT_FORM_URL = "https://kraynux.snake-mackarel.ts.net/contact/"


class ContactSupportScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._release_notes_url = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            with Center():
                yield Static(_("CONTACT ET SUPPORT"), classes="omega-title")
            yield Static(_("Aidez le développeur : omega-log est développé et maintenu par une "
                           "seule personne."),
                         classes="omega-hint")

            yield Static(_("Payer un café"), classes="omega-subtitle")
            yield Static(_("Un don aide à couvrir les frais des serveurs (électricité)."), classes="omega-hint")
            yield Static(PAYPAL_URL)
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Payer un café"), id="coffee", variant="primary")

            yield Static(_("Se déclarer utilisateur (anonyme)"), classes="omega-subtitle")
            yield Static(_("Une déclaration volontaire et anonyme, qui sert uniquement à "
                           "compter les utilisateurs et, si vous le souhaitez, leur continent "
                           "ou leur pays."), classes="omega-hint")
            yield Static("", id="declaration-state")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Se déclarer utilisateur (anonyme)"), id="declare", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Ne plus me déclarer"), id="withdraw", variant="error", disabled=True)

            yield Static(_("Contacter le support"), classes="omega-subtitle")
            yield Static(_("Mail : {SUPPORT_MAIL}").format(SUPPORT_MAIL=SUPPORT_MAIL))
            yield Static(_("Formulaire de contact : {CONTACT_FORM_URL}").format(CONTACT_FORM_URL=CONTACT_FORM_URL))
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Contacter le support"), id="contact", variant="primary")

            # Verification manuelle des mises a jour (portee d'omega-serv 2.6.0, 2026-11-07) : aucune connexion
            # sans clic.
            yield Static(_("Version et mises à jour"), classes="omega-subtitle")
            yield Static(_("Compare votre version à la liste des versions publiées sur le site. Rien n'est envoyé, "
                           "et rien n'est vérifié sans votre clic."), classes="omega-hint")
            yield Static(_("Version installée : {version}").format(version=self._container.app_version),
                         id="update-state")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Vérifier les mises à jour"), id="check-update", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Voir les nouveautés"), id="release-notes", disabled=True)
        with Center(), Horizontal(classes="omega-actions omega-fixed-actions"), Container(classes="omega-btn-frame"):
            yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        stored = self._container.declaration_store.load()
        state = self.query_one("#declaration-state", Static)
        declare_button = self.query_one("#declare", Button)
        withdraw_button = self.query_one("#withdraw", Button)
        if stored is None:
            state.update(_("État : non déclaré."))
            declare_button.label = _("Se déclarer utilisateur (anonyme)")
            withdraw_button.disabled = True
            return
        state.update(_("État : déclaré le {value} (envoi : une seule fois).").format(value=local_date(stored.declared_at)))
        declare_button.label = _("Modifier ma déclaration")
        withdraw_button.disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "coffee":
            self._open(PAYPAL_URL)
        elif button_id == "contact":
            self._open(CONTACT_FORM_URL)
        elif button_id == "check-update":
            self._check_update()
        elif button_id == "release-notes" and self._release_notes_url:
            self._open(self._release_notes_url)
        elif button_id == "declare":
            self.app.push_screen(DeclarationScreen(container=self._container), lambda _result: self._refresh())
        elif button_id == "withdraw":
            self.app.push_screen(ConfirmScreen(
                title=_("NE PLUS ME DÉCLARER ?"),
                message=_("Votre entrée sera supprimée du compteur et la clé effacée de cette "
                          "installation."),
            ), self._withdraw_if_confirmed)

    def _open(self, url: str) -> None:
        self.app.notify(_("Ouverture dans le navigateur..."))
        self.run_worker(lambda: self._open_in_thread(url), thread=True, exclusive=True)

    def _open_in_thread(self, url: str) -> None:
        if not self._container.open_url(url):
            self.app.call_from_thread(
                self.app.notify,
                _("Aucun navigateur disponible ici (session sans affichage) : ouvrez cette "
                  "adresse vous-même : {url}").format(url=url),
                severity="warning", timeout=15,
            )

    def _withdraw_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        self.query_one("#withdraw", Button).disabled = True
        store, sender = self._container.declaration_store, self._container.declaration_sender
        self.run_worker(lambda: self.app.call_from_thread(self._finish_withdraw, withdraw(store, sender)),
                        thread=True, exclusive=True)

    def _finish_withdraw(self, result: WithdrawResult) -> None:
        if result.reception_reached:
            self.app.notify(_("Vous n'êtes plus déclaré : votre entrée est supprimée et la clé "
                              "effacée."))
        else:
            self.app.notify(_("Clé effacée. Réception injoignable : votre entrée y disparaîtra "
                              "seule (1 an)."),
                            severity="warning", timeout=12)
        self._refresh()

    def _check_update(self) -> None:
        self.query_one("#check-update", Button).disabled = True
        self.query_one("#update-state", Static).update(_("Vérification en cours..."))
        source, installed = self._container.release_source, self._container.app_version
        self.run_worker(lambda: self.app.call_from_thread(self._show_update, check_for_update(source, installed)),
                        thread=True, exclusive=True)

    def _show_update(self, check: UpdateCheck) -> None:
        try:
            state = self.query_one("#update-state", Static)
            notes = self.query_one("#release-notes", Button)
            self.query_one("#check-update", Button).disabled = False
        except NoMatches:
            return  # ecran deja ferme
        self._release_notes_url = ""
        notes.disabled = True
        if check.status is UpdateStatus.UPDATE_AVAILABLE:
            self._release_notes_url = check.notes_url
            notes.disabled = False
            state.update(_("Nouvelle version disponible : {latest} (installée : {installed}).\nArchive : {url}").format(
                latest=check.latest, installed=check.installed, url=check.archive_url))
        elif check.status is UpdateStatus.UP_TO_DATE:
            state.update(_("Vous avez la dernière version publiée ({version}).").format(version=check.installed))
        elif check.status is UpdateStatus.AHEAD:
            state.update(_("Votre version ({installed}) est plus récente que la dernière publiée ({latest}) : "
                           "version en cours, pas encore publiée.").format(installed=check.installed, latest=check.latest))
        else:
            state.update(_("Version installée : {version}. Site injoignable ou liste des versions illisible : "
                           "réessayez plus tard.").format(version=check.installed))
