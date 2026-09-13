"""Tests for generated-site Git deploy helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.site_deploy import (
    DEPLOY_COMMIT_MESSAGE,
    DEPLOY_REMOTE_NAME,
    deploy_generated_site,
    should_offer_deploy,
)
from harrix_swiss_knife.actions.common.subprocess_run import run_argv_output

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")


def test_should_offer_deploy_with_remote_or_git(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert should_offer_deploy(empty, None) is False
    assert should_offer_deploy(empty, "root@127.0.0.1:/var/git/site.git") is True

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    assert should_offer_deploy(repo, None) is True


def test_deploy_generated_site_commits_and_pushes(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<h1>Hello</h1>\n", encoding="utf-8")
    bare = tmp_path / "remote.git"
    _git(tmp_path, "init", "--bare", str(bare))

    ok, log = deploy_generated_site(site, remote_url=str(bare))
    assert ok, log
    assert "Pushed" in log

    clone = tmp_path / "clone"
    _git(tmp_path, "clone", str(bare), str(clone))
    assert (clone / "index.html").read_text(encoding="utf-8") == "<h1>Hello</h1>\n"
    subject = _git_out(clone, "log", "-1", "--pretty=format:%s")
    assert subject == DEPLOY_COMMIT_MESSAGE


def test_deploy_generated_site_skips_when_clean(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<h1>Hello</h1>\n", encoding="utf-8")
    bare = tmp_path / "remote.git"
    _git(tmp_path, "init", "--bare", str(bare))
    ok, log = deploy_generated_site(site, remote_url=str(bare))
    assert ok, log

    ok, log = deploy_generated_site(site, remote_url=str(bare))
    assert ok, log
    assert "No changes to commit." in log


def test_deploy_generated_site_updates_remote_url(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<h1>One</h1>\n", encoding="utf-8")
    first = tmp_path / "first.git"
    second = tmp_path / "second.git"
    _git(tmp_path, "init", "--bare", str(first))
    _git(tmp_path, "init", "--bare", str(second))

    ok, log = deploy_generated_site(site, remote_url=str(first))
    assert ok, log
    (site / "index.html").write_text("<h1>Two</h1>\n", encoding="utf-8")
    ok, log = deploy_generated_site(site, remote_url=str(second))
    assert ok, log
    url = _git_out(site, "remote", "get-url", DEPLOY_REMOTE_NAME)
    assert Path(url).resolve() == second.resolve()


def _git(cwd: Path, *args: str) -> None:
    code, output = run_argv_output(["git", *args], cwd=cwd)
    assert code == 0, output


def _git_out(cwd: Path, *args: str) -> str:
    code, output = run_argv_output(["git", *args], cwd=cwd)
    assert code == 0, output
    return output.strip()
