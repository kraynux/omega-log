# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Bibliotheque (plan_omega_log.md §3/§10) : hub central
referencant tous les logs a traiter — alimentee par le Registre (import
au detail/en totalite) ou manuellement ici, jamais l'inverse.

Repris d'omega-serv (2026-11-06) : table commune (colonnes #/Modifie/Etat),
« Ajouter les logs connus d'Omega-Serv » (installations trouvees en local,
WAF et magnet inclus s'ils sont actifs) et « Sources distantes (SSH) »."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import (
    add_to_library,
    list_library,
    remove_from_library,
)
from omega_log.application.use_cases.omega_serv_logs import import_omega_serv_logs
from omega_log.domain.entities.log_file import LogFile
from omega_log.infrastructure.privileged.file_access import Access, probe_file
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.screens.remote_log_sources_screen import RemoteLogSourcesScreen
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


class LibraryScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_path: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("BIBLIOTHÈQUE"), classes="omega-title")
            yield Static("", id="library-hint", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder=_("Chemin à ajouter manuellement"), id="path-input")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Ajouter"), id="add", variant="primary")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Ajouter les logs connus d'Omega-Serv"), id="add-known")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Sources distantes (SSH)"), id="remote-sources")
            yield LogLibraryTable(id="log-list")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retirer la sélection"), id="remove", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Rafraîchir"), id="refresh")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()
        # Focus sur la liste (2026-11-07, retour utilisateur) : sur le champ de saisie, les raccourcis d'une lettre
        # (q, t, r, a, s) servent a taper et la barre de statut n'affichait plus qu'Echap, contrairement aux
        # autres ecrans.
        self.query_one("#log-list").focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "log-list":
            return
        row = event.data_table.get_row_at(event.cursor_row)
        self._selected_path = str(row[1]) if row else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "refresh":
            self._refresh()
        elif button_id == "add":
            self._add_manual()
        elif button_id == "add-known":
            self._add_known()
        elif button_id == "remote-sources":
            self.app.push_screen(RemoteLogSourcesScreen(container=self._container), lambda _result: self._refresh())
        elif button_id == "remove":
            self._remove_selected()

    def _refresh(self) -> None:
        entries = list_library(self._container.log_repository)
        self.query_one("#log-list", LogLibraryTable).load(entries)
        stale = sum(1 for e in entries if e.is_stale)
        missing = sum(1 for e in entries if not e.exists and not e.protected)
        protected = sum(1 for e in entries if e.protected)
        self.query_one("#library-hint", Static).update(
            _("{count} log(s) référencé(s) — {stale} suspect(s), {missing} introuvable(s), {protected} protégé(s) "
              "(lus avec sudo).").format(count=len(entries), stale=stale, missing=missing, protected=protected)
        )

    def _add_manual(self) -> None:
        path_input = self.query_one("#path-input", Input)
        raw_path = path_input.value.strip()
        if not raw_path:
            self.app.notify(_("Saisissez un chemin."), severity="warning")
            return
        path_input.value = ""
        probe = probe_file(raw_path)
        if probe.protected and not probe.exists:
            # Dossier ferme a votre compte (ex. /var/log/lighttpd/, demande 2026-11-26) : sudo verifie le fichier.
            self.app.push_screen(
                ConfirmScreen(
                    title=_("LOG PROTÉGÉ"),
                    message=_("{path} est dans un dossier fermé à votre compte. Confirmer : votre mot de passe sudo "
                              "est demandé dans le terminal, omega-log vérifie que le fichier existe puis "
                              "l'ajoute.").format(path=raw_path),
                ),
                lambda confirmed: self._add_after_sudo(confirmed, raw_path),
            )
            return
        self._add_path(raw_path, probe.access)

    def _add_after_sudo(self, confirmed: bool | None, path: str) -> None:
        if not confirmed or not request_elevation(self, self._container.process_runner):
            self.app.notify(_("Log non ajouté : {path}").format(path=path), severity="warning")
            return
        probe = probe_file(path, self._container.process_runner)
        if probe.access is Access.MISSING:
            self.app.notify(_("Fichier introuvable : {path}").format(path=path), severity="error")
            return
        self._add_path(path, probe.access)

    def _add_path(self, path: str, access: Access) -> None:
        add_to_library(self._container.log_repository, LogFile(path=path, access="file"))
        if access is Access.PROTECTED:
            self.app.notify(_("Log protégé ajouté : il sera lu avec votre mot de passe sudo."))
        elif access is Access.MISSING:
            self.app.notify(_("Ajouté, mais introuvable pour l'instant : {path}").format(path=path), severity="warning")
        self._refresh()

    def _add_known(self) -> None:
        """Logs connus des installations omega-serv de la machine (porte d'omega-serv 2026-11-06) : access,
        error, alertes WAF si le WAF est actif, logs magnet si le magnet l'est. Lecture seule, sur clic."""
        scan = self._container.find_omega_serv_logs()
        if not scan.installs:
            self.app.notify(_("Aucune installation d'Omega-Serv trouvée sur cette machine."), severity="warning")
            return
        added = import_omega_serv_logs(self._container.log_repository, scan.logs)
        self.app.notify(
            _("{count} installation(s) d'Omega-Serv trouvée(s), {added} log(s) ajouté(s) (déjà "
              "présents remplacés, jamais dupliqués).").format(count=len(scan.installs), added=added)
        )
        for root in scan.unreadable:
            self.app.notify(_("Configuration illisible : {root}/config/omega-serve.json").format(root=root), severity="warning")
        self._refresh()

    def _remove_selected(self) -> None:
        if self._selected_path is None:
            self.app.notify(_("Sélectionnez une ligne dans la liste."), severity="warning")
            return
        path = self._selected_path
        self.app.push_screen(
            ConfirmScreen(title=_("RETIRER DE LA BIBLIOTHÈQUE ?"), message=path),
            lambda confirmed: self._remove_if_confirmed(confirmed, path),
        )

    def _remove_if_confirmed(self, confirmed: bool | None, path: str) -> None:
        if not confirmed:
            return
        remove_from_library(self._container.log_repository, path)
        self._selected_path = None
        self._refresh()
