"""Tests for optional GitHub token resolution and download headers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.common.github_https import (
    github_api_headers,
    github_download_headers,
    is_github_hosted_url,
    resolve_github_token,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_resolve_github_token_prefers_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")
    token_file = tmp_path / "api-keys" / "github-token.txt"
    token_file.parent.mkdir(parents=True)
    token_file.write_text("file-token\n", encoding="utf-8")
    assert resolve_github_token(config={"github_token": "config-token"}, project_root=tmp_path) == "env-token"


def test_resolve_github_token_from_config_when_no_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert resolve_github_token(config={"github_token": "config-token"}, project_root=tmp_path) == "config-token"


def test_resolve_github_token_from_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    token_file = tmp_path / "api-keys" / "github-token.txt"
    token_file.parent.mkdir(parents=True)
    token_file.write_text("file-token\n# comment ignored\n", encoding="utf-8")
    assert resolve_github_token(config={}, project_root=tmp_path) == "file-token"


def test_resolve_github_token_ignores_placeholder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    token_file = tmp_path / "api-keys" / "github-token.txt"
    token_file.parent.mkdir(parents=True)
    token_file.write_text("paste-your-github-token-here-one-line-no-quotes\n", encoding="utf-8")
    assert (
        resolve_github_token(
            config={"github_token": "paste-your-github-token-here-one-line-no-quotes"},
            project_root=tmp_path,
        )
        == ""
    )


def test_resolve_github_token_missing_returns_empty(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert resolve_github_token(config={}, project_root=tmp_path) == ""


def test_is_github_hosted_url() -> None:
    assert is_github_hosted_url("https://github.com/owner/repo/releases/download/x/a.zip")
    assert is_github_hosted_url("https://api.github.com/repos/owner/repo/releases/latest")
    assert is_github_hosted_url("https://objects.githubusercontent.com/github-production-release-asset-2e65be/1")
    assert not is_github_hosted_url("https://update.code.visualstudio.com/latest/win32-x64-user/stable")
    assert not is_github_hosted_url("https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe")


def test_github_api_headers_with_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    headers = github_api_headers(project_root=tmp_path, user_agent="Test-UA")
    assert headers["Authorization"] == "Bearer secret"
    assert headers["User-Agent"] == "Test-UA"
    assert headers["Accept"] == "application/vnd.github+json"


def test_github_api_headers_without_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    headers = github_api_headers(config={}, project_root=tmp_path)
    assert "Authorization" not in headers


def test_github_download_headers_only_on_github(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    gh = github_download_headers(
        "https://github.com/astral-sh/uv/releases/latest/download/uv.zip",
        project_root=tmp_path,
    )
    assert gh["Authorization"] == "Bearer secret"
    other = github_download_headers(
        "https://update.code.visualstudio.com/latest/win32-x64-user/stable",
        project_root=tmp_path,
    )
    assert "Authorization" not in other
    assert "User-Agent" in other
