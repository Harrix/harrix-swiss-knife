"""Tests for Quick paste snippets seed, sort, parse, and registration."""

# ruff: noqa: RUF001

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.apps.snippets import OnSnippets
from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.apps.snippets.constants import SORT_ADDED, SORT_ALPHA, SORT_USED, ZONE_COLOR, ZONE_SYMBOL
from harrix_swiss_knife.apps.snippets.database_manager import DatabaseManager, SnippetItem
from harrix_swiss_knife.apps.snippets.parse import (
    display_text,
    item_matches_search,
    parse_bulk_lines,
    parse_value_hint_line,
)
from harrix_swiss_knife.apps.snippets.seed import (
    SEED_EMOJIS_BASE,
    SEED_PHRASES,
    build_recover_sql,
    ensure_seed_emojis,
    extract_phrase_emojis,
    seed_emojis,
)
from harrix_swiss_knife.apps.snippets.sort import sort_items
from harrix_swiss_knife.menu_structure import get_menu_structure

_ROOT = Path(__file__).resolve().parents[1]
_RECOVER_SQL = _ROOT / "src" / "harrix_swiss_knife" / "apps" / "snippets" / "recover.sql"
_EXAMPLE_CONFIG = _ROOT / "config" / "config.example.json"


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _item(
    item_id: int,
    value: str,
    *,
    created_at: str = "2026-01-01T00:00:00+00:00",
    last_used_at: str | None = None,
) -> SnippetItem:
    return SnippetItem(
        item_id=item_id,
        zone="phrase",
        value=value,
        hint="",
        created_at=created_at,
        last_used_at=last_used_at,
        sort_index=item_id,
    )


def test_extract_phrase_emojis_includes_commit_prefixes() -> None:
    emojis = extract_phrase_emojis(SEED_PHRASES)
    assert "➕" in emojis
    assert "🐞" in emojis
    assert "📜" in emojis


def test_seed_emojis_merges_phrase_extras_without_duplicates() -> None:
    merged = seed_emojis()
    assert merged.count("🔍") == 1
    assert merged.count("📚") == 1
    for extra in ("➕", "☕", "🚀", "✨", "📜", "🏃", "🍔", "🤖", "🧮", "👃"):
        assert extra in merged
    for base in SEED_EMOJIS_BASE:
        assert base in merged


def test_sort_items_used_puts_unused_last_alphabetically() -> None:
    items = [
        _item(1, "Beta", last_used_at="2026-08-20T10:00:00+00:00"),
        _item(2, "Alpha"),
        _item(3, "Gamma", last_used_at="2026-08-25T10:00:00+00:00"),
        _item(4, "Zed"),
    ]
    ordered = [item.value for item in sort_items(items, SORT_USED, descending=False)]
    assert ordered == ["Gamma", "Beta", "Alpha", "Zed"]
    reversed_used = [item.value for item in sort_items(items, SORT_USED, descending=True)]
    assert reversed_used[:2] == ["Beta", "Gamma"]
    assert reversed_used[2:] == ["Alpha", "Zed"]


def test_sort_items_added_and_alpha() -> None:
    items = [
        _item(1, "Beta", created_at="2026-01-02T00:00:00+00:00"),
        _item(2, "Alpha", created_at="2026-01-03T00:00:00+00:00"),
        _item(3, "Gamma", created_at="2026-01-01T00:00:00+00:00"),
    ]
    assert [item.value for item in sort_items(items, SORT_ADDED, descending=False)] == ["Alpha", "Beta", "Gamma"]
    assert [item.value for item in sort_items(items, SORT_ADDED, descending=True)] == ["Gamma", "Beta", "Alpha"]
    assert [item.value for item in sort_items(items, SORT_ALPHA, descending=False)] == ["Alpha", "Beta", "Gamma"]
    assert [item.value for item in sort_items(items, SORT_ALPHA, descending=True)] == ["Gamma", "Beta", "Alpha"]


def test_item_matches_search_ignores_case_and_layout() -> None:
    assert item_matches_search("🐞 Fix ruff check issues", "", "FIX")
    assert item_matches_search("Quick paste", "", "зфыеу")
    assert item_matches_search("#ffffff", "white color in icons", "white")
    assert not item_matches_search("Add", "", "zzzz")


def test_parse_value_hint_line_and_bulk_lines() -> None:
    assert parse_value_hint_line("— | Век живи — век учись. | Тире") == (
        "—",
        "Век живи — век учись. | Тире",
    )
    assert parse_value_hint_line("#ffffff: white color in icons") == ("#ffffff", "white color in icons")
    assert parse_bulk_lines("➕ Add\n\n🐞 Fix\n", "phrase") == [("➕ Add", ""), ("🐞 Fix", "")]
    assert parse_bulk_lines("© | Знак копирайта\n", ZONE_SYMBOL) == [("©", "Знак копирайта")]
    assert parse_bulk_lines("#de2b26: logo\n", ZONE_COLOR) == [("#de2b26", "logo")]


def test_display_text_adds_hint_brackets() -> None:
    assert display_text("—", "Век живи — век учись. | Тире", ZONE_SYMBOL) == ("— [Век живи — век учись. | Тире]")


def test_recover_sql_matches_builder_and_creates_seed(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    assert _RECOVER_SQL.is_file()
    assert _RECOVER_SQL.read_text(encoding="utf-8") == build_recover_sql()
    db_path = tmp_path / "snippets.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(_RECOVER_SQL))
    manager = DatabaseManager(str(db_path))
    try:
        assert manager.table_exists("items")
        assert manager.table_exists("zone_sort")
        phrases = manager.list_items("phrase")
        emojis = manager.list_items("emoji")
        symbols = manager.list_items("symbol")
        colors = manager.list_items("color")
        assert [item.value for item in phrases] == list(SEED_PHRASES)
        assert [item.value for item in emojis] == seed_emojis()
        assert symbols[0].value == "—"
        assert "Тире" in symbols[0].hint
        assert colors[0].value == "#ffffff"
        assert colors[-1].value == "#66442b"
        assert ensure_seed_emojis(manager) == 0
    finally:
        manager.close()


def test_ensure_seed_emojis_inserts_missing(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    db_path = tmp_path / "snippets.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(_RECOVER_SQL))
    manager = DatabaseManager(str(db_path))
    try:
        first = manager.list_items("emoji")[0]
        assert manager.delete_item(first.item_id)
        assert ensure_seed_emojis(manager) == 1
        assert first.value in {item.value for item in manager.list_items("emoji")}
        assert ensure_seed_emojis(manager) == 0
    finally:
        manager.close()


def test_on_snippets_is_quick_launcher_action() -> None:
    assert OnSnippets.quick_launcher is True
    assert OnSnippets.title == "Quick paste"
    assert OnSnippets in list(iter_menu_structure(get_menu_structure()))


def test_example_config_binds_ctrl_shift_f3() -> None:
    data = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    assert data["sqlite_snippets"].endswith("snippets.db")
    matching = [entry for entry in data["hotkeys"] if entry.get("action") == "OnSnippets"]
    assert matching
    assert "Ctrl+Shift+F3" in matching[0]["hotkeys"]
