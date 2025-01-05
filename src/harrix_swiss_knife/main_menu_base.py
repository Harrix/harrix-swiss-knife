from typing import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu

from harrix_swiss_knife import functions as f


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

    def get_icon(self, icon: str) -> QIcon:
        """
        Retrieves an icon for menu items.

        Args:

        - `icon` (`str`): The path or description of the icon in `resources_rc.py`. Example: "rye.svg", "🏆"

        Returns:

        - `QIcon`: A QIcon object for the given icon path or emoji icon.
        """
        return QIcon(f":/assets/{icon}") if ".svg" in icon else f.pyside_create_emoji_icon(icon)

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
        filename = f.get_project_root() / "README.md"
        list_of_menu = "\n".join(f.pyside_generate_markdown_from_qmenu(self.menu))

        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        start_index = end_index = None
        for i, line in enumerate(lines):
            if line.startswith("## List of commands"):
                start_index = i
            elif start_index is not None and line.startswith("##") and i != start_index:
                end_index = i
                break

        if start_index is not None and end_index is not None:
            new_lines = "".join(lines[: start_index + 1]) + "\n" + list_of_menu + "\n\n" + "".join(lines[end_index:])
            with open(filename, "w", encoding="utf-8") as file:
                file.writelines(new_lines)

        return list_of_menu

    def new_menu(self, title: str, icon: str) -> QMenu:
        """
        Creates and returns a new QMenu with a title and an icon.

        Args:

        - `title` (`str`): The title of the new menu.
        - `icon` (`str`): Path in `resources_rc.py` or emoji for the icon of the menu. Example: "rye.svg", "🏆".

        Returns:

        - `QMenu`: A newly created QMenu object.
        """
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu
