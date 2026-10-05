# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Gestion du pty et du sous-processus lnav.

Porte VERBATIM depuis omega-fire (infrastructure/lnav/pty_session.py) —
aucune dependance omega_fire, uniquement la stdlib (fcntl/os/pty/signal/
struct/subprocess/termios), donc rien a adapter. Toute cette logique a
ete validee empiriquement pendant un spike chez omega-fire (negociation
de capacites terminal, decoupage de sequences d'echappement) — voir
plan_omega_log.md §2 : exactement le genre de code a porter tel quel,
pas a re-deriver.

Encapsule tout ce qui touche au processus externe lnav : ouverture d'un
pty, lancement, redimensionnement, arret propre, et le petit repondeur
de capacites terminal sans lequel lnav (notcurses) reste bloque
indefiniment au demarrage.

Conforme a la charte d'architecture de la suite :
- Seul point du sous-systeme lnav qui appelle subprocess/pty/fcntl/termios
- Ne modifie jamais lnav lui-meme
- Aucune couleur ni logique de rendu ici (voir infrastructure/lnav/render.py)
"""
from __future__ import annotations

import fcntl
import os
import pty
import re
import signal
import struct
import subprocess
import termios
import time
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent
LNAV_BINARY = "lnav"

_OSC52_RE = re.compile(rb"\x1b\]52;[^\x07\x1b]*(?:\x07|\x1b\\)")


def spawn_lnav(rows: int, cols: int, log_paths: list[Path], *, use_sudo: bool = False) -> tuple[int, int]:
    """Ouvre un pty et y lance lnav sur les fichiers donnes (fusionnes
    automatiquement par lnav si plusieurs). Retourne (master_fd, pid).

    `use_sudo` AJOUTE le 2026-10-03 (plan §5.1) : au moins un des
    fichiers donnes requiert une elevation (ex. /var/log/audit). Le mot
    de passe sudo sera alors demande A L'INTERIEUR du pty lui-meme (lnav
    n'a pas encore ecrit son interface a cet instant) — relaye au vrai
    terminal par le mecanisme de rendu existant (render.py), aucune
    adaptation necessaire ici. `-E` : preserve l'environnement (TERM
    notamment, requis par lnav/notcurses pour negocier ses capacites)."""
    if not log_paths:
        raise ValueError("au moins un fichier de log est requis")

    master_fd, slave_fd = pty.openpty()

    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

    cmd = [LNAV_BINARY, "-I", str(CONFIG_DIR), *[str(p) for p in log_paths]]
    if use_sudo:
        cmd = ["sudo", "-E", *cmd]
    proc = subprocess.Popen(
        cmd,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        preexec_fn=os.setsid,  # noqa: PLW1509 - requis pour killpg() dans kill_lnav()/resize_pty()
        close_fds=True,
    )
    os.close(slave_fd)
    return master_fd, proc.pid


def resize_pty(master_fd: int, pid: int, rows: int, cols: int) -> None:
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
    try:
        os.killpg(os.getpgid(pid), signal.SIGWINCH)
    except ProcessLookupError:
        pass


def wait_dead(pid: int, timeout: float) -> bool:
    """Attend au plus `timeout` secondes que le process se termine (non
    bloquant, jamais indefiniment). Retourne True s'il est mort."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            done_pid, _ = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            return True
        if done_pid == pid:
            return True
        time.sleep(0.1)
    return False


def kill_lnav(pid: int) -> None:
    """Arret propre avec filet de securite : SIGTERM, on attend un peu,
    SIGKILL si toujours vivant -- jamais de blocage indefini."""
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError:
        return
    if wait_dead(pid, 3.0):
        return
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    except ProcessLookupError:
        return
    wait_dead(pid, 2.0)


def relay_osc52(data: bytes, out_fd: int) -> int:
    """Relaie vers le vrai terminal toute sequence OSC 52 (presse-papier)
    presente dans `data` -- lnav ecrit sa reponse dans notre pty, jamais
    renvoye tel quel vers le vrai terminal sinon. Retourne le nombre de
    sequences relayees."""
    matches = _OSC52_RE.findall(data)
    for seq in matches:
        os.write(out_fd, seq)
    return len(matches)


class TerminalResponder:
    """Repond au minimum vital aux sondes de capacites terminal que lnav
    envoie au demarrage (notcurses). Sans ca, lnav reste bloque
    indefiniment a attendre des reponses qu'un pty muet ne renverra
    jamais -- DSR (position du curseur) et DA1 (device attributes)
    suffisent a debloquer le rendu.

    Repond a CHAQUE occurrence, pas seulement la premiere : lnav peut
    re-sonder (ex. apres un redimensionnement)."""

    def __init__(self, master_fd: int, rows: int, cols: int) -> None:
        self._fd = master_fd
        self._rows = rows
        self._cols = cols
        self._buffer = b""

    def update_size(self, rows: int, cols: int) -> None:
        self._rows, self._cols = rows, cols

    def feed(self, data: bytes) -> None:
        self._buffer += data
        while b"\x1b[6n" in self._buffer:
            os.write(self._fd, f"\x1b[{self._rows};1R".encode())
            self._buffer = self._buffer.replace(b"\x1b[6n", b"", 1)
        while b"\x1b[c" in self._buffer:
            os.write(self._fd, b"\x1b[?1;2c")
            self._buffer = self._buffer.replace(b"\x1b[c", b"", 1)
        if len(self._buffer) > 8192:
            self._buffer = self._buffer[-256:]
