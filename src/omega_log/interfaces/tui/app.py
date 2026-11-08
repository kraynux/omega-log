# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree Textual de l'application, cable par le composition root
(app/bootstrap.py). Adapte du patron app.py du reste de la suite omega-."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, ClassVar, cast

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import App, SystemCommand
from textual.binding import Binding, BindingType

from omega_log.application.commands.select_theme import select_theme
from omega_log.application.exceptions import UnknownThemeError
from omega_log.application.queries.detect_terminal import detect_terminal
from omega_log.interfaces.tui.controllers.startup_controller import (
    StartupState,
    resolve_startup_state,
)
from omega_log.interfaces.tui.language_setting import notify_language_at_startup
from omega_log.interfaces.tui.rendering.stylesheet_loader import load_paths_for
from omega_log.interfaces.tui.rendering.textual_theme_builder import build_all_textual_themes
from omega_log.interfaces.tui.screens.help_screen import HelpScreen
from omega_log.interfaces.tui.screens.home import HomeScreen
from omega_log.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_log.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_log.interfaces.tui.screens.splash import SplashScreen
from omega_log.interfaces.tui.screens.terminal_warning import TerminalWarningScreen
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from textual.screen import Screen

    from omega_log.app.dependency_container import DependencyContainer

TITLE = "\U0001f4dc OMEGA-LOG"
"""Icone rouleau incluse DANS la chaine de titre (memes raisons que le
reste de la suite : HeaderIcon/HeaderTitle sont deux widgets Textual
distincts, les fondre dans une seule chaine les fait apparaitre comme
une unite)."""


class OmegaLogApp(App[None]):
    """Application TUI d'omega-log : resout theme/profil de rendu au
    demarrage, puis enchaine splash -> (avertissement terminal) -> accueil."""

    TITLE = TITLE
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", _("Quitter"), show=True),
        Binding("ctrl+q", "quit", _("Quitter"), show=False),
        Binding("t", "cycle_theme", _("Thème suivant"), show=True),
        Binding("r", "refresh_terminal", _("Rafraîchir"), show=True),
        Binding("a", "help", _("Aide"), show=True),
        Binding("s", "open_settings", _("Options"), show=True),
    ]

    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self._startup_state = resolve_startup_state(
            terminal_detector=container.terminal_detector,
            settings_store=container.settings_store,
        )
        css_path = cast(
            "list[str | PurePath]", load_paths_for(self._startup_state.theme.render_profile)
        )
        super().__init__(css_path=css_path)
        for theme in build_all_textual_themes():
            self.register_theme(theme)
        self.theme = self._startup_state.theme.theme_name
        # Version dans la barre de titre (portee d'omega-serv 2.6.0, 2026-11-07) : pyproject.toml, seule source.
        self.title = f"{TITLE} {self._container.app_version}"
        self.pending_language: str | None = None
        """Langue choisie dans les Options : __main__.py relance l'interface apres la sortie."""

    def on_mount(self) -> None:
        notify_language_at_startup(self)
        self.push_screen(SplashScreen(version=self._container.app_version), self._after_splash)

    def _after_splash(self, _result: None) -> None:
        terminal = self._startup_state.terminal
        too_small = (
            terminal.signals.columns < 80 or terminal.signals.rows < 24
        )
        if terminal.render_profile == RenderProfile.MONO or too_small:
            message = (
                _("Terminal détecté : {family} ({columns}x{rows}). Rendu appliqué : {value}.").format(family=terminal.signals.family, columns=terminal.signals.columns, rows=terminal.signals.rows, value=terminal.render_profile.value)
            )
            self.push_screen(TerminalWarningScreen(message=message), self._show_home)
        else:
            self._show_home(None)

    def _show_home(self, _result: None) -> None:
        self.push_screen(HomeScreen(container=self._container))

    def watch_theme(self, _theme_name: str) -> None:
        terminal = self._startup_state.terminal
        self.sub_title = f"{self.theme} | {terminal.signals.columns}x{terminal.signals.rows}"

    async def action_quit(self) -> None:
        """Surcharge : demande confirmation avant de fermer."""
        self.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.exit()

    def action_cycle_theme(self) -> None:
        """Touche `t` : bascule vers le theme SUIVANT du catalogue, sans
        confirmation."""
        names = list(TUI_THEMES.keys())
        current_index = names.index(self.theme) if self.theme in names else 0
        next_name = names[(current_index + 1) % len(names)]
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=next_name)
        except UnknownThemeError as exc:
            self.notify(str(exc), severity="error")
            return
        except OSError as exc:
            # Meme correctif applique ici par coherence (audit de la
            # suite, bug reel deja rencontre chez omega-fire/omega-check :
            # une simple erreur de persistance faisait planter cette
            # action sans aucun rattrapage). Le theme change quand meme
            # visuellement (self.theme = next_name plus bas) : seule la
            # PERSISTANCE du choix echoue, pas la fonctionnalite immediate.
            self.notify(_("Thème appliqué mais non enregistré : {exc}").format(exc=exc), severity="warning")
        self.theme = next_name

    def action_refresh_terminal(self) -> None:
        """Touche `r` : redetecte taille/famille du terminal et met a
        jour le sous-titre du Header."""
        terminal = detect_terminal(terminal_detector=self._container.terminal_detector)
        self._startup_state = StartupState(terminal=terminal, theme=self._startup_state.theme)
        self.sub_title = f"{self.theme} | {terminal.signals.columns}x{terminal.signals.rows}"
        self.notify(
            f"{terminal.signals.family} ({terminal.signals.columns}x{terminal.signals.rows})",
            title=_("Terminal rafraîchi"),
        )

    def action_help(self) -> None:
        self.push_screen(HelpScreen(container=self._container))

    def action_open_settings(self) -> None:
        self.push_screen(SettingsScreen(container=self._container))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Remplace la liste par defaut de Textual plutot que d'appeler
        `super()` (meme raisonnement que le reste de la suite)."""
        yield SystemCommand(_("Thème"), _("Changer le thème actif"), self.action_change_theme)
        yield SystemCommand(
            _("Quitter"), _("Quitter l'application (avec confirmation)"), self.action_quit
        )
        yield SystemCommand(
            _("Capture d'écran"),
            _("Enregistrer une capture SVG de l'écran courant"),
            self._deliver_screenshot_to_configured_dir,
        )

    def _deliver_screenshot_to_configured_dir(self) -> None:
        configured = self._container.settings_store.get(
            "screenshots_dir_override", str(self._container.default_screenshots_dir)
        )
        directory = Path(configured or self._container.default_screenshots_dir)
        directory.mkdir(parents=True, exist_ok=True)
        self.deliver_screenshot(path=str(directory))

    def _handle_exception(self, error: Exception) -> None:
        """Filet de securite unique cote TUI : toute exception technique
        non prevue est journalisee puis affichee comme notification,
        sans jamais fermer l'application."""
        logging.getLogger("omega_log").error("Exception non prevue", exc_info=error)
        self.notify(
            str(error) or type(error).__name__,
            title=_("Erreur inattendue"),
            severity="error",
            timeout=10,
        )
