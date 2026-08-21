"""Tests for hidden subprocess helpers used by `hsk py check`."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from harrix_swiss_knife.actions.common.subprocess_run import (
    hidden_subprocess_kwargs,
    run_argv,
    venv_module_argv,
    venv_python,
)


def test_hidden_subprocess_kwargs_hides_console_on_windows() -> None:
    kwargs = hidden_subprocess_kwargs()
    if sys.platform != "win32":
        assert kwargs == {}
        return
    assert kwargs["creationflags"] == subprocess.CREATE_NO_WINDOW
    startupinfo = kwargs["startupinfo"]
    assert startupinfo.dwFlags & subprocess.STARTF_USESHOWWINDOW
    assert startupinfo.wShowWindow == subprocess.SW_HIDE


def test_run_argv_uses_hidden_console_kwargs(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.subprocess_run.subprocess.run",
        fake_run,
    )
    run_argv(["python", "--version"])
    if sys.platform == "win32":
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
    else:
        assert "creationflags" not in captured


def test_venv_module_argv_uses_project_python_not_uv(tmp_path: Path) -> None:
    argv = venv_module_argv(tmp_path, "pytest")
    assert argv[0] == str(venv_python(tmp_path))
    assert argv[1:3] == ["-m", "pytest"]
    assert "uv" not in argv


def test_venv_python_points_at_scripts_on_windows(tmp_path: Path) -> None:
    python = venv_python(tmp_path)
    if sys.platform == "win32":
        assert python == tmp_path / ".venv" / "Scripts" / "python.exe"
    else:
        assert python == tmp_path / ".venv" / "bin" / "python"
