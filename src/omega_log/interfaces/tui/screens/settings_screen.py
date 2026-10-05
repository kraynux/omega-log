# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Options : theme, profil de rendu, et purge des dossiers
applicatifs a plat (exports/ screenshots/ — jamais un dossier de logs
scannes, voir application/use_cases/clear_directory.py). Bouton Retour
explicite AJOUTE (2026-10-03, retour utilisateur) : OmegaScreen gere deja
`echap` -> retour, mais tous les autres ecrans de l'application exposent
AUSSI un bouton "Retour" explicite (purge_screen.py, rotate_screen.py,
process_ip_screen.py...) — cet ecran en etait prive par oubli, pas par
choix delibere."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Select, Static

from omega_log.application.commands.select_render_profile import select_render_profile
from omega_log.application.commands.select_theme import select_theme
from omega_log.application.exceptions import UnknownThemeError
from omega_log.application.use_cases.clear_directory import clear_directory
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_AUTO = "auto"


class SettingsScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        store = self._container.settings_store
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static("OPTIONS", classes="omega-title")

            yield Static("Theme", classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], value=self.app.theme, id="theme-select")

            yield Static("Profil de rendu (redemarrage requis)", classes="omega-subtitle")
            current_override = store.get("render_profile_override", "")
            yield Select(
                [("Automatique", _AUTO)] + [(p.value, p.value) for p in RenderProfile],
                value=current_override or _AUTO,
                id="render-profile-select",
            )

            yield Static("Maintenance des dossiers", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider le dossier exports", id="clear-exports", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider le dossier screenshots", id="clear-screenshots", variant="error")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme-select":
            if str(event.value) == self.app.theme:
                return
            self._apply_theme(str(event.value))
        elif event.select.id == "render-profile-select":
            current_override = self._container.settings_store.get("render_profile_override", "") or _AUTO
            if str(event.value) == current_override:
                return
            self._apply_render_profile(str(event.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "clear-exports":
            self._confirm_clear("exports", self._container.default_exports_dir)
        elif event.button.id == "clear-screenshots":
            self._confirm_clear("screenshots", self._container.default_screenshots_dir)

    def _apply_theme(self, theme_name: str) -> None:
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=theme_name)
        except UnknownThemeError as exc:
            self.app.notify(str(exc), severity="error")
            return
        self.app.theme = theme_name

    def _apply_render_profile(self, value: str) -> None:
        profile = None if value == _AUTO else RenderProfile(value)
        select_render_profile(settings_store=self._container.settings_store, render_profile=profile)
        self.app.notify("Applique au prochain demarrage.", title="Profil de rendu")

    def _confirm_clear(self, label: str, directory: Path) -> None:
        self.app.push_screen(
            ConfirmScreen(
                title=f"VIDER LE DOSSIER {label.upper()} ?",
                message=f"Supprime definitivement tous les fichiers de {directory}.",
            ),
            lambda confirmed: self._clear_if_confirmed(confirmed, label, directory),
        )

    def _clear_if_confirmed(self, confirmed: bool | None, label: str, directory: Path) -> None:
        if not confirmed:
            return
        result = clear_directory(directory)
        if result.success:
            self.app.notify(f"{result.deleted_count} fichier(s) supprime(s) dans {label}/.")
        else:
            self.app.notify("; ".join(result.errors), severity="error")
