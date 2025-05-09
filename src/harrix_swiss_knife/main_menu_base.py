from collections.abc import Callable

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu


class MainMenuBase:
    """A base class for handling menu operations in a PyQt application.

    This class provides methods to create and manage menu items,
    retrieve icons, and generate documentation for menu items in a README file.

    Attributes:

    - `menu` (`QMenu`): The main menu object for the application, initialized in `__init__`.

    """

    def __init__(self) -> None:
        """Initializes the `MainMenuBase` with an empty QMenu."""
        self.menu = QMenu()

    def add_item(self, menu: QMenu, class_action: Callable, icon="") -> None:
        """Adds an item to the given menu.

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
            action._icon = icon
        elif hasattr(action_instance, "icon") and action_instance.icon:
            action = QAction(self.get_icon(action_instance.icon), action_instance.title, triggered=action_instance)
            action._icon = action_instance.icon
        else:
            action = QAction(action_instance.title, triggered=action_instance)
        setattr(self, f"action_{class_action.__name__}", action)

        menu.addAction(action)

    def create_emoji_icon(self, emoji: str, size: int = 32) -> QIcon:
        """Creates an icon with the given emoji.

        Args:

        - `emoji` (`str`): The emoji to be used in the icon.
        - `size` (`int`): The size of the icon in pixels. Defaults to `32`.

        Returns:

        - `QIcon`: A QIcon object containing the emoji as an icon.

        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    def generate_markdown_from_qmenu(self, menu: QMenu, level: int = 0) -> list[str]:
        """Generates a markdown representation of a QMenu structure.

        This function traverses the QMenu and its submenus to produce a nested list in markdown format.

        Args:

        - `menu` (`QMenu`): The QMenu object to convert to markdown.
        - `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

        Returns:

        - `List[str]`: A list of strings, each representing a line of markdown text that describes the menu structure.

        """
        markdown_lines: list[str] = []
        for action in menu.actions():
            if action.menu():  # If the action has a submenu
                # Add a header for the submenu
                markdown_lines.append(f"{'  ' * level}- **{action.text()}**")
                # Recursively traverse the submenu
                markdown_lines.extend(self.generate_markdown_from_qmenu(action.menu(), level + 1))
            else:
                # Add a regular menu item
                icon = action._icon if hasattr(action, "_icon") and "." not in action._icon else ""
                if action.text():
                    markdown_lines.append(f"{'  ' * level}- {icon} {action.text()}")
        return markdown_lines

    def get_icon(self, icon: str, size: int = 32) -> QIcon:
        """Retrieves an icon for menu items.

        Args:

        - `icon` (`str`): The path or description of the icon in `resources_rc.py`. Example: "uv.svg", "🏆".
        - `size` (`int`): The size of the icon in pixels. Defaults to `32`.

        Returns:

        - `QIcon`: A QIcon object for the given icon path or emoji icon.

        """
        if ".svg" in icon:
            # Load the icon from the assets if it's an SVG file
            return QIcon(f":/assets/{icon}")
        # Generate a safe filename for the emoji icon
        filename = f"emoji_{'_'.join(f'{ord(c):X}' for c in icon)}.png"
        icon_folder = h.dev.get_project_root() / "temp" / "icons"
        icon_path = icon_folder / filename

        if icon_path.exists():
            # If the icon already exists, load it from the file
            return QIcon(str(icon_path))
        return self.create_emoji_icon(icon, size)

    def get_menu(self) -> str:
        """Updates the README.md file with the current menu structure.

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
        list_of_menu = "\n".join(self.generate_markdown_from_qmenu(self.menu))

        h.md.replace_section(filename, list_of_menu, "## List of commands")

        return list_of_menu

    def new_menu(self, title: str, icon: str) -> QMenu:
        """Creates and returns a new QMenu with a title and an icon.

        Args:

        - `title` (`str`): The title of the new menu.
        - `icon` (`str`): Path in `resources_rc.py` or emoji for the icon of the menu. Example: "uv.svg", "🏆".

        Returns:

        - `QMenu`: A newly created QMenu object.

        """
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu
