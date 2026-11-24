"""Tests for selective commit helpers and non-blocking GitHub Desktop open."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from harrix_swiss_knife.actions.common import git_dirty_ops
from harrix_swiss_knife.actions.common.git_dirty_ops import (
    add_git_root,
    commit_selected_paths,
    configured_git_roots,
    count_commits_by_day,
    count_recent_commits,
    discard_changed_paths,
    discover_git_repos,
    github_repo_visibility,
    list_changed_files,
    open_github_desktop_nonblocking,
    parse_github_slug,
    parse_porcelain_files,
    push_current_branch,
    read_repo_access,
    refresh_repo_statuses,
    repo_access_from_remote,
    scan_dirty_repos,
    unpushed_commit_count,
    visibility_from_github_payload,
)
from harrix_swiss_knife.apps.git_commit.diff_view import diff_line_kind

if TYPE_CHECKING:
    import pytest


def test_add_git_root_appends_once(tmp_path: Path) -> None:
    """A new folder is stored once in `paths_git_roots` with forward slashes."""
    config = tmp_path / "config.json"
    existing = tmp_path / "existing"
    existing.mkdir()
    config.write_text(json.dumps({"paths_git_roots": [str(existing)]}), encoding="utf-8")
    new_folder = tmp_path / "new-folder"
    new_folder.mkdir()

    added = add_git_root(new_folder, config_path=str(config))
    assert added.added is True
    assert added.path == new_folder.resolve()

    again = add_git_root(Path(str(new_folder)), config_path=str(config))
    assert again.added is False
    loaded = json.loads(config.read_text(encoding="utf-8"))
    assert loaded["paths_git_roots"] == [str(existing), new_folder.resolve().as_posix()]


def test_add_git_root_rejects_missing_folder(tmp_path: Path) -> None:
    """A missing folder is not written to config."""
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    missing = tmp_path / "missing"
    result = add_git_root(missing, config_path=str(config))
    assert result.added is False
    assert "not found" in result.message.casefold()
    assert json.loads(config.read_text(encoding="utf-8")) == {}


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


def test_count_commits_by_day_filters_local_scope(tmp_path: Path) -> None:
    """Local scope keeps commits from repos without a remote."""
    root = tmp_path / "repos"
    local = root / "local-repo"
    _git_init(local)
    (local / "extra.md").write_text("more\n", encoding="utf-8")
    subprocess.run(["git", "add", "extra.md"], cwd=local, check=True, capture_output=True)  # noqa: S607
    subprocess.run(["git", "commit", "-m", "Second"], cwd=local, check=True, capture_output=True)  # noqa: S607

    today = datetime.now().astimezone().date()
    all_counts = count_commits_by_day([root], today - timedelta(days=7), today, scope="all")
    local_counts = count_commits_by_day([root], today - timedelta(days=7), today, scope="local")
    public_counts = count_commits_by_day([root], today - timedelta(days=7), today, scope="public")
    assert sum(all_counts.values()) >= 1
    assert sum(local_counts.values()) >= 1
    assert sum(public_counts.values()) == 0


def test_count_recent_commits_splits_public_private_and_skips_old(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Today and yesterday are split by GitHub visibility. Older commits are ignored."""
    root = tmp_path / "repos"
    public = root / "public-repo"
    private = root / "private-repo"
    local = root / "local-repo"
    other = root / "other-repo"
    old = root / "old-repo"
    for path in (public, private, local, other, old):
        _git_init(path)
    _github_remote(public, "public-repo")
    _github_remote(private, "private-repo")
    subprocess.run(
        ["git", "remote", "add", "origin", "https://gitlab.com/me/other-repo.git"],  # noqa: S607
        cwd=other,
        check=True,
        capture_output=True,
    )
    _commit_file_at(public, "yesterday.txt", _local_iso(days_ago=1))
    _recommit_at(old, _local_iso(days_ago=10))

    seen: list[str] = []

    def fake_visibility(_owner: str, repo: str) -> str:
        seen.append(repo)
        if repo == "public-repo":
            return "public"
        if repo == "private-repo":
            return "private"
        return "unknown"

    git_dirty_ops._visibility_cache.clear()
    monkeypatch.setattr(git_dirty_ops, "github_repo_visibility", fake_visibility)

    summary = count_recent_commits([root])
    assert summary.today.total == 4
    assert summary.today.public == 1
    assert summary.today.private == 1
    assert summary.today.local == 1
    assert summary.today.other == 1
    assert summary.yesterday.total == 1
    assert summary.yesterday.public == 1
    assert summary.yesterday.private == 0
    assert "old-repo" not in seen
    assert "public-repo" in seen
    assert "private-repo" in seen

    missing = count_recent_commits([tmp_path / "missing"])
    assert missing.today.total == 0
    assert missing.yesterday.total == 0


