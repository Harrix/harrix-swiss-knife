"""Base class for application launcher actions."""

from __future__ import annotations

from typing import Any, ClassVar

from shiboken6 import isValid

from harrix_swiss_knife.actions.base import ActionBase


class AppLauncherAction(ActionBase):
    """Launch a tracker application window, reusing an existing instance when valid."""

    main_window_class: ClassVar[type]
    show_in_compact_mode: ClassVar[bool] = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching application")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = self.main_window_class()
            self.main_window.destroyed.connect(self._clear_main_window_ref)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _clear_main_window_ref(self, *_args: object) -> None:
        self.main_window = None
