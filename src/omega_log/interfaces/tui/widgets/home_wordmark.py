# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Bandeau texte OMEGA-LOG affiche en haut de screens/home.py — lettres
reprises telles que fournies dans ascii.txt (racine du projet), deja
alignees sur la police lettree partagee par toute la suite omega- (le
bloc OMEGA initial est caractere pour caractere identique a celui de
omega-check/omega-fire/omega-serv/... ; les lettres L/O/G correspondent
exactement aux glyphes deja utilises ailleurs dans la suite — "L" reprise
d'omega-fold, "O"/"G" de la police OMEGA commune).

Couleur par jetons de theme Rich/Textual directement dans le markup
(reactif au changement de theme, pas des couleurs hex figees) — ligne 1 et
3 en $accent (vif), ligne 2 en $foreground (clair), consigne explicite
d'ascii.txt. Meme technique que widgets/splash_hero.py et que le reste
de la suite (home_wordmark.py de omega-check/omega-fire/...)."""
from __future__ import annotations

from textual.widgets import Static

_WORDMARK_LINES = (
    "┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐   ┌╦      ┌╦═══╦┐ ┌╦═══╦┐",
    "│║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═ │║      │║   ║│ │║  ═╦┐",
    "└╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘   └╩═══╩┘ └╩═══╩┘ └╩═══╩┘",
)
"""OMEGA-LOG en un seul bandeau de lettres — caracteres non modifies par
rapport a ascii.txt."""

_MARKUP = "\n".join((
    f"[$accent]{_WORDMARK_LINES[0]}[/]",
    f"[$foreground]{_WORDMARK_LINES[1]}[/]",
    f"[$accent]{_WORDMARK_LINES[2]}[/]",
))


class HomeWordmark(Static):
    """Bandeau decoratif centre en haut de screens/home.py."""

    def __init__(self) -> None:
        super().__init__(_MARKUP, classes="omega-home-wordmark")
