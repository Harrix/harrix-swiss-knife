"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING

import harrix_swiss_knife.main_menu_base as main_menu_base
from harrix_swiss_knife.app_startup import (
    install_diagnostic_handlers,
    log_startup_context,
    run_tray_application,
    setup_file_logging,
    show_fatal_error_dialog,
)
from harrix_swiss_knife.menu_structure import get_menu_structure

if TYPE_CHECKING:
    from harrix_swiss_knife.action_output_bus import ActionOutputBus


class MainMenu(main_menu_base.MainMenuBase):
    """Main menu class that defines the application's menu structure.

    This class extends the MainMenuBase class and creates all the menu items
    and submenus for the application.
    """

    def __init__(self, *, output_bus: ActionOutputBus, config: dict | None = None) -> None:
        """Initialize the main menu with all submenus and actions.

        Create and organizes all menu categories and their respective items.
        """
        super().__init__(output_bus=output_bus, config=config)
        self.add_menu_structure(self.menu, get_menu_structure())


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    log_path = setup_file_logging()
    log = logging.getLogger("harrix_swiss_knife")
    install_diagnostic_handlers(log)
    log_startup_context(log, log_path)

    try:
        rc = run_tray_application(log, main_menu_cls=MainMenu)
        sys.exit(rc)
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log.exception("Fatal error during startup; exiting.")
        show_fatal_error_dialog(f"Fatal error during startup.\n\nLog: {log_path}\n\n{tb}")
        sys.exit(1)


if __name__ == "__main__":
    main()
