# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Rendu live de lnav dans un pty, avec header/footer OMEGA-LOG persistants.

ADAPTE depuis omega-fire/interfaces/cli/renderers/lnav_live.py, PAS porte
verbatim : la version source lit un registre de themes Rich/CLI
COMPLETEMENT SEPARE (`interfaces/cli/themes/registry.py::theme_registry`)
du theme Textual de l'application (`omega_lib.theme`) — une deuxieme
palette parallele, jamais utilisee par rien d'autre dans omega-fire.
Plutot que de porter ce sous-systeme entier pour un seul ecran, cette
version lit directement `omega_lib.theme.policies.TUI_THEMES` (deja le
catalogue reellement utilise par le reste de l'app) — meme reactivite
au theme courant, sans dependance supplementaire.

Cycle de theme [t] RETABLI (2026-10-04, retour utilisateur : "le
changement de theme (raccourci t) ne fonctionne pas dans lnav" — une
version precedente l'avait delibrement omis, jugeant "change de theme
en dehors de lnav (Options)" suffisant ; le retour utilisateur contredit
ce choix, la coherence avec le reste de l'app — ou `t` cycle PARTOUT
ailleurs — l'emporte). Meme mecanisme que omega-fire (interception de la
touche `t` avant relais a lnav, cycle + `full_redraw()`), mais sur
`TUI_THEMES` plutot que le `theme_registry` CLI de la source — voir
`render_lnav_live()` : retourne le nom du theme actif a la fermeture,
que l'appelant (screens/lnav_screen.py) applique et persiste sur
`self.app.theme` apres la reprise, exactement comme
`app.py::action_cycle_theme` pour rester coherent partout.

Fiabilite Ctrl-C/Ctrl-Q RENFORCEE (2026-10-04, retour utilisateur :
"le Ctrl+C fonctionne pour marquer mais ne copie pas (probleme deja
rencontre sur omega-serv et fire)") : portage du correctif deja trouve
et valide chez omega-serv, absent ici jusqu'ici — un terminal capable du
protocole clavier Kitty (que Textual negocie pour son propre usage)
envoie Ctrl-C/Ctrl-Q sous une sequence etendue (`\x1b[99;5u`/
`\x1b[113;5u`) plutot que les octets classiques `\x03`/`\x11` ; sans
conversion, `if b"\x03" in key` ne matchait jamais, Ctrl-C etait relayee
brute a lnav (qui, lui, l'interprete comme une touche quelconque — d'ou
"ca marque mais ne copie jamais", lnav executant SA propre action sur
l'octet recu, jamais la notre). `\x1b[<u` ecrit au demarrage depile
l'amelioration clavier active herite de Textual sur le VRAI terminal,
AVANT meme d'y lire quoi que ce soit. La copie OSC 52 elle-meme reste,
comme chez SERV/FIRE, dependante du support reel de l'emulateur de
terminal cote utilisateur — aucune des deux suites n'a de solution pour
un terminal qui n'implemente pas OSC 52 du tout, limite connue,
documentee, pas un bug corrigible cote notre code.

NE PEUT PAS ETRE TESTE HEADLESS : exige un vrai terminal interactif
(tty reel pour stdin/stdout, `App.suspend()` cote appelant) — aucun
pilote Textual ne peut simuler ca. Verifie uniquement par inspection et
par les fonctions pures isolees ci-dessous (classify_hue,
compute_baseline_bg, render_row_colored, extract_current_line_text),
testables sur un pyte.Screen construit en memoire."""
from __future__ import annotations

import base64
import os
import re
import select
import shutil
import signal
import sys
import termios
import time
import tty
from pathlib import Path

import pyte
from omega_lib.theme.policies import TUI_THEMES, Palette
from rich.style import Style

from omega_log.infrastructure.lnav.pty_session import (
    TerminalResponder,
    kill_lnav,
    relay_osc52,
    resize_pty,
    spawn_lnav,
)

HEADER_ROWS = 1
FOOTER_ROWS = 3

CSI = "\x1b["
ALT_SCREEN_ON = CSI + "?1049h"
ALT_SCREEN_OFF = CSI + "?1049l"
HIDE_CURSOR = CSI + "?25l"
SHOW_CURSOR = CSI + "?25h"
CLEAR_SCREEN = CSI + "2J"

MENU_LABEL = "Viewer 3 (lnav) — fusion multi-logs"

MAX_DRAIN_SECONDS = 0.02

_KITTY_CTRL_C_RE = re.compile(rb"\x1b\[99;5u")
_KITTY_CTRL_Q_RE = re.compile(rb"\x1b\[113;5u")
"""Protocole clavier Kitty (sequences CSI u) : certains terminaux
envoient Ctrl-C/Ctrl-Q sous cette forme etendue plutot que les octets
classiques `\x03`/`\x11` — converties en entree de boucle pour que les
interceptions ci-dessous (marquage+copie, fermeture) matchent dans les
deux cas. Correctif deja valide chez omega-serv (retour utilisateur
2026-09-13), porte ici le 2026-10-04."""

_NAMED_HUES = {
    "red": "red", "green": "green", "yellow": "yellow", "blue": "blue",
    "magenta": "magenta", "cyan": "cyan", "white": "neutral", "black": "neutral",
    "default": "neutral",
}


def move_to(row: int, col: int = 1) -> str:
    return f"{CSI}{row};{col}H"


def pad_line(text: str, width: int) -> str:
    return text[:width].ljust(width)


def classify_hue(fg: str) -> str:
    """Classe une couleur pyte (nom ou hex 6 caracteres) dans une famille
    de teinte grossiere, pour la reassocier ensuite a une couleur de la
    palette active. Fonction pure, testable isolement."""
    if fg in _NAMED_HUES:
        return _NAMED_HUES[fg]
    if len(fg) != 6:
        return "neutral"
    try:
        r, g, b = int(fg[0:2], 16), int(fg[2:4], 16), int(fg[4:6], 16)
    except ValueError:
        return "neutral"
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 24:
        return "neutral"
    if mx == r and g >= b:
        return "orange" if g > 100 else "red"
    if mx == r:
        return "magenta"
    if mx == g:
        return "yellow" if r > 140 else "green"
    return "cyan" if g > r else "blue"


def hue_color(hue: str, palette: Palette) -> str:
    mapping = {
        "red": palette.error,
        "orange": palette.warning,
        "yellow": palette.warning,
        "green": palette.success,
        "cyan": palette.secondary,
        "blue": palette.accent,
        "magenta": palette.accent,
        "neutral": palette.foreground,
    }
    return mapping.get(hue, palette.foreground)


def chrome_bar_style(palette: Palette) -> Style:
    """Style pour les barres internes de lnav (breadcrumb, statut) —
    fond explicite (accent) + texte clair sur ce fond, pas un simple
    `reverse` (signale trop agressif a l'usage chez omega-fire)."""
    return Style(color=palette.background, bgcolor=palette.accent, bold=True)


def compute_baseline_bg(screen: pyte.Screen, cols: int) -> str:
    """Devine le fond "normal" du contenu de lnav (pas nos barres a nous,
    pas les barres internes lnav), en prenant le fond le plus frequent
    parmi les cellules non vides. Fonction pure, testable isolement."""
    counts: dict[str, int] = {}
    for y in range(len(screen.display)):
        row = screen.buffer[y]
        for col in range(cols):
            ch = row.get(col)
            if ch is None or not ch.data or ch.data == " ":
                continue
            counts[ch.bg] = counts.get(ch.bg, 0) + 1
    if not counts:
        return "default"
    return max(counts, key=counts.get)


def render_row_colored(screen: pyte.Screen, y: int, cols: int, palette: Palette, baseline_bg: str = "default") -> str:
    """Construit une ligne ANSI coloree a partir de la palette active, en
    regroupant les colonnes consecutives qui partagent le meme style en
    un seul segment. Fonction pure, testable isolement."""
    buffer_row = screen.buffer[y]
    default = screen.default_char
    segments: list[tuple[str, str]] = []
    current_text: list[str] = []
    current_key: str | None = None

    for col in range(cols):
        ch = buffer_row.get(col, default)
        highlighted = ch.reverse or (ch.bg != "default" and ch.bg != baseline_bg)
        key = f"{classify_hue(ch.fg)}|{highlighted}"
        if key != current_key:
            if current_text:
                segments.append(("".join(current_text), current_key))
            current_text = []
            current_key = key
        current_text.append(ch.data if ch.data else " ")
    if current_text:
        segments.append(("".join(current_text), current_key))

    out = []
    for text, key in segments:
        hue, highlighted_s = key.split("|")
        style = chrome_bar_style(palette) if highlighted_s == "True" else Style(color=hue_color(hue, palette))
        out.append(style.render(text))
    return "".join(out)


_BREADCRUMB_ISO_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2})")


def _row_is_highlighted(screen: pyte.Screen, row: int) -> bool:
    """La ligne reellement focalisee par lnav est surlignee sur (quasi)
    toute sa largeur — jamais un simple "au moins une cellule non
    'default'", qui matcherait a tort la colonne d'ascenseur que lnav
    dessine (fond distinct) sur CHAQUE ligne de contenu, pas seulement
    la focalisee. Seuil a la majorite des caracteres non-espace pour ne
    compter que le VRAI surlignage pleine ligne. Porte depuis omega-serv
    (meme bug reel deja trouve et corrige la-bas, 2026-09-13)."""
    buffer_row = screen.buffer.get(row)
    if not buffer_row:
        return False
    non_space = [char for char in buffer_row.values() if char.data.strip()]
    if not non_space:
        return False
    highlighted = sum(1 for char in non_space if char.bg != "default")
    return highlighted > len(non_space) / 2


def extract_current_line_text(screen: pyte.Screen) -> str | None:
    """Retrouve le texte brut de la ligne actuellement focalisee par lnav
    (breadcrumb ISO timestamp vs ligne de contenu portant le meme
    horodatage). Fonction pure, testable isolement — voir
    infrastructure/lnav/pty_session.py pour le pourquoi (xclip bloquant).

    Departage les candidats par la couleur de fond (lnav surligne la
    ligne focalisee) quand PLUSIEURS lignes partagent la meme seconde
    (rafale de requetes, tres courant dans un log d'acces reel) —
    conserve le comportement existant (premier candidat) quand aucun
    n'est surligne, pour ne jamais regresser le cas a seule ligne deja
    fonctionnel. Porte depuis omega-serv (meme bug reel deja trouve et
    corrige la-bas, 2026-09-13)."""
    lines = screen.display
    breadcrumb_idx = None
    hms = None
    for i, line in enumerate(lines):
        m = _BREADCRUMB_ISO_TS_RE.search(line)
        if m and "：" in line:
            breadcrumb_idx = i
            hms = m.group(1)
            break
    if hms is None:
        return None
    candidates = [i for i, line in enumerate(lines) if i != breadcrumb_idx and hms in line]
    if not candidates:
        return None
    chosen = next((i for i in candidates if _row_is_highlighted(screen, i)), candidates[0])
    return lines[chosen].strip().strip("│").strip()


def osc52_copy(text: str) -> bytes:
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"\x1b]52;c;{b64}\x07".encode()


def render_lnav_live(log_paths: list[Path], theme_name: str, *, use_sudo: bool = False) -> str:
    """Encapsule lnav sur `log_paths` (fusionnes automatiquement par lnav
    si plusieurs) dans le terminal courant, avec header/footer OMEGA-LOG
    persistants. Bloquant jusqu'a Ctrl-Q ou fermeture de lnav.

    Doit etre appele depuis un vrai terminal interactif (stdin/stdout un
    tty), typiquement via `App.suspend()` cote appelant — voir
    screens/lnav_screen.py. `use_sudo` : voir pty_session.py::spawn_lnav.

    `theme_name` : theme actif de l'app au moment de l'appel (cycle
    possible pendant la session via [t], voir plus bas) — retourne le
    nom EFFECTIVEMENT actif a la fermeture, que l'appelant applique et
    persiste sur `self.app.theme`."""

    def _resolve_palette(name: str) -> Palette:
        theme = TUI_THEMES.get(name) or next(iter(TUI_THEMES.values()))
        return theme.palette

    palette = _resolve_palette(theme_name)
    theme_names = list(TUI_THEMES.keys())

    out_fd = sys.stdout.fileno()
    os.write(out_fd, b"\x1b[<u")  # depile toute amelioration clavier Kitty heritee de Textual
    term_cols, term_rows = shutil.get_terminal_size()
    inner_rows = max(term_rows - HEADER_ROWS - FOOTER_ROWS, 5)

    master_fd, pid = spawn_lnav(inner_rows, term_cols, log_paths, use_sudo=use_sudo)
    screen = pyte.Screen(term_cols, inner_rows)
    stream = pyte.Stream(screen)
    stream.use_utf8 = False
    responder = TerminalResponder(master_fd, inner_rows, term_cols)

    baseline_bg = "default"

    stdin_fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(stdin_fd)
    tty.setraw(stdin_fd)

    def draw_chrome(cols: int, rows: int) -> None:
        title_style = Style(color=palette.accent, bold=True)
        muted_style = Style(color=palette.foreground, dim=True)
        link_style = Style(color=palette.secondary)
        border_style = Style(color=palette.foreground, dim=True)

        header_plain = f"OMEGA-LOG  |  {MENU_LABEL}"
        header_line = (
            title_style.render("OMEGA-LOG")
            + muted_style.render(f"  |  {MENU_LABEL}")
            + muted_style.render(" " * max(cols - len(header_plain), 0))
        )

        sep_line = border_style.render("─" * cols)

        shortcuts_plain = (
            "lnav  |  [up/down] Naviguer  |  [left/right] Defiler  |  [g/G] Debut/Fin  |  "
            f"[Ctrl-C] Marquer+Copier  |  [t] Theme: {theme_name}  |  [Ctrl-Q] Quitter"
        )
        shortcuts_line = (
            muted_style.render("lnav  |  ")
            + link_style.render("[up/down] Naviguer")
            + muted_style.render("  |  ")
            + link_style.render("[left/right] Defiler")
            + muted_style.render("  |  ")
            + link_style.render("[g/G] Debut/Fin")
            + muted_style.render("  |  ")
            + link_style.render("[Ctrl-C] Marquer+Copier")
            + muted_style.render("  |  ")
            + link_style.render(f"[t] Theme: {theme_name}")
            + muted_style.render("  |  ")
            + link_style.render("[Ctrl-Q] Quitter")
            + muted_style.render(" " * max(cols - len(shortcuts_plain), 0))
        )

        names = ", ".join(p.name for p in log_paths)
        status_line = muted_style.render(pad_line(f"Fichiers ({len(log_paths)}) : {names}", cols))

        buf = (
            move_to(1) + header_line
            + move_to(rows - 2) + sep_line
            + move_to(rows - 1) + shortcuts_line
            + move_to(rows) + status_line
        )
        os.write(out_fd, buf.encode())

    def full_redraw(cols: int, rows: int) -> None:
        nonlocal baseline_bg
        baseline_bg = compute_baseline_bg(screen, cols)
        buf = [CLEAR_SCREEN]
        for y in range(len(screen.display)):
            buf.append(move_to(HEADER_ROWS + 1 + y) + render_row_colored(screen, y, cols, palette, baseline_bg))
        os.write(out_fd, "".join(buf).encode())
        draw_chrome(cols, rows)
        screen.dirty.clear()

    def diff_redraw(cols: int) -> int:
        if not screen.dirty:
            return 0
        display = screen.display
        buf = []
        for y in sorted(screen.dirty):
            if 0 <= y < len(display):
                buf.append(move_to(HEADER_ROWS + 1 + y) + render_row_colored(screen, y, cols, palette, baseline_bg))
        n = len(buf)
        os.write(out_fd, "".join(buf).encode())
        screen.dirty.clear()
        return n

    def handle_resize(signum, frame):
        nonlocal term_cols, term_rows, inner_rows
        term_cols, term_rows = shutil.get_terminal_size()
        inner_rows = max(term_rows - HEADER_ROWS - FOOTER_ROWS, 5)
        screen.resize(inner_rows, term_cols)
        resize_pty(master_fd, pid, inner_rows, term_cols)
        responder.update_size(inner_rows, term_cols)
        full_redraw(term_cols, term_rows)

    def cycle_theme() -> None:
        nonlocal theme_name, palette
        idx = theme_names.index(theme_name) if theme_name in theme_names else 0
        theme_name = theme_names[(idx + 1) % len(theme_names)]
        palette = _resolve_palette(theme_name)

    signal.signal(signal.SIGWINCH, handle_resize)

    os.write(out_fd, (ALT_SCREEN_ON + HIDE_CURSOR).encode())
    settle_redraws_remaining = 5

    try:
        while True:
            r, _, _ = select.select([master_fd, stdin_fd], [], [], 0.05)

            if stdin_fd in r:
                key = os.read(stdin_fd, 4096)
                key = _KITTY_CTRL_C_RE.sub(b"\x03", key)
                key = _KITTY_CTRL_Q_RE.sub(b"\x11", key)

                if b"\x11" in key:  # Ctrl-Q : interceptee, jamais transmise a lnav
                    break

                if b"\x03" in key:
                    # Ctrl-C : jamais transmise telle quelle. "c" de lnav
                    # invoque xclip sans fermer son entree -> bloque
                    # indefiniment (constate empiriquement cote omega-fire).
                    os.write(master_fd, b"m")
                    current_line = extract_current_line_text(screen)
                    if current_line:
                        os.write(out_fd, osc52_copy(current_line))
                    key = key.replace(b"\x03", b"")

                if b"t" in key:
                    cycle_theme()
                    full_redraw(term_cols, term_rows)
                    key = key.replace(b"t", b"")

                if key:
                    os.write(master_fd, key)

            if master_fd in r:
                got_data = False
                drain_deadline = time.monotonic() + MAX_DRAIN_SECONDS
                while time.monotonic() < drain_deadline:
                    try:
                        data = os.read(master_fd, 65536)
                    except OSError:
                        data = b""
                    if not data:
                        break
                    got_data = True
                    responder.feed(data)
                    relay_osc52(data, out_fd)
                    stream.feed(data.decode("utf-8", errors="replace"))
                    more, _, _ = select.select([master_fd], [], [], 0.002)
                    if master_fd not in more:
                        break

                if not got_data:
                    break  # pty ferme (lnav a quitte)

                if settle_redraws_remaining > 0:
                    full_redraw(term_cols, term_rows)
                    settle_redraws_remaining -= 1
                else:
                    diff_redraw(term_cols)
    finally:
        os.write(out_fd, (SHOW_CURSOR + ALT_SCREEN_OFF).encode())
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term)
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)
        kill_lnav(pid)
        try:
            os.close(master_fd)
        except OSError:
            pass

    return theme_name
