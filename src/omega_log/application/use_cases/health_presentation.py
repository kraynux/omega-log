# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Textes de la Sante des logs (porte d'omega-serv 2.6.0 le 2026-11-07, application/logs/health_presentation.py ;
adapte : logs de la Bibliotheque seulement, sauvegardes d'omega-log, sauvegardes planifiees).

Tout part de la forme DONNEES du rapport (`report_to_dict`, aussi l'export JSON) : l'ecran, l'export TXT et
l'export HTML en tirent leurs phrases, traduites a l'appel. Dans une autre langue d'export, le processus
enfant recoit ce dictionnaire (jamais une nouvelle collecte) et produit les memes phrases dans sa langue."""
from __future__ import annotations

from datetime import datetime

from omega_log.domain.logs.health import (
    DiskHealth,
    Finding,
    HealthLevel,
    HealthReport,
    LogHealth,
)
from omega_log.shared.i18n import N_, _

LEVEL_LABELS: dict[str, str] = {
    "ok": N_("OK"), "info": N_("Info"), "warning": N_("Attention"), "problem": N_("Problème"),
}
"""Cle = `HealthLevel.code` (jamais traduite, sert aussi de classe CSS dans l'export HTML)."""



def format_bytes(size: float) -> str:
    for unit, factor in ((_("Go"), 1024 ** 3), (_("Mo"), 1024 ** 2), (_("Ko"), 1024)):
        if size >= factor:
            return f"{size / factor:.1f} {unit}"
    return f"{int(size)} o"


# ---- forme donnees (export JSON) -------------------------------------------

def _iso(moment: datetime | None) -> str | None:
    return None if moment is None else moment.isoformat()


def _finding_dict(finding: Finding) -> dict:
    return {"code": finding.code, "level": finding.level.code, "params": dict(finding.params)}


def _log_dict(log: LogHealth) -> dict:
    facts = log.facts
    return {
        "path": facts.path,
        "origin": facts.origin,
        "level": log.level.code,
        "exists": facts.exists,
        "size_bytes": facts.size if facts.exists else None,
        "modified_at": _iso(facts.modified_at),
        "mode": None if facts.mode is None else f"{facts.mode:o}",
        "first_timestamp": _iso(facts.first_timestamp),
        "last_timestamp": _iso(facts.last_timestamp),
        "detected_source": facts.detected_source,
        "logrotate_covered": facts.logrotate_covered,
        "growth_bytes_per_day": None if log.growth_per_day is None else round(log.growth_per_day),
        "findings": [_finding_dict(finding) for finding in log.findings],
    }


def _disk_dict(disk: DiskHealth) -> dict:
    return {
        "mount_point": disk.facts.mount_point,
        "total_bytes": disk.facts.total,
        "free_bytes": disk.facts.free,
        "used_percent": round(disk.used_percent, 1),
        "growth_bytes_per_day": None if disk.growth_per_day is None else round(disk.growth_per_day),
        "days_to_full": None if disk.days_to_full is None else round(disk.days_to_full, 1),
        "level": disk.level.code,
        "logs": disk.logs,
        "findings": [_finding_dict(finding) for finding in disk.findings],
    }


def report_to_dict(report: HealthReport) -> dict:
    counts = report.counts()
    archives = None
    if report.archives is not None:
        facts = report.archives.facts
        archives = {
            "directory": facts.directory, "count": facts.count, "total_bytes": facts.total_bytes,
            "oldest": _iso(facts.oldest), "newest": _iso(facts.newest), "keep": facts.keep,
            "findings": [_finding_dict(finding) for finding in report.archives.findings],
        }
    return {
        "generated_at": report.generated_at.isoformat(),
        "level": report.level.code,
        "counts": {level.code: counts[level] for level in HealthLevel},
        "logs": [_log_dict(log) for log in report.logs],
        "disks": [_disk_dict(disk) for disk in report.disks],
        "archives": archives,
        "automations": None if report.automations is None else {
            "count": report.automations.count,
            "scheduled": report.automations.scheduled,
            "level": report.automations.level.code,
            "findings": [_finding_dict(finding) for finding in report.automations.findings],
        },
    }


# ---- phrases -----------------------------------------------------------------

def level_label(code: str) -> str:
    return _(LEVEL_LABELS.get(code, code))


def origin_label(_log: dict) -> str:
    return _("Bibliothèque")


def format_age(moment_iso: str | None, now: datetime) -> str:
    if moment_iso is None:
        return "-"
    seconds = max(0.0, (now - datetime.fromisoformat(moment_iso)).total_seconds())
    if seconds < 60:
        return _("à l'instant")
    if seconds < 3600:
        return _("il y a {count} min").format(count=int(seconds // 60))
    if seconds < 86400:
        return _("il y a {count} h").format(count=int(seconds // 3600))
    return _("il y a {count} j").format(count=int(seconds // 86400))


def format_growth(bytes_per_day: float | None) -> str:
    return "-" if bytes_per_day is None else _("{size}/jour").format(size=format_bytes(bytes_per_day))


def finding_text(finding: dict) -> str:
    code, params = finding["code"], finding.get("params", {})
    if code == "broken_link":
        return _("Lien symbolique cassé : la cible n'existe plus.")
    if code == "missing_library":
        return _("Fichier absent : le chemin de la Bibliothèque ne mène plus à rien.")
    if code == "not_regular":
        return _("Ce n'est pas un fichier ordinaire (dossier, tube ou périphérique).")
    if code == "unreadable":
        return _("Illisible par votre compte (droits {mode}) : Statistiques, Voir et Traiter IP et les viewers "
                 "demanderont votre mot de passe sudo.").format(mode=params.get("mode", "?"))
    if code == "world_writable":
        return _("Inscriptible par tout le monde (droits {mode}) : n'importe quel compte peut falsifier ce "
                 "log.").format(mode=params.get("mode", "?"))
    if code == "empty":
        return _("Fichier vide.")
    if code == "silent":
        return _("Aucune écriture depuis {days} j.").format(days=params.get("days", "?"))
    if code == "nul_bytes":
        return _("Octets nuls à la fin du fichier : log abîmé (coupure ou disque plein pendant une écriture).")
    if code == "undated":
        return _("Seules {percent} % des dernières lignes ont une date reconnue : les périodes 24h, 7j, 30j "
                 "et les statistiques seront faussées.").format(percent=params.get("percent", "?"))
    if code == "future_dates":
        return _("Dernière ligne datée du {last}, dans le futur : horloge ou fuseau horaire faux.").format(
            last=params.get("last", "?"))
    if code == "no_logrotate":
        return _("{size} et aucune règle logrotate ne couvre ce fichier : il grossira sans fin.").format(
            size=format_bytes(float(params.get("size", 0))))
    if code == "duplicate":
        return _("Même fichier que {other} (lien ou chemin en double).").format(other=params.get("other", "?"))
    if code == "disk_almost_full":
        return _("Disque rempli à {percent} %.").format(percent=params.get("percent", "?"))
    if code == "disk_full_soon":
        return _("À ce rythme, disque plein dans environ {days} j.").format(days=params.get("days", "?"))
    if code == "no_archives":
        return _("Aucune sauvegarde.")
    if code == "schedule_missing":
        return _("{count} sauvegarde(s) planifiée(s), mais aucune tâche planifiée ne les exécute.").format(
            count=params.get("count", "?"))
    if code == "automation_failing":
        return _("Sauvegarde planifiée de {path} en échec, en retard de {days} j : {error}").format(
            path=params.get("path", "?"), days=params.get("days", "?"), error=params.get("error", "?"))
    if code == "automation_overdue":
        return _("Sauvegarde planifiée de {path} en retard de {days} j : la tâche planifiée ne s'exécute pas "
                 "(machine éteinte la nuit sans systemd, démon cron arrêté ?).").format(
            path=params.get("path", "?"), days=params.get("days", "?"))
    return str(code)


def finding_hint(finding: dict, path: str) -> str | None:
    """Ce que l'utilisateur peut faire (commande ou ecran a ouvrir) ; None si rien a proposer."""
    code = finding["code"]
    if code == "unreadable":
        return _("Ajoutez votre compte au groupe du fichier (ls -l {path}), puis rouvrez votre session.").format(path=path)
    if code == "world_writable":
        return _("Santé des logs → « Corriger les droits » (chmod o-w {path}).").format(path=path)
    if code == "no_logrotate":
        return _("Ajoutez une règle dans /etc/logrotate.d/ (voir man logrotate).")
    if code in ("missing_library", "duplicate"):
        return _("Bibliothèque : retirez ce log ou corrigez son chemin.")
    if code in ("disk_almost_full", "disk_full_soon"):
        return _("Supprimez les vieilles sauvegardes (Rotate → « Supprimer l'archive ») ou videz les gros logs "
                 "(Purger).")
    if code == "silent":
        return _("Vérifiez que le programme qui écrit ce log tourne encore.")
    if code == "future_dates":
        return _("Vérifiez l'heure du serveur : timedatectl")
    if code == "nul_bytes":
        return _("Sauvegardez ce log (Rotate) puis videz-le (Purger) pour repartir d'un fichier propre.")
    if code in ("schedule_missing", "automation_overdue"):
        return _("Rotate → « Sauvegardes planifiées » → « Réinstaller l'exécution ».")
    if code == "automation_failing":
        return _("Un log protégé ne peut pas être sauvegardé la nuit sans mot de passe : sauvegardez-le depuis "
                 "Rotate, ou retirez sa sauvegarde planifiée.")
    return None


def summary_line(data: dict) -> str:
    counts = data["counts"]
    return " · ".join(f"{counts[code]} {level_label(code)}" for code in ("ok", "info", "warning", "problem"))


def log_summary(log: dict) -> str:
    """Le constat le plus grave d'un log, en une phrase (colonne Constat de l'ecran)."""
    if not log["findings"]:
        return _("Aucun problème.")
    order = {"ok": 0, "info": 1, "warning": 2, "problem": 3}
    worst = max(log["findings"], key=lambda finding: order[finding["level"]])
    extra = len(log["findings"]) - 1
    text = finding_text(worst)
    return text if not extra else text + " " + _("(+{count} autre(s))").format(count=extra)


def log_facts_line(log: dict, now: datetime) -> str:
    if not log["exists"]:
        return ""
    parts = [
        _("Taille {size}").format(size=format_bytes(float(log["size_bytes"] or 0))),
        _("dernière écriture {age}").format(age=format_age(log["modified_at"], now)),
        _("croissance {growth}").format(growth=format_growth(log["growth_bytes_per_day"])),
    ]
    if log["mode"]:
        parts.append(_("droits {mode}").format(mode=log["mode"]))
    if log["detected_source"]:
        parts.append(_("format {source}").format(source=log["detected_source"]))
    return " · ".join(parts)


def format_days_to_full(days: float | None) -> str:
    """« environ 12 j » ; au-dela de 10 ans, un nombre de jours n'a plus de sens."""
    if days is None:
        return "-"
    if days > 3650:
        return _("plus de 10 ans")
    return _("environ {days} j").format(days=round(days) if days >= 10 else days)


def disk_line(disk: dict) -> str:
    days = format_days_to_full(disk["days_to_full"])
    return _("{mount} : {free} libres sur {total} ({used} % utilisés) · croissance des logs {growth} · plein "
             "dans {days}").format(
        mount=disk["mount_point"], free=format_bytes(disk["free_bytes"]), total=format_bytes(disk["total_bytes"]),
        used=disk["used_percent"], growth=format_growth(disk["growth_bytes_per_day"]), days=days)


def automations_line(automations: dict) -> str:
    if not automations["count"]:
        return _("Aucune sauvegarde planifiée.")
    state = {True: _("tâche planifiée installée"), False: _("aucune tâche planifiée"),
             None: _("tâche planifiée non vérifiée")}[automations["scheduled"]]
    return _("{count} sauvegarde(s) planifiée(s) · {state}").format(count=automations["count"], state=state)


def archives_line(archives: dict) -> str:
    if not archives["count"]:
        return _("{directory} : aucune sauvegarde.").format(directory=archives["directory"])
    oldest = (archives["oldest"] or "")[:10]
    return _("{directory} : {count} sauvegarde(s), {size}, la plus ancienne du {oldest}.").format(
        directory=archives["directory"], count=archives["count"], size=format_bytes(archives["total_bytes"]),
        oldest=oldest)


# ---- export TXT ----------------------------------------------------------------

def render_text(data: dict) -> str:
    now = datetime.fromisoformat(data["generated_at"])
    lines = [
        "OMEGA-LOG — " + _("Santé des logs"),
        _("Généré le {date}").format(date=now.strftime("%Y-%m-%d %H:%M UTC")),
        _("Résumé : {summary}").format(summary=summary_line(data)),
        "",
        "== " + _("LOGS") + " ==",
    ]
    for log in data["logs"]:
        lines.append(f"[{level_label(log['level']).upper()}] {log['path']}  ({origin_label(log)})")
        facts = log_facts_line(log, now)
        if facts:
            lines.append("  " + facts)
        if not log["findings"]:
            lines.append("  - " + _("Aucun problème."))
        for finding in log["findings"]:
            lines.append(f"  - [{level_label(finding['level'])}] {finding_text(finding)}")
            hint = finding_hint(finding, log["path"])
            if hint:
                lines.append(f"    → {hint}")
        lines.append("")
    lines.append("== " + _("DISQUES") + " ==")
    for disk in data["disks"]:
        lines.append(f"[{level_label(disk['level']).upper()}] {disk_line(disk)}")
        for finding in disk["findings"]:
            lines.append(f"  - [{level_label(finding['level'])}] {finding_text(finding)}")
            hint = finding_hint(finding, disk["mount_point"])
            if hint:
                lines.append(f"    → {hint}")
    if data["archives"] is not None:
        lines += ["", "== " + _("SAUVEGARDES") + " ==", archives_line(data["archives"])]
    automations = data.get("automations")
    if automations is not None:
        lines += ["", "== " + _("SAUVEGARDES PLANIFIÉES") + " ==",
                  f"[{level_label(automations['level']).upper()}] {automations_line(automations)}"]
        for finding in automations["findings"]:
            lines.append(f"  - [{level_label(finding['level'])}] {finding_text(finding)}")
            hint = finding_hint(finding, "")
            if hint:
                lines.append(f"    → {hint}")
    return "\n".join(lines) + "\n"


# ---- export HTML -----------------------------------------------------------------

def html_arguments(data: dict) -> dict:
    """Arguments de `export_log_health_html` : phrases deja traduites, le modele ne fait que les placer."""
    now = datetime.fromisoformat(data["generated_at"])

    def findings(items: list[dict], path: str) -> list[dict]:
        return [{"level": finding["level"], "level_label": level_label(finding["level"]), "text": finding_text(finding),
                 "hint": finding_hint(finding, path)} for finding in items]

    return {
        "generated_at": now.strftime("%Y-%m-%d %H:%M UTC"),
        "level": data["level"],
        "level_label": level_label(data["level"]),
        "counts": [{"level": code, "label": level_label(code), "count": data["counts"][code]}
                   for code in ("ok", "info", "warning", "problem")],
        "logs": [{"path": log["path"], "origin": origin_label(log), "level": log["level"],
                  "level_label": level_label(log["level"]), "facts": log_facts_line(log, now),
                  "findings": findings(log["findings"], log["path"])} for log in data["logs"]],
        "disks": [{"line": disk_line(disk), "level": disk["level"], "level_label": level_label(disk["level"]),
                   "findings": findings(disk["findings"], disk["mount_point"])} for disk in data["disks"]],
        "archives": None if data["archives"] is None else archives_line(data["archives"]),
        "automations": None if data.get("automations") is None else {
            "line": automations_line(data["automations"]), "level": data["automations"]["level"],
            "level_label": level_label(data["automations"]["level"]),
            "findings": findings(data["automations"]["findings"], ""),
        },
    }
