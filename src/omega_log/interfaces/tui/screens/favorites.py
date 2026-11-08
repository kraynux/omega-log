# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Favoris (plan_omega_log.md §3/§7) : constitution et liste des
favoris (source = Bibliotheque), lancement direct depuis cet ecran.
Meme convention de selection par numeros que screens/view_logs.py."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.manage_favorites import (
    create_favorite,
    list_favorites,
    remove_favorite,
)
from omega_log.domain.value_objects.viewer_type import ViewerType
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.screens.live_tail_screen import LiveTailScreen
from omega_log.interfaces.tui.screens.lnav_screen import LnavScreen
from omega_log.interfaces.tui.screens.log_viewer_screen import LogViewerScreen
from omega_log.interfaces.tui.widgets.library_selection import SELECTION_HINT, LibrarySelectionMixin
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.shared.i18n import N_, _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


_VIEWER_LABELS = {"simple": N_("Simple"), "classique": N_("Classique")}
"""Libelle traduit du selecteur ; la valeur (enregistree dans le favori) ne change jamais."""


class FavoritesScreen(LibrarySelectionMixin, OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._library_entries: list = []
        self._selected_favorite: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("FAVORIS"), classes="omega-title")

            yield DataTable(id="favorites-table")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Lancer"), id="launch", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Supprimer"), id="delete", variant="error")

            yield Static(_("Créer un favori"), classes="omega-subtitle")
            yield LogLibraryTable(id="library-table")
            yield Input(placeholder=_("Numéros séparés par des virgules (ex: 1,3)"), id="selection-input")
            yield Static(SELECTION_HINT, classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder=_("Nom du favori"), id="name-input")
                yield Select([(_(_VIEWER_LABELS.get(v.value, v.value)), v.value) for v in ViewerType],
                             value=ViewerType.SIMPLE.value, id="viewer-select")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Enregistrer"), id="save")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#favorites-table", DataTable).cursor_type = "row"
        self.query_one("#favorites-table", DataTable).add_columns(_("Nom"), _("Logs"), _("Viewer"))
        self._refresh_favorites()
        self._refresh_library()

    def _refresh_favorites(self) -> None:
        table = self.query_one("#favorites-table", DataTable)
        table.clear()
        for fav in list_favorites(self._container.favorite_repository):
            table.add_row(fav.name, ", ".join(fav.paths), fav.viewer.value, key=fav.name)

    def _refresh_library(self) -> None:
        self._library_entries = list_library(self._container.log_repository)
        self.query_one("#library-table", LogLibraryTable).load(self._library_entries)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "favorites-table":
            row = event.data_table.get_row_at(event.cursor_row)
            self._selected_favorite = str(row[0]) if row else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "launch":
            self._launch()
        elif button_id == "delete":
            self._delete()
        elif button_id == "save":
            self._save()

    def _launch(self) -> None:
        if self._selected_favorite is None:
            self.app.notify(_("Sélectionnez un favori."), severity="warning")
            return
        favorite = next(
            (f for f in list_favorites(self._container.favorite_repository) if f.name == self._selected_favorite),
            None,
        )
        if favorite is None:
            return
        if favorite.viewer == ViewerType.SIMPLE:
            self.app.push_screen(LiveTailScreen(container=self._container, path=favorite.paths[0]))
        elif favorite.viewer == ViewerType.CLASSIC:
            self.app.push_screen(LogViewerScreen(container=self._container, path=favorite.paths[0]))
        else:
            self.app.push_screen(LnavScreen(container=self._container, paths=list(favorite.paths)))

    def _delete(self) -> None:
        if self._selected_favorite is None:
            self.app.notify(_("Sélectionnez un favori."), severity="warning")
            return
        name = self._selected_favorite
        self.app.push_screen(
            ConfirmScreen(title=_("SUPPRIMER CE FAVORI ?"), message=name),
            lambda confirmed: self._delete_if_confirmed(confirmed, name),
        )

    def _delete_if_confirmed(self, confirmed: bool | None, name: str) -> None:
        if not confirmed:
            return
        remove_favorite(self._container.favorite_repository, name)
        self._selected_favorite = None
        self._refresh_favorites()

    def _save(self) -> None:
        raw_selection = self._library_selection()
        name = self.query_one("#name-input", Input).value.strip()
        viewer_value = self.query_one("#viewer-select", Select).value

        paths: list[str] = []
        for token in raw_selection.split(","):
            token = token.strip()
            if not token:
                continue
            if not token.isdigit() or not (1 <= int(token) <= len(self._library_entries)):
                self.app.notify(_("Numéro invalide : '{token}'.").format(token=token), severity="warning")
                return
            paths.append(self._library_entries[int(token) - 1].path)

        result = create_favorite(
            self._container.favorite_repository, name=name, paths=paths, viewer=ViewerType(viewer_value),
        )
        if not result.success:
            self.app.notify(result.message, severity="warning")
            return

        self.app.notify(result.message)
        self.query_one("#selection-input", Input).value = ""
        self.query_one("#name-input", Input).value = ""
        self._refresh_favorites()
