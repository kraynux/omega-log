# Copyright (c) 2026 kraynux - Licence MIT
"""Traduction de l'interface (OMEGA-SUITE_PLAN-DETAILLE_I18N.md §5) - seul point d'acces aux
phrases traduites pour tout le code d'omega-log (meme interface que omega_fire/shared/i18n.py).

    from omega_log.shared.i18n import _, N_, ngettext

- `_("Texte")` : phrase traduite dans la langue active (francais par defaut : texte tel quel).
- `ngettext("{n} element", "{n} elements", n)` : pluriels (3 formes en russe).
- `N_("Texte")` : marque une constante pour l'extraction, traduite plus tard avec `_()`.

Catalogues : locale/<langue>/LC_MESSAGES/omega-log.mo pour les phrases propres a l'outil,
chaine au catalogue partage omega-lib (phrases communes a tous les outils omega, Q3).
La langue est installee UNE fois, avant d'importer l'interface (__main__.py) ; dans
omega-suite, c'est la suite qui l'impose (omega_lib.i18n.host). Changer de langue redemarre
l'interface (os.execv). La ligne de commande n'installe jamais de langue (R3) : elle reste en
francais."""
from __future__ import annotations

from pathlib import Path

from omega_lib.i18n.service import mark
from omega_lib.i18n.translator import ToolTranslator
from omega_lib.infrastructure.i18n.tool_language import ToolLanguage

DOMAIN = "omega-log"
TRANSLATOR = ToolTranslator(DOMAIN)
STATE = TRANSLATOR.state
LANGUAGE = ToolLanguage(
    TRANSLATOR, Path(__file__).resolve().parents[1] / "locale", "OMEGA_LOG_LANG"
)

N_ = mark
lazy = TRANSLATOR.lazy
retranslate = TRANSLATOR.retranslate
translating_as = TRANSLATOR.translating_as
log_text = TRANSLATOR.log_text
"""Ligne de journal relayee a l'ecran (R2) : francaise dans le fichier, retraduite a l'ecran."""
log_message = TRANSLATOR.log_message


def _(message: str) -> str:
    return TRANSLATOR.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    return TRANSLATOR.ngettext(singular, plural, n)
