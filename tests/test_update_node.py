"""Tests for Update Node.js action install prompt flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from harrix_swiss_knife.actions.development.update_node import OnUpdateNode


def test_execute_asks_and_cancels_when_node_missing() -> None:
    action = OnUpdateNode()
    action.add_line = MagicMock()
    action.show_result = MagicMock()
    action.get_yes_no_question = MagicMock(return_value=False)
    action.start_thread = MagicMock()

    with (
        patch("harrix_swiss_knife.actions.development.update_node.sys.platform", "win32"),
        patch("harrix_swiss_knife.actions.development.update_node.refresh_path"),
        patch(
            "harrix_swiss_knife.actions.development.update_node.shutil.which",
            side_effect=lambda name: "winget" if name == "winget" else None,
        ),
    ):
        action.execute()

    action.get_yes_no_question.assert_called_once()
    action.start_thread.assert_not_called()
    joined = " ".join(str(c.args[0]) for c in action.add_line.call_args_list)
    assert "Cancelled" in joined


def test_execute_asks_and_starts_install_when_confirmed() -> None:
    action = OnUpdateNode()
    action.get_yes_no_question = MagicMock(return_value=True)
    action.start_thread = MagicMock()

    with (
        patch("harrix_swiss_knife.actions.development.update_node.sys.platform", "win32"),
        patch("harrix_swiss_knife.actions.development.update_node.refresh_path"),
        patch(
            "harrix_swiss_knife.actions.development.update_node.shutil.which",
            side_effect=lambda name: "winget" if name == "winget" else None,
        ),
    ):
        action.execute()

    assert action._do_install is True
    action.start_thread.assert_called_once()


def test_execute_skips_prompt_when_node_present() -> None:
    action = OnUpdateNode()
    action.get_yes_no_question = MagicMock()
    action.start_thread = MagicMock()

    with (
        patch("harrix_swiss_knife.actions.development.update_node.sys.platform", "win32"),
        patch("harrix_swiss_knife.actions.development.update_node.refresh_path"),
        patch(
            "harrix_swiss_knife.actions.development.update_node.shutil.which",
            side_effect=lambda name: f"C:\\\\fake\\\\{name}.exe",
        ),
    ):
        action.execute()

    action.get_yes_no_question.assert_not_called()
    assert action._do_install is False
    action.start_thread.assert_called_once()


def test_in_thread_installs_lts_when_requested() -> None:
    action = OnUpdateNode()
    action._do_install = True
    action._winget_install = MagicMock(return_value="Successfully installed")
    action._node_version_line = MagicMock(return_value="v22.0.0")

    with patch("harrix_swiss_knife.actions.development.update_node.refresh_path"):
        result = action.in_thread()

    assert result is not None
    assert "winget install (OpenJS.NodeJS.LTS)" in result
    assert "Installed Node.js LTS" in result
    assert "v22.0.0" in result
    action._winget_install.assert_called_once_with("OpenJS.NodeJS.LTS")
