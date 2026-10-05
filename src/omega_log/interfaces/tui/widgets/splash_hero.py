# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Composition ASCII de l'ecran de demarrage — reproduction de la
maquette fournie dans ascii.txt (racine du projet : toits/piliers
"||||", liste verticale des sources de logs, base arrondie "~___~",
boite de titre, bandeau OMEGA-LOG, tagline). Corrige une simplification
excessive d'une version precedente qui avait remplace toute
l'illustration par deux lignes de texte plates — perte de fidelite
signalee par l'utilisateur (2026-10-03).

Chaque bloc est CENTRE INDIVIDUELLEMENT sur une largeur de reference
commune (`_WIDTH`, celle du plus large — le grand cadre OMEGA-LOG) via
`_centered()`, plutot que de reprendre l'indentation brute de
ascii.txt telle quelle : cette derniere n'est elle-meme pas
rigoureusement centree d'un bloc a l'autre (croquis dessine a la main),
ce qui donnait un rendu visuellement decentre une fois affiche — retour
utilisateur (2026-10-04) sur une premiere version qui preservait cette
indentation d'origine.

Regle de securite OBLIGATOIRE pour tout markup ajoute dans ce fichier,
constatee par capture d'ecran reelle (2026-10-03, pas une supposition) :
Textual deplace les espaces places en DEBUT ou FIN d'un span
`[couleur]...[/]` vers la PROCHAINE frontiere de style au lieu de les
laisser sur place, decalant tout ce qui suit (une ligne entiere peut
se retrouver visuellement coupee en deux). Les espaces INTERNES a un
span (entre deux mots d'un meme span) ne sont, eux, jamais affectes.
Toute fonction ci-dessous passe donc par `_span()`, qui extrait
automatiquement les espaces de bord d'un segment AVANT de le colorer et
les replace en texte brut hors du span — jamais de span construit a la
main avec un espace comme premier ou dernier caractere.

Regles de couleur reprises d'ascii.txt + precedent omega-fire (meme
widget, meme principe de cadre/texte distincts) :
- "container" (cadres/boites/piliers/toits/base) : $foreground (clair) —
  s'applique a la boite de titre, la barre de version, les deux toits
  de pilier, les onze lignes de pilier inferieures (le texte des
  sources de logs et "MULTI-VIEWVERS" qu'elles contiennent n'est pas
  mis en valeur separement, ascii.txt ne le demande pas).
- boite de titre "LINUX LOG-VIEWVER" : cadre ($foreground) distinct du
  texte ($accent), meme patron que omega-fire/splash_hero.py::_lfs_line
  ("LINUX FIREWALL SUITE"). La barre de version, elle, reste ENTIEREMENT
  $foreground chez omega-fire (groupee avec les "cadres" dans sa propre
  regle ecrite) — meme choix repris ici pour "▒V1.00▒", pas de accent.
- bandeau OMEGA-LOG (grand cadre) : inchange, deja correct (ligne 1 et 3
  $accent, ligne 2 $foreground, cadre "│" toujours $foreground) — meme
  regle que widgets/home_wordmark.py.
- tagline finale : "|" vifs ($accent), mots normaux ($foreground) —
  inchange, deja correct.

Caracteres de ligne des piliers (toit + corps) ALIGNES sur
ascii.txt (2026-10-04, retour utilisateur) : ascii.txt N'EST PAS LU au
demarrage (reproduction manuelle en constantes Python ci-dessous, comme
documente plus haut) — un simple edit de ce fichier seul, SANS reporter
le changement ici, n'a donc aucun effet sur l'appli. L'utilisateur y a
remplace les barres ASCII brutes "||||"/"="/"-" par des caracteres de
ligne Unicode compatibles Rich ("│║║│", "═", "─") pour eviter des
coupures visuelles — reporte ici caractere pour caractere (longueurs
inchangees, le centrage via `_centered()` reste donc valide)."""
from __future__ import annotations

from textual.widgets import Static

_WIDTH = 69
"""Largeur de reference commune a tout le logo — celle du plus large
element (le grand cadre OMEGA-LOG, voir _WORDMARK_BOX_TOP) : chaque
autre bloc, plus etroit, est centre sur cette meme largeur via
`_centered()` plutot que de garder sa propre indentation d'origine."""

_TITLE_BOX_TOP = "┌─────────────────────┐"
_TITLE_BOX_MID = "│  LINUX LOG-VIEWVER  │"
_TITLE_BOX_BOTTOM = "└─────────────────────┘"
_VERSION_BAR = "▒V1.00▒"

