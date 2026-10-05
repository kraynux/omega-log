# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Classe de base partagee par tous les ecrans navigables (retour clavier).
Copiee verbatim depuis le reste de la suite omega-, a l'exception de
`_maybe_suspend` (ADAPTE depuis omega-serv/interfaces/tui/screens/_base.py,
ajoute 2026-10-03 pour l'elevation sudo ponctuelle, plan §5.1 — meme
mecanisme eprouve que omega-serv pour `sudo -v`, y compris le filet de
securite `_ensure_terminal_truly_released` sans lequel un bug reel deja
rencontre chez SERV se reproduirait : le thread clavier interne de
Textual reste actif apres `App.suspend()` et lit CONCURREMMENT le mot de
passe sudo sur le meme tty, le dispersant entre les deux lecteurs)."""
from __future__ import annotations

import termios
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, ClassVar

from textual.app import SuspendNotSupported
from textual.binding import Binding, BindingType
from textual.screen import Screen

if TYPE_CHECKING:
    from textual.app import App

_INPUT_THREAD_JOIN_TIMEOUT_SECONDS = 1.0


def _ensure_terminal_truly_released(app: App[None]) -> None:
    """Repli defensif AJOUTE PAR-DESSUS `App.suspend()` (jamais un
    correctif dans Textual lui-meme) : attend reellement que le thread
    d'entree du pilote soit mort avant de rendre la main a l'appelant
    (qui va lancer `sudo -v` sur ce meme terminal). `getattr` partout :
    purement best-effort, silencieux sur tout driver/version ou ces
    attributs prives n'existeraient pas."""
    driver = getattr(app, "_driver", None)
    if driver is None:
        return
    key_thread = getattr(driver, "_key_thread", None)
    if key_thread is not None and key_thread.is_alive():
        exit_event = getattr(driver, "exit_event", None)
        if exit_event is not None:
            exit_event.set()
        key_thread.join(timeout=_INPUT_THREAD_JOIN_TIMEOUT_SECONDS)
        if exit_event is not None:
            exit_event.clear()
    writer_thread = getattr(driver, "_writer_thread", None)
    if writer_thread is not None and writer_thread.is_alive():
        stop = getattr(writer_thread, "stop", None)
        if callable(stop):
            stop()
        else:
            writer_thread.join(timeout=_INPUT_THREAD_JOIN_TIMEOUT_SECONDS)
    fileno = getattr(driver, "fileno", None)
    if isinstance(fileno, int):
        try:
            termios.tcflush(fileno, termios.TCIFLUSH)
        except OSError:
            pass


class OmegaScreen(Screen[None]):
    """Ecran navigable standard : ajoute `echap` -> retour, sans qu'aucun
    ecran n'ait a redeclarer son propre binding. `home.py` et
    `quit_confirm.py` n'en heritent pas (voir leurs propres fichiers)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", "Retour", show=True),
        Binding("up", "focus_previous_item", "Monter", show=False),
        Binding("down", "focus_next_item", "Descendre", show=False),
    ]

    def action_back(self) -> None:
        self.dismiss()

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    @contextmanager
    def _maybe_suspend(self) -> Iterator[None]:
        """A utiliser autour de tout appel a `authenticate_sudo()`
        (infrastructure/privileged/elevation.py) : rend la main au vrai
        terminal pour le prompt de mot de passe, la reprend ensuite."""
        caught: BaseException | None = None
        try:
            with self.app.suspend():
                _ensure_terminal_truly_released(self.app)
                try:
                    yield
                except BaseException as exc:  # noqa: BLE001 - repropagee plus bas, jamais avalee
                    caught = exc
        except SuspendNotSupported:
            yield
            return
        if caught is not None:
            raise caught
