"""Tests for discarding uncommitted git changes in folder repos."""

from __future__ import annotations

import subprocess
from pathlib import Path

from harrix_swiss_knife.actions.files.discard_git_changes_folder import (
    OnDiscardGitChangesFolder,
    find_git_repos,
    git_porcelain,
    is_git_repo,
)


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


def test_find_git_repos_returns_root_when_root_is_repo(tmp_path: Path) -> None:
    _git_init(tmp_path)
    assert find_git_repos(tmp_path) == [tmp_path.resolve()]


def test_find_git_repos_returns_immediate_child_repos(tmp_path: Path) -> None:
    notes = tmp_path / "Notes"
    diaries = tmp_path / "Notes-Diaries"
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    _git_init(notes)
    _git_init(diaries)

    found = find_git_repos(tmp_path)
    assert found == [notes.resolve(), diaries.resolve()]


def test_is_git_repo_false_for_plain_folder(tmp_path: Path) -> None:
    assert not is_git_repo(tmp_path)


def test_discard_restores_tracked_and_removes_untracked(tmp_path: Path) -> None:
    repo_a = tmp_path / "RepoA"
    repo_b = tmp_path / "RepoB"
    _git_init(repo_a)
    _git_init(repo_b)

    (repo_a / "README.md").write_text("changed\n", encoding="utf-8")
    (repo_a / "new-file.txt").write_text("untracked\n", encoding="utf-8")
    (repo_b / "README.md").write_text("also changed\n", encoding="utf-8")

    assert git_porcelain(repo_a).strip()
    assert git_porcelain(repo_b).strip()

    action = OnDiscardGitChangesFolder()
    action(folder_path=tmp_path, noninteractive=True)

    assert (repo_a / "README.md").read_text(encoding="utf-8") == "hello\n"
    assert not (repo_a / "new-file.txt").exists()
    assert (repo_b / "README.md").read_text(encoding="utf-8") == "hello\n"
    assert not git_porcelain(repo_a).strip()
    assert not git_porcelain(repo_b).strip()
    assert any("✅ RepoA" in line for line in action.result_lines)
    assert any("✅ RepoB" in line for line in action.result_lines)


def test_status_only_lists_dirty_repos_without_discarding(tmp_path: Path) -> None:
    repo_a = tmp_path / "RepoA"
    repo_b = tmp_path / "RepoB"
    _git_init(repo_a)
    _git_init(repo_b)

    (repo_a / "README.md").write_text("changed\n", encoding="utf-8")
    (repo_a / "new-file.txt").write_text("untracked\n", encoding="utf-8")

    action = OnDiscardGitChangesFolder()
    action(folder_path=tmp_path, noninteractive=True, status_only=True)

    assert (repo_a / "README.md").read_text(encoding="utf-8") == "changed\n"
    assert (repo_a / "new-file.txt").exists()
    assert (repo_b / "README.md").read_text(encoding="utf-8") == "hello\n"
    assert git_porcelain(repo_a).strip()
    assert not git_porcelain(repo_b).strip()
    assert any("🔶 RepoA" in line for line in action.result_lines)
    assert any("⚪ RepoB: clean" in line for line in action.result_lines)
    assert any("1 repository(ies) with uncommitted changes" in line for line in action.result_lines)
    assert not any("discarded uncommitted changes" in line for line in action.result_lines)
