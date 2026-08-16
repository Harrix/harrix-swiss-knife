"""Tests for argv-based editor launcher."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from harrix_swiss_knife.actions.common.open_in_editor import open_in_editor

if TYPE_CHECKING:
    from pathlib import Path


def test_open_in_editor_uses_argv_list_not_shell() -> None:
    completed = MagicMock()
    completed.stdout = ""
    completed.stderr = ""
    with (
        patch("harrix_pylib.funcs_dev.shutil.which", return_value="code-insiders"),
        patch("harrix_pylib.funcs_dev.subprocess.run", return_value=completed) as run,
    ):
        open_in_editor("code-insiders", r"D:\ws\Notes.code-workspace", r"D:\notes\file.md")

    run.assert_called_once()
    args, kwargs = run.call_args
    assert args[0] == ["code-insiders", r"D:\ws\Notes.code-workspace", r"D:\notes\file.md"]
    assert kwargs["shell"] is False


def test_open_in_editor_rejects_empty_editor() -> None:
    with pytest.raises(ValueError, match="empty"):
        open_in_editor("  ", "ws", "file.md")


def test_open_in_editor_timeout_message(tmp_path: Path) -> None:
    with (
        patch("harrix_pylib.funcs_dev.shutil.which", return_value="editor"),
        patch(
            "harrix_pylib.funcs_dev.subprocess.run",
            side_effect=__import__("subprocess").TimeoutExpired(cmd="editor", timeout=1),
        ),
    ):
        result = open_in_editor("editor", tmp_path / "ws", tmp_path / "f.md", timeout=1.0)
    assert "timed out" in result.lower()
