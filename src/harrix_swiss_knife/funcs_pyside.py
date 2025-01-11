from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu


def create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
    """
    Creates an icon with the given emoji.

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


def generate_markdown_from_qmenu(menu: QMenu, level: int = 0) -> List[str]:
    """
    Generates a markdown representation of a QMenu structure.

    This function traverses the QMenu and its submenus to produce a nested list in markdown format.

    Args:

    - `menu` (`QMenu`): The QMenu object to convert to markdown.
    - `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

    Returns:

    - `List[str]`: A list of strings, each representing a line of markdown text that describes the menu structure.
    """
    markdown_lines: List[str] = []
    for action in menu.actions():
        if action.menu():  # If the action has a submenu
            # Add a header for the submenu
            markdown_lines.append(f'{"  " * level}- **{action.text()}**')
            # Recursively traverse the submenu
            markdown_lines.extend(generate_markdown_from_qmenu(action.menu(), level + 1))
        else:
            # Add a regular menu item
            if action.text():
                markdown_lines.append(f'{"  " * level}- {action.text()}')
    return markdown_lines
