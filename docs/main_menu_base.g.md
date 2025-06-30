---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `main_menu_base.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `MainMenuBase`](#class-mainmenubase)
  - [Method `__init__`](#method-__init__)
  - [Method `_add_item`](#method-_add_item)
  - [Method `add_items`](#method-add_items)
  - [Method `add_menus_and_items`](#method-add_menus_and_items)
  - [Method `create_emoji_icon`](#method-create_emoji_icon)
  - [Method `generate_markdown_from_qmenu`](#method-generate_markdown_from_qmenu)
  - [Method `get_icon`](#method-get_icon)
  - [Method `get_menu`](#method-get_menu)
  - [Method `new_menu`](#method-new_menu)

</details>

## Class `MainMenuBase`

```python
class MainMenuBase
```

A base class for handling menu operations in a PySide application.

This class provides methods to create and manage menu items,
retrieve icons, and generate documentation for menu items in a README file.

Attributes:

- `menu` (`QMenu`): The main menu object for the application, initialized in `__init__`.

<details>
<summary>Code:</summary>

```python
class MainMenuBase:

    def __init__(self) -> None:
        """Initialize the `MainMenuBase` with an empty QMenu."""
        self.menu = QMenu()

    def _add_item(self, menu: QMenu, class_action: Callable, icon: str = "") -> None:
        """Add an item to the given menu.

        Args:

        - `menu` (`QMenu`): The menu to which the action will be added.
        - `class_action` (`Callable`): The callable to be executed when the menu item is triggered.
        - `icon` (`str`, optional): Path or emoji for the icon of the menu item. Defaults to `""`.

        Returns:

        - `None`

        """
        action_instance = class_action(parent=self)

        if icon:
            action = QAction(self.get_icon(icon), action_instance.title)
            action.triggered.connect(action_instance)
            action.setData(icon)
        elif hasattr(action_instance, "icon") and action_instance.icon:
            action = QAction(self.get_icon(action_instance.icon), action_instance.title)
            action.triggered.connect(action_instance)
            action.setData(action_instance.icon)
        else:
            action = QAction(action_instance.title)

        # Check if the action should have bold text
        if hasattr(action_instance, "bold_title") and action_instance.bold_title:
            font = action.font()
            font.setBold(True)
            action.setFont(font)

        setattr(self, f"action_{class_action.__name__}", action)
        menu.addAction(action)

    def add_items(self, menu: QMenu, items: list) -> None:
        """Add multiple items to the given menu with sorting by title within groups.

        Args:

        - `menu` (`QMenu`): The menu to which the actions will be added.
        - `items` (`list`): List of callables or separators. Use `"-"` string for separator.

        Returns:

        - `None`

        """
        # Split the list into groups by separators
        groups = []
        current_group = []

        for item in items:
            if item == "-":
                if current_group:  # Add group only if it's not empty
                    groups.append(current_group)
                    current_group = []
                groups.append(["-"])  # Separator as a separate group
            else:
                current_group.append(item)

        # Add the last group if it's not empty
        if current_group:
            groups.append(current_group)

        # Process each group
        for group in groups:
            if group == ["-"]:
                menu.addSeparator()
            else:
                # Sort group by title
                sorted_group = sorted(group, key=lambda x: x.title if hasattr(x, "title") else "")

                # Add sorted items
                for item in sorted_group:
                    self._add_item(menu, item)

    def add_menus_and_items(self, parent_menu: QMenu, menus: list | None = None, items: list | None = None) -> None:
        """Add submenus and items to the parent menu.

        Args:

        - `parent_menu` (`QMenu`): The parent menu to which submenus and items will be added.
        - `menus` (`list`, optional): List of QMenu objects to add as submenus. Defaults to `None`.
        - `items` (`list`, optional): List of callables or separators to add as items. Use `"-"` string for separator.
          Defaults to `None`.

        Returns:

        - `None`

        """
        # Add submenus
        if menus:
            for menu in menus:
                parent_menu.addMenu(menu)

        # Add separator between submenus and items if both exist
        if menus and items:
            parent_menu.addSeparator()

        # Add menu items
        if items:
            self.add_items(parent_menu, items)

    def create_emoji_icon(self, emoji: str, size: int = 32) -> QIcon:
        """Create an icon with the given emoji.

        Args:

        - `emoji` (`str`): The emoji to be used in the icon.
        - `size` (`int`): The size of the icon in pixels. Defaults to `32`.

        Returns:

        - `QIcon`: A QIcon object containing the emoji as an icon.

        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    def generate_markdown_from_qmenu(self, menu: QMenu, level: int = 0) -> list[str]:
        """Generate a Markdown representation of a QMenu structure.

        This function traverses the QMenu and its submenus to produce a nested list in Markdown format.

        Args:

        - `menu` (`QMenu`): The QMenu object to convert to Markdown.
        - `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

        Returns:

        - `List[str]`: A list of strings, each representing a line of Markdown text that describes the menu structure.

        """
        markdown_lines: list[str] = []
        for action in menu.actions():
            if action.menu():  # If the action has a submenu
                # Add a header for the submenu
                markdown_lines.append(f"{'  ' * level}- **{action.text()}**")
                # Recursively traverse the submenu
                submenu = action.menu()
                if isinstance(submenu, QMenu):
                    markdown_lines.extend(self.generate_markdown_from_qmenu(submenu, level + 1))
            else:
                # Add a regular menu item
                icon = (
                    getattr(action, "icon_name", "")
                    if hasattr(action, "icon_name") and "." not in getattr(action, "icon_name", "")
                    else ""
                )
                if action.text():
                    markdown_lines.append(f"{'  ' * level}- {icon} {action.text()}")
        return markdown_lines

    def get_icon(self, icon: str, size: int = 32) -> QIcon:
        """Retrieve an icon for menu items.

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
        """Update the README.md file with the current menu structure.

        This method:

        - Reads the content of README.md.
        - Locates the section to update by looking for "## List of commands" and the next heading.
        - Inserts the current menu structure into the file between these markers.
        - Overwrites the README.md with the updated content.
        - Returns the Markdown representation of the menu.

        Returns:

        - `str`: The Markdown formatted menu list.

        """
        filename = h.dev.get_project_root() / "README.md"
        list_of_menu = "\n".join(self.generate_markdown_from_qmenu(self.menu))

        h.md.replace_section(filename, list_of_menu, "## List of commands")

        return list_of_menu

    def new_menu(self, title: str, icon: str) -> QMenu:
        """Create and returns a new QMenu with a title and an icon.

        Args:

        - `title` (`str`): The title of the new menu.
        - `icon` (`str`): Path in `resources_rc.py` or emoji for the icon of the menu. Example: "uv.svg", "🏆".

        Returns:

        - `QMenu`: A newly created QMenu object.

        """
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu
```

