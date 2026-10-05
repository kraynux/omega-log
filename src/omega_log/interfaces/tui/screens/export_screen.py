# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Exporter (plan_omega_log.md §3/§7) : ADAPTE depuis
omega-serv/export_log_archives_screen.py (source retenue, mecanisme
complet et deja utilise en production) — meme patron JSON/HTML via
jinja2 (infrastructure/exporters/html_exporter.py), applique aux
archives de LOG (ports/persistence.py) plutot qu'aux archives SERV."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Select, Static

from omega_log.infrastructure.exporters.html_exporter import export_log_archives_html
from omega_log.interfaces.tui.screens._base import OmegaScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


def _export_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


class ExportScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._infos: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("EXPORTER LA LISTE DES ARCHIVES", classes="omega-title")
            yield Static("", id="export-error", classes="omega-hint")
            yield DataTable(id="archives-table")
            yield Static("Theme d'export HTML", classes="omega-subtitle")
            yield Select([(name, name) for name in EXPORT_PALETTES], value=DEFAULT_EXPORT_THEME, id="export-theme-select")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Rafraichir", id="refresh", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter JSON", id="export-json")
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter HTML", id="export-html")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#archives-table", DataTable)
        table.add_columns("Archive", "Taille (octets)", "Creee le")
        self._refresh()

    def _refresh(self) -> None:
        backups = self._container.persistence_port.list_backups(self._container.backup_dir)
        self._infos = [
            {"name": b.path.name, "size_bytes": b.size_bytes, "created_at": b.created_at.isoformat()}
            for b in backups
        ]
        table = self.query_one("#archives-table", DataTable)
        table.clear()
        for info in self._infos:
            table.add_row(info["name"], str(info["size_bytes"]), info["created_at"], key=info["name"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
            return
        if button_id == "refresh":
            self._refresh()
            return
        if button_id == "export-json":
            self._export_json()
            return
        if button_id == "export-html":
            self._export_html()

    def _export_json(self) -> None:
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"archives-{_export_timestamp()}.json"
        out_path.write_text(json.dumps(self._infos, indent=2, ensure_ascii=False), encoding="utf-8")
        self.app.notify(f"Export JSON : {out_path}")

    def _export_html(self) -> None:
        theme_name = self.query_one("#export-theme-select", Select).value
        html = export_log_archives_html(self._infos, theme_name=str(theme_name))
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"archives-{_export_timestamp()}.html"
        out_path.write_text(html, encoding="utf-8")
        self.app.notify(f"Export HTML : {out_path}")
