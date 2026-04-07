---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `on_item_clicked`](#%EF%B8%8F-method-on_item_clicked)
  - [⚙️ Method `populate_list`](#%EF%B8%8F-method-populate_list)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `show_window`](#%EF%B8%8F-method-show_window)
  - [⚙️ Method `_on_active_output_changed`](#%EF%B8%8F-method-_on_active_output_changed)
  - [⚙️ Method `_on_line_appended`](#%EF%B8%8F-method-_on_line_appended)
  - [⚙️ Method `_set_placeholder`](#%EF%B8%8F-method-_set_placeholder)
  - [⚙️ Method `_setup_window_size_and_position`](#%EF%B8%8F-method-_setup_window_size_and_position)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow)
```

The main window of the application that displays a menu and handles user interactions.

Attributes:

- `list_widget` (`QListWidget`): Widget to display the list of menu actions.
- `text_edit` (`QTextEdit`): Widget to display information about performed actions.
- `current_content` (`str`): Current content shown in the output panel.

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow):

    def __init__(self, menu: QMenu, *, output_bus: ActionOutputBus | None = None) -> None:
        """Initialize the main window with the given menu.

        Args:

        - `menu` (`QMenu`): The menu whose actions will be displayed in the list widget.

        """
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        self.resize(1024, 800)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        splitter = QSplitter()
        layout.addWidget(splitter)

        self.list_widget = QListWidget()
        splitter.addWidget(self.list_widget)

        self.text_edit = QTextEdit()
        splitter.addWidget(self.text_edit)

        splitter.setSizes([300, 700])

        # Initialize current content to track changes
        self.current_content = ""
        self._active_output_path: Path | None = None

        self._output_bus = output_bus
        if self._output_bus is not None:
            self._output_bus.active_output_changed.connect(self._on_active_output_changed)
            self._output_bus.line_appended.connect(self._on_line_appended)
        else:
            self._set_placeholder("No action output yet")

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Override the close event to hide the window instead of closing it.

        Args:

        - `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

        """
        event.ignore()
        self.hide()

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle the event when an item in the list widget is clicked.

        Args:

        - `item` (`QListWidgetItem`): The item that was clicked.

        """
        # Check if the item is enabled
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return  # Do nothing if the item is disabled

        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()

    def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None:
        """Populate the list widget with actions, handling submenus recursively.

        Args:

        - `actions` (`list[QAction]`): A list of actions to add to the list widget.
        - `indent_level` (`int`): The current indentation level for submenu actions. Defaults to `0`.

        """
        for action in actions:
            if not action.text():
                continue

            item = QListWidgetItem()
            # Add indentation for submenus
            text = ("    " * indent_level) + action.text()
            item.setText(text)
            if not action.icon().isNull():
                item.setIcon(action.icon())

            if action.menu() is not None and isinstance(action.menu(), QMenu):
                # The action has a submenu
                # Make the text bold
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                # Set the item flags to make it not selectable and disabled
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                # Do not set UserRole data for this item
                self.list_widget.addItem(item)
                # Recursively add actions from the submenu
                self.populate_list(action.menu().actions(), indent_level + 1)
            else:
                # Regular action without submenu
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.list_widget.addItem(item)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Override the show event to restart the timer when the window is shown.

        Args:

        - `event` (`QShowEvent`): The show event triggered when the window is displayed.

        """
        super().showEvent(event)

    def show_window(self) -> None:
        """Show the window with proper state and restart timer."""
        self.show()

    def _on_active_output_changed(self, path_str: str) -> None:
        try:
            path = Path(path_str)
            self._active_output_path = path
            if path.exists():
                output_txt = path.read_text(encoding="utf8")
                self.text_edit.setPlainText(output_txt)
                self.current_content = output_txt
            else:
                self.text_edit.setPlainText("")
                self.current_content = ""
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            self._set_placeholder(f"File reading error: {e!s}")

    def _on_line_appended(self, path_str: str, line: str) -> None:
        if self._active_output_path is None:
            return
        if str(self._active_output_path.resolve()) != path_str:
            return
        self.text_edit.append(line)
        self.current_content = self.text_edit.toPlainText()
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def _set_placeholder(self, placeholder: str) -> None:
        if placeholder != self.current_content:
            self.text_edit.setPlainText(placeholder)
            self.current_content = placeholder
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0  # Standard aspect ratio (16:9, 16:10, etc.)
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio

        standard_width = 1920
        if is_standard_aspect and screen_width >= standard_width:
            # For standard aspect ratios with width >= 1920, set window to maximized state
            # but don't show it yet - it will be maximized when shown
            self.setWindowState(Qt.WindowState.WindowMaximized)
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = standard_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, menu: QMenu) -> None
```

Initialize the main window with the given menu.

Args:

- `menu` (`QMenu`): The menu whose actions will be displayed in the list widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, menu: QMenu, *, output_bus: ActionOutputBus | None = None) -> None:
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        self.resize(1024, 800)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        splitter = QSplitter()
        layout.addWidget(splitter)

        self.list_widget = QListWidget()
        splitter.addWidget(self.list_widget)

        self.text_edit = QTextEdit()
        splitter.addWidget(self.text_edit)

        splitter.setSizes([300, 700])

        # Initialize current content to track changes
        self.current_content = ""
        self._active_output_path: Path | None = None

        self._output_bus = output_bus
        if self._output_bus is not None:
            self._output_bus.active_output_changed.connect(self._on_active_output_changed)
            self._output_bus.line_appended.connect(self._on_line_appended)
        else:
            self._set_placeholder("No action output yet")

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        self._setup_window_size_and_position()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Override the close event to hide the window instead of closing it.

Args:

- `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()
        self.hide()
```

</details>

### ⚙️ Method `on_item_clicked`

```python
def on_item_clicked(self, item: QListWidgetItem) -> None
```

Handle the event when an item in the list widget is clicked.

Args:

- `item` (`QListWidgetItem`): The item that was clicked.

<details>
<summary>Code:</summary>

```python
def on_item_clicked(self, item: QListWidgetItem) -> None:
        # Check if the item is enabled
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return  # Do nothing if the item is disabled

        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()
```

</details>

### ⚙️ Method `populate_list`

```python
def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None
```

Populate the list widget with actions, handling submenus recursively.

Args:

- `actions` (`list[QAction]`): A list of actions to add to the list widget.
- `indent_level` (`int`): The current indentation level for submenu actions. Defaults to `0`.

<details>
<summary>Code:</summary>

```python
def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None:
        for action in actions:
            if not action.text():
                continue

            item = QListWidgetItem()
            # Add indentation for submenus
            text = ("    " * indent_level) + action.text()
            item.setText(text)
            if not action.icon().isNull():
                item.setIcon(action.icon())

            if action.menu() is not None and isinstance(action.menu(), QMenu):
                # The action has a submenu
                # Make the text bold
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                # Set the item flags to make it not selectable and disabled
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                # Do not set UserRole data for this item
                self.list_widget.addItem(item)
                # Recursively add actions from the submenu
                self.populate_list(action.menu().actions(), indent_level + 1)
            else:
                # Regular action without submenu
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.list_widget.addItem(item)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Override the show event to restart the timer when the window is shown.

Args:

- `event` (`QShowEvent`): The show event triggered when the window is displayed.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
```

</details>

### ⚙️ Method `show_window`

```python
def show_window(self) -> None
```

Show the window with proper state and restart timer.

<details>
<summary>Code:</summary>

```python
def show_window(self) -> None:
        self.show()
```

</details>

### ⚙️ Method `_on_active_output_changed`

```python
def _on_active_output_changed(self, path_str: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_active_output_changed(self, path_str: str) -> None:
        try:
            path = Path(path_str)
            self._active_output_path = path
            if path.exists():
                output_txt = path.read_text(encoding="utf8")
                self.text_edit.setPlainText(output_txt)
                self.current_content = output_txt
            else:
                self.text_edit.setPlainText("")
                self.current_content = ""
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            self._set_placeholder(f"File reading error: {e!s}")
```

</details>

### ⚙️ Method `_on_line_appended`

```python
def _on_line_appended(self, path_str: str, line: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_line_appended(self, path_str: str, line: str) -> None:
        if self._active_output_path is None:
            return
        if str(self._active_output_path.resolve()) != path_str:
            return
        self.text_edit.append(line)
        self.current_content = self.text_edit.toPlainText()
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
```

</details>

### ⚙️ Method `_set_placeholder`

```python
def _set_placeholder(self, placeholder: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _set_placeholder(self, placeholder: str) -> None:
        if placeholder != self.current_content:
            self.text_edit.setPlainText(placeholder)
            self.current_content = placeholder
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
```

</details>

### ⚙️ Method `_setup_window_size_and_position`

```python
def _setup_window_size_and_position(self) -> None
```

Set window size and position based on screen resolution and characteristics.

<details>
<summary>Code:</summary>

```python
def _setup_window_size_and_position(self) -> None:
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0  # Standard aspect ratio (16:9, 16:10, etc.)
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio

        standard_width = 1920
        if is_standard_aspect and screen_width >= standard_width:
            # For standard aspect ratios with width >= 1920, set window to maximized state
            # but don't show it yet - it will be maximized when shown
            self.setWindowState(Qt.WindowState.WindowMaximized)
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = standard_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )
```

</details>
