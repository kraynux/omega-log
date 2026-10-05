# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Bibliotheque (plan_omega_log.md §3/§10) : hub central
referencant tous les logs a traiter — alimentee par le Registre (import
au detail/en totalite) ou manuellement ici, jamais l'inverse."""
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
from omega_log.domain.entities.log_file import LogFile
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.widgets.log_list import LogList

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
            yield Static("BIBLIOTHEQUE", classes="omega-title")
            yield Static("", id="library-hint", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder="Chemin a ajouter manuellement", id="path-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Ajouter", id="add", variant="primary")
            yield LogList(id="log-list")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Retirer la selection", id="remove", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Rafraichir", id="refresh")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#log-list", LogList).cursor_type = "row"
        self._refresh()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "log-list":
            return
        row = event.data_table.get_row_at(event.cursor_row)
        self._selected_path = str(row[0]) if row else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "refresh":
            self._refresh()
        elif button_id == "add":
            self._add_manual()
        elif button_id == "remove":
            self._remove_selected()

    def _refresh(self) -> None:
        entries = list_library(self._container.log_repository)
        self.query_one("#log-list", LogList).load(entries)
        stale = sum(1 for e in entries if e.is_stale)
        missing = sum(1 for e in entries if not e.exists)
        self.query_one("#library-hint", Static).update(
            f"{len(entries)} log(s) reference(s) — {stale} suspect(s), {missing} introuvable(s) actuellement."
        )

    def _add_manual(self) -> None:
        path_input = self.query_one("#path-input", Input)
        raw_path = path_input.value.strip()
        if not raw_path:
            self.app.notify("Saisissez un chemin.", severity="warning")
            return
        add_to_library(self._container.log_repository, LogFile(path=raw_path, access="file"))
        path_input.value = ""
        self._refresh()

    def _remove_selected(self) -> None:
        if self._selected_path is None:
            self.app.notify("Selectionnez une ligne dans la liste.", severity="warning")
            return
        path = self._selected_path
        self.app.push_screen(
            ConfirmScreen(title="RETIRER DE LA BIBLIOTHEQUE ?", message=path),
            lambda confirmed: self._remove_if_confirmed(confirmed, path),
        )

    def _remove_if_confirmed(self, confirmed: bool | None, path: str) -> None:
        if not confirmed:
            return
        remove_from_library(self._container.log_repository, path)
        self._selected_path = None
        self._refresh()
