# Copyright (c) 2026 kraynux - Licence MIT
"""Reglage « Langue / Language » (OMEGA-SUITE_PLAN-DETAILLE_I18N.md lot 2, repris d'omega-fire) :
le selecteur de l'ecran Reglages, et les messages de langue affiches au demarrage.

Le libelle « Langue / Language » n'est jamais traduit : il reste reperable quelle que soit la
langue affichee. Chaque langue s'affiche dans SA langue, « Français » toujours en tete.
Choisir une langue enregistre le reglage puis redemarre l'interface (os.execv, dans
__main__.py, apres la fermeture de Textual)."""
from __future__ import annotations

import os

from omega_lib.i18n.host import host_name
from omega_lib.i18n.models import LanguageStatus
from omega_lib.i18n.policies import PSEUDO_LANGUAGE_CODE, language_for
from omega_lib.infrastructure.i18n.tool_language import LANGUAGE_LABEL, UnknownLanguageError
from omega_lib.ports.settings_store import SettingsStore
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Select, Static

from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.shared.i18n import LANGUAGE, STATE, _


def language_options() -> list[tuple[str, str]]:
    options: list[tuple[str, str]] = []
    for language in LANGUAGE.available():
        label = language.native_name
        if language.status is LanguageStatus.TESTING and language.code != PSEUDO_LANGUAGE_CODE:
            label = _("{label} ({value})").format(label=label, value=_("en test"))
        options.append((label, language.code))
    return options


SAME_AS_INTERFACE = "interface"
"""Valeur du selecteur « Langue des exports » pour « comme l'interface » (reglage vide)."""


def export_language_options() -> list[tuple[str, str]]:
    return [(_("Comme l'interface"), SAME_AS_INTERFACE), *language_options()]


class LanguageSetting(Vertical):
    """A placer dans l'ecran Reglages. Un outil affiche dans omega-suite prend la langue choisie
    dans les reglages de la suite : son selecteur est remplace par une phrase qui le dit."""

    DEFAULT_CSS = """
    LanguageSetting {
        height: auto;
    }
    """

    def __init__(self, settings_store: SettingsStore) -> None:
        super().__init__()
        self._settings_store = settings_store

    def compose(self) -> ComposeResult:
        yield Static(LANGUAGE_LABEL, classes="omega-subtitle")
        host = host_name()
        if host is not None:
            yield Static(
                _("Langue choisie dans les réglages de {host}.").format(host=host),
                classes="omega-hint",
            )
            yield Static(_("Langue des exports"), classes="omega-subtitle")
            yield Static(
                _("Langue des exports choisie dans les réglages de {host}.").format(host=host),
                classes="omega-hint",
            )
            return
        yield Select(
            language_options(), value=STATE.language.code, allow_blank=False, id="language-select"
        )
        yield Static(_("Langue des exports"), classes="omega-subtitle")
        yield Select(
            export_language_options(),
            value=LANGUAGE.export_language_setting(self._settings_store) or SAME_AS_INTERFACE,
            allow_blank=False,
            id="export-language-select",
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        if event.select.id == "export-language-select":
            # Ouverture de l'ecran (2026-11-07, retour utilisateur : notification comme si on avait choisi) : la
            # valeur initiale emet aussi Changed - seulement un vrai changement de reglage est applique et annonce.
            current = LANGUAGE.export_language_setting(self._settings_store) or SAME_AS_INTERFACE
            if str(event.value) != current:
                self._change_export_language(str(event.value))
            return
        code = str(event.value)
        if code == STATE.language.code:
            return
        names = {language.code: language.native_name for language in LANGUAGE.available()}
        self.app.push_screen(
            ConfirmScreen(
                title=_("REDÉMARRER L'INTERFACE ?"),
                message=_(
                    "La langue « {name} » sera appliquée après le redémarrage de l'interface."
                ).format(name=names.get(code, code)),
            ),
            lambda confirmed: self._restart_for_language(code, confirmed),
        )

    def _change_export_language(self, value: str) -> None:
        """Effet immediat : chaque export relit le reglage (aucun redemarrage)."""
        code = "" if value == SAME_AS_INTERFACE else value
        try:
            LANGUAGE.select_export_language(self._settings_store, code)
        except (UnknownLanguageError, OSError) as exc:
            self.app.notify(str(exc), title=_("Langue des exports"), severity="error")
            return
        names = {language.code: language.native_name for language in LANGUAGE.available()}
        self.app.notify(
            names.get(code, code) if code else _("Comme l'interface"), title=_("Langue des exports")
        )

    def _restore(self) -> None:
        self.query_one("#language-select", Select).value = STATE.language.code

    def _restart_for_language(self, code: str, confirmed: bool | None) -> None:
        if not confirmed:
            self._restore()
            return
        try:
            LANGUAGE.select(self._settings_store, code)
        except (UnknownLanguageError, OSError) as exc:
            self.app.notify(str(exc), title=LANGUAGE_LABEL, severity="error")
            self._restore()
            return
        request_language_restart(self.app, code)


def request_language_restart(app: App[None], code: str) -> None:
    """Ferme l'interface ; __main__.py relance le processus dans la nouvelle langue."""
    setattr(app, "pending_language", code)  # noqa: B010 - attribut lu par __main__.py
    app.exit()


def notify_language_at_startup(app: App[None]) -> None:
    """Une fois au demarrage : langue appliquee apres un redemarrage, langue indisponible,
    ou langue que ce terminal ne sait pas afficher."""
    if os.environ.pop(LANGUAGE.changed_env_var, None) is not None:
        app.notify(_("{LANGUAGE_LABEL} : {native_name}").format(LANGUAGE_LABEL=LANGUAGE_LABEL, native_name=STATE.language.native_name), title=LANGUAGE_LABEL)
    if STATE.fell_back_from is not None:
        app.notify(
            _("Langue « {code} » indisponible : interface en français.").format(
                code=STATE.fell_back_from),
            title=LANGUAGE_LABEL, severity="warning", timeout=10,
        )
    if LANGUAGE.console_fallback_from is not None:
        app.notify(
            _(
                "Ce terminal (console texte) ne peut pas afficher la langue « {name} » : "
                "interface en anglais pour cette session. Le réglage est conservé - la langue "
                "revient dans un terminal graphique."
            ).format(name=language_for(LANGUAGE.console_fallback_from).native_name),
            title=LANGUAGE_LABEL, severity="warning", timeout=15,
        )
