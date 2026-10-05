# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Rotate (plan_omega_log.md §3/§7) : sauvegarder/restaurer un log
de la Bibliotheque. Selection par numero, meme convention que
screens/view_logs.py."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_log.application.commands.restore_backup import RestoreBackupCommand, RestoreBackupRequest
from omega_log.application.commands.rotate_logs import RotateLogsCommand, RotateLogsRequest
from omega_log.application.use_cases.library import list_library
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


class RotateScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._backups: list = []
        self._selected_backup_path: str | None = None
        self._elevated = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("ROTATE — SAUVEGARDER / RESTAURER", classes="omega-title")
            yield Static("", id="rotate-hint", classes="omega-hint")

            yield DataTable(id="library-table")
            yield Input(placeholder="Numero du log a sauvegarder (ex: 1)", id="selection-input")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder="Rotations a conserver", value="7", id="keep-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Sauvegarder maintenant", id="rotate", variant="primary")

            yield Static("Archives disponibles", classes="omega-subtitle")
            yield DataTable(id="backups-table")
            with Horizontal(classes="omega-actions"):
                yield Select([("Fusion (append)", "append"), ("Ecrasement (overwrite)", "overwrite")],
                             value="append", id="mode-select")
                with Container(classes="omega-btn-frame"):
                    yield Button("Restaurer", id="restore")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer l'archive", id="delete-backup", variant="error")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#library-table", DataTable).cursor_type = "row"
        self.query_one("#library-table", DataTable).add_columns("#", "Chemin")
        self.query_one("#backups-table", DataTable).cursor_type = "row"
        self.query_one("#backups-table", DataTable).add_columns("Archive", "Taille", "Cree le")
        self._refresh_library()
        self._refresh_backups()

    def _refresh_library(self) -> None:
        self._entries = list_library(self._container.log_repository)
        table = self.query_one("#library-table", DataTable)
        table.clear()
        for idx, entry in enumerate(self._entries, start=1):
            table.add_row(str(idx), entry.path)

    def _refresh_backups(self) -> None:
        self._backups = sorted(
            self._container.persistence_port.list_backups(self._container.backup_dir),
            key=lambda b: b.created_at, reverse=True,
        )
        table = self.query_one("#backups-table", DataTable)
        table.clear()
        for backup in self._backups:
            table.add_row(backup.path.name, f"{backup.size_bytes} o", backup.created_at.isoformat(), key=str(backup.path))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "backups-table":
            return
        self._selected_backup_path = str(event.row_key.value) if event.row_key is not None else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "rotate":
            self._rotate()
        elif button_id == "restore":
            self._restore()
        elif button_id == "delete-backup":
            self._delete_backup()

    def _resolve_selected_path(self) -> str | None:
        raw = self.query_one("#selection-input", Input).value.strip()
        if not raw.isdigit() or not (1 <= int(raw) <= len(self._entries)):
            self.app.notify("Numero de log invalide.", severity="warning")
            return None
        return self._entries[int(raw) - 1].path

    def _rotate(self) -> None:
        path = self._resolve_selected_path()
        if path is None:
            return
        keep_raw = self.query_one("#keep-input", Input).value.strip()
        keep = int(keep_raw) if keep_raw.isdigit() else 7

        command = RotateLogsCommand(
            self._container.persistence_port, self._container.backup_dir, self._container.elevated_tmp_dir,
        )
        runner = self._container.process_runner if self._elevated else None
        try:
            result = command.execute(RotateLogsRequest(source_path=path, keep=keep), runner=runner)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify(f"Permission refusee sur {path}.", severity="error")
                return
            self._elevated = True
            result = command.execute(RotateLogsRequest(source_path=path, keep=keep), runner=self._container.process_runner)
        self.app.notify(result.message, severity="information" if result.success else "error")
        self._refresh_backups()

    def _restore(self) -> None:
        if self._selected_backup_path is None:
            self.app.notify("Selectionnez une archive.", severity="warning")
            return
        path = self._resolve_selected_path()
        if path is None:
            return
        mode = self.query_one("#mode-select", Select).value

        self.app.push_screen(
            ConfirmScreen(
                title="RESTAURER CETTE ARCHIVE ?",
                message=f"Mode : {mode}. Cible : {path}.",
            ),
            lambda confirmed: self._restore_if_confirmed(confirmed, path, mode),
        )

    def _restore_if_confirmed(self, confirmed: bool | None, target_path: str, mode: str) -> None:
        if not confirmed:
            return
        from pathlib import Path as _Path

        command = RestoreBackupCommand(
            self._container.persistence_port, self._container.restore_temp_dir, self._container.backup_dir,
            self._container.elevated_tmp_dir,
        )
        request = RestoreBackupRequest(
            backup_path=self._selected_backup_path, target_dir=str(_Path(target_path).parent), mode=mode,
        )
        runner = self._container.process_runner if self._elevated else None
        try:
            result = command.execute(request, runner=runner)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify(f"Permission refusee sur {target_path}.", severity="error")
                return
            self._elevated = True
            result = command.execute(request, runner=self._container.process_runner)
        self.app.notify(result.message, severity="information" if result.success else "error")
        self._refresh_backups()

    def _delete_backup(self) -> None:
        if self._selected_backup_path is None:
            self.app.notify("Selectionnez une archive.", severity="warning")
            return
        backup_path = self._selected_backup_path
        self.app.push_screen(
            ConfirmScreen(title="SUPPRIMER CETTE ARCHIVE ?", message=backup_path),
            lambda confirmed: self._delete_backup_if_confirmed(confirmed, backup_path),
        )

    def _delete_backup_if_confirmed(self, confirmed: bool | None, backup_path: str) -> None:
        if not confirmed:
            return
        backup = next((b for b in self._backups if str(b.path) == backup_path), None)
        if backup is None:
            return
        self._container.persistence_port.delete_backup(backup)
        self._selected_backup_path = None
        self._refresh_backups()
