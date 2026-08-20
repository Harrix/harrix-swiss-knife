"""Tests for startup diagnostics helpers."""

from __future__ import annotations

import faulthandler
import logging
from typing import TYPE_CHECKING
from unittest.mock import patch

from harrix_swiss_knife import app_startup, desktop_shortcut
from harrix_swiss_knife.app_startup import install_diagnostic_handlers, is_ignored_qt_message

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_is_ignored_qt_message_filters_svg_noise() -> None:
    assert is_ignored_qt_message(
        r"D:\Dropbox\Graphic\Vector\Background\light (4).svg:1:2004848: Could not resolve property: #aoG"
    )
    assert is_ignored_qt_message("Invalid path data; path truncated.")
    assert is_ignored_qt_message("link #SVGID_1_ is undefined!")
    assert not is_ignored_qt_message("QPainter::begin: Paint device returned engine == 0")
    assert not is_ignored_qt_message("")


def test_install_diagnostic_handlers_without_stderr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Shortcuts start the app through `pythonw.exe`, where `sys.stderr` is `None`."""
    monkeypatch.setattr(app_startup.sys, "stderr", None)
    monkeypatch.setattr(app_startup, "get_log_dir", lambda: tmp_path)
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    try:
        install_diagnostic_handlers(logging.getLogger("test_app_startup"))
        assert faulthandler.is_enabled()
        assert (tmp_path / "faulthandler.log").is_file()
    finally:
        faulthandler.disable()
        for handler in list(root.handlers):
            if handler not in handlers_before:
                root.removeHandler(handler)


def test_app_shortcut_targets_pythonw_launcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "harrix-swiss-knife"
    scripts = root / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "pythonw.exe").write_bytes(b"x")
    (scripts / "harrix-swiss-knife.exe").write_bytes(b"x")
    (root / "launch_tray.py").write_text("#", encoding="utf-8")
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    captured: dict[str, object] = {}

    def fake_write(lnk_path: Path, **kwargs: object) -> None:
        captured.update(kwargs)
        lnk_path.write_text("lnk", encoding="utf-8")

    monkeypatch.setattr(desktop_shortcut.sys, "platform", "win32")
    with (
        patch.object(desktop_shortcut, "_get_shell_folder", return_value=desktop),
        patch.object(desktop_shortcut, "_write_shortcut_file", side_effect=fake_write),
    ):
        lnk = desktop_shortcut.create_desktop_shortcut(root)

    assert lnk == desktop / desktop_shortcut.SHORTCUT_NAME
    assert captured["target"] == scripts / "pythonw.exe"
    assert captured["arguments"] == f'"{root / "launch_tray.py"}"'


def test_remove_desktop_uninstall_shortcut(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    lnk = desktop / desktop_shortcut.UNINSTALL_SHORTCUT_NAME
    lnk.write_text("lnk", encoding="utf-8")
    monkeypatch.setattr(desktop_shortcut.sys, "platform", "win32")
    with patch.object(desktop_shortcut, "_get_shell_folder", return_value=desktop):
        assert desktop_shortcut.remove_desktop_uninstall_shortcut() == lnk
        assert desktop_shortcut.remove_desktop_uninstall_shortcut() is None
    assert not lnk.exists()
