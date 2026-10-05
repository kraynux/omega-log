# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Purger (plan_omega_log.md §3/§7) : vider le contenu d'un log
(troncature en place, securisee — voir application/use_cases/
purge_logs.py) ou supprimer completement un ou plusieurs fichiers
(toujours avec confirmation). Selection par numeros, meme convention que
screens/view_logs.py."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.purge_logs import delete_log_files, purge_log_content
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


class PurgeScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._elevated = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("PURGER", classes="omega-title")
            yield Static(
                "Vider le contenu tronque le fichier EN PLACE (securise pour un service qui "
                "l'a encore ouvert) ; supprimer efface completement le(s) fichier(s).",
                classes="omega-hint",
            )
            yield DataTable(id="library-table")
            yield Input(placeholder="Numeros separes par des virgules (ex: 1,2)", id="selection-input")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider le contenu", id="purge-content", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer le(s) fichier(s)", id="delete-files", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#library-table", DataTable).cursor_type = "row"
        self.query_one("#library-table", DataTable).add_columns("#", "Chemin")
        self._refresh_library()

    def _refresh_library(self) -> None:
        self._entries = list_library(self._container.log_repository)
        table = self.query_one("#library-table", DataTable)
        table.clear()
        for idx, entry in enumerate(self._entries, start=1):
            table.add_row(str(idx), entry.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "purge-content":
            self._confirm_purge_content()
        elif button_id == "delete-files":
            self._confirm_delete_files()

    def _selected_paths(self) -> list[str] | None:
        raw = self.query_one("#selection-input", Input).value.strip()
        if not raw:
            self.app.notify("Saisissez au moins un numero de ligne.", severity="warning")
            return None
        paths: list[str] = []
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit() or not (1 <= int(token) <= len(self._entries)):
                self.app.notify(f"Numero invalide : '{token}'.", severity="warning")
                return None
            paths.append(self._entries[int(token) - 1].path)
        return paths

    def _confirm_purge_content(self) -> None:
        paths = self._selected_paths()
        if paths is None:
            return
        self.app.push_screen(
            ConfirmScreen(
                title="VIDER LE CONTENU ?",
                message="Le(s) fichier(s) seront conserves mais vides :\n" + "\n".join(paths),
            ),
            lambda confirmed: self._purge_content_if_confirmed(confirmed, paths),
        )

    def _purge_content_if_confirmed(self, confirmed: bool | None, paths: list[str]) -> None:
        if not confirmed:
            return
        messages = []
        for path in paths:
            runner = self._container.process_runner if self._elevated else None
            try:
                result = purge_log_content(path, runner=runner)
            except PermissionRequiredError:
                if not request_elevation(self, self._container.process_runner):
                    messages.append(f"ECHEC — {path} : permission refusee.")
                    continue
                self._elevated = True
                result = purge_log_content(path, runner=self._container.process_runner)
            messages.append(result.message if result.success else f"ECHEC — {result.message}")
        self.app.notify("\n".join(messages))

    def _confirm_delete_files(self) -> None:
        paths = self._selected_paths()
        if paths is None:
            return
        self.app.push_screen(
            ConfirmScreen(
                title="SUPPRIMER CES FICHIERS ?",
                message="Suppression definitive :\n" + "\n".join(paths),
            ),
            lambda confirmed: self._delete_files_if_confirmed(confirmed, paths),
        )

    def _delete_files_if_confirmed(self, confirmed: bool | None, paths: list[str]) -> None:
        if not confirmed:
            return
        runner = self._container.process_runner if self._elevated else None
        try:
            result = delete_log_files(paths, runner=runner)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify("Permission refusee sur au moins un fichier.", severity="error")
                return
            self._elevated = True
            result = delete_log_files(paths, runner=self._container.process_runner)
        if result.deleted:
            self.app.notify(f"{len(result.deleted)} fichier(s) supprime(s).")
        if result.errors:
            self.app.notify("; ".join(result.errors), severity="error")
        self._refresh_library()
