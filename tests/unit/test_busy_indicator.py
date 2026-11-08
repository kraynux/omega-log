# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Taille et nombre de lignes estime de la selection, affiches avant un calcul (2026-11-06)."""
from pathlib import Path

from omega_log.interfaces.tui.widgets.busy_indicator import describe_selection


def test_small_file_is_counted_exactly(tmp_path: Path) -> None:
    log = tmp_path / "a.log"
    log.write_text("ligne\n" * 120)
    assert describe_selection([str(log)]) == "1 log(s) · 720 o · environ 120 lignes"


def test_big_file_estimate_from_spread_samples(tmp_path: Path) -> None:
    """Longueurs de lignes variees, comme un vrai access.log (user-agents de 20 a 400 caracteres)."""
    import random

    rng = random.Random(7)
    log = tmp_path / "b.log"
    log.write_text("".join("z" * rng.randint(20, 400) + "\n" for _ in range(40_000)))
    text = describe_selection([str(log)])
    estimated = int(text.split("environ ")[1].split(" lignes")[0].replace(" ", ""))
    assert abs(estimated - 40_000) / 40_000 < 0.1


def test_missing_file_and_empty_selection(tmp_path: Path) -> None:
    assert describe_selection([]) == ""
    assert describe_selection([str(tmp_path / "absent.log")]) == "1 log(s) · 0 o"
