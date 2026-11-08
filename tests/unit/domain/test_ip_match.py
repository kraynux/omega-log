# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regle commune de correspondance d'une IP (portee d'omega-serv 2.6.0, 2026-11-07)."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.process_ip import count_ip_occurrences, remove_ip_from_file
from omega_log.domain.logs.ip_match import ip_line_pattern, line_contains_ip, normalize_ip


def _matches(ip: str, line: str) -> bool:
    return line_contains_ip(line, ip, ip_line_pattern(ip))


def test_normalize_ip() -> None:
    assert normalize_ip(" 203.0.113.42 ") == "203.0.113.42"
    assert normalize_ip("2A03:2880:F800:0015::") == "2a03:2880:f800:15::"
    assert normalize_ip("1.2.3") is None


def test_ipv4_never_matches_a_longer_address() -> None:
    assert _matches("1.1.1.1", "1.1.1.1 - - x")
    assert not _matches("1.1.1.1", "1.1.1.11 - - x")
    assert not _matches("1.1.1.1", "21.1.1.1 - - x")
    assert _matches("1.1.1.1", "client 1.1.1.1:443 closed")


def test_ipv6_ending_with_double_colon_is_found() -> None:
    """Regression : la limite de mot \\b ne trouvait jamais cette adresse (0 ligne retiree)."""
    assert _matches("2a03:2880:f800:15::", "2a03:2880:f800:15:: host - x")
    assert not _matches("2a03:2880:f800:15::", "2a03:2880:f800:15::1 host - x")


def test_count_and_remove_ipv6_double_colon(tmp_path: Path) -> None:
    log = tmp_path / "access.log"
    log.write_text("2a03:2880:f800:15:: - - x\n1.1.1.1 - - y\n2a03:2880:f800:15:: - - z\n")
    assert count_ip_occurrences(str(log), "2a03:2880:f800:15::") == 2
    result = remove_ip_from_file(str(log), "2a03:2880:f800:15::")
    assert result.success and result.occurrences == 2
    assert log.read_text() == "1.1.1.1 - - y\n"
