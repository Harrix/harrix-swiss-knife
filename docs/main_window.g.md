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
  - [⚙️ Method `update_output_content`](#%EF%B8%8F-method-update_output_content)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow)
```

The main window of the application that displays a menu and handles user interactions.

Attributes:

- `list_widget` (`QListWidget`): Widget to display the list of menu actions.
- `text_edit` (`QTextEdit`): Widget to display information about performed actions.
- `update_timer` (`QTimer`): Timer for periodically updating the text edit content.
- `current_content` (`str`): Current content of the output file to track changes.

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow):

    def __init__(self, menu: QMenu) -> None:
        """Initialize the `MainWindow` with the given menu.

        Args:

        - `menu` (`QMenu`): The menu whose actions will be displayed in the list widget.

        Sets up the main window layout, initializes widgets, populates the list with menu actions,
        and connects signals to their respective handlers.

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

        # Initialize timer for updating text edit content
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_output_content)
        self.update_timer.start(2000)  # Update every 2 seconds

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Override the close event to hide the window instead of closing it.

        Args:

        - `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

        Prevents the window from closing and hides it instead.

        """
        # Stop the timer when hiding the window
        self.update_timer.stop()
        event.ignore()
        self.hide()

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle the event when an item in the list widget is clicked.

        Args:

        - `item` (`QListWidgetItem`): The item that was clicked.

        If the associated action is a `QAction`, it triggers the action and logs the action's text
        in the text edit widget.

        Returns:

        - None

        """
        # Check if the item is enabled
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return  # Do nothing if the item is disabled
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()
            # Update the output content immediately
            self.update_output_content()

    def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None:
        """Populate the list widget with actions, handling submenus recursively.

        Args:

        - `actions` (`list[QAction]`): A list of actions to add to the list widget.
        - `indent_level` (`int`): The current indentation level for submenu actions. Defaults to `0`.

        For each action, an item is created with appropriate indentation and icon. If the action
        has a submenu, the text is made bold and the submenu actions are added recursively with increased indentation.

        Returns:

        - None

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
                self.populate_list(action.menu().actions(), indent_level + 1)  # type: ignore noqa: PGH003
            else:
                # Regular action without submenu
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.list_widget.addItem(item)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Override the show event to restart the timer when the window is shown.

        Args:

        - `event`: The show event triggered when the window is displayed.

        Restarts the timer to continue updating the output content.

        """
        super().showEvent(event)
        # Restart the timer when showing the window
        self.update_timer.start(2000)

    def update_output_content(self) -> None:
        """Update the text edit content from the output.txt file.

        Reads the content of the output.txt file and displays it in the text edit widget
        only if the content has changed. If the file doesn't exist or can't be read,
        displays an appropriate message.

        Returns:

        - None

        """
        try:
            output_file = h.dev.get_project_root() / "temp/output.txt"
            if output_file.exists():
                output_txt = output_file.read_text(encoding="utf8")
                if output_txt != self.current_content:
                    self.text_edit.setPlainText(output_txt)
                    self.current_content = output_txt
                    # Scroll to the end of the text
                    self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
            else:
                error_message = "File output.txt not found"
                if error_message != self.current_content:
                    self.text_edit.setPlainText(error_message)
                    self.current_content = error_message
                    # Scroll to the end of the text
                    self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            error_message = f"File reading error: {e!s}"
            if error_message != self.current_content:
                self.text_edit.setPlainText(error_message)
                self.current_content = error_message
                # Scroll to the end of the text
                self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, menu: QMenu) -> None
```

Initialize the `MainWindow` with the given menu.

Args:

- `menu` (`QMenu`): The menu whose actions will be displayed in the list widget.

Sets up the main window layout, initializes widgets, populates the list with menu actions,
and connects signals to their respective handlers.

<details>
<summary>Code:</summary>

```python
def __init__(self, menu: QMenu) -> None:
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

        # Initialize timer for updating text edit content
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_output_content)
        self.update_timer.start(2000)  # Update every 2 seconds

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Override the close event to hide the window instead of closing it.

Args:

- `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

Prevents the window from closing and hides it instead.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        # Stop the timer when hiding the window
        self.update_timer.stop()
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

If the associated action is a `QAction`, it triggers the action and logs the action's text
in the text edit widget.

Returns:

- None

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
            # Update the output content immediately
            self.update_output_content()
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

For each action, an item is created with appropriate indentation and icon. If the action
has a submenu, the text is made bold and the submenu actions are added recursively with increased indentation.

Returns:

- None

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
                self.populate_list(action.menu().actions(), indent_level + 1)  # type: ignore noqa: PGH003
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

- `event`: The show event triggered when the window is displayed.

Restarts the timer to continue updating the output content.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        # Restart the timer when showing the window
        self.update_timer.start(2000)
```

</details>

### ⚙️ Method `update_output_content`

```python
def update_output_content(self) -> None
```

Update the text edit content from the output.txt file.

Reads the content of the output.txt file and displays it in the text edit widget
only if the content has changed. If the file doesn't exist or can't be read,
displays an appropriate message.

Returns:

- None

<details>
<summary>Code:</summary>

```python
def update_output_content(self) -> None:
        try:
            output_file = h.dev.get_project_root() / "temp/output.txt"
            if output_file.exists():
                output_txt = output_file.read_text(encoding="utf8")
                if output_txt != self.current_content:
                    self.text_edit.setPlainText(output_txt)
                    self.current_content = output_txt
                    # Scroll to the end of the text
                    self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
            else:
                error_message = "File output.txt not found"
                if error_message != self.current_content:
                    self.text_edit.setPlainText(error_message)
                    self.current_content = error_message
                    # Scroll to the end of the text
                    self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            error_message = f"File reading error: {e!s}"
            if error_message != self.current_content:
                self.text_edit.setPlainText(error_message)
                self.current_content = error_message
                # Scroll to the end of the text
                self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
```

</details>
