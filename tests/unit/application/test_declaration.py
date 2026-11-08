# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Declaration anonyme simplifiee (une seule fois, champ logiciel) - 2026-11-06."""
from pathlib import Path

import pytest

from omega_log.application.use_cases.declaration import declare, preview_payload, withdraw
from omega_log.domain.declaration.model import Declaration, build_payload, declaration_errors
from omega_log.infrastructure.declaration.json_declaration_store import JsonDeclarationStore
from omega_log.ports.declaration_port import SendOutcome

KEY = "0123456789abcdef0123456789abcdef"


class _Sender:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok
        self.sent: list[dict] = []

    def send(self, payload: dict) -> SendOutcome:
        self.sent.append(payload)
        return SendOutcome(self.ok, "" if self.ok else "unreachable")


def test_payload_names_the_software_and_is_always_once() -> None:
    assert build_payload(Declaration(KEY, "EU", "FR"), "1.5.0") == {
        "cle": KEY, "logiciel": "omega-log", "version": "1.5.0", "envoi": "unique", "continent": "EU", "pays": "FR",
    }
    assert "pays" not in build_payload(Declaration(KEY), "1.5.0")


def test_invalid_fields_are_reported() -> None:
    assert declaration_errors(Declaration("x", "ZZ", "QQ")) == ["cle", "continent", "pays"]


def test_declare_saves_only_on_success_and_keeps_key(tmp_path: Path) -> None:
    store = JsonDeclarationStore(tmp_path / "declaration.json")
    assert not declare(store, _Sender(ok=False), "1.5.0", key_factory=lambda: KEY).ok
    assert store.load() is None
    sender = _Sender()
    assert declare(store, sender, "1.5.0", "EU", key_factory=lambda: KEY).ok
    assert store.load().declaration == Declaration(KEY, "EU", "")
    declare(store, sender, "1.5.0", country="FR", key_factory=lambda: "f" * 32)
    assert sender.sent[-1]["cle"] == KEY            # une modification garde la meme cle
    assert preview_payload(store, "1.5.0", "", "")["cle"] == KEY


def test_withdraw_deletes_even_when_unreachable(tmp_path: Path) -> None:
    store = JsonDeclarationStore(tmp_path / "declaration.json")
    declare(store, _Sender(), "1.5.0", key_factory=lambda: KEY)
    sender = _Sender(ok=False)
    result = withdraw(store, sender)
    assert result.was_declared and not result.reception_reached
    assert sender.sent == [{"cle": KEY, "retrait": True}]
    assert store.load() is None


def test_bad_values_never_sent(tmp_path: Path) -> None:
    sender = _Sender()
    with pytest.raises(ValueError):
        declare(JsonDeclarationStore(tmp_path / "d.json"), sender, "1.5.0", "XX", key_factory=lambda: KEY)
    assert sender.sent == []
