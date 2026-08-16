"""Tests for public Notes Explorer sync (strip HSK CLI from Icons Browse menu)."""

from __future__ import annotations

import json
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.actions.vscode.sync_harrix_notes_explorer import OnSyncHarrixNotesExplorer


def _hsk_extension_dir() -> Path:
    return h.dev.get_project_root() / "vscode" / "harrix-notes-explorer-hsk"


def _cli_manifest() -> dict[str, object]:
    path = _hsk_extension_dir() / "package.harrix-cli.contributes.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _cli_command_ids(manifest: dict[str, object]) -> list[str]:
    raw = manifest.get("commandIds")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, str)]


def test_strip_cli_from_icons_browse_menu_removes_hsk_commands() -> None:
    source = (_hsk_extension_dir() / "icons-browse-menu.js").read_text(encoding="utf-8")
    manifest = _cli_manifest()
    stripped = OnSyncHarrixNotesExplorer._strip_cli_from_icons_browse_menu(source, manifest)

    for command_id in _cli_command_ids(manifest):
        short = command_id.rsplit(".", 1)[-1]
        assert f"CMD.{short}" not in stripped
        assert f"{short}:" not in stripped

    assert "discardGitChangesInFolder" in stripped
    assert "createNote" in stripped
    assert "beautifyMd" not in stripped
    assert "regenerateGMd" not in stripped
    assert "beautifyRegenerateGMd" not in stripped
