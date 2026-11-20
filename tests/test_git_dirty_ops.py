"""Tests for selective commit helpers and non-blocking GitHub Desktop open."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from harrix_swiss_knife.actions.common import git_dirty_ops
from harrix_swiss_knife.actions.common.git_dirty_ops import (
    commit_selected_paths,
    configured_git_roots,
    github_repo_visibility,
    open_github_desktop_nonblocking,
    parse_github_slug,
    parse_porcelain_files,
    read_repo_access,
    refresh_repo_statuses,
    repo_access_from_remote,
    scan_dirty_repos,
    visibility_from_github_payload,
)
from harrix_swiss_knife.apps.git_commit.diff_view import diff_line_kind

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


def test_configured_git_roots_dedupes_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "GitHub"
    root.mkdir()

    def fake_load(*_args: object, **_kwargs: object) -> dict[str, list[str]]:
        return {"paths_git_roots": [str(root), "  ", str(root)]}

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.load_app_config",
        fake_load,
    )
    assert configured_git_roots() == [root.resolve()]


def test_diff_line_kind_marks_add_delete_and_hunk() -> None:
    assert diff_line_kind("+added") == "add"
    assert diff_line_kind("-removed") == "delete"
    assert diff_line_kind("@@ -1,2 +1,3 @@") == "hunk"
    assert diff_line_kind("+++ b/file.md") == "meta"
    assert diff_line_kind("--- a/file.md") == "meta"
    assert diff_line_kind(" context") == "context"


def test_github_repo_visibility_retries_without_rejected_token(monkeypatch: pytest.MonkeyPatch) -> None:
    git_dirty_ops._visibility_cache.clear()
    calls: list[bool] = []

    def fake_payload(_owner: str, repo: str, *, headers: dict[str, str]) -> tuple[int, object]:
        calls.append("Authorization" in headers)
        if "Authorization" in headers:
            return 401, None
        if repo == "harrix-swiss-knife":
            return 200, {"private": False, "visibility": "public"}
        return 404, None

    monkeypatch.setattr(git_dirty_ops, "_github_repo_payload", fake_payload)
    assert github_repo_visibility("Harrix", "harrix-swiss-knife") == "public"
    assert github_repo_visibility("Harrix", "Notes") == "private"
    assert calls == [True, False, True, False]
    git_dirty_ops._visibility_cache.clear()


def test_open_github_desktop_nonblocking_detaches_from_console(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_popen(command: list[str], **kwargs: object) -> MagicMock:
        calls.append((list(command), kwargs))
        return MagicMock()

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.sys.platform",
        "win32",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.subprocess.Popen",
        fake_popen,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.git_dirty_ops.subprocess.run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("blocking run")),
    )

    ok, detail = open_github_desktop_nonblocking(repo)
    assert ok is True
    assert calls
    command, kwargs = calls[0]
    assert command[:4] == ["cmd", "/c", "start", ""]
    assert command[-1].startswith("x-github-client://openLocalRepo/")
    flags = kwargs["creationflags"]
    assert isinstance(flags, int)
    assert flags & subprocess.DETACHED_PROCESS
    assert kwargs["stdout"] is subprocess.DEVNULL
    assert kwargs["stderr"] is subprocess.DEVNULL
    assert "blocking" not in detail


def test_parse_github_slug_accepts_https_and_ssh() -> None:
    assert parse_github_slug("https://github.com/harrix/harrix-swiss-knife.git") == (
        "harrix",
        "harrix-swiss-knife",
    )
    assert parse_github_slug("git@github.com:harrix/notes.git") == ("harrix", "notes")
    assert parse_github_slug("ssh://git@github.com/harrix/notes") == ("harrix", "notes")
    assert parse_github_slug("https://gitlab.com/harrix/notes.git") is None


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


def test_read_repo_access_local_and_github_remote(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    assert read_repo_access(repo).kind == "local"
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:harrix/notes.git"],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
    )
    access = read_repo_access(repo)
    assert access.kind == "remote"
    assert access.github_slug == "harrix/notes"


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


def test_repo_access_from_remote_marks_local_remote_and_visibility() -> None:
    assert repo_access_from_remote("").kind == "local"
    remote = repo_access_from_remote("https://gitlab.com/harrix/notes.git")
    assert remote.kind == "remote"
    assert remote.github_slug == ""
    github = repo_access_from_remote("git@github.com:harrix/notes.git")
    assert github.kind == "remote"
    assert github.github_slug == "harrix/notes"
    assert repo_access_from_remote("git@github.com:harrix/notes.git", visibility="public").kind == "public"
    assert repo_access_from_remote("git@github.com:harrix/notes.git", visibility="private").kind == "private"


def test_scan_dirty_repos_finds_only_dirty_children(tmp_path: Path) -> None:
    root = tmp_path / "roots"
    dirty = root / "dirty"
    clean = root / "clean"
    (root / "notes").mkdir(parents=True)
    _git_init(dirty)
    _git_init(clean)
    (dirty / "note.txt").write_text("n\n", encoding="utf-8")

    found = scan_dirty_repos([root, tmp_path / "missing"])
    assert [item.path.resolve() for item in found] == [dirty.resolve()]


def test_visibility_from_github_payload() -> None:
    assert visibility_from_github_payload({"private": False}, status=200) == "public"
    assert visibility_from_github_payload({"visibility": "private"}, status=200) == "private"
    assert visibility_from_github_payload({"visibility": "internal"}, status=200) == "private"
    assert visibility_from_github_payload(None, status=404) == "private"
    assert visibility_from_github_payload(None, status=403) == "unknown"


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
