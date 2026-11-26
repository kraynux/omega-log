# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""omega-log.sh ancre var/ sur le dossier de l'application, quel que soit le repertoire courant.

Constate sur hpc-109 (2026-11-26) : `log` lance depuis / voulait ecrire /var/app.log (PermissionError). Le test
lance le vrai script avec un faux venv qui affiche seulement OMEGA_LOG_VAR_DIR."""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "omega-log.sh"


def _fake_install(tmp_path: Path) -> Path:
    app = tmp_path / "app"
    bin_dir = app / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    shutil.copy(LAUNCHER, app / "omega-log.sh")
    (bin_dir / "activate").write_text(f'PATH="{bin_dir}:$PATH"\n', encoding="utf-8")
    for name, body in (("python", "exit 0"), ("omega-log", 'printf "%s" "$OMEGA_LOG_VAR_DIR"')):
        script = bin_dir / name
        script.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return app


def _run(app: Path, cwd: str, env_extra: dict[str, str] | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if k != "OMEGA_LOG_VAR_DIR"}
    env.update(env_extra or {})
    result = subprocess.run(
        ["bash", str(app / "omega-log.sh")], cwd=cwd, env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.splitlines()[-1]


def test_var_dans_le_dossier_de_l_application_meme_lance_depuis_la_racine(tmp_path: Path) -> None:
    app = _fake_install(tmp_path)
    assert _run(app, "/") == str(app / "var")
    assert _run(app, str(tmp_path)) == str(app / "var")


def test_omega_log_var_dir_deja_defini_reste_prioritaire(tmp_path: Path) -> None:
    app = _fake_install(tmp_path)
    assert _run(app, "/", {"OMEGA_LOG_VAR_DIR": "/srv/ailleurs"}) == "/srv/ailleurs"