_PILLAR_ROOF = (
    "____________________   ____________________",
    "./││                  \\ /                  ││\\.",
    "│║║│                   │                   │║║│",
)

_WORDMARK_BOX_TOP = "┌" + "─" * 67 + "┐"
_WORDMARK_LINES = (
    "┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐   ┌╦      ┌╦═══╦┐ ┌╦═══╦┐",
    "│║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═ │║      │║   ║│ │║  ═╦┐",
    "└╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘   └╩═══╩┘ └╩═══╩┘ └╩═══╩┘",
)
_WORDMARK_BOX_BOTTOM = "└" + "─" * 67 + "┘"

_PILLAR_BODY = (
    "│║║│    Acces          │                   │║║│",
    "│║║│    Error          │                   │║║│",
    "│║║│    Alerts         │                   │║║│",
    "│║║│    Waf            │  MULTI-VIEWVERS   │║║│",
    "│║║│    Audit          │                   │║║│",
    "│║║│    ...            │                   │║║│",
    "│║║│                   │                   │║║│",
    "│║║│                   │                   │║║│",
    "│║║│__________________ │ __________________│║║│",
    "│║/═══════════════════\\│/═══════════════════\\║│",
    "└────────────────────~___~────────────────────┘",
)

_TAGLINE = "LOG | SERVER | VIEW | ROTATE | EXPORT"


def _centered(content: str) -> str:
    return content.center(_WIDTH)


def _span(text: str, color: str) -> str:
    """Colore `text`, SAUF ses espaces de debut/fin (laisses en texte
    brut, hors du span) — voir la note de securite en tete de fichier.
    Seule maniere autorisee ici de produire un span colore."""
    stripped = text.strip(" ")
    if not stripped:
        return text
    lead = text[: len(text) - len(text.lstrip(" "))]
    trail = text[len(text.rstrip(" ")):]
    return f"{lead}[{color}]{stripped}[/]{trail}"


def _title_text_line(line: str) -> str:
    """Boite de titre, ligne avec texte : cadre "│" en $foreground, le
    texte "LINUX LOG-VIEWVER" en $accent — 3 segments colores separement
    via `_span()` (chacun protege independamment de ses propres espaces
    de bord)."""
    prefix, sep1, tail = line.partition("│")
    inner, sep2, suffix = tail.rpartition("│")
    return f"{_span(prefix + sep1, '$foreground')}{_span(inner, '$accent')}{_span(sep2 + suffix, '$foreground')}"


def _wordmark_box_line(line: str) -> str:
    """Boite encadrant le bandeau OMEGA-LOG : bordure + contenu en
    $foreground, le bandeau lui-meme garde ses propres couleurs (vif/
    clair/vif) appliquees separement dans _build_markup()."""
    return _span(line, "$foreground")


def _wordmark_row(line: str, color: str) -> str:
    return f"{_span('│', '$foreground')} {_span(line, color)} {_span('│', '$foreground')}"


def _tagline(line: str) -> str:
    parts = line.split("|")
    colored = [_span(part, "$foreground") for part in parts]
    return _span("|", "$accent").join(colored)


def _build_markup() -> str:
    lines: list[str] = []

    lines.append(_span(_centered(_TITLE_BOX_TOP), "$foreground"))
    lines.append(_title_text_line(_centered(_TITLE_BOX_MID)))
    lines.append(_span(_centered(_TITLE_BOX_BOTTOM), "$foreground"))
    lines.append(_span(_centered(_VERSION_BAR), "$foreground"))

    for raw in _PILLAR_ROOF:
        lines.append(_span(_centered(raw), "$foreground"))

    lines.append(_wordmark_box_line(_WORDMARK_BOX_TOP))
    wordmark_colors = ("$accent", "$foreground", "$accent")
    for raw, color in zip(_WORDMARK_LINES, wordmark_colors, strict=True):
        lines.append(_wordmark_row(raw, color))
    lines.append(_wordmark_box_line(_WORDMARK_BOX_BOTTOM))

    for raw in _PILLAR_BODY:
        lines.append(_span(_centered(raw), "$foreground"))

    lines.append("")
    lines.append(_tagline(_centered(_TAGLINE)))
    return "\n".join(lines)


_MARKUP = _build_markup()


class SplashHero(Static):
    """Bloc decoratif de l'ecran de demarrage (screens/splash.py)."""

    def __init__(self) -> None:
        super().__init__(_MARKUP, classes="omega-splash-hero")