def test_diff_line_kind_marks_add_delete_and_hunk() -> None:
    assert diff_line_kind("+added") == "add"
    assert diff_line_kind("-removed") == "delete"
    assert diff_line_kind("@@ -1,2 +1,3 @@") == "hunk"
    assert diff_line_kind("+++ b/file.md") == "meta"
    assert diff_line_kind("--- a/file.md") == "meta"
    assert diff_line_kind(" context") == "context"


def test_discard_changed_paths_restores_tracked_and_removes_untracked(tmp_path: Path) -> None:
    """Discard restores modified files and deletes untracked / newly staged files."""
    repo = tmp_path / "repo"
    _git_init(repo)
    tracked = repo / "README.md"
    tracked.write_text("changed\n", encoding="utf-8")
    untracked = repo / "notes.txt"
    untracked.write_text("temp\n", encoding="utf-8")
    nested = repo / "docs"
    nested.mkdir()
    added = nested / "new.md"
    added.write_text("new\n", encoding="utf-8")
    subprocess.run(["git", "add", "docs/new.md"], cwd=repo, check=True, capture_output=True)  # noqa: S607

    before = {item.path for item in list_changed_files(repo)}
    assert before >= {"README.md", "notes.txt", "docs/new.md"}

    ok, detail = discard_changed_paths(repo, ["README.md", "notes.txt", "docs/new.md"])
    assert ok is True
    assert "Discarded" in detail
    assert tracked.read_text(encoding="utf-8") == "hello\n"
    assert not untracked.exists()
    assert not added.exists()
    assert list_changed_files(repo) == []


def test_discover_git_repos_marks_only_repos_that_need_attention(tmp_path: Path) -> None:
    """A parent folder lists child repos; a repository folder lists only itself."""
    root = tmp_path / "folder"
    dirty = root / "dirty"
    clean = root / "clean"
    _git_init(dirty)
    _git_init(clean)
    (dirty / "note.txt").write_text("n\n", encoding="utf-8")

    found = {item.path.name: item for item in discover_git_repos(root)}
    assert set(found) == {"clean", "dirty"}
    assert found["dirty"].needs_attention is True
    assert found["clean"].status is None

    solo = discover_git_repos(clean)
    assert [item.path.resolve() for item in solo] == [clean.resolve()]
    assert solo[0].needs_attention is False


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


def test_push_current_branch_publishes_ahead_commit(tmp_path: Path) -> None:
    """Push sends commits that are not on the remote-tracking branch."""
    repo = tmp_path / "repo"
    _git_with_local_remote(repo, pushed=True)
    (repo / "extra.md").write_text("more\n", encoding="utf-8")
    subprocess.run(["git", "add", "extra.md"], cwd=repo, check=True, capture_output=True)  # noqa: S607
    subprocess.run(["git", "commit", "-m", "Second"], cwd=repo, check=True, capture_output=True)  # noqa: S607
    assert unpushed_commit_count(repo) == 1
    ok, _detail = push_current_branch(repo)
    assert ok
    assert unpushed_commit_count(repo) == 0


def test_push_current_branch_sets_upstream_when_missing(tmp_path: Path) -> None:
    """A branch with no upstream is pushed to origin."""
    repo = tmp_path / "repo"
    _git_with_local_remote(repo, pushed=False)
    assert unpushed_commit_count(repo) >= 1
    ok, _detail = push_current_branch(repo)
    assert ok
    assert unpushed_commit_count(repo) == 0


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


