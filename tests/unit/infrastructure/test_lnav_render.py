# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Teste les fonctions pures de infrastructure/lnav/render.py — jamais
render_lnav_live() lui-meme (boucle bloquante exigeant un vrai terminal
interactif, testable uniquement a la main, meme limite que omega-serv/
omega-fire). Couverture ajoutee le 2026-10-04 (absente jusqu'ici malgre
le docstring du module qui la promettait) en meme temps que le portage
des correctifs Ctrl-C/Ctrl-Q deja valides chez omega-serv — tests repris
de son tests/unit/test_lnav_live_renderer.py, adaptes au style pytest
(fonctions) deja utilise partout ailleurs dans ce projet."""
from __future__ import annotations

import base64

import pyte
from omega_lib.theme.policies import TUI_THEMES

from omega_log.infrastructure.lnav.render import (
    _KITTY_CTRL_C_RE,
    _KITTY_CTRL_Q_RE,
    _row_is_highlighted,
    classify_hue,
    compute_baseline_bg,
    extract_current_line_text,
    move_to,
    osc52_copy,
    pad_line,
    render_row_colored,
)

_BG_HIGHLIGHT = "\x1b[48;2;43;43;43m"  # #2b2b2b, meme teinte observee chez un vrai lnav 0.14
_BG_RESET = "\x1b[0m"
_BREADCRUMB_LINE = "LOG ▼  ：2026-10-04T14:00:02.000000 ：access_log"


def _feed(screen: pyte.Screen, lines: list[str]) -> None:
    stream = pyte.Stream(screen)
    for line in lines:
        stream.feed(line + "\r\n")


def test_pad_line_pads_short_text() -> None:
    assert pad_line("hi", 5) == "hi   "


def test_pad_line_truncates_long_text() -> None:
    assert pad_line("hello world", 5) == "hello"


def test_move_to_default_column() -> None:
    assert move_to(3) == "\x1b[3;1H"


def test_move_to_explicit_column() -> None:
    assert move_to(3, 7) == "\x1b[3;7H"


def test_classify_hue_named_colors() -> None:
    assert classify_hue("red") == "red"
    assert classify_hue("default") == "neutral"


def test_classify_hue_hex_red() -> None:
    assert classify_hue("ff0000") == "red"


def test_classify_hue_hex_green() -> None:
    assert classify_hue("00ff00") == "green"


def test_classify_hue_low_saturation_is_neutral() -> None:
    assert classify_hue("808080") == "neutral"


def test_classify_hue_invalid_hex_is_neutral() -> None:
    assert classify_hue("zzzzzz") == "neutral"


def test_compute_baseline_bg_no_content_returns_default() -> None:
    screen = pyte.Screen(20, 5)
    assert compute_baseline_bg(screen, 20) == "default"


def test_compute_baseline_bg_most_frequent_background_wins() -> None:
    screen = pyte.Screen(20, 3)
    stream = pyte.Stream(screen)
    stream.feed("\x1b[42mgreen bg text\x1b[0m\r\n")
    stream.feed("normal text\r\n")
    assert isinstance(compute_baseline_bg(screen, 20), str)


def test_render_row_colored_renders_plain_text_without_crashing() -> None:
    screen = pyte.Screen(20, 3)
    stream = pyte.Stream(screen)
    stream.feed("hello world\r\n")
    palette = next(iter(TUI_THEMES.values())).palette
    rendered = render_row_colored(screen, 0, 20, palette)
    assert "hello world" in rendered


def test_render_row_colored_renders_colored_text_without_crashing() -> None:
    screen = pyte.Screen(20, 3)
    stream = pyte.Stream(screen)
    stream.feed("\x1b[31merror\x1b[0m normal\r\n")
    palette = next(iter(TUI_THEMES.values())).palette
    rendered = render_row_colored(screen, 0, 20, palette)
    assert "error" in rendered
    assert "normal" in rendered


def test_osc52_copy_encodes_text_as_base64_sequence() -> None:
    result = osc52_copy("hello")
    assert result.startswith(b"\x1b]52;c;")
    assert result.endswith(b"\x07")
    encoded = result[len(b"\x1b]52;c;"):-1]
    assert base64.b64decode(encoded) == b"hello"


def test_kitty_ctrl_c_sequence_converted_to_etx() -> None:
    assert _KITTY_CTRL_C_RE.sub(b"\x03", b"\x1b[99;5u") == b"\x03"


def test_kitty_ctrl_q_sequence_converted_to_dc1() -> None:
    assert _KITTY_CTRL_Q_RE.sub(b"\x11", b"\x1b[113;5u") == b"\x11"


def test_kitty_regex_leaves_classic_byte_unchanged() -> None:
    assert _KITTY_CTRL_C_RE.sub(b"\x03", b"\x03") == b"\x03"


def test_kitty_regex_does_not_match_unrelated_sequence() -> None:
    assert _KITTY_CTRL_C_RE.sub(b"\x03", b"\x1b[97;5u") == b"\x1b[97;5u"
    assert _KITTY_CTRL_Q_RE.sub(b"\x11", b"\x1b[97;5u") == b"\x1b[97;5u"


# ---------------------------------------------------------------------
# _row_is_highlighted / extract_current_line_text — regression du bug
# reel deja trouve et corrige chez omega-serv (2026-09-13), porte ici le
# 2026-10-04 (retour utilisateur : Ctrl-C "marque mais ne copie pas").
# ---------------------------------------------------------------------

def test_row_is_highlighted_false_for_a_single_stray_cell() -> None:
    """La colonne d'ascenseur que lnav dessine sur CHAQUE ligne de
    contenu (une seule cellule en bord de ligne, fond distinct) ne doit
    jamais a elle seule faire matcher une ligne comme focalisee."""
    screen = pyte.Screen(20, 3)
    stream = pyte.Stream(screen)
    stream.feed("normal text" + " " * 7 + _BG_HIGHLIGHT + "x" + _BG_RESET + "\r\n")
    assert not _row_is_highlighted(screen, 0)


def test_row_is_highlighted_true_when_majority_of_row_is_highlighted() -> None:
    screen = pyte.Screen(20, 3)
    stream = pyte.Stream(screen)
    stream.feed(_BG_HIGHLIGHT + "highlighted content" + _BG_RESET + "\r\n")
    assert _row_is_highlighted(screen, 0)


def test_row_is_highlighted_false_for_a_blank_row() -> None:
    screen = pyte.Screen(20, 3)
    assert not _row_is_highlighted(screen, 0)


def test_extract_current_line_text_returns_none_without_a_breadcrumb() -> None:
    screen = pyte.Screen(80, 5)
    _feed(screen, ["no breadcrumb here", "127.0.0.1 something"])
    assert extract_current_line_text(screen) is None


def test_extract_current_line_text_single_matching_line_is_returned() -> None:
    screen = pyte.Screen(80, 5)
    _feed(screen, [_BREADCRUMB_LINE, "127.0.0.1 GET /only-one HTTP/1.1 14:00:02"])
    result = extract_current_line_text(screen)
    assert result is not None
    assert "/only-one" in result


def test_extract_current_line_text_duplicate_timestamps_prefer_highlighted_line() -> None:
    screen = pyte.Screen(80, 5)
    stream = pyte.Stream(screen)
    stream.feed(_BREADCRUMB_LINE + "\r\n")
    stream.feed("127.0.0.1 GET /a.html 14:00:02\r\n")
    stream.feed(_BG_HIGHLIGHT + "127.0.0.1 GET /b.html 14:00:02" + _BG_RESET + "\r\n")
    stream.feed("127.0.0.1 GET /c.html 14:00:02\r\n")
    result = extract_current_line_text(screen)
    assert result is not None
    assert "/b.html" in result


def test_extract_current_line_text_duplicate_timestamps_without_highlight_fall_back_to_first() -> None:
    screen = pyte.Screen(80, 5)
    _feed(
        screen,
        [
            _BREADCRUMB_LINE,
            "127.0.0.1 GET /a.html 14:00:02",
            "127.0.0.1 GET /b.html 14:00:02",
        ],
    )
    result = extract_current_line_text(screen)
    assert result is not None
    assert "/a.html" in result
