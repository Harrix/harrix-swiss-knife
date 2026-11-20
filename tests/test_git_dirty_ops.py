"""Tests for selective commit helpers and non-blocking GitHub Desktop open."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from harrix_swiss_knife.actions.common.git_dirty_ops import (
    commit_selected_paths,
    open_github_desktop_nonblocking,
    parse_porcelain_files,
    refresh_repo_statuses,
)

if TYPE_CHECKING:
    import pytest


def test_commit_selected_paths_stages_only_checked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    (repo / "keep.md").write_text("keep\n", encoding="utf-8")
    (repo / "skip.md").write_text("skip\n", encoding="utf-8")

    calls: list[tuple[str, ...]] = []

    def fake_run(_cwd: Path, *args: str) -> MagicMock:
        calls.append(args)
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.git_run",
        fake_run,
    )
    ok, detail = commit_selected_paths(repo, ["keep.md"], "⬆️ Update keep.md")
    assert ok is True
    assert detail == "⬆️ Update keep.md"
    assert ("add", "--", "keep.md") in calls
    assert ("commit", "-m", "⬆️ Update keep.md") in calls
    assert not any(arg == "-A" for call in calls for arg in call)


def test_open_github_desktop_nonblocking_uses_startfile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    started: list[str] = []

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.sys.platform",
        "win32",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.os.startfile",
        started.append,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.subprocess.run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("blocking run")),
    )

    ok, detail = open_github_desktop_nonblocking(repo)
    assert ok is True
    assert started
    assert started[0].startswith("x-github-client://openLocalRepo/")
    assert "blocking" not in detail


def test_parse_porcelain_files_rename_and_plain() -> None:
    files = parse_porcelain_files(" M notes.md\nR  old.txt -> new.txt\n?? fresh.md\n")
    assert [item.path for item in files] == ["notes.md", "new.txt", "fresh.md"]
    assert files[0].status == " M"
    assert files[1].status == "R "
    assert files[2].status == "??"


def test_parse_porcelain_keeps_leading_space_of_unstaged_path() -> None:
    """Unstaged porcelain starts with a space; the path must stay intact."""
    files = parse_porcelain_files(" M Prompts/Promts-Common/Promts-Common.md\n")
    assert len(files) == 1
    assert files[0].status == " M"
    assert files[0].path == "Prompts/Promts-Common/Promts-Common.md"


def test_refresh_repo_statuses_drops_clean(tmp_path: Path) -> None:
    dirty = tmp_path / "dirty"
    clean = tmp_path / "clean"
    _git_init(dirty)
    _git_init(clean)
    (dirty / "extra.txt").write_text("x\n", encoding="utf-8")

    statuses = refresh_repo_statuses([dirty, clean], prefer_first=dirty)
    paths = {item.path.resolve() for item in statuses}
    assert dirty.resolve() in paths
    assert clean.resolve() not in paths
    assert statuses[0].path.resolve() == dirty.resolve()


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)  # noqa: S607
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
    (path / "README.md").write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)  # noqa: S607
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