</details>

### Method `__init__`

```python
def __init__(self) -> None
```

Initialize the `MainMenuBase` with an empty QMenu.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        self.menu = QMenu()
```

</details>

### Method `_add_item`

```python
def _add_item(self, menu: QMenu, class_action: Callable, icon: str = "") -> None
```

Add an item to the given menu.

Args:

- `menu` (`QMenu`): The menu to which the action will be added.
- `class_action` (`Callable`): The callable to be executed when the menu item is triggered.
- `icon` (`str`, optional): Path or emoji for the icon of the menu item. Defaults to `""`.

Returns:

- `None`

<details>
<summary>Code:</summary>

```python
def _add_item(self, menu: QMenu, class_action: Callable, icon: str = "") -> None:
        action_instance = class_action(parent=self)

        if icon:
            action = QAction(self.get_icon(icon), action_instance.title)
            action.triggered.connect(action_instance)
            action.setData(icon)
        elif hasattr(action_instance, "icon") and action_instance.icon:
            action = QAction(self.get_icon(action_instance.icon), action_instance.title)
            action.triggered.connect(action_instance)
            action.setData(action_instance.icon)
        else:
            action = QAction(action_instance.title)

        # Check if the action should have bold text
        if hasattr(action_instance, "bold_title") and action_instance.bold_title:
            font = action.font()
            font.setBold(True)
            action.setFont(font)

        setattr(self, f"action_{class_action.__name__}", action)
        menu.addAction(action)
```

</details>

### Method `add_items`

```python
def add_items(self, menu: QMenu, items: list) -> None
```

Add multiple items to the given menu with sorting by title within groups.

Args:

- `menu` (`QMenu`): The menu to which the actions will be added.
- `items` (`list`): List of callables or separators. Use `"-"` string for separator.

Returns:

- `None`

<details>
<summary>Code:</summary>

```python
def add_items(self, menu: QMenu, items: list) -> None:
        # Split the list into groups by separators
        groups = []
        current_group = []

        for item in items:
            if item == "-":
                if current_group:  # Add group only if it's not empty
                    groups.append(current_group)
                    current_group = []
                groups.append(["-"])  # Separator as a separate group
            else:
                current_group.append(item)

        # Add the last group if it's not empty
        if current_group:
            groups.append(current_group)

        # Process each group
        for group in groups:
            if group == ["-"]:
                menu.addSeparator()
            else:
                # Sort group by title
                sorted_group = sorted(group, key=lambda x: x.title if hasattr(x, "title") else "")

                # Add sorted items
                for item in sorted_group:
                    self._add_item(menu, item)
```

</details>

### Method `add_menus_and_items`

```python
def add_menus_and_items(self, parent_menu: QMenu, menus: list | None = None, items: list | None = None) -> None
```

Add submenus and items to the parent menu.

Args:

- `parent_menu` (`QMenu`): The parent menu to which submenus and items will be added.
- `menus` (`list`, optional): List of QMenu objects to add as submenus. Defaults to `None`.
- `items` (`list`, optional): List of callables or separators to add as items. Use `"-"` string for separator.
  Defaults to `None`.

Returns:

- `None`

<details>
<summary>Code:</summary>

```python
def add_menus_and_items(self, parent_menu: QMenu, menus: list | None = None, items: list | None = None) -> None:
        # Add submenus
        if menus:
            for menu in menus:
                parent_menu.addMenu(menu)

        # Add separator between submenus and items if both exist
        if menus and items:
            parent_menu.addSeparator()

        # Add menu items
        if items:
            self.add_items(parent_menu, items)
```

</details>

### Method `create_emoji_icon`

```python
def create_emoji_icon(self, emoji: str, size: int = 32) -> QIcon
```

Create an icon with the given emoji.

Args:

- `emoji` (`str`): The emoji to be used in the icon.
- `size` (`int`): The size of the icon in pixels. Defaults to `32`.

Returns:

- `QIcon`: A QIcon object containing the emoji as an icon.

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(self, emoji: str, size: int = 32) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)
```

</details>

### Method `generate_markdown_from_qmenu`

```python
def generate_markdown_from_qmenu(self, menu: QMenu, level: int = 0) -> list[str]
```

Generate a Markdown representation of a QMenu structure.

This function traverses the QMenu and its submenus to produce a nested list in Markdown format.

Args:

- `menu` (`QMenu`): The QMenu object to convert to Markdown.
- `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

Returns:

- `List[str]`: A list of strings, each representing a line of Markdown text that describes the menu structure.

<details>
<summary>Code:</summary>

```python
def generate_markdown_from_qmenu(self, menu: QMenu, level: int = 0) -> list[str]:
        markdown_lines: list[str] = []
        for action in menu.actions():
            if action.menu():  # If the action has a submenu
                # Add a header for the submenu
                markdown_lines.append(f"{'  ' * level}- **{action.text()}**")
                # Recursively traverse the submenu
                submenu = action.menu()
                if isinstance(submenu, QMenu):
                    markdown_lines.extend(self.generate_markdown_from_qmenu(submenu, level + 1))
            else:
                # Add a regular menu item
                icon = (
                    getattr(action, "icon_name", "")
                    if hasattr(action, "icon_name") and "." not in getattr(action, "icon_name", "")
                    else ""
                )
                if action.text():
                    markdown_lines.append(f"{'  ' * level}- {icon} {action.text()}")
        return markdown_lines
```

</details>

### Method `get_icon`

```python
def get_icon(self, icon: str, size: int = 32) -> QIcon
```

Retrieve an icon for menu items.

Args:

- `icon` (`str`): The path or description of the icon in `resources_rc.py`. Example: "uv.svg", "🏆".
- `size` (`int`): The size of the icon in pixels. Defaults to `32`.

Returns:

- `QIcon`: A QIcon object for the given icon path or emoji icon.

<details>
<summary>Code:</summary>

```python
def get_icon(self, icon: str, size: int = 32) -> QIcon:
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
```

</details>

### Method `get_menu`

```python
def get_menu(self) -> str
```

Update the README.md file with the current menu structure.

This method:

- Reads the content of README.md.
- Locates the section to update by looking for "## List of commands" and the next heading.
- Inserts the current menu structure into the file between these markers.
- Overwrites the README.md with the updated content.
- Returns the Markdown representation of the menu.

Returns:

- `str`: The Markdown formatted menu list.

<details>
<summary>Code:</summary>

```python
def get_menu(self) -> str:
        filename = h.dev.get_project_root() / "README.md"
        list_of_menu = "\n".join(self.generate_markdown_from_qmenu(self.menu))

        h.md.replace_section(filename, list_of_menu, "## List of commands")

        return list_of_menu
```

</details>

### Method `new_menu`

```python
def new_menu(self, title: str, icon: str) -> QMenu
```

Create and returns a new QMenu with a title and an icon.

Args:

- `title` (`str`): The title of the new menu.
- `icon` (`str`): Path in `resources_rc.py` or emoji for the icon of the menu. Example: "uv.svg", "🏆".

Returns:

- `QMenu`: A newly created QMenu object.

<details>
<summary>Code:</summary>

```python
def new_menu(self, title: str, icon: str) -> QMenu:
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu
```

</details>
