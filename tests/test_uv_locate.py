"""Tests for locating uv outside of a stale process PATH."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from harrix_swiss_knife.actions.development.update_uv import OnUpdateUv
from harrix_swiss_knife.uv_locate import find_uv_exe


def test_find_uv_exe_falls_back_to_local_bin(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.uv_locate.shutil.which", lambda _name: None)
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))
    uv = tmp_path / ".local" / "bin" / "uv.exe"
    uv.parent.mkdir(parents=True)
    uv.write_bytes(b"")
    found = find_uv_exe()
    assert found == uv


def test_find_uv_exe_prefers_which(tmp_path: Path, monkeypatch) -> None:
    which_uv = tmp_path / "path-uv.exe"
    which_uv.write_bytes(b"")
    monkeypatch.setattr("harrix_swiss_knife.uv_locate.shutil.which", lambda _name: str(which_uv))
    assert find_uv_exe() == which_uv


def test_update_uv_uses_absolute_path_when_not_on_path(tmp_path: Path, monkeypatch) -> None:
    uv = tmp_path / ".local" / "bin" / "uv.exe"
    uv.parent.mkdir(parents=True)
    uv.write_bytes(b"")
    monkeypatch.setattr("harrix_swiss_knife.actions.development.update_uv.refresh_path", lambda: None)
    monkeypatch.setattr("harrix_swiss_knife.actions.development.update_uv.find_uv_exe", lambda: uv)

    with patch("harrix_swiss_knife.actions.development.update_uv.h.dev.run_command", return_value="ok") as run:
        result = OnUpdateUv().in_thread()

    assert result is not None
    assert str(uv) in result
    run.assert_called_once_with([str(uv), "self", "update"], is_shell=False)


def test_update_uv_reports_missing_uv_clearly(monkeypatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.actions.development.update_uv.refresh_path", lambda: None)
    monkeypatch.setattr("harrix_swiss_knife.actions.development.update_uv.find_uv_exe", lambda: None)
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.development.update_uv.OnUpdateUv._windows_winget_blocks",
        lambda _self: [],
    )
    result = OnUpdateUv().in_thread()
    assert result is not None
    assert "uv not found" in result
    assert "WinError" not in result
