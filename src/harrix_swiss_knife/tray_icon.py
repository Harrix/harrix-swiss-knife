"""
Module providing a system tray icon implementation for the Harrix Swiss Knife application.

This module defines the TrayIcon class, which extends QSystemTrayIcon to provide
functionality for displaying the application in the system tray with appropriate
context menu and interaction handling.
"""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from harrix_swiss_knife import main_window


class TrayIcon(QSystemTrayIcon):
    """Represent a system tray icon with an associated context menu and main window.

    Attributes:

    - `main_window` (`main_window.MainWindow | None`):
      The main window associated with the tray icon. Defaults to `None`.
    - `menu` (`QMenu`):
      The context menu displayed when interacting with the tray icon.

    """

    def __init__(self, icon: QIcon, menu: QMenu, parent: QWidget | None = None) -> None:
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
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle the activation event of the system tray icon.

        Args:

        - `reason` (`QSystemTrayIcon.ActivationReason`):
          The reason for the activation event.

        If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window is None:
                self.main_window = main_window.MainWindow(self.menu)
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
