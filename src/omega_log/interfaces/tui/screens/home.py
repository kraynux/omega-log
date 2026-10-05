# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran d'accueil : menu principal a 2 colonnes, conforme au menu
revise de plan_omega_log.md §7 (2026-10-03). Adapte du patron
screens/home.py du reste de la suite omega- — a la difference des
outils de reference (items = ecrans independants), ici les deux
colonnes sont explicitement groupees (classes CSS dediees) pour
refleter la distinction fonctionnelle Registre/Bibliotheque/.../
Statistiques (colonne 1) vs Rotate/Purger/Exporter/Options/Aide/Quitter
(colonne 2) du plan.

Aucun ecran de fonctionnalite n'est encore construit (Phase 1 du plan :
socle + splash + menu uniquement) — chaque entree non encore migree
notifie plutot que d'echouer silencieusement, meme patron que
omega-fire/home.py pour ses sections pas encore portees."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from omega_log.interfaces.tui.screens.access_log_stats_screen import AccessLogStatsScreen
from omega_log.interfaces.tui.screens.export_screen import ExportScreen
from omega_log.interfaces.tui.screens.favorites import FavoritesScreen
from omega_log.interfaces.tui.screens.help_screen import HelpScreen
from omega_log.interfaces.tui.screens.library import LibraryScreen
from omega_log.interfaces.tui.screens.process_ip_screen import ProcessIpScreen
from omega_log.interfaces.tui.screens.purge_screen import PurgeScreen
from omega_log.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_log.interfaces.tui.screens.registry import RegistryScreen
from omega_log.interfaces.tui.screens.rotate_screen import RotateScreen
from omega_log.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_log.interfaces.tui.screens.view_logs import ViewLogsScreen
from omega_log.interfaces.tui.widgets.home_wordmark import HomeWordmark

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

# (id, label) — labels repris tels quels du menu revise (plan §7).
_COLUMN_1: tuple[tuple[str, str], ...] = (
    ("registry", "Registre des capacites"),
    ("library", "Bibliotheque"),
    ("view_logs", "Voir les logs"),
    ("favorites", "Favoris"),
    ("process_ip", "Voir et Traiter IP"),
    ("access_log_stats", "Statistiques (acces)"),
)
_COLUMN_2: tuple[tuple[str, str], ...] = (
    ("rotate", "Rotate"),
    ("purge", "Purger"),
    ("export", "Exporter"),
    ("options", "Options"),
    ("help", "Aide"),
    ("quit", "Quitter"),
)

_NOT_YET_BUILT: set[str] = set()
_SCREEN_BY_ID = {
    "library": LibraryScreen,
    "view_logs": ViewLogsScreen,
    "favorites": FavoritesScreen,
    "process_ip": ProcessIpScreen,
    "access_log_stats": AccessLogStatsScreen,
    "export": ExportScreen,
    "rotate": RotateScreen,
    "purge": PurgeScreen,
}
_LABEL_BY_ID: dict[str, str] = {item_id: label for item_id, label in (*_COLUMN_1, *_COLUMN_2)}


class HomeScreen(Screen[None]):
    """Menu principal, racine de la pile de navigation. N'herite pas de
    OmegaScreen : `echap` ici demande confirmation de sortie, pas un
    dismiss() (rien "en dessous" de cet ecran)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", "Retour", show=True),
        Binding("up", "focus_previous_item", "Monter", show=False),
        Binding("down", "focus_next_item", "Descendre", show=False),
    ]

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-home-root"):
            with Center():
                yield HomeWordmark()
            with Center(), Horizontal(classes="omega-home-columns"):
                with Vertical(classes="omega-home-menu") as col1:
                    for item_id, label in _COLUMN_1:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                col1.border_title = "MENU PRINCIPAL"
                with Vertical(classes="omega-home-menu") as col2:
                    for item_id, label in _COLUMN_2:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                col2.border_title = "MAINTENANCE"
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        item_id = event.button.id
        if item_id == "help":
            self.app.push_screen(HelpScreen())
            return
        if item_id == "options":
            self.app.push_screen(SettingsScreen(container=self._container))
            return
        if item_id == "registry":
            self.app.push_screen(RegistryScreen(container=self._container))
            return
        if item_id in _SCREEN_BY_ID:
            self.app.push_screen(_SCREEN_BY_ID[item_id](container=self._container))
            return
        if item_id == "quit":
            self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)
            return
        if item_id in _NOT_YET_BUILT:
            self.app.notify(
                "Cet ecran n'est pas encore construit (voir plan_omega_log.md, phases suivantes).",
                title=_LABEL_BY_ID.get(item_id, ""),
                severity="information",
            )

    def action_back(self) -> None:
        self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.app.exit()
