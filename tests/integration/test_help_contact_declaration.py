# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Aide reprise d'omega-serv (2026-11-06) : export HTML, Contact et support, Se declarer. Jamais de
vrai envoi ni de vrai navigateur : faux expediteur, faux ouvreur."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from textual.widgets import Button, Select, Static

from omega_log.app.bootstrap import bootstrap
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.contact_support_screen import ContactSupportScreen
from omega_log.interfaces.tui.screens.declaration_screen import DeclarationScreen
from omega_log.interfaces.tui.screens.help_screen import HelpScreen
from omega_log.interfaces.tui.screens.home import HomeScreen
from omega_log.ports.declaration_port import SendOutcome


class _Sender:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, payload: dict) -> SendOutcome:
        self.sent.append(payload)
        return SendOutcome(True)


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    built.declaration_sender = _Sender()
    built.open_url = lambda url: False
    yield built
    built.close()


async def _help(app: OmegaLogApp, pilot, container) -> HelpScreen:
    app.push_screen(HomeScreen(container=container))
    await pilot.pause()
    screen = HelpScreen(container=container)
    app.push_screen(screen)
    await pilot.pause()
    return screen


@pytest.mark.asyncio
async def test_help_exports_html_with_whole_content(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _help(app, pilot, container)
        screen.query_one("#export-html", Button).press()
        await pilot.pause()
    exports = list(container.default_exports_dir.glob("aide-*.html"))
    assert len(exports) == 1
    html = exports[0].read_text(encoding="utf-8")
    for text in ("Raccourcis clavier", "Bibliothèque", "Sources distantes (SSH)", "Concepts et glossaire",
                 "<strong>Ajouter les logs connus d&#39;Omega-Serv</strong>"):
        assert text in html
    assert "[b]" not in html


@pytest.mark.asyncio
async def test_contact_then_declare_once(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        help_screen = await _help(app, pilot, container)
        help_screen.query_one("#contact-support", Button).press()
        await pilot.pause()
        contact = app.screen
        assert isinstance(contact, ContactSupportScreen)
        assert "non déclaré" in str(contact.query_one("#declaration-state", Static).render())
        contact.query_one("#declare", Button).press()
        await pilot.pause()
        declaration = app.screen
        assert isinstance(declaration, DeclarationScreen)
        declaration.query_one("#declaration-continent", Select).value = "EU"
        await pilot.pause()
        assert '"logiciel": "omega-log"' in str(declaration.query_one("#declaration-preview", Static).render())
        declaration.query_one("#send", Button).press()
        await pilot.pause()
        await asyncio.sleep(0.3)
        await pilot.pause()
        assert app.screen is contact
        assert "déclaré le" in str(contact.query_one("#declaration-state", Static).render())
        assert not contact.query_one("#withdraw", Button).disabled
    sent = container.declaration_sender.sent
    assert len(sent) == 1 and sent[0]["logiciel"] == "omega-log" and sent[0]["envoi"] == "unique"
    assert sent[0]["continent"] == "EU"
