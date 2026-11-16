"""Tests for Cursor AI backup packing."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from harrix_swiss_knife.cursor_backup.pack import (
    BackupPart,
    pack_cursor_backup,
    parts_from_labels,
)
from harrix_swiss_knife.cursor_backup.paths import (
    discover_project_cursor_dirs,
    iter_dot_cursor_entries,
)


@pytest.fixture
def fake_cursor_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    return home


def test_parts_from_labels() -> None:
    assert parts_from_labels(
        [
            "Cursor User (settings, chats, workspaceStorage)",
            "Home .cursor/extensions",
        ]
    ) == [BackupPart.USER, BackupPart.EXTENSIONS]


def test_discover_project_cursor_dirs(tmp_path: Path) -> None:
    project = tmp_path / "repo"
    cursor_dir = project / ".cursor"
    cursor_dir.mkdir(parents=True)
    (cursor_dir / "rules").mkdir()
    storage = tmp_path / "workspaceStorage" / "abc"
    storage.mkdir(parents=True)
    uri = project.resolve().as_uri()
    (storage / "workspace.json").write_text(json.dumps({"folder": uri}), encoding="utf-8")
    found = discover_project_cursor_dirs(tmp_path / "workspaceStorage")
    assert found == [cursor_dir]


def test_iter_dot_cursor_entries_skips_extensions(fake_cursor_home: Path) -> None:
    root = fake_cursor_home / ".cursor"
    (root / "projects").mkdir(parents=True)
    (root / "extensions").mkdir()
    (root / "skills-cursor").mkdir()
    (root / "browser-logs").mkdir()
    names = {path.name for path in iter_dot_cursor_entries()}
    assert names == {"projects", "skills-cursor"}


def test_pack_cursor_backup_writes_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    user = tmp_path / "User"
    user.mkdir()
    (user / "settings.json").write_text('{"editor.fontSize": 14}\n', encoding="utf-8")
    global_storage = user / "globalStorage"
    global_storage.mkdir()
    (global_storage / "state.vscdb").write_bytes(b"sqlite-fake")

    home = tmp_path / "home"
    dot = home / ".cursor"
    (dot / "projects" / "demo" / "agent-transcripts").mkdir(parents=True)
    (dot / "projects" / "demo" / "agent-transcripts" / "chat.jsonl").write_text("{}\n", encoding="utf-8")
    (dot / "extensions" / "ext").mkdir(parents=True)
    (dot / "extensions" / "ext" / "package.json").write_text("{}\n", encoding="utf-8")

    project = tmp_path / "repo"
    project_cursor = project / ".cursor"
    project_cursor.mkdir(parents=True)
    (project_cursor / "rules.mdc").write_text("rule\n", encoding="utf-8")
    storage = user / "workspaceStorage" / "ws1"
    storage.mkdir(parents=True)
    (storage / "workspace.json").write_text(json.dumps({"folder": project.resolve().as_uri()}), encoding="utf-8")

    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("harrix_swiss_knife.cursor_backup.pack.cursor_user_dir", lambda: user)
    monkeypatch.setattr("harrix_swiss_knife.cursor_backup.paths.cursor_user_dir", lambda: user)

    out = tmp_path / "backup.zip"
    result = pack_cursor_backup(
        out,
        [BackupPart.USER, BackupPart.DOT_CURSOR, BackupPart.EXTENSIONS, BackupPart.PROJECT_CURSOR],
    )
    assert result.zip_path == out.resolve()
    assert result.file_count >= 4
    with zipfile.ZipFile(out, "r") as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert "Cursor/User/settings.json" in names
        assert "Cursor/User/globalStorage/state.vscdb" in names
        assert any(name.startswith("dot-cursor/projects/") for name in names)
        assert any(name.startswith("dot-cursor/extensions/") for name in names)
        assert any(name.endswith("/.cursor/rules.mdc") for name in names)
        manifest = json.loads(archive.read("manifest.json"))
    assert set(manifest["parts"]) == {
        "cursor-user",
        "dot-cursor",
        "dot-cursor-extensions",
        "project-cursor",
    }


def test_pack_skips_missing_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "missing-user"
    home = tmp_path / "home"
    (home / ".cursor").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr("harrix_swiss_knife.cursor_backup.pack.cursor_user_dir", lambda: missing)
    out = tmp_path / "empty-user.zip"
    result = pack_cursor_backup(out, [BackupPart.USER, BackupPart.DOT_CURSOR])
    assert result.file_count == 0
    assert out.is_file()
