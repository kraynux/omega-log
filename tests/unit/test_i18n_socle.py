"""Socle i18n (OMEGA-SUITE_PLAN-DETAILLE_I18N.md lot 2) : catalogue de l'outil chaine au catalogue
partage, langue imposee par omega-suite, selecteur « Langue / Language » et redemarrage."""
from __future__ import annotations

import pytest
from omega_lib.i18n.host import clear_host_language, set_host_language
from omega_lib.infrastructure.i18n.tool_language import LANGUAGE_KEY
from textual.app import App, ComposeResult
from textual.widgets import Select, Static

from omega_log.interfaces.tui.language_setting import LanguageSetting
from omega_log.shared.i18n import DOMAIN, LANGUAGE, STATE, _


class _Store:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self.data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self.data)


class _SettingApp(App[None]):
    def __init__(self, store: _Store) -> None:
        super().__init__()
        self.store = store
        self.pending_language: str | None = None

    def compose(self) -> ComposeResult:
        yield LanguageSetting(self.store)


@pytest.fixture(autouse=True)
def _french_after_each_test():
    yield
    clear_host_language()
    LANGUAGE.install(settings_store=None, environ={})


def test_catalogue_of_the_tool() -> None:
    assert DOMAIN == "omega-log"
    assert LANGUAGE.locale_dir.name == "locale"
    assert LANGUAGE.locale_dir.parent.name == "omega_log"
    assert LANGUAGE.env_var == "OMEGA_LOG_LANG"


def test_french_by_default_and_environment_override() -> None:
    LANGUAGE.install(settings_store=_Store(), environ={})
    assert STATE.language.code == "fr" and _("Retour") == "Retour"
    LANGUAGE.install(settings_store=_Store(), environ={"OMEGA_LOG_LANG": "x-test"})
    assert _("Retour") == "⟦Retour⟧"


def test_language_imposed_by_omega_suite_wins() -> None:
    store = _Store()
    store.set(LANGUAGE_KEY, "fr")
    set_host_language("x-test", "omega-suite")
    LANGUAGE.install(settings_store=store, environ={"OMEGA_LOG_LANG": "fr"})
    assert _("Retour") == "⟦Retour⟧"


async def test_selector_saves_the_language_and_asks_for_a_restart() -> None:
    app = _SettingApp(_Store())
    async with app.run_test() as pilot:
        select = app.query_one("#language-select", Select)
        assert select.value == "fr"
        select.value = "en"
        await pilot.pause()
        await pilot.click("#confirm")
        await pilot.pause()
    assert app.pending_language == "en"
    assert app.store.data[LANGUAGE_KEY] == "en"


async def test_inside_omega_suite_the_selector_is_replaced_by_a_note() -> None:
    set_host_language("fr", "omega-suite")
    app = _SettingApp(_Store())
    async with app.run_test():
        assert not app.query("#language-select")
        assert any("omega-suite" in str(widget.render()) for widget in app.query(Static))
