# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Registre (plan_omega_log.md §4/§7) : detection de services +
scan manuel de dossier, branches sur application/use_cases/scan_logs.py
(Phase 2, deja construit et verifie par un scan reel). Execute en
arriere-plan (thread), meme patron que
omega_fire/interfaces/tui/screens/scanning.py — jamais sur le thread UI,
~45 appels subprocess (pgrep/systemctl) bloqueraient sinon l'affichage.

Import (au detail/en totalite) relie a la Bibliotheque depuis la
Phase 5 (application/use_cases/library.py)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import add_many_to_library
from omega_log.application.use_cases.scan_logs import ScanLogsResult, scan_directory, scan_logs
from omega_log.domain.entities.log_file import LogFile
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.live_tail_screen import LiveTailScreen
from omega_log.interfaces.tui.screens.lnav_screen import LnavScreen
from omega_log.interfaces.tui.screens.log_viewer_screen import LogViewerScreen
from omega_log.interfaces.tui.widgets.log_list import LogList

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


class RegistryScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._result: ScanLogsResult | None = None
        self._manual_entries: list = []
        self._selected_path: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("REGISTRE DES CAPACITES", classes="omega-title")
            yield Static("", id="registry-status", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Scanner les services", id="scan", variant="primary")
                yield Input(placeholder="Dossier a scanner (ex. /var/log)", id="path-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Scanner ce dossier", id="scan-path")
            yield LogList(id="log-list")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (simple)", id="view-simple")
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (classique)", id="view-classic")
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir (lnav)", id="view-lnav")
                with Container(classes="omega-btn-frame"):
                    yield Button("Importer la selection", id="import-selection")
                with Container(classes="omega-btn-frame"):
                    yield Button("Importer tout", id="import-all")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#log-list", LogList).cursor_type = "row"
        self._run_service_scan()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "log-list":
            return
        row = event.data_table.get_row_at(event.cursor_row)
        self._selected_path = str(row[0]) if row else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "scan":
            self._run_service_scan()
        elif button_id == "scan-path":
            self._run_directory_scan()
        elif button_id == "view-simple":
            self._open_viewer(LiveTailScreen)
        elif button_id == "view-classic":
            self._open_viewer(LogViewerScreen)
        elif button_id == "view-lnav":
            self._open_lnav()
        elif button_id == "import-selection":
            self._import_selection()
        elif button_id == "import-all":
            self._import_all()

    def _open_viewer(self, screen_cls: type) -> None:
        if self._selected_path is None:
            self.app.notify("Selectionnez une ligne dans la liste.", severity="warning")
            return
        self.app.push_screen(screen_cls(container=self._container, path=self._selected_path))

    def _open_lnav(self) -> None:
        if self._selected_path is None:
            self.app.notify("Selectionnez une ligne dans la liste.", severity="warning")
            return
        self.app.push_screen(LnavScreen(container=self._container, paths=[self._selected_path]))

    def _all_entries(self) -> list[LogFile]:
        discovered = self._result.discovered if self._result is not None else []
        return [*discovered, *self._manual_entries]

    def _import_selection(self) -> None:
        if self._selected_path is None:
            self.app.notify("Selectionnez une ligne dans la liste.", severity="warning")
            return
        match = next((e for e in self._all_entries() if e.path == self._selected_path), None)
        if match is None:
            self.app.notify("Ligne introuvable (relancez un scan).", severity="warning")
            return
        add_many_to_library(self._container.log_repository, [match])
        self.app.notify(f"{self._selected_path} ajoute a la Bibliotheque.")

    def _import_all(self) -> None:
        entries = self._all_entries()
        if not entries:
            self.app.notify("Rien a importer (lancez un scan).", severity="warning")
            return
        count = add_many_to_library(self._container.log_repository, entries)
        self.app.notify(f"{count} log(s) ajoute(s) a la Bibliotheque.")

    def _run_service_scan(self) -> None:
        self._set_status("Analyse des services en cours...")
        self.query_one("#log-list", LogList).loading = True

        def _work() -> None:
            try:
                result = scan_logs()
            except Exception as exc:  # noqa: BLE001 - toute panne doit se degrader en notification
                self.app.call_from_thread(self._show_scan_error, str(exc))
                return
            self.app.call_from_thread(self._show_service_scan_result, result)

        self.run_worker(_work, thread=True)

    def _run_directory_scan(self) -> None:
        raw_path = self.query_one("#path-input", Input).value.strip()
        if not raw_path:
            self.app.notify("Indiquez un dossier a scanner.", severity="warning")
            return

        directory = Path(raw_path)
        self._set_status(f"Scan de {directory} en cours...")
        self.query_one("#log-list", LogList).loading = True

        def _work() -> None:
            try:
                entries = scan_directory(directory)
            except Exception as exc:  # noqa: BLE001
                self.app.call_from_thread(self._show_scan_error, str(exc))
                return
            self.app.call_from_thread(self._show_directory_scan_result, entries)

        self.run_worker(_work, thread=True)

    def _show_scan_error(self, message: str) -> None:
        self.query_one("#log-list", LogList).loading = False
        self._set_status(f"Erreur : {message}")

    def _show_service_scan_result(self, result: ScanLogsResult) -> None:
        self._result = result
        self._manual_entries = []
        self._refresh_list()
        self._set_status(
            f"{result.capabilities_registered} capacites sondees — "
            f"{len(result.discovered)} log(s) decouvert(s) "
            f"({len(result.stale)} suspect(s)), {len(result.errors)} erreur(s)."
        )

    def _show_directory_scan_result(self, entries: list) -> None:
        self._manual_entries = entries
        self._refresh_list()
        self._set_status(f"Scan manuel : {len(entries)} fichier(s) trouve(s).")

    def _refresh_list(self) -> None:
        log_list = self.query_one("#log-list", LogList)
        log_list.loading = False
        discovered = self._result.discovered if self._result is not None else []
        log_list.load([*discovered, *self._manual_entries])

    def _set_status(self, message: str) -> None:
        self.query_one("#registry-status", Static).update(message)
