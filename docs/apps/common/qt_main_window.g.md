---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_main_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppWindowMixin`](#%EF%B8%8F-class-appwindowmixin)
  - [⚙️ Method `_copy_table_selection_to_clipboard`](#%EF%B8%8F-method-_copy_table_selection_to_clipboard)
  - [⚙️ Method `_handle_ctrl_c_for_tables`](#%EF%B8%8F-method-_handle_ctrl_c_for_tables)
  - [⚙️ Method `_setup_window_size_and_position`](#%EF%B8%8F-method-_setup_window_size_and_position)
  - [⚙️ Method `_validate_database_connection`](#%EF%B8%8F-method-_validate_database_connection)

</details>

## 🏛️ Class `AppWindowMixin`

```python
class AppWindowMixin
```

Mixin with common `QMainWindow` helpers shared across apps.

<details>
<summary>Code:</summary>

```python
class AppWindowMixin:

    db_manager: Any

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from `table_view` to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        rows_data: dict[int, dict[int, str]] = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        clipboard_text: list[str] = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(final_text)
                print(f"Copied {len(clipboard_text)} rows to clipboard")

    def _handle_ctrl_c_for_tables(self, event: QKeyEvent, table_views: list[QTableView]) -> bool:
        """Copy table selection to clipboard on Ctrl+C if a table is focused.

        Args:

        - `event` (`QKeyEvent`): Key press event.
        - `table_views` (`list[QTableView]`): Candidate table views.

        Returns:

        - `bool`: `True` if the shortcut was handled, `False` otherwise.

        """
        if not (event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            return False

        focused_widget = QApplication.focusWidget()
        for table_view in table_views:
            if focused_widget == table_view:
                self._copy_table_selection_to_clipboard(table_view)
                return True

        for table_view in table_views:
            if focused_widget and table_view.isAncestorOf(focused_widget):
                self._copy_table_selection_to_clipboard(table_view)
                return True

        return False

    def _setup_window_size_and_position(self, *, standard_width: int = 1920) -> None:
        """Set window size and position based on screen resolution and characteristics.

        Args:

        - `standard_width` (`int`): Reference width used to decide between
          `showMaximized` and a fixed layout. Defaults to `1920`.

        """
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio

        if is_standard_aspect and screen_width >= standard_width:
            self.showMaximized()  # type: ignore[attr-defined]
        else:
            title_bar_height = 30
            windows_task_bar_height = 48
            window_width = standard_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            screen_center = screen_geometry.center()
            self.setGeometry(  # type: ignore[attr-defined]
                screen_center.x() - window_width // 2,
                title_bar_height,
                window_width,
                window_height,
            )

    def _validate_database_connection(self) -> bool:
        """Validate that database connection is available and open.

        Returns:

        - `bool`: True if database connection is valid, False otherwise.

        """
        if not getattr(self, "db_manager", None):
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True
```

</details>

### ⚙️ Method `_copy_table_selection_to_clipboard`

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None
```

Copy selected cells from `table_view` to clipboard as tab-separated text.

Args:

- `table_view` (`QTableView`): The table view to copy data from.

<details>
<summary>Code:</summary>

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        rows_data: dict[int, dict[int, str]] = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        clipboard_text: list[str] = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(final_text)
                print(f"Copied {len(clipboard_text)} rows to clipboard")
```

</details>

### ⚙️ Method `_handle_ctrl_c_for_tables`

```python
def _handle_ctrl_c_for_tables(self, event: QKeyEvent, table_views: list[QTableView]) -> bool
```

Copy table selection to clipboard on Ctrl+C if a table is focused.

Args:

- `event` (`QKeyEvent`): Key press event.
- `table_views` (`list[QTableView]`): Candidate table views.

Returns:

- `bool`: `True` if the shortcut was handled, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def _handle_ctrl_c_for_tables(self, event: QKeyEvent, table_views: list[QTableView]) -> bool:
        if not (event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            return False

        focused_widget = QApplication.focusWidget()
        for table_view in table_views:
            if focused_widget == table_view:
                self._copy_table_selection_to_clipboard(table_view)
                return True

        for table_view in table_views:
            if focused_widget and table_view.isAncestorOf(focused_widget):
                self._copy_table_selection_to_clipboard(table_view)
                return True

        return False
```

</details>

### ⚙️ Method `_setup_window_size_and_position`

```python
def _setup_window_size_and_position(self) -> None
```

Set window size and position based on screen resolution and characteristics.

Args:

- `standard_width` (`int`): Reference width used to decide between
  `showMaximized` and a fixed layout. Defaults to `1920`.

<details>
<summary>Code:</summary>

```python
def _setup_window_size_and_position(self, *, standard_width: int = 1920) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio

        if is_standard_aspect and screen_width >= standard_width:
            self.showMaximized()  # type: ignore[attr-defined]
        else:
            title_bar_height = 30
            windows_task_bar_height = 48
            window_width = standard_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            screen_center = screen_geometry.center()
            self.setGeometry(  # type: ignore[attr-defined]
                screen_center.x() - window_width // 2,
                title_bar_height,
                window_width,
                window_height,
            )
```

</details>

### ⚙️ Method `_validate_database_connection`

```python
def _validate_database_connection(self) -> bool
```

Validate that database connection is available and open.

Returns:

- `bool`: True if database connection is valid, False otherwise.

<details>
<summary>Code:</summary>

```python
def _validate_database_connection(self) -> bool:
        if not getattr(self, "db_manager", None):
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True
```

</details>
