"""Tests for Dev → Update Lucide icons wiring and sync helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtGui import QIcon

import harrix_swiss_knife.qt_lucide_icon as lucide_mod
from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.development.update_lucide_icons import OnUpdateLucideIcons
from harrix_swiss_knife.assets.sync_lucide_icons import LucideSyncResult, read_lucide_version
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.qt_lucide_icon import clear_lucide_icon_caches


def test_on_update_lucide_icons_metadata() -> None:
    """Action title and icon match the Dev menu entry."""
    action = OnUpdateLucideIcons()
    assert action.title == "Update Lucide icons"
    assert action.icon == "⬇️"


def test_on_update_lucide_icons_in_menu_structure() -> None:
    """Dev menu registers OnUpdateLucideIcons."""
    assert OnUpdateLucideIcons in list(iter_menu_structure(get_menu_structure()))


def test_read_lucide_version_missing(tmp_path: Path) -> None:
    """Missing VERSION.txt yields an empty string."""
    assert read_lucide_version(tmp_path) == ""


def test_read_lucide_version_present(tmp_path: Path) -> None:
    """VERSION.txt content is stripped."""
    (tmp_path / "VERSION.txt").write_text("1.2.3\n", encoding="utf-8")
    assert read_lucide_version(tmp_path) == "1.2.3"


def test_clear_lucide_icon_caches() -> None:
    """Cache clear empties painted-icon and name-list caches."""
    lucide_mod._CACHE[("x", 16, "#000000", 1.0)] = QIcon()
    lucide_mod._LUCIDE_NAME_LIST = ("a",)
    clear_lucide_icon_caches()
    assert lucide_mod._CACHE == {}
    assert lucide_mod._LUCIDE_NAME_LIST is None


def test_thread_after_clears_caches_and_summarizes(tmp_path: Path) -> None:
    """Successful sync clears Lucide caches and reports old→new version."""
    action = OnUpdateLucideIcons()
    action.add_line = MagicMock()  # type: ignore[method-assign]
    action.show_toast = MagicMock()  # type: ignore[method-assign]
    action.show_result = MagicMock()  # type: ignore[method-assign]
    result = LucideSyncResult(
        dest=tmp_path / "lucide",
        old_version="1.0.0",
        new_version="1.1.0",
        svg_count=42,
    )
    with patch("harrix_swiss_knife.actions.development.update_lucide_icons.clear_lucide_icon_caches") as clear_mock:
        action.thread_after(result)
    clear_mock.assert_called_once()
    summary = "Lucide icons updated: 1.0.0 → 1.1.0 (42 SVGs)."
    action.show_toast.assert_called_once_with(summary)
    action.show_result.assert_called_once()
