# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran "Voir les logs" (plan_omega_log.md §3/§7) : selection d'un ou
plusieurs logs EXCLUSIVEMENT depuis la Bibliotheque (aucun import
manuel ici, voir plan §10) + choix du viewer, avec la regle de
compatibilite du plan §5 (1 log -> les 3 viewers ; 2+ logs -> lnav
uniquement). Selection par NUMEROS separes par des virgules — meme
convention deja eprouvee pour la fusion multi-fichiers d'omega-fire/
lnav_screen.py, reprise ici plutot que re-derivee."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import list_library
from omega_log.domain.value_objects.viewer_type import ViewerType, allowed_viewers
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.live_tail_screen import LiveTailScreen
from omega_log.interfaces.tui.screens.lnav_screen import LnavScreen
from omega_log.interfaces.tui.screens.log_viewer_screen import LogViewerScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


class ViewLogsScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("VOIR LES LOGS", classes="omega-title")
            yield Static(
                "Logs references dans la Bibliotheque uniquement — importez-en "
                "d'autres depuis le Registre ou la Bibliotheque.",
                classes="omega-hint",
            )
            yield DataTable(id="library-table")
            yield Static("Sources a ouvrir (numeros ci-dessus, separes par des virgules)", classes="omega-subtitle")
            yield Input(placeholder="ex: 1,3", id="selection-input")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (simple)", id="view-simple", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (classique)", id="view-classic")
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (lnav)", id="view-lnav")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#library-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("#", "Chemin", "Service", "Acces", "Etat")
        self._refresh()

    def _refresh(self) -> None:
        self._entries = list_library(self._container.log_repository)
        table = self.query_one("#library-table", DataTable)
        table.clear()
        for idx, entry in enumerate(self._entries, start=1):
            state = "SUSPECT" if entry.is_stale else ("ABSENT" if not entry.exists else "OK")
            table.add_row(str(idx), entry.path, entry.service_id or "-", entry.access, state)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "view-simple":
            self._open(ViewerType.SIMPLE)
        elif button_id == "view-classic":
            self._open(ViewerType.CLASSIC)
        elif button_id == "view-lnav":
            self._open(ViewerType.LNAV)

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

    def _open(self, viewer: ViewerType) -> None:
        paths = self._selected_paths()
        if paths is None:
            return
        if viewer not in allowed_viewers(len(paths)):
            self.app.notify(
                f"{len(paths)} log(s) selectionne(s) : seul {allowed_viewers(len(paths))[-1].value} est compatible.",
                severity="warning",
            )
            return

        if viewer == ViewerType.SIMPLE:
            self.app.push_screen(LiveTailScreen(container=self._container, path=paths[0]))
        elif viewer == ViewerType.CLASSIC:
            self.app.push_screen(LogViewerScreen(container=self._container, path=paths[0]))
        else:
            self.app.push_screen(LnavScreen(container=self._container, paths=paths))
