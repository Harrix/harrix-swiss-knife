"""Tests for Dev → Update Lucide icons wiring and sync helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtGui import QIcon

import harrix_swiss_knife.qt_lucide_icon as lucide_mod
from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.development.update_lucide_icons import (
    LUCIDE_COMMIT_MESSAGE,
    LucideGitChanges,
    OnUpdateLucideIcons,
    _change_kind,
    commit_lucide_updates,
    list_lucide_git_changes,
)
from harrix_swiss_knife.assets.sync_lucide_icons import LucideSyncResult, read_lucide_version
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.qt_lucide_icon import clear_lucide_icon_caches


def test_change_kind_classifies_porcelain_status() -> None:
    assert _change_kind("??") == "added"
    assert _change_kind("A ") == "added"
    assert _change_kind("M ") == "modified"
    assert _change_kind(" M") == "modified"
    assert _change_kind("D ") == "deleted"


def test_clear_lucide_icon_caches() -> None:
    """Cache clear empties painted-icon and name-list caches."""
    lucide_mod._CACHE[("x", 16, "#000000", 1.0)] = QIcon()
    lucide_mod._LUCIDE_NAME_LIST = ("a",)
    clear_lucide_icon_caches()
    assert lucide_mod._CACHE == {}
    assert lucide_mod._LUCIDE_NAME_LIST is None


def test_commit_lucide_updates_creates_commit(tmp_path: Path) -> None:
    lucide = tmp_path / "lucide"
    lucide.mkdir()
    calls: list[tuple[str, ...]] = []

    def fake_run(_cwd: Path, *args: str) -> MagicMock:
        calls.append(args)
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if args[:2] == ("diff", "--cached"):
            result.returncode = 1
        return result

    with patch(
        "harrix_swiss_knife.actions.development.update_lucide_icons.git_run",
        side_effect=fake_run,
    ):
        ok, detail = commit_lucide_updates(tmp_path, lucide)
    assert ok is True
    assert LUCIDE_COMMIT_MESSAGE in detail
    assert ("add", "--", "lucide") in calls
    assert ("-c", "commit.gpgsign=false", "commit", "-m", LUCIDE_COMMIT_MESSAGE) in calls


def test_commit_lucide_updates_skips_when_index_clean(tmp_path: Path) -> None:
    lucide = tmp_path / "lucide"
    lucide.mkdir()

    def fake_run(_cwd: Path, *args: str) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if args[:2] == ("diff", "--cached"):
            result.returncode = 0
        return result

    with patch(
        "harrix_swiss_knife.actions.development.update_lucide_icons.git_run",
        side_effect=fake_run,
    ):
        ok, detail = commit_lucide_updates(tmp_path, lucide)
    assert ok is True
    assert "No Lucide changes" in detail


def test_list_lucide_git_changes_splits_added_and_modified(tmp_path: Path) -> None:
    lucide = tmp_path / "assets" / "lucide"
    lucide.mkdir(parents=True)
    porcelain = "?? assets/lucide/new-icon.svg\n M assets/lucide/old-icon.svg\n M assets/lucide/VERSION.txt\n"

    class _Proc:
        returncode = 0
        stdout = porcelain
        stderr = ""

    with patch(
        "harrix_swiss_knife.actions.development.update_lucide_icons.git_run",
        return_value=_Proc(),
    ):
        changes = list_lucide_git_changes(tmp_path, lucide)
    assert changes.added == ("new-icon",)
    assert changes.modified == ("old-icon",)
    assert changes.has_changes is True
    assert changes.svg_names == ("new-icon", "old-icon")


def test_on_update_lucide_icons_in_menu_structure() -> None:
    """Dev menu registers OnUpdateLucideIcons."""
    assert OnUpdateLucideIcons in list(iter_menu_structure(get_menu_structure()))


def test_on_update_lucide_icons_metadata() -> None:
    """Action title and icon match the Dev menu entry."""
    action = OnUpdateLucideIcons()
    assert action.title == "Update Lucide icons"
    assert action.icon == "⬇️"


def test_read_lucide_version_missing(tmp_path: Path) -> None:
    """Missing `VERSION.txt` yields an empty string."""
    assert read_lucide_version(tmp_path) == ""


def test_read_lucide_version_present(tmp_path: Path) -> None:
    """`VERSION.txt` content is stripped."""
    (tmp_path / "VERSION.txt").write_text("1.2.3\n", encoding="utf-8")
    assert read_lucide_version(tmp_path) == "1.2.3"


def test_thread_after_clears_caches_and_summarizes(tmp_path: Path) -> None:
    """Successful sync clears Lucide caches, commits, and previews thumbnails."""
    action = OnUpdateLucideIcons()
    action.add_line = MagicMock()  # type: ignore[method-assign]
    action.show_toast = MagicMock()  # type: ignore[method-assign]
    action.show_result = MagicMock()  # type: ignore[method-assign]
    action.dialogs = MagicMock()
    result = LucideSyncResult(
        dest=tmp_path / "lucide",
        old_version="1.0.0",
        new_version="1.1.0",
        svg_count=42,
    )
    changes = LucideGitChanges(added=("sparkles",), modified=("save",))
    with (
        patch("harrix_swiss_knife.actions.development.update_lucide_icons.clear_lucide_icon_caches") as clear_mock,
        patch(
            "harrix_swiss_knife.actions.development.update_lucide_icons.list_lucide_git_changes",
            return_value=changes,
        ),
        patch(
            "harrix_swiss_knife.actions.development.update_lucide_icons.commit_lucide_updates",
            return_value=(True, f"Committed `{LUCIDE_COMMIT_MESSAGE}`"),
        ) as commit_mock,
        patch(
            "harrix_swiss_knife.actions.development.update_lucide_icons.get_project_root",
            return_value=tmp_path,
        ),
    ):
        action.thread_after(result)
    clear_mock.assert_called_once()
    commit_mock.assert_called_once()
    summary = "Lucide icons updated: 1.0.0 → 1.1.0 (42 SVGs)."
    action.show_toast.assert_called_once_with(summary)
    action.show_result.assert_called_once()
    action.dialogs.show_lucide_icon_thumbnails.assert_called_once()
    args = action.dialogs.show_lucide_icon_thumbnails.call_args.args
    assert args[0] == "Lucide changes"
    assert ("Added (1)", ["sparkles"]) in args[2]
    assert ("Updated (1)", ["save"]) in args[2]
