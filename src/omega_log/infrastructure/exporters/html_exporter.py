# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Export HTML (Jinja2 + theme d'export choisi) — ADAPTE depuis
omega-serv (infrastructure/exporters/html_exporter.py) : conserve
`export_log_archives_html()` (mecanisme reel, deja en production), retire
`export_capabilities_html()`/`export_guide_html()` (sans objet pour LOG).

Ajoute `export_access_log_stats_html()` (NEUF, plan_omega_log.md §2/§6) :
applique ce MEME mecanisme (jinja2, 5 themes omega_lib.theme.policies) a
l'ecran Statistiques — assemblage de deux pieces existantes jamais faites
ensemble dans la suite, pas du code neuf au sens du moteur d'export
lui-meme."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from omega_lib.theme.policies import DEFAULT_EXPORT_THEME

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def export_log_archives_html(archives: Sequence[dict], theme_name: str = DEFAULT_EXPORT_THEME) -> str:
    from omega_log.infrastructure.exporters.html_theme_resolver import resolve_export_palette

    template = _env.get_template("log_archives_report.html.j2")
    palette = resolve_export_palette(theme_name)
    return template.render(
        archives=archives,
        generated_at=datetime.now(timezone.utc).isoformat(),
        palette=palette,
    )


def export_access_log_stats_html(
    *,
    sources: Sequence[str],
    period: str | None,
    total_entries: int,
    unique_ips: int,
    error_rate: float,
    top_ips: Sequence[dict],
    hourly_stats: Sequence[dict],
    theme_name: str = DEFAULT_EXPORT_THEME,
) -> str:
    from omega_log.infrastructure.exporters.html_theme_resolver import resolve_export_palette

    template = _env.get_template("access_log_stats_report.html.j2")
    palette = resolve_export_palette(theme_name)
    return template.render(
        sources=sources,
        period=period,
        total_entries=total_entries,
        unique_ips=unique_ips,
        error_rate=error_rate,
        top_ips=top_ips,
        hourly_stats=hourly_stats,
        generated_at=datetime.now(timezone.utc).isoformat(),
        palette=palette,
    )
