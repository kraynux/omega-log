# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Viewer 3 (LNAV) — fusion multi-logs via lnav dans un pty.

ADAPTE depuis omega-fire/interfaces/tui/screens/lnav_screen.py : meme
mecanisme de handoff (`App.suspend()` + encapsulation PTY+pyte, voir
infrastructure/lnav/render.py), simplifie pour Phase 4 — pas encore de
gestion d'epingles/historique (ManageLiveTailPinsCommand releve de la
Bibliotheque/Favoris, Phase 5). Prend directement une liste de chemins
au constructeur, fournie pour l'instant par screens/registry.py (ligne
selectionnee) ; sera remplacee par la selection Bibliotheque/Favoris.

Elevation sudo ponctuelle (plan §5.1, 2026-10-03) AJOUTEE : si au moins
un chemin n'est pas lisible par l'utilisateur courant, lnav est lance
via `sudo -E` (pty_session.py::spawn_lnav) — le mot de passe est alors
demande A L'INTERIEUR du pty, relaye par le mecanisme de rendu existant
(render.py), aucune authentification separee necessaire ici contrairement
aux Viewers 1/2 (ceux-la font de l'I/O Python directe, pas un
sous-processus dans un pty).

Persistance du cycle de theme [t] AJOUTEE (2026-10-04, retour
utilisateur) : `render_lnav_live()` retourne le nom du theme
EFFECTIVEMENT actif a la fermeture (peut differer de celui donne en
entree si l'utilisateur a cycle pendant la session) — applique et
persiste ici sur reprise, exactement le meme patron que
`app.py::action_cycle_theme` (meme rattrapage sur `OSError` de
persistance : le theme reste applique visuellement meme si
l'enregistrement echoue).

`self.app.suspend()` brut REMPLACE par `self._maybe_suspend()`
(2026-10-04, retour utilisateur : en cyclant les themes avec [t] dans
lnav, "le logiciel s'eteint" et le terminal reste bloque, ne rendant la
main qu'apres un Ctrl+C) : ce fichier etait le SEUL appelant de
`App.suspend()` sans le filet de securite deja ajoute dans
`_base.py::_ensure_terminal_truly_released` (meme bug reel que chez
omega-serv — voir son commentaire) — le thread clavier interne de
Textual restait actif pendant toute la session lnav et lisait le meme
tty EN PARALLELE de notre boucle brute (render.py). `app.py` liant `q`
-> `quit` et `t` -> `cycle_theme` AU NIVEAU APPLICATION, une frappe
destinee a lnav (tres communes toutes les deux a l'interieur de lnav
lui-meme) pouvait etre captee par ce thread parasite et declencher
l'action correspondante sur l'appli ENTIERE au lieu de lnav — `q`
l'eteignant purement et simplement en plein handoff pty, d'ou le blocage
observe (plus de prompt tant que le process du pool de calcul,
collateral, ne recoit pas lui aussi le Ctrl+C de secours)."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from omega_log.application.commands.select_theme import select_theme
from omega_log.application.exceptions import UnknownThemeError
from omega_log.infrastructure.probe.lnav_capability import probe_lnav
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_ERROR_MESSAGE = (
    _("lnav est introuvable ou non fonctionnel sur ce système. Sur Arch/Manjaro : sudo pacman "
      "-S lnav. Sur Debian/Ubuntu : sudo apt install lnav.")
)


_LOGGER = logging.getLogger(__name__)


class LnavScreen(OmegaScreen):
    """Lancement DIRECT (2026-11-07, retour utilisateur : « peut-on supprimer cette interface secondaire qui
    redemande la meme operation ? ») : lnav part des l'ouverture ; a sa fermeture, retour a l'ecran precedent.
    L'ecran ne reste affiche qu'en cas d'echec, avec l'erreur et « Lancer lnav » pour reessayer. La trace
    complete d'un echec est ecrite dans var/app.log."""

    def __init__(self, *, container: DependencyContainer, paths: list[str]) -> None:
        super().__init__()
        self._container = container
        self._paths = paths

    def on_mount(self) -> None:
        self.call_after_refresh(self._launch_directly)

    def _launch_directly(self) -> None:
        if self._launch():
            self.dismiss()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("VOIR LES LOGS — LNAV (FUSION MULTI-LOGS)"), classes="omega-title")
            yield Static(_("Fichiers : {join}").format(join=', '.join(self._paths)), classes="omega-hint")
            yield Static("", id="lnav-error", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Lancer lnav"), id="launch", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "launch":
            self._launch()

    def _launch(self) -> bool:
        """True si lnav a tourne puis a ete quitte normalement ; False en cas d'echec (ecran garde)."""
        capability = probe_lnav()
        if not capability.is_usable():
            self.app.notify(_ERROR_MESSAGE, severity="error")
            self.query_one("#lnav-error", Static).update(_ERROR_MESSAGE)
            return False

        missing = [p for p in self._paths if not Path(p).is_file()]
        if missing:
            message = _("Fichier(s) introuvable(s) : {join}").format(join=', '.join(missing))
            self.app.notify(message, severity="error")
            self.query_one("#lnav-error", Static).update(message)
            return False

        try:
            self._run_lnav()
        except Exception as exc:
            _LOGGER.exception("Echec du lancement de lnav sur %s (theme %s)", self._paths, self.app.theme)
            message = _("Échec du lancement de lnav : {exc}").format(exc=exc)
            self.app.notify(message, severity="error")
            self.query_one("#lnav-error", Static).update(message)
            return False
        return True

    def _run_lnav(self) -> None:
        """Isole pour etre substituable en test (lnav exige un vrai
        terminal interactif, non disponible sous Pilot — voir
        infrastructure/lnav/render.py)."""
        from omega_log.infrastructure.lnav.render import render_lnav_live

        theme_name = self.app.theme
        use_sudo = any(not os.access(p, os.R_OK) for p in self._paths)

        with self._maybe_suspend():
            final_theme_name = render_lnav_live([Path(p) for p in self._paths], theme_name, use_sudo=use_sudo)

        if final_theme_name != theme_name:
            self._apply_theme(final_theme_name)

    def _apply_theme(self, theme_name: str) -> None:
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=theme_name)
        except UnknownThemeError as exc:
            self.app.notify(str(exc), severity="error")
            return
        except OSError as exc:
            self.app.notify(_("Thème appliqué mais non enregistré : {exc}").format(exc=exc), severity="warning")
        self.app.theme = theme_name
