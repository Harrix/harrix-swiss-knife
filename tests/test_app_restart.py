"""Tests for restarting the running application."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from harrix_swiss_knife.app_restart import restart_argv, restart_current_application, spawn_replacement_process


def test_restart_argv_starts_with_current_interpreter() -> None:
    argv = restart_argv()
    assert argv[0] == sys.executable
    assert argv[1:] == sys.argv


def test_spawn_replacement_process_uses_detached_flags() -> None:
    with patch("harrix_swiss_knife.app_restart.subprocess.Popen") as popen:
        popen.return_value = MagicMock()
        proc = spawn_replacement_process(["python", "main.py"])

    assert proc is popen.return_value
    kwargs = popen.call_args.kwargs
    if sys.platform == "win32":
        assert kwargs["creationflags"]
        assert "start_new_session" not in kwargs
    else:
        assert kwargs["start_new_session"] is True


def test_spawn_replacement_process_returns_none_on_os_error() -> None:
    with patch("harrix_swiss_knife.app_restart.subprocess.Popen", side_effect=OSError("fail")):
        assert spawn_replacement_process(["python", "main.py"]) is None


def test_restart_current_application_quits_qt_after_spawn() -> None:
    app = MagicMock()
    with (
        patch("harrix_swiss_knife.app_restart.release_held_instance") as release,
        patch("harrix_swiss_knife.app_restart.spawn_replacement_process", return_value=MagicMock()),
        patch("harrix_swiss_knife.app_restart.QApplication.instance", return_value=app),
    ):
        assert restart_current_application() is True
    release.assert_called_once()
    app.quit.assert_called_once()


def test_restart_current_application_does_not_quit_when_spawn_fails() -> None:
    app = MagicMock()
    held = MagicMock()
    with (
        patch("harrix_swiss_knife.app_restart.release_held_instance", return_value=held),
        patch("harrix_swiss_knife.app_restart.restore_held_instance") as restore,
        patch("harrix_swiss_knife.app_restart.spawn_replacement_process", return_value=None),
        patch("harrix_swiss_knife.app_restart.QApplication.instance", return_value=app),
    ):
        assert restart_current_application() is False
    restore.assert_called_once_with(held)
    app.quit.assert_not_called()


def test_restart_current_application_releases_singleton_before_spawn() -> None:
    order: list[str] = []

    def release() -> None:
        order.append("release")

    def spawn() -> MagicMock:
        order.append("spawn")
        return MagicMock()

    with (
        patch("harrix_swiss_knife.app_restart.release_held_instance", side_effect=release),
        patch("harrix_swiss_knife.app_restart.spawn_replacement_process", side_effect=spawn),
        patch("harrix_swiss_knife.app_restart.QApplication.instance", return_value=MagicMock()),
    ):
        assert restart_current_application() is True
    assert order == ["release", "spawn"]
