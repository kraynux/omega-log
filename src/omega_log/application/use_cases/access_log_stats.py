# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use case Statistiques (plan_omega_log.md §2/§6) : ADAPTE depuis
omega-serv/log_stats_screen.py (source retenue) — meme principe
(periode 24h/7j/30j, top IPs, repartition horaire), mais generalise a
N'IMPORTE QUEL log de la Bibliotheque via domain/logs/{parser,
analytics}.py (generiques, Phase 2) au lieu du seul access log fixe de
SERV.

`runner` optionnel (AJOUTE 2026-10-03, plan §5.1, elevation sudo
ponctuelle) : transmis a read_entries_for_paths, meme contrat que
_log_reading.py (PermissionRequiredError sans lui)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from omega_log.application.use_cases._log_reading import read_entries_for_paths
from omega_log.domain.logs.analytics import compute_stats
from omega_log.domain.logs.models import LogStats

if TYPE_CHECKING:
    from omega_log.ports.process_runner_port import ProcessRunnerPort


@dataclass
class AccessLogStatsResult:
    sources: list[str]
    period: str | None
    stats: LogStats


def compute_access_log_stats(
    paths: list[str], *, period: str | None = None, top_n: int = 10,
    runner: ProcessRunnerPort | None = None,
) -> AccessLogStatsResult:
    entries = read_entries_for_paths(paths, period=period, runner=runner)
    stats = compute_stats(entries, top_n=top_n)
    return AccessLogStatsResult(sources=paths, period=period, stats=stats)


def hourly_stats_for_export(stats: LogStats) -> list[dict]:
    """Forme attendue par le template access_log_stats_report.html.j2 —
    pourcentage pre-calcule pour le graphique en barres (Jinja2 ne fait
    pas de calcul de ce type proprement)."""
    max_count = max((h.count for h in stats.hourly_stats), default=0) or 1
    return [
        {"hour": h.hour, "count": h.count, "percent": round((h.count / max_count) * 100, 1)}
        for h in stats.hourly_stats
    ]
