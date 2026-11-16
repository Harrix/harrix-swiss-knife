"""Tests for Git working-tree change discovery used by `--only-changed`."""

from __future__ import annotations

import subprocess
from pathlib import Path

from harrix_swiss_knife.actions.common.git_changed_files import (
    git_repo_root,
    list_changed_python_files,
    list_git_changed_files,
)
from harrix_swiss_knife.actions.python.sort_ruff_fmt_docs_python_code import OnSortRuffFmtDocsPythonCode


def test_docs_relative_path_strips_package_root() -> None:
    src = Path("src")
    py_file = src / "harrix_swiss_knife" / "actions" / "foo.py"
    relative = OnSortRuffFmtDocsPythonCode._docs_g_md_relative_path(py_file, src)
    assert relative.as_posix() == "actions/foo.g.md"


def test_git_repo_root_and_changed_python(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    assert git_repo_root(repo / "src") == repo.resolve()

    tracked = repo / "src" / "pkg" / "tracked.py"
    tracked.write_text("x = 2\n", encoding="utf-8")
    untracked = repo / "src" / "pkg" / "new_mod.py"
    untracked.write_text("y = 1\n", encoding="utf-8")
    (repo / "readme.txt").write_text("hi\n", encoding="utf-8")

    changed = list_git_changed_files(repo)
    assert tracked.resolve() in changed
    assert untracked.resolve() in changed

    py_only = list_changed_python_files(repo)
    assert py_only is not None
    assert tracked.resolve() in py_only
    assert untracked.resolve() in py_only
    assert all(path.suffix == ".py" for path in py_only)


def test_list_changed_python_files_none_outside_git(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    assert list_changed_python_files(plain) is None


def test_only_changed_noop_when_clean(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "pyproject.toml").write_text("[project]\nname='x'\nversion='0'\n", encoding="utf-8")
    action = OnSortRuffFmtDocsPythonCode()
    action.format_and_sort_python_common(str(repo), is_include_docs_generation=False, only_changed=True)
    assert any("nothing to do" in line.lower() for line in action.result_lines)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)  # noqa: S607


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    tracked = repo / "src" / "pkg" / "tracked.py"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "src/pkg/tracked.py")
    _git(repo, "commit", "-m", "init")
    return repo
