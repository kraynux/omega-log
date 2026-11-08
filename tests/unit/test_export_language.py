# Copyright (c) 2026 kraynux - Licence MIT
"""Langue des exports (lot 9 du portage, meme mecanisme que la suite omega) : l'aide et les rapports
HTML s'ecrivent dans la langue des exports, quelle que soit celle de l'interface."""
from __future__ import annotations

from omega_log.infrastructure.exporters.html_exporter import (
    export_help_html,
    export_log_archives_html,
)
from omega_log.interfaces.tui.screens.help_screen import help_export_content
from omega_log.shared.i18n import LANGUAGE, translating_as


def _help_html() -> str:
    shortcut_tables, sections = help_export_content()
    return export_help_html(shortcut_tables, sections, "1.5.0")


def test_help_follows_the_export_language() -> None:
    with translating_as(LANGUAGE.load_state("en")):
        html = _help_html()
    assert '<html lang="en" dir="ltr">' in html
    assert "Démarrage rapide" not in html and "Bibliothèque" not in html


def test_exports_stay_in_french_by_default() -> None:
    html = _help_html()
    assert '<html lang="fr" dir="ltr">' in html
    assert "Démarrage rapide" in html
    assert "Archives de logs" in export_log_archives_html([])


def test_arabic_report_is_right_to_left() -> None:
    with translating_as(LANGUAGE.load_state("ar")):
        assert 'dir="rtl"' in export_log_archives_html([])
