"""Tests for `data-for-hsk` folder setup and config path wiring."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.db_git import ensure_folder_git_repo
from harrix_swiss_knife.data_for_hsk import (
    apply_data_for_hsk_to_config,
    create_data_for_hsk,
    ensure_missing_tracker_databases,
    needs_data_for_hsk_setup,
    suggest_data_for_hsk_root,
)
from harrix_swiss_knife.data_for_hsk_config import (
    DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS,
    build_config_updates,
)


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt SQL drivers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_build_config_updates_maps_notes_and_databases(tmp_path: Path) -> None:
    data_root = tmp_path / "data-for-hsk"
    updates = build_config_updates(data_root, DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS)
    assert updates["data_for_hsk_root"] == data_root.resolve().as_posix()
    assert updates["sqlite_finance"].endswith("/databases/finance.db")
    assert updates["path_notes"] == (data_root / "Notes" / "Notes").resolve().as_posix()
    assert updates["path_diary"] == (data_root / "Notes" / "Notes-Diaries").resolve().as_posix()
    assert updates["path_cases"] == (data_root / "Notes" / "Notes-External").resolve().as_posix()
    assert len(updates["paths_notes"]) == len(DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS)
    assert updates["paths_git"][-1] == (data_root / "databases").resolve().as_posix()


def test_needs_data_for_hsk_setup_when_databases_missing(tmp_path: Path) -> None:
    data_root = tmp_path / "data-for-hsk"
    updates = build_config_updates(data_root, DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS)
    config = {k: v for k, v in updates.items() if k != "data_for_hsk_setup_done"}
    assert needs_data_for_hsk_setup(config) is True


def test_needs_data_for_hsk_setup_false_when_complete(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    data_root = tmp_path / "data-for-hsk"
    result = create_data_for_hsk(data_root, init_databases=True, init_git=False)
    config = dict(result.config_updates)
    assert needs_data_for_hsk_setup(config) is False


def test_ensure_missing_tracker_databases_creates_only_absent_files(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
) -> None:
    data_root = tmp_path / "data-for-hsk"
    result = create_data_for_hsk(data_root, init_databases=True, init_git=False)
    snippets = result.databases_dir / "snippets.db"
    snippets.unlink()
    created = ensure_missing_tracker_databases(result.config_updates)
    assert created == ("snippets.db",)
    assert snippets.is_file()
    assert needs_data_for_hsk_setup(result.config_updates) is False


def test_create_data_for_hsk_creates_structure(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    data_root = tmp_path / "parent" / "data-for-hsk"
    result = create_data_for_hsk(data_root, init_databases=True, init_git=False)
    assert result.data_root.is_dir()
    assert result.databases_dir.is_dir()
    assert result.notes_dir.is_dir()
    for name in DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS:
        assert (result.notes_dir / name).is_dir()
    for db_name in ("finance.db", "fitness.db", "habits.db", "food.db", "snippets.db"):
        assert (result.databases_dir / db_name).is_file()


def test_apply_data_for_hsk_to_config_writes_config(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    config_path = tmp_path / "config.json"
    data_root = tmp_path / "data-for-hsk"
    apply_data_for_hsk_to_config(data_root, config_path=config_path, init_git=False)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["data_for_hsk_setup_done"] is True
    assert Path(data["sqlite_food"]).name == "food.db"


def test_suggest_data_for_hsk_root_uses_path_github(tmp_path: Path) -> None:
    github = tmp_path / "install-root"
    github.mkdir()
    suggested = suggest_data_for_hsk_root({"path_github": github.as_posix()})
    assert suggested == (github / "data-for-hsk").resolve()


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
def test_ensure_folder_git_repo_creates_gitkeep_commit(tmp_path: Path) -> None:
    folder = tmp_path / "Notes-Lists"
    assert ensure_folder_git_repo(folder) is True
    assert (folder / ".git").is_dir()
    assert (folder / ".gitkeep").is_file()
