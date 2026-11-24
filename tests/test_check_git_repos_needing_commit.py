"""Tests for scanning dirty Git repos under `paths_git_roots`."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.apps.git_commit import OnGitCommit
from harrix_swiss_knife.actions.common.git_dirty_ops import DirtyRepoStatus

if TYPE_CHECKING:
    import pytest


def test_noninteractive_missing_roots(monkeypatch: pytest.MonkeyPatch) -> None:
    action = OnGitCommit()
    monkeypatch.setattr(action, "_configured_roots", list)
    action.execute(noninteractive=True)
    assert any("paths_git_roots" in line for line in action.result_lines)


def test_noninteractive_reports_all_clean(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "GitHub"
    repo = root / "project"
    _git_init(repo)

    action = OnGitCommit()
    monkeypatch.setattr(action, "_configured_roots", lambda: [root.resolve()])
    saved: list[bool] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.apps.git_commit.save_git_repos_all_clean",
        lambda *, all_clean: saved.append(all_clean),
    )
    action.execute(noninteractive=True)

    assert any("No repositories need a commit" in line for line in action.result_lines)
    assert saved == [True]


def test_noninteractive_reports_dirty_repos(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "GitHub"
    repo = root / "project"
    _git_init(repo)
    (repo / "README.md").write_text("changed\n", encoding="utf-8")

    action = OnGitCommit()
    monkeypatch.setattr(action, "_configured_roots", lambda: [root.resolve()])
    saved: list[bool] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.apps.git_commit.save_git_repos_all_clean",
        lambda *, all_clean: saved.append(all_clean),
    )
    action.execute(noninteractive=True)

    assert any("1 repository(ies) need a commit" in line for line in action.result_lines)
    assert any(str(repo.resolve()) in line or "project" in line for line in action.result_lines)
    assert saved == [False]


def test_noninteractive_reports_unpushed_public_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A clean public repository with unpushed commits marks the checklist failed."""
    root = tmp_path / "GitHub"
    root.mkdir()
    repo = root / "public-repo"
    status = DirtyRepoStatus(path=repo, files=(), unpushed=2, access_kind="public")

    action = OnGitCommit()
    monkeypatch.setattr(action, "_configured_roots", lambda: [root.resolve()])
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.apps.git_commit.scan_dirty_repos",
        lambda _roots: [status],
    )
    saved: list[bool] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.apps.git_commit.save_git_repos_all_clean",
        lambda *, all_clean: saved.append(all_clean),
    )
    action.execute(noninteractive=True)

    assert any("public repository(ies) need a push" in line for line in action.result_lines)
    assert any("2 unpushed" in line for line in action.result_lines)
    assert saved == [False]


def test_scan_dirty_repos_across_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root_a = tmp_path / "GitHub"
    root_b = tmp_path / "Notes"
    dirty = root_a / "dirty-repo"
    clean = root_a / "clean-repo"
    notes_dirty = root_b / "Notes-Lists"
    _git_init(dirty)
    _git_init(clean)
    _git_init(notes_dirty)
    (dirty / "README.md").write_text("changed\n", encoding="utf-8")
    (notes_dirty / "extra.txt").write_text("untracked\n", encoding="utf-8")

    action = OnGitCommit()
    monkeypatch.setattr(action, "_configured_roots", lambda: [root_a.resolve(), root_b.resolve()])
    found = action._scan_dirty_repos(action._configured_roots())
    paths = {repo.path.resolve() for repo in found}
    assert dirty.resolve() in paths
    assert notes_dirty.resolve() in paths
    assert clean.resolve() not in paths


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
