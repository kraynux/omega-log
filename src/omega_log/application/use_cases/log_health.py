# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Collecte de la Sante des logs (porte d'omega-serv 2.6.0 le 2026-11-07, application/logs/log_health.py) :
lit ce qu'il faut de chaque log de la Bibliotheque (stat, debut et fin du fichier, jamais le fichier entier),
le disque qui le porte, les regles logrotate et les sauvegardes d'omega-log, puis laisse les regles de
domain/logs/health.py juger.

Lecture seule. Sudo seulement sur demande (« Analyser avec sudo » : debut et fin des logs illisibles). Seule
correction : un log inscriptible par tout le monde (`chmod o-w`, directement si le fichier vous appartient,
sinon avec sudo apres confirmation - jamais chown, jamais recursif, un seul fichier)."""
from __future__ import annotations

import os
import stat
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from omega_log.domain.logs.health import (
    ArchiveFacts,
    AutomationsHealth,
    DiskFacts,
    HealthReport,
    LogFacts,
    build_health_report,
    covered_by_logrotate,
    parse_logrotate_patterns,
)
from omega_log.domain.logs.parser import detect_log_source, extract_timestamp
from omega_log.infrastructure.privileged.elevation import running_as_root

if TYPE_CHECKING:
    from omega_log.domain.entities.log_file import LogFile
    from omega_log.ports.process_runner_port import ProcessRunnerPort

SAMPLE_BYTES = 64 * 1024
"""Debut et fin du fichier lus pour les dates et le format : quelques millisecondes meme pour un gros log."""
MAX_SAMPLED_LINES = 200
LOGROTATE_SOURCES: tuple[Path, ...] = (Path("/etc/logrotate.conf"), Path("/etc/logrotate.d"))
SAMPLE_TIMEOUT_SECONDS = 15.0
FIX_TIMEOUT_SECONDS = 15.0


def privileged(args: list[str]) -> list[str]:
    return list(args) if running_as_root() else ["sudo", "-n", *args]


def health_paths(library: Iterable[LogFile]) -> list[str]:
    """Logs locaux de la Bibliotheque (une source journald n'a pas de fichier a controler)."""
    paths: list[str] = []
    for log_file in library:
        if log_file.access == "journald":
            continue
        path = os.path.abspath(log_file.path)
        if path not in paths:
            paths.append(path)
    return paths


def _read_samples(path: str, size: int) -> tuple[str, str]:
    """(debut, fin) du fichier, SAMPLE_BYTES octets chacun, decodes."""
    with open(path, "rb") as handle:
        head = handle.read(SAMPLE_BYTES)
        if size > SAMPLE_BYTES:
            handle.seek(max(0, size - SAMPLE_BYTES))
            tail = handle.read(SAMPLE_BYTES)
        else:
            tail = head
    return head.decode("utf-8", errors="replace"), tail.decode("utf-8", errors="replace")


def read_privileged_sample(runner: ProcessRunnerPort, path: str, size: int) -> tuple[str, str] | None:
    """(debut, fin) lus avec `sudo -n head/tail -c` ; None si sudo refuse (authentification expiree)."""
    head = runner.run(privileged(["head", "-c", str(SAMPLE_BYTES), "--", path]), timeout=SAMPLE_TIMEOUT_SECONDS)
    if not head.ok:
        return None
    if size <= SAMPLE_BYTES:
        return head.stdout, head.stdout
    tail = runner.run(privileged(["tail", "-c", str(SAMPLE_BYTES), "--", path]), timeout=SAMPLE_TIMEOUT_SECONDS)
    return (head.stdout, tail.stdout) if tail.ok else None


def _split_samples(head: str, tail: str, size: int) -> tuple[list[str], list[str], bool]:
    """(lignes du debut, lignes de la fin, octets nuls dans la fin). Lignes coupees aux bords ecartees."""
    head_lines, tail_lines = head.splitlines(), tail.splitlines()
    if size > SAMPLE_BYTES:
        head_lines = head_lines[:-1]
        tail_lines = tail_lines[1:]
    return head_lines, tail_lines[-MAX_SAMPLED_LINES:], "\x00" in tail


def _aware(moment: datetime | None) -> datetime | None:
    """L'analyseur d'omega-log rend des heures sans fuseau, lues comme locales partout ailleurs dans omega-log :
    meme lecture ici, pour les comparer a l'heure actuelle (avec fuseau)."""
    if moment is None or moment.tzinfo is not None:
        return moment
    return moment.astimezone()


def _first_timestamp(lines: list[str]) -> datetime | None:
    for line in lines:
        moment = extract_timestamp(line)
        if moment is not None:
            return _aware(moment)
    return None


def _sample_facts(path: str, size: int, runner: ProcessRunnerPort | None = None) -> dict[str, Any]:
    """Dates, format et octets nuls d'apres le debut et la fin du log ; lus avec sudo si `runner`."""
    if runner is not None:
        texts = read_privileged_sample(runner, path, size)
        if texts is None:
            return {}
    else:
        try:
            texts = _read_samples(path, size)
        except OSError:
            return {}
    head, tail, nul_bytes = _split_samples(*texts, size)
    stamps = [extract_timestamp(line) for line in tail if line.strip()]
    dated = [moment for moment in stamps if moment is not None]
    sources = [detect_log_source(line).value for line in tail if line.strip()]
    return {
        "first_timestamp": _first_timestamp(head),
        "last_timestamp": _aware(dated[-1]) if dated else None,
        "sampled_lines": len(stamps),
        "dated_lines": len(dated),
        "nul_bytes": nul_bytes,
        "detected_source": max(set(sources), key=sources.count) if sources else None,
    }


def collect_log_facts(
    path: str, *, logrotate_patterns: list[str], privileged_runner: ProcessRunnerPort | None = None,
) -> LogFacts:
    base = LogFacts(path=path)
    try:
        link = os.lstat(path)
    except OSError:
        return base
    try:
        info = os.stat(path)
    except OSError:
        return replace(base, broken_link=stat.S_ISLNK(link.st_mode))
    if not stat.S_ISREG(info.st_mode):
        return replace(base, exists=True, regular=False, device=info.st_dev)
    readable = os.access(path, os.R_OK)
    facts = replace(
        base,
        exists=True,
        size=info.st_size,
        modified_at=datetime.fromtimestamp(info.st_mtime, tz=timezone.utc),
        mode=stat.S_IMODE(info.st_mode),
        readable=readable,
        world_writable=bool(info.st_mode & stat.S_IWOTH),
        device=info.st_dev,
        logrotate_covered=covered_by_logrotate(path, logrotate_patterns),
    )
    if readable:
        return replace(facts, **_sample_facts(path, info.st_size))
    if privileged_runner is not None:  # illisible par votre compte : constat garde, le reste lu avec sudo
        return replace(facts, **_sample_facts(path, info.st_size, privileged_runner))
    return facts


def read_logrotate_patterns(sources: tuple[Path, ...] = LOGROTATE_SOURCES) -> list[str] | None:
    """Motifs de tous les fichiers logrotate lisibles ; None si logrotate n'est pas installe."""
    files: list[Path] = []
    for source in sources:
        if source.is_dir():
            try:
                files.extend(sorted(entry for entry in source.iterdir() if entry.is_file()))
            except OSError:
                continue
        elif source.is_file():
            files.append(source)
    if not files:
        return None
    patterns: list[str] = []
    for file in files:
        try:
            patterns.extend(parse_logrotate_patterns(file.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return patterns


def _mount_point(path: str) -> str:
    current = os.path.abspath(path)
    while not os.path.ismount(current):
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current


def collect_disk_facts(logs: list[LogFacts]) -> list[DiskFacts]:
    disks: dict[int, DiskFacts] = {}
    for facts in logs:
        if facts.device is None or facts.device in disks:
            continue
        try:
            usage = os.statvfs(facts.path)
        except OSError:
            continue
        disks[facts.device] = DiskFacts(
            device=facts.device, mount_point=_mount_point(facts.path),
            total=usage.f_blocks * usage.f_frsize, free=usage.f_bavail * usage.f_frsize,
        )
    return list(disks.values())


def archive_facts(directory: Path, backups: list[tuple[int, datetime]]) -> ArchiveFacts:
    """`backups` = (taille, date) de chaque sauvegarde d'omega-log (PersistencePort.list_backups)."""
    moments = [moment for _size, moment in backups]
    return ArchiveFacts(
        directory=str(directory),
        count=len(backups),
        total_bytes=sum(size for size, _moment in backups),
        oldest=min(moments, default=None),
        newest=max(moments, default=None),
    )


def collect_log_health(
    paths: list[str], *, archives: ArchiveFacts | None, automations: AutomationsHealth | None = None,
    now: datetime | None = None, logrotate_patterns: list[str] | None = None,
    privileged_runner: ProcessRunnerPort | None = None,
) -> HealthReport:
    patterns = read_logrotate_patterns() if logrotate_patterns is None else logrotate_patterns
    facts: list[LogFacts] = []
    real_paths: dict[str, str] = {}
    for path in paths:
        item = collect_log_facts(path, logrotate_patterns=patterns or [], privileged_runner=privileged_runner)
        if patterns is None and item.logrotate_covered is False:
            item = replace(item, logrotate_covered=None)  # logrotate absent : rien a reprocher au log
        real = os.path.realpath(path)
        if item.exists and real in real_paths:
            item = replace(item, duplicate_of=real_paths[real])
        elif item.exists:
            real_paths[real] = path
        facts.append(item)
    return build_health_report(facts, collect_disk_facts(facts), archives, now or datetime.now(timezone.utc),
                               automations)


def fix_world_writable(path: str) -> None:
    """Retire l'ecriture pour tout le monde sur un log qui vous appartient. OSError remonte."""
    mode = stat.S_IMODE(os.stat(path).st_mode)
    os.chmod(path, mode & ~stat.S_IWOTH)


def owns(path: str) -> bool:
    try:
        return os.stat(path).st_uid == os.getuid()
    except OSError:
        return False


def sudo_fix_command(path: str) -> list[str]:
    return ["chmod", "o-w", "--", path]


def shown_command(command: list[str]) -> str:
    """Telle qu'affichee avant confirmation (sans le `-n` technique)."""
    prefix = "" if running_as_root() else "sudo "
    return prefix + " ".join(part for part in command if part != "--")


def run_sudo_fix(runner: ProcessRunnerPort, command: list[str]) -> str | None:
    """None si la commande passe, sinon son message d'erreur."""
    result = runner.run(privileged(command), timeout=FIX_TIMEOUT_SECONDS)
    if result.ok:
        return None
    return (result.stderr or result.stdout).strip() or str(result.returncode)
