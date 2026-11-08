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
from markupsafe import Markup, escape
from omega_lib.theme.policies import DEFAULT_EXPORT_THEME

from omega_log.shared.i18n import TRANSLATOR, _

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)
# Langue des exports (meme mecanisme que la suite omega) : texte des gabarits traduit par `_` dans la
# langue active (celle des exports sous translating_as) ; lang= et dir= du document suivent.
_env.globals.update(_=_, html_lang=TRANSLATOR.html_lang, html_dir=TRANSLATOR.html_dir)


def _rich_markup(text: str) -> Markup:
    """Texte de l'aide (balises Rich [b]...[/b]) vers HTML : tout est echappe d'abord, seules les
    balises de gras deviennent <strong>."""
    return Markup(str(escape(text)).replace("[b]", "<strong>").replace("[/b]", "</strong>"))


_env.filters["rich_markup"] = _rich_markup


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
    period_label: str,
    report: dict,
    volume: str,
    theme_name: str = DEFAULT_EXPORT_THEME,
) -> str:
    """Rapport de statistiques (2026-11-06, presentation du rapport periodique d'omega-fire) : `report` =
    `dataclasses.asdict(StatsReport)`, ce module reste agnostique du modele de domaine."""
    from omega_log.infrastructure.exporters.html_theme_resolver import resolve_export_palette

    template = _env.get_template("access_log_stats_report.html.j2")
    return template.render(
        sources=sources,
        period_label=period_label,
        report=report,
        volume=volume,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        palette=resolve_export_palette(theme_name),
    )


def export_help_html(
    shortcut_tables: Sequence[dict], sections: Sequence[dict], version: str, theme_name: str = DEFAULT_EXPORT_THEME,
) -> str:
    """Aide d'omega-log en HTML (repris du guide d'omega-serv, 2026-11-06). `shortcut_tables` :
    {title, rows: [(touche, description)]} ; `sections` : {title, body} avec balises Rich [b]."""
    from omega_log.infrastructure.exporters.html_theme_resolver import resolve_export_palette

    template = _env.get_template("help_report.html.j2")
    return template.render(
        shortcut_tables=shortcut_tables,
        sections=sections,
        version=version,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        palette=resolve_export_palette(theme_name),
    )


def export_log_health_html(*, theme_name: str = DEFAULT_EXPORT_THEME, **arguments: object) -> str:
    """Sante des logs (portee d'omega-serv 2.6.0, 2026-11-07) : `arguments` =
    `health_presentation.html_arguments(...)`, phrases deja traduites (appel sous translating_as)."""
    from omega_log.infrastructure.exporters.html_theme_resolver import resolve_export_palette

    template = _env.get_template("log_health_report.html.j2")
    return template.render(palette=resolve_export_palette(theme_name), **arguments)
