# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""« Voir les exports » (demande 2026-11-26, meme principe que les autres outils : methode commune de la suite,
~/DEV/OMEGA_A_FAIRE_VOIR_LES_EXPORTS.md ; repris d'omega-tail) : le dossier des exports s'ouvre dans le navigateur
de l'utilisateur, chaque export se lit d'un clic, sans quitter omega-log.

Repli sans navigateur (serveur, connexion SSH) : la liste du dossier, et chaque export lu ici meme (texte, JSON ;
page HTML rendue en texte). Rien n'est interprete : le contenu est affiche tel quel, jamais comme des balises de
l'interface (lecon du scan de securite d'omega-fire, 2026-11-21)."""
from __future__ import annotations

import contextlib
import html
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

MAX_READ_BYTES = 2 * 1024 * 1024
_HIDDEN = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
_BLOCKS = re.compile(r"<(br|/p|/h[1-6]|/div|/tr|/li|/table|/section|/pre|/header|/footer)\b[^>]*>", re.IGNORECASE)
_TAGS = re.compile(r"<[^>]+>")
_SPACES = re.compile(r"[ \t]+")


def list_exports(folder: Path) -> list[Path]:
    """Fichiers ordinaires du dossier (jamais un lien, jamais un sous-dossier), le plus recent d'abord."""
    try:
        files = [path for path in folder.iterdir() if path.is_file() and not path.is_symlink()]
    except OSError:
        return []
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def read_export(path: Path) -> str:
    """Contenu lisible d'un export : texte ou JSON tels quels, page HTML ramenee a son texte."""
    try:
        if path.is_symlink() or path.stat().st_size > MAX_READ_BYTES:
            return _("Fichier trop volumineux pour être lu ici : {path}").format(path=path)
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return _("Lecture impossible : {exc}").format(exc=exc.strerror or exc)
    if path.suffix.lower() in (".html", ".htm"):
        content = html.unescape(_TAGS.sub(" ", _BLOCKS.sub("\n", _HIDDEN.sub(" ", content))))
        content = "\n".join(_SPACES.sub(" ", line).strip() for line in content.splitlines() if line.strip())
    return content


class ExportsScreen(OmegaScreen):
    def __init__(self, *, folder: Path) -> None:
        super().__init__()
        self._folder = folder
        self._files: list[Path] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="exports-panel", classes="omega-panel"):
            with Center():
                yield Static(_("EXPORTS"), classes="omega-title")
            yield Static(_("Pas de navigateur dans cette session (serveur, connexion SSH) : les exports sont listés "
                           "et lus ici. Choisissez une ligne (Entrée) pour la lire."), classes="omega-hint")
            yield Static(Text(str(self._folder)), id="exports-folder", classes="omega-hint")
            yield DataTable(id="exports-table")
            with VerticalScroll(id="export-reader"):
                yield Static("", id="export-content")
            with Center(), Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Lire"), id="read", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#exports-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(_("Export"), _("Date"), _("Taille"))
        self._files = list_exports(self._folder)
        for path in self._files:
            info = path.stat()
            table.add_row(Text(path.name), datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M"),
                          f"{info.st_size / 1024:.1f} Ko")
        if not self._files:
            self.query_one("#export-content", Static).update(_("Aucun export pour l'instant."))
        table.focus()

    def _read(self) -> None:
        with contextlib.suppress(Exception):
            index = self.query_one("#exports-table", DataTable).cursor_row
            if 0 <= index < len(self._files):
                self.query_one("#export-content", Static).update(Text(read_export(self._files[index])))
                self.query_one("#export-reader", VerticalScroll).scroll_home(animate=False)

    def on_data_table_row_selected(self, _event: DataTable.RowSelected) -> None:
        self._read()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "read":
            self._read()
        elif event.button.id == "back":
            self.dismiss()


def view_exports(screen: OmegaScreen, container: DependencyContainer) -> None:
    """Le dossier des exports dans le navigateur de l'utilisateur (omega-lib, sa session graphique seulement) ;
    sans navigateur ni session graphique, la liste et la lecture dans l'interface (ExportsScreen)."""
    app = screen.app
    folder = container.default_exports_dir

    def after(opened: bool) -> None:
        if opened:
            app.notify(_("Dossier des exports ouvert dans le navigateur : {path}").format(path=folder))
        else:
            app.push_screen(ExportsScreen(folder=folder))

    def work() -> None:
        opened = False
        with contextlib.suppress(Exception):
            folder.mkdir(parents=True, exist_ok=True)
            opened = bool(container.open_folder(folder))
        app.call_from_thread(after, opened)

    screen.run_worker(work, thread=True, group="view-exports", exclusive=True)
