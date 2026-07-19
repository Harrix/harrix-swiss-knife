"""Actions for Python development and code management."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase


class OnExit(ActionBase):
    """Exit the application.

    This action terminates the current Qt application instance,
    closing all application dialogs and ending the program execution.

    """

    icon = "×"  # noqa: RUF001
    title = "Exit"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Exit the application."""
        QApplication.quit()
