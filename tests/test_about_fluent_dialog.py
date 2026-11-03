"""Tests for the Fluent About dialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.common.about_fluent_dialog import FluentAboutDialog
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.text import FluentHyperlinkLabel, TitleLabel


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_fluent_about_dialog_builds_content_and_copy_text(qapp: QApplication) -> None:
    assert qapp is not None
    copied: list[str] = []
    dialog = FluentAboutDialog(
        app_name="Harrix Swiss Knife",
        version="1.2.3",
        description="A multifunctional tool for developers.",
        author="Anton Severienko (Harrix)",
        license_text="MIT License",
        github="https://github.com/harrix/harrix-swiss-knife",
        on_copied=lambda: copied.append("ok"),
    )
    titles = dialog.findChildren(TitleLabel)
    assert any(label.text() == "Harrix Swiss Knife" for label in titles)
    links = dialog.findChildren(FluentHyperlinkLabel)
    assert links and links[0].url() == "https://github.com/harrix/harrix-swiss-knife"
    assert isinstance(dialog.primary_button, FluentPrimaryButton)
    copy_buttons = [button for button in dialog.findChildren(FluentPushButton) if button.text() == "Copy"]
    assert copy_buttons
    text = dialog.clipboard_text()
    assert "Harrix Swiss Knife" in text
    assert "Version: 1.2.3" in text
    assert "MIT License" in text
    copy_buttons[0].click()
    assert copied == ["ok"]
    assert QApplication.clipboard().text() == text
    dialog.close()
