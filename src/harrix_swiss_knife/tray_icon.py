"""Module providing a system tray icon implementation for the Harrix Swiss Knife application.

This module defines the TrayIcon class, which extends QSystemTrayIcon to provide
functionality for displaying the application in the system tray with appropriate
context menu and interaction handling.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from harrix_swiss_knife import main_window
from harrix_swiss_knife.main_menu_base import set_menu_tooltips_visible_recursive

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon


class TrayIcon(QSystemTrayIcon):
    """Represent a system tray icon with an associated context menu and main window.

    Attributes:

    - `main_window` (`main_window.MainWindow | None`):
      The main window associated with the tray icon. Defaults to `None`.
    - `menu` (`QMenu`):
      The context menu displayed when interacting with the tray icon.

    """

    _instance: ClassVar[TrayIcon | None] = None

    def __init__(
        self,
        icon: QIcon,
        menu: QMenu,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the `TrayIcon` with the given icon and menu.

        Args:

        - `icon` (`QIcon`):
          The icon to display in the system tray.
        - `menu` (`QMenu`):
          The context menu to associate with the tray icon.
        - `parent` (`QWidget | None`):
          The parent widget. Defaults to `None`.

        Sets up the system tray icon, context menu, and connects the activation signal
        to handle user interactions.

        """
        super().__init__(icon, parent)
        TrayIcon._instance = self
        set_menu_tooltips_visible_recursive(menu)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu

    @classmethod
    def active(cls) -> TrayIcon | None:
        """Return the process tray icon, if one was created."""
        return cls._instance

    def ensure_main_window(self) -> main_window.MainWindow:
        """Create the main window on first use."""
        if self.main_window is None:
            self.main_window = main_window.MainWindow(self.menu)
        return self.main_window

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle the activation event of the system tray icon.

        Args:

        - `reason` (`QSystemTrayIcon.ActivationReason`):
          The reason for the activation event.

        If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_command_window()

    def show_command_window(self) -> None:
        """Show the command-cards window and bring it to the front."""
        window = self.ensure_main_window()
        window.show()
        window.raise_()
        window.activateWindow()
        window.focus_initial_input()


def show_command_window() -> bool:
    """Show the tray command-cards window when a tray icon exists.

    Returns:

    - `bool`: `True` when the window was shown.

    """
    tray = TrayIcon.active()
    if tray is None:
        return False
    tray.show_command_window()
    return True
