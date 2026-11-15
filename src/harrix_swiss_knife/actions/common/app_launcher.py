"""Base class for application launcher actions."""

from __future__ import annotations

import importlib
import inspect
import traceback
from typing import Any, ClassVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.common.app_startup_toast import app_loading_toast_scope
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.apps.common.uic_compile import install_safe_qt_translate


class AppLauncherAction(ActionBase):
    """Launch a tracker application window, reusing an existing instance when valid."""

    main_window_module: ClassVar[str] = ""
    main_window_class_name: ClassVar[str] = "MainWindow"
    _resolved_main_window_class: ClassVar[type | None] = None

    hide_on_close: ClassVar[bool] = False

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize launcher state and optional parent widget."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None
        self._is_creating_window = False

    @ActionBase.handle_exceptions("launching application")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show an existing app window or create a new one.

        Keyword Args:

        - `presentation_mode` (`bool`): When `True`, open (or switch to) a temp
          fake database. Defaults to `False`.

        """
        presentation_mode = bool(kwargs.get("presentation_mode", False))

        if self.main_window is not None and isValid(self.main_window):
            current = bool(getattr(self.main_window, "presentation_mode", False))
            if current == presentation_mode:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                return
            if presentation_mode or current:
                self._destroy_main_window_for_mode_switch()
            else:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                return

        if self._is_creating_window:
            return

        app = QApplication.instance()
        if app is not None:
            self.main_window = None
            for _ in range(10):
                app.processEvents()

        self._is_creating_window = True
        try:
            with app_loading_toast_scope(self.title):
                install_safe_qt_translate()
                window_cls = type(self).get_main_window_class()
                window_kwargs: dict[str, Any] = {"hide_on_close": type(self).hide_on_close}
                if "presentation_mode" in inspect.signature(window_cls.__init__).parameters:
                    window_kwargs["presentation_mode"] = presentation_mode
                window = window_cls(**window_kwargs)
                self.main_window = window
                window.destroyed.connect(self._clear_main_window_ref)
                if getattr(window, "defer_initial_show", False):
                    return
                self.main_window.show()
                apply_app_window_size_and_position(self.main_window)
                self.main_window.raise_()
                self.main_window.activateWindow()
        except Exception:
            self.main_window = None
            traceback.print_exc()
            raise
        finally:
            self._is_creating_window = False

    @classmethod
    def get_main_window_class(cls) -> type:
        """Import and cache the tracker `MainWindow` class on first use."""
        if cls._resolved_main_window_class is None:
            module = importlib.import_module(cls.main_window_module)
            cls._resolved_main_window_class = getattr(module, cls.main_window_class_name)
        return cls._resolved_main_window_class

    def _clear_main_window_ref(self, *_args: object) -> None:
        self.main_window = None

    def _destroy_main_window_for_mode_switch(self) -> None:
        """Close the live window so the next launch can use a different DB mode."""
        window = self.main_window
        self.main_window = None
        if window is None or not isValid(window):
            return
        if hasattr(window, "_hide_on_close"):
            window._hide_on_close = False  # noqa: SLF001
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        window.close()
        app = QApplication.instance()
        if app is not None:
            for _ in range(20):
                if not isValid(window):
                    break
                app.processEvents()