def test_refresh_keeps_cached_public_unpushed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A timer refresh keeps a public unpushed repo using the visibility cache."""
    repo = tmp_path / "public-repo"
    _git_with_unpushed_commit(repo, "harrix/public-repo")
    monkeypatch.setitem(git_dirty_ops._visibility_cache, "harrix/public-repo", "public")
    statuses = refresh_repo_statuses([repo])
    assert len(statuses) == 1
    assert statuses[0].unpushed == 1
    assert statuses[0].access_kind == "public"


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


def test_scan_includes_public_unpushed_and_skips_private_and_local(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clean public repos with unpushed commits are listed; local and private are not."""
    root = tmp_path / "roots"
    public = root / "public-repo"
    private = root / "private-repo"
    local = root / "local-repo"
    _git_with_unpushed_commit(public, "harrix/public-repo")
    _git_with_unpushed_commit(private, "harrix/private-repo")
    _git_init(local)
    (local / "again.md").write_text("local only\n", encoding="utf-8")
    subprocess.run(["git", "add", "again.md"], cwd=local, check=True, capture_output=True)  # noqa: S607
    subprocess.run(["git", "commit", "-m", "Local only"], cwd=local, check=True, capture_output=True)  # noqa: S607

    def visibility(_owner: str, repo: str) -> str:
        if repo == "public-repo":
            return "public"
        if repo == "private-repo":
            return "private"
        return "unknown"

    monkeypatch.setattr(git_dirty_ops, "github_repo_visibility", visibility)
    found = {item.path.name: item for item in scan_dirty_repos([root])}
    assert set(found) == {"public-repo"}
    assert found["public-repo"].unpushed == 1
    assert found["public-repo"].files == ()
    assert found["public-repo"].access_kind == "public"


def test_unpushed_commit_count_ignores_repos_without_remote(tmp_path: Path) -> None:
    """Local repositories are not treated as unpushed."""
    repo = tmp_path / "local"
    _git_init(repo)
    assert unpushed_commit_count(repo) == 0


def test_visibility_from_github_payload() -> None:
    assert visibility_from_github_payload({"private": False}, status=200) == "public"
    assert visibility_from_github_payload({"visibility": "private"}, status=200) == "private"
    assert visibility_from_github_payload({"visibility": "internal"}, status=200) == "private"
    assert visibility_from_github_payload(None, status=404) == "private"
    assert visibility_from_github_payload(None, status=403) == "unknown"


def _commit_file_at(repo: Path, name: str, when: str) -> None:
    (repo / name).write_text(name + "\n", encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=repo, check=True, capture_output=True)  # noqa: S607
    subprocess.run(
        ["git", "commit", "-m", name],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_date_env(when),
    )


def _git_date_env(when: str) -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = when
    env["GIT_COMMITTER_DATE"] = when
    return env


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


def _git_with_local_remote(path: Path, *, pushed: bool) -> None:
    origin = path.parent / f"{path.name}-origin.git"
    subprocess.run(["git", "init", "--bare", str(origin)], check=True, capture_output=True)  # noqa: S607
    _git_init(path)
    subprocess.run(
        ["git", "remote", "add", "origin", str(origin)],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
    if not pushed:
        return
    subprocess.run(
        ["git", "push", "-u", "origin", "HEAD"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )


def _git_with_unpushed_commit(path: Path, slug: str) -> None:
    _git_with_local_remote(path, pushed=True)
    (path / "extra.md").write_text("more\n", encoding="utf-8")
    subprocess.run(["git", "add", "extra.md"], cwd=path, check=True, capture_output=True)  # noqa: S607
    subprocess.run(["git", "commit", "-m", "Second"], cwd=path, check=True, capture_output=True)  # noqa: S607
    subprocess.run(
        ["git", "remote", "set-url", "origin", f"https://github.com/{slug}.git"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )


def _github_remote(repo: Path, slug: str) -> None:
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/me/{slug}.git"],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _local_iso(*, days_ago: int) -> str:
    moment = datetime.now().astimezone() - timedelta(days=days_ago)
    return moment.replace(hour=15, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")


def _recommit_at(repo: Path, when: str) -> None:
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit"],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_date_env(when),
    )
