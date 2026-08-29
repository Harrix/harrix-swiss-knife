"""Tests for habit daily comments stored as Markdown notes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.habit_comments import (
    HabitCommentsStore,
    HabitDayComment,
    apply_habit_comments_root_to_config,
    habit_comment_folder_slug,
    parse_habit_comment_file,
    persist_habit_comments_root,
    preview_habit_comment,
    render_habit_comment_file,
    resolve_habit_comments_root,
    resolve_notes_parent,
)
from harrix_swiss_knife.apps.habits.habit_comments_list_dialog import HabitCommentsListDialog
from harrix_swiss_knife.apps.habits.habit_day_comment_dialog import HabitDayCommentDialog


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_preview_habit_comment() -> None:
    assert preview_habit_comment("first\nsecond") == "first"
    assert preview_habit_comment("") == ""


def test_habit_comment_folder_slug() -> None:
    assert habit_comment_folder_slug("Sleep well") == "Sleep-well"
    assert habit_comment_folder_slug("  ") == "habit"


def test_parse_and_render_habit_comment_file() -> None:
    rendered = render_habit_comment_file(
        [
            HabitDayComment("2026-08-25", "Late night"),
            HabitDayComment("2026-08-26", "Slept 7h"),
        ],
        habit_id=3,
        habit_name="Sleep",
        beginning="---\nlang: ru\n---\n",
    )
    assert "habit-id: 3" in rendered
    assert rendered.index("2026-08-26") < rendered.index("2026-08-25")
    parsed = parse_habit_comment_file(rendered)
    assert [item.date for item in parsed] == ["2026-08-26", "2026-08-25"]
    assert parsed[0].text == "Slept 7h"


def test_resolve_habit_comments_root_from_diary() -> None:
    root = resolve_habit_comments_root({"path_diary": "D:/Dropbox/Notes/Notes-Diaries/Diary"})
    assert root == Path("D:/Dropbox/Notes/Notes-Habits")
    data_root = resolve_habit_comments_root({"path_diary": "C:/data/Notes/Notes-Diaries"})
    assert data_root == Path("C:/data/Notes/Notes-Habits")


def test_resolve_habit_comments_root_from_path_notes(tmp_path: Path) -> None:
    notes_parent = tmp_path / "Notes"
    (notes_parent / "Notes-Diaries").mkdir(parents=True)
    (notes_parent / "Notes").mkdir()
    assert resolve_notes_parent({"path_notes": str(notes_parent)}) == notes_parent
    assert resolve_habit_comments_root({"path_notes": str(notes_parent)}) == notes_parent / "Notes-Habits"
    nested_notes = notes_parent / "Notes"
    assert resolve_notes_parent({"path_notes": str(nested_notes)}) == notes_parent
    assert resolve_habit_comments_root({"path_notes": str(nested_notes)}) == notes_parent / "Notes-Habits"


def test_apply_habit_comments_root_to_config(tmp_path: Path) -> None:
    root = tmp_path / "Notes-Habits"
    config: dict[str, object] = {"paths_git": ["D:/other"], "paths_notes": []}
    assert apply_habit_comments_root_to_config(config, root) is True
    assert config["path_habit_comments"] == root.as_posix()
    assert root.as_posix() in config["paths_git"]
    assert root.as_posix() in config["paths_notes"]
    assert apply_habit_comments_root_to_config(config, root) is False


def test_persist_habit_comments_root(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}\n", encoding="utf-8")
    root = tmp_path / "Notes-Habits"
    live: dict[str, object] = {}
    persist_habit_comments_root(root, live, config_path=config_path)
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["path_habit_comments"] == root.as_posix()
    assert live["path_habit_comments"] == root.as_posix()


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
def test_set_comment_creates_notes_habits_git_repo_then_note(tmp_path: Path) -> None:
    notes_parent = tmp_path / "Notes"
    (notes_parent / "Notes-Diaries").mkdir(parents=True)
    store = HabitCommentsStore.from_config({"path_notes": str(notes_parent)}, commit=False)
    root = store.root()
    assert root == notes_parent / "Notes-Habits"
    assert root is not None
    assert not root.exists()
    path = store.set_comment(1, "2026-08-30", "5 km", habit_name="Run")
    assert root.is_dir()
    assert (root / ".git").exists()
    assert path is not None
    assert path.is_file()
    assert store.comment(1, "2026-08-30") == "5 km"


def test_habit_comments_store_roundtrip(tmp_path: Path) -> None:
    store = HabitCommentsStore(tmp_path, beginning="---\nlang: ru\n---\n", commit=False)
    path = store.set_comment(1, "2026-08-26", "5 km", habit_name="Run")
    assert path is not None
    assert path.name.startswith("0001-")
    assert store.comment(1, "2026-08-26") == "5 km"
    store.set_comment(1, "2026-08-25", "Rest", habit_name="Run")
    dates = store.dates_with_comments([1])[1]
    assert dates == {"2026-08-26", "2026-08-25"}
    store.set_comment(1, "2026-08-26", "", habit_name="Run")
    assert store.comment(1, "2026-08-26") == ""
    assert [item.date for item in store.comments_for_habit(1)] == ["2026-08-25"]


def test_set_comment_empty_does_not_create_file(tmp_path: Path) -> None:
    store = HabitCommentsStore(tmp_path, beginning="---\nlang: ru\n---\n", commit=False)
    assert store.set_comment(2, "2026-08-26", "", habit_name="Walk") is None
    assert list(tmp_path.glob("*")) == []


def test_habit_day_comment_dialog_returns_text(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = HabitDayCommentDialog(habit_name="Run", date_str="2026-08-26", text="old")
    dialog._edit.setPlainText("new note")
    assert dialog.comment_text() == "new note"


def test_habit_comments_list_dialog_selects_date(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = HabitCommentsListDialog(
        habit_name="Run",
        comments=[HabitDayComment("2026-08-26", "5 km")],
    )
    item = dialog._list.item(0)
    assert item is not None
    dialog._on_item_activated(item)
    assert dialog.chosen_date() == "2026-08-26"
