"""Hide and restore application Windows during screenshot capture."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

HSK_SCREENSHOT_UI_PROP = "hsk_screenshot_ui"


def hide_app_windows() -> list[QWidget]:
    """Hide all visible top-level application Windows except screenshot UI.

    Returns:
    Widgets that were hidden and should be restored later.

    """
    app = QApplication.instance()
    if app is None:
        return []

    hidden: list[QWidget] = []
    for widget in app.topLevelWidgets():
        if not widget.isVisible():
            continue
        if is_screenshot_ui(widget):
            continue
        widget.hide()
        hidden.append(widget)

    QApplication.processEvents()
    return hidden


def is_screenshot_ui(widget: QWidget) -> bool:
    """Return whether the widget belongs to the screenshot capture UI."""
    return bool(widget.property(HSK_SCREENSHOT_UI_PROP))


def mark_screenshot_ui(widget: QWidget) -> None:
    """Mark a widget so it is not hidden with the rest of the application."""
    widget.setProperty(HSK_SCREENSHOT_UI_PROP, True)  # noqa: FBT003


def restore_app_windows(widgets: list[QWidget]) -> None:
    """Show Windows previously hidden by `hide_app_windows`."""
    for widget in widgets:
        widget.show()
    QApplication.processEvents()
