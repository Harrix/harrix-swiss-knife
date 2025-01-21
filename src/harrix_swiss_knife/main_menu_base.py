from typing import Callable

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu


class MainMenuBase:
    """
    A base class for handling menu operations in a PyQt application.

    This class provides methods to create and manage menu items,
    retrieve icons, and generate documentation for menu items in a README file.

    Attributes:

    - `menu` (`QMenu`): The main menu object for the application, initialized in `__init__`.
    """

    def __init__(self):
        """
        Initializes the `MainMenuBase` with an empty QMenu.
        """
        self.menu = QMenu()

    def add_item(self, menu: QMenu, class_action: Callable, icon: str = "") -> None:
        """
        Adds an item to the given menu.

        Args:

        - `menu` (`QMenu`): The menu to which the action will be added.
        - `class_action` (`Callable`): The callable to be executed when the menu item is triggered.
        - `icon` (`str`, optional): Path or emoji for the icon of the menu item. Defaults to `""`.

        Returns:

        - `None`
        """
        action_instance = class_action(parent=self)

        if icon:
            action = QAction(self.get_icon(icon), action_instance.title, triggered=action_instance)
        elif hasattr(action_instance, "icon") and action_instance.icon:
            action = QAction(self.get_icon(action_instance.icon), action_instance.title, triggered=action_instance)
        else:
            action = QAction(action_instance.title, triggered=action_instance)
        setattr(self, f"action_{class_action.__name__}", action)

        if hasattr(action_instance, "tip") and action_instance.tip:
            action.setToolTip(action_instance.tip)

        menu.addAction(action)

    def get_icon(self, icon: str, size: int = 32) -> QIcon:
        """
        Retrieves an icon for menu items.

        Args:

        - `icon` (`str`): The path or description of the icon in `resources_rc.py`. Example: "uv.svg", "🏆".
        - `size` (`int`): The size of the icon in pixels. Defaults to `32`.

        Returns:

        - `QIcon`: A QIcon object for the given icon path or emoji icon.
        """
        if ".svg" in icon:
            # Load the icon from the assets if it's an SVG file
            return QIcon(f":/assets/{icon}")
        else:
            # Generate a safe filename for the emoji icon
            filename = f"emoji_{'_'.join(f'{ord(c):X}' for c in icon)}.png"
            icon_folder = h.dev.get_project_root() / "temp" / "icons"
            icon_path = icon_folder / filename

            if icon_path.exists():
                # If the icon already exists, load it from the file
                return QIcon(str(icon_path))
            else:
                return h.pyside.create_emoji_icon(icon, size)

    def get_menu(self) -> str:
        """
        Updates the README.md file with the current menu structure.

        This method:

        - Reads the content of README.md.
        - Locates the section to update by looking for "## List of commands" and the next heading.
        - Inserts the current menu structure into the file between these markers.
        - Overwrites the README.md with the updated content.
        - Returns the markdown representation of the menu.

        Args:

        Returns:

        - `str`: The markdown formatted menu list.

        """
        filename = h.dev.get_project_root() / "README.md"
        list_of_menu = "\n".join(h.pyside.generate_markdown_from_qmenu(self.menu))

        h.md.replace_section(filename, list_of_menu, "## List of commands")

        return list_of_menu

    def new_menu(self, title: str, icon: str) -> QMenu:
        """
        Creates and returns a new QMenu with a title and an icon.

        Args:

        - `title` (`str`): The title of the new menu.
        - `icon` (`str`): Path in `resources_rc.py` or emoji for the icon of the menu. Example: "uv.svg", "🏆".

        Returns:

        - `QMenu`: A newly created QMenu object.
        """
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu
