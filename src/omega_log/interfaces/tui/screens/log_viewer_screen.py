# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Viewer 2 (CLASSIC) — lecture + suivi incremental d'un fichier log.

ADAPTE depuis omega-serv/interfaces/tui/screens/log_viewer_screen.py :
meme mecanisme (lecture des dernieres lignes au montage, "Suivre en
direct" via `set_interval`, RichLog, `LiveTailPort`), mais generalise a
UN CHEMIN ARBITRAIRE passe au constructeur au lieu des 3 boutons fixes
`_KNOWN_LOGS` (access/error/waf_alerts) de la version source — LOG n'a
pas de liste fixe de logs connus, voir plan_omega_log.md §2.

Elevation sudo ponctuelle (plan §5.1, 2026-10-03) AJOUTEE sur
`PermissionError` specifiquement (jamais sur un `OSError` generique —
fichier introuvable/disque plein n'ont rien a voir avec un probleme de
permission) : une seule authentification par ouverture d'ecran
(`self._elevated`), reutilisee pour le suivi en direct ensuite."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.timer import Timer
from textual.widgets import Button, Footer, Header, RichLog, Static

from omega_log.infrastructure.privileged.privileged_file_ops import read_file_privileged
from omega_log.infrastructure.tail.live_tail_reader import LiveTailReader
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_TAIL_INTERVAL_SECONDS = 1.0
_INITIAL_LINES = 200


class LogViewerScreen(OmegaScreen):
    """Viewer 2 : affiche les dernieres lignes d'un fichier, avec un
    bouton pour basculer le suivi en direct."""

    def __init__(self, *, container: DependencyContainer, path: str) -> None:
        super().__init__()
        self._container = container
        self._path = Path(path)
        self._reader: LiveTailReader | None = None
        self._following = False
        self._timer: Timer | None = None
        self._elevated = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(f"VOIR LES LOGS — CLASSIQUE — {self._path}", classes="omega-title")
            yield Static("", id="viewer-error", classes="omega-hint")
            yield RichLog(id="log-content", wrap=False, highlight=False, markup=False)
            with Horizontal(classes="omega-actions"):
                yield Button("Suivre en direct", id="follow")
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._load_initial()

    def action_back(self) -> None:
        self._stop_follow()
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "follow":
            self._toggle_follow()

    def _load_initial(self) -> None:
        log_widget = self.query_one("#log-content", RichLog)
        log_widget.clear()
        if not self._path.is_file():
            self.query_one("#viewer-error", Static).update(f"Fichier introuvable : {self._path}")
            return

        try:
            text = self._path.read_text(encoding="utf-8", errors="replace")
        except PermissionError:
            text = self._load_privileged()
            if text is None:
                return
        except OSError as exc:
            self.query_one("#viewer-error", Static).update(f"Lecture impossible : {exc}")
            return

        lines = text.splitlines()[-_INITIAL_LINES:]
        for line in lines:
            log_widget.write(line)

        self._reader = LiveTailReader(self._path)

    def _load_privileged(self) -> str | None:
        """Repli sur une lecture privilegiee (sudo ponctuel) apres un
        PermissionError — plan §5.1, 2026-10-03."""
        if not request_elevation(self, self._container.process_runner):
            self.query_one("#viewer-error", Static).update(
                f"Permission refusee sur {self._path} (authentification sudo requise)."
            )
            return None
        result = read_file_privileged(self._container.process_runner, str(self._path))
        if not result.success:
            self.query_one("#viewer-error", Static).update(f"Lecture privilegiee impossible : {result.message}")
            return None
        self._elevated = True
        return result.content

    def _toggle_follow(self) -> None:
        if self._following:
            self._stop_follow()
        else:
            self._start_follow()

    def _start_follow(self) -> None:
        if self._reader is None:
            self.app.notify("Rien a suivre (fichier introuvable).", severity="warning")
            return
        self._following = True
        self.query_one("#follow", Button).label = "Arreter le suivi"
        self._timer = self.set_interval(_TAIL_INTERVAL_SECONDS, self._poll)

    def _stop_follow(self) -> None:
        self._following = False
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        try:
            self.query_one("#follow", Button).label = "Suivre en direct"
        except NoMatches:
            pass  # l'ecran peut etre en cours de fermeture (widget deja demonte)

    def _poll(self) -> None:
        if self._reader is None:
            return
        try:
            if self._elevated:
                new_lines = self._reader.read_new_lines_privileged(self._container.process_runner)
            else:
                new_lines = self._reader.read_new_lines()
        except OSError as exc:
            self.query_one("#viewer-error", Static).update(f"Lecture impossible : {exc}")
            self._stop_follow()
            return
        if new_lines:
            log_widget = self.query_one("#log-content", RichLog)
            for line in new_lines:
                log_widget.write(line)
