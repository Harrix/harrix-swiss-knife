"""Tests for creating a Git repo next to a tracker SQLite database."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.subprocess_run import run_argv_output
from harrix_swiss_knife.apps.common.db_git import (
    ensure_sqlite_folder_git_repo,
    sqlite_folder_git_commit_message,
)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")


def _git_subject(folder: Path) -> str:
    code, output = run_argv_output(["git", "log", "-1", "--pretty=format:%s"], cwd=folder)
    assert code == 0, output
    return output


def _git_tracked(folder: Path) -> list[str]:
    code, output = run_argv_output(["git", "ls-files"], cwd=folder)
    assert code == 0, output
    return [line for line in output.splitlines() if line]


def test_sqlite_folder_git_commit_message_uses_filename_and_date() -> None:
    message = sqlite_folder_git_commit_message(Path("C:/data/food.db"), on=date(2026, 8, 21))
    assert message == "➕ Add food.db (2026-08-21)"  # noqa: RUF001


def test_ensure_sqlite_folder_git_repo_inits_and_commits(tmp_path: Path) -> None:
    db_path = tmp_path / "food.db"
    db_path.write_bytes(b"sqlite")
    assert ensure_sqlite_folder_git_repo(db_path) is True
    assert (tmp_path / ".git").exists()
    assert _git_tracked(tmp_path) == ["food.db"]
    assert _git_subject(tmp_path) == sqlite_folder_git_commit_message(db_path)


def test_ensure_sqlite_folder_git_repo_skips_existing_repo(tmp_path: Path) -> None:
    db_path = tmp_path / "fitness.db"
    db_path.write_bytes(b"sqlite")
    code, output = run_argv_output(["git", "init"], cwd=tmp_path)
    assert code == 0, output
    assert ensure_sqlite_folder_git_repo(db_path) is False
    code, output = run_argv_output(["git", "rev-parse", "--verify", "HEAD"], cwd=tmp_path)
    assert code != 0
    assert _git_tracked(tmp_path) == []


def test_ensure_sqlite_folder_git_repo_skips_missing_file(tmp_path: Path) -> None:
    assert ensure_sqlite_folder_git_repo(tmp_path / "missing.db") is False
    assert not (tmp_path / ".git").exists()
