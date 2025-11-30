---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `filtered_combobox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FilteredComboBox`](#%EF%B8%8F-class-filteredcombobox)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `addItem`](#%EF%B8%8F-method-additem)
  - [⚙️ Method `addItem`](#%EF%B8%8F-method-additem-1)
  - [⚙️ Method `addItem`](#%EF%B8%8F-method-additem-2)
  - [⚙️ Method `addItems`](#%EF%B8%8F-method-additems)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `setCurrentText`](#%EF%B8%8F-method-setcurrenttext)
  - [⚙️ Method `_on_completion_activated`](#%EF%B8%8F-method-_on_completion_activated)
  - [⚙️ Method `_on_text_edited`](#%EF%B8%8F-method-_on_text_edited)
- [🏛️ Class `SmartFilterProxyModel`](#%EF%B8%8F-class-smartfilterproxymodel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `filterAcceptsRow`](#%EF%B8%8F-method-filteracceptsrow)
  - [⚙️ Method `lessThan`](#%EF%B8%8F-method-lessthan)
  - [⚙️ Method `set_filter_text`](#%EF%B8%8F-method-set_filter_text)
- [🔧 Function `apply_smart_filtering`](#-function-apply_smart_filtering)

</details>

## 🏛️ Class `FilteredComboBox`

```python
class FilteredComboBox(QComboBox)
```

ComboBox with smart filtering functionality.

Features:

- Shows matching items as you type
- Case-insensitive filtering
- Items starting with typed text appear first
- Items containing typed text (>= 2 chars) appear after
- Dropdown opens automatically when typing
- Resets to full list when cleared
- Allows entering custom text not in the list

<details>
<summary>Code:</summary>

```python
class FilteredComboBox(QComboBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the filtered combobox."""
        super().__init__(parent)

        # Make it editable to allow typing
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Setup model and proxy
        self.string_model = QStringListModel()
        self.proxy_model = SmartFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.string_model)

        # Setup completer
        self.completer_widget = QCompleter(self.proxy_model, self)
        self.completer_widget.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_widget.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer_widget.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(self.completer_widget)

        # Store original items for reset
        self._original_items = []
        self._is_programmatic_change = False

        # Connect signals, but guard for absent lineEdit/textEdited attribute to avoid possible errors
        line_edit = self.lineEdit()
        if line_edit is not None and hasattr(line_edit, "textEdited"):
            line_edit.textEdited.connect(self._on_text_edited)
        self.completer_widget.activated.connect(self._on_completion_activated)

    @typing.overload
    def addItem(self, text: str, /, userData: typing.Any = ...) -> None: ...  # noqa: N803

    @typing.overload
    def addItem(self, icon: QIcon | QPixmap, text: str, /, userData: typing.Any = ...) -> None: ...  # noqa: N803

    def addItem(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: N802, ARG002
        """Add a single item to the combobox."""
        # Parse arguments to extract text
        if len(args) == 0:
            return

        # Determine if first arg is icon or text
        if isinstance(args[0], (QIcon, QPixmap)):
            # First signature: icon, text, [userData]
            min_args_for_icon = 2
            if len(args) < min_args_for_icon:
                return
            # Use constant variable for the magic value '2'
            text = args[1]
        else:
            # Second signature: text, [userData]
            text = args[0]

        self._original_items.append(text)
        self._original_items = sorted(self._original_items, key=str.lower)
        self.string_model.setStringList(self._original_items)
        super().clear()
        super().addItems(self._original_items)

    def addItems(self, texts: collections.abc.Sequence[str], /) -> None:  # noqa: N802
        """Add multiple items to the combobox."""
        self._original_items = sorted(texts, key=str.lower)
        self.string_model.setStringList(self._original_items)
        # Add items to combobox itself (for when no filter is active)
        super().clear()
        super().addItems(self._original_items)

    def clear(self) -> None:
        """Clear all items."""
        self._original_items = []
        self.string_model.setStringList([])
        super().clear()

    def setCurrentText(self, text: str) -> None:  # noqa: N802
        """Set current text (override to handle programmatic changes)."""
        self._is_programmatic_change = True
        super().setCurrentText(text)
        self._is_programmatic_change = False

    def _on_completion_activated(self, text: str) -> None:
        """Handle completion selection."""
        self._is_programmatic_change = True
        self.setCurrentText(text)
        self._is_programmatic_change = False

    def _on_text_edited(self, text: str) -> None:
        """Handle text editing to show filtered dropdown."""
        if self._is_programmatic_change:
            return

        # Update filter
        self.proxy_model.set_filter_text(text)

        if text:
            # Show dropdown with filtered items
            self.completer_widget.setCompletionPrefix(text)
            self.completer_widget.complete()
        else:
            # Empty text - reset to full list and hide popup
            self.proxy_model.set_filter_text("")
            popup = self.completer_widget.popup()
            if popup is not None and hasattr(popup, "isVisible") and popup.isVisible():
                popup = self.completer_widget.popup()
                if hasattr(popup, "hide") and callable(getattr(popup, "hide", None)):
                    popup.hide()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the filtered combobox.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Make it editable to allow typing
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Setup model and proxy
        self.string_model = QStringListModel()
        self.proxy_model = SmartFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.string_model)

        # Setup completer
        self.completer_widget = QCompleter(self.proxy_model, self)
        self.completer_widget.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_widget.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer_widget.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(self.completer_widget)

        # Store original items for reset
        self._original_items = []
        self._is_programmatic_change = False

        # Connect signals, but guard for absent lineEdit/textEdited attribute to avoid possible errors
        line_edit = self.lineEdit()
        if line_edit is not None and hasattr(line_edit, "textEdited"):
            line_edit.textEdited.connect(self._on_text_edited)
        self.completer_widget.activated.connect(self._on_completion_activated)
```

</details>

### ⚙️ Method `addItem`

```python
def addItem(userData: typing.Any = ...) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def addItem(self, text: str, /, userData: typing.Any = ...) -> None: ...  # noqa: N803
```

</details>

### ⚙️ Method `addItem`

```python
def addItem(userData: typing.Any = ...) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def addItem(self, icon: QIcon | QPixmap, text: str, /, userData: typing.Any = ...) -> None: ...  # noqa: N803
```

</details>

### ⚙️ Method `addItem`

```python
def addItem(self, *args: typing.Any, **kwargs: typing.Any) -> None
```

Add a single item to the combobox.

<details>
<summary>Code:</summary>

```python
def addItem(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: N802, ARG002
        # Parse arguments to extract text
        if len(args) == 0:
            return

        # Determine if first arg is icon or text
        if isinstance(args[0], (QIcon, QPixmap)):
            # First signature: icon, text, [userData]
            min_args_for_icon = 2
            if len(args) < min_args_for_icon:
                return
            # Use constant variable for the magic value '2'
            text = args[1]
        else:
            # Second signature: text, [userData]
            text = args[0]

        self._original_items.append(text)
        self._original_items = sorted(self._original_items, key=str.lower)
        self.string_model.setStringList(self._original_items)
        super().clear()
        super().addItems(self._original_items)
```

</details>

### ⚙️ Method `addItems`

```python
def addItems() -> None
```

Add multiple items to the combobox.

<details>
<summary>Code:</summary>

```python
def addItems(self, texts: collections.abc.Sequence[str], /) -> None:  # noqa: N802
        self._original_items = sorted(texts, key=str.lower)
        self.string_model.setStringList(self._original_items)
        # Add items to combobox itself (for when no filter is active)
        super().clear()
        super().addItems(self._original_items)
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Clear all items.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._original_items = []
        self.string_model.setStringList([])
        super().clear()
```

</details>

### ⚙️ Method `setCurrentText`

```python
def setCurrentText(self, text: str) -> None
```

Set current text (override to handle programmatic changes).

<details>
<summary>Code:</summary>

```python
def setCurrentText(self, text: str) -> None:  # noqa: N802
        self._is_programmatic_change = True
        super().setCurrentText(text)
        self._is_programmatic_change = False
```

</details>

### ⚙️ Method `_on_completion_activated`

```python
def _on_completion_activated(self, text: str) -> None
```

Handle completion selection.

<details>
<summary>Code:</summary>

```python
def _on_completion_activated(self, text: str) -> None:
        self._is_programmatic_change = True
        self.setCurrentText(text)
        self._is_programmatic_change = False
```

</details>

### ⚙️ Method `_on_text_edited`

```python
def _on_text_edited(self, text: str) -> None
```

Handle text editing to show filtered dropdown.

<details>
<summary>Code:</summary>

```python
def _on_text_edited(self, text: str) -> None:
        if self._is_programmatic_change:
            return

        # Update filter
        self.proxy_model.set_filter_text(text)

        if text:
            # Show dropdown with filtered items
            self.completer_widget.setCompletionPrefix(text)
            self.completer_widget.complete()
        else:
            # Empty text - reset to full list and hide popup
            self.proxy_model.set_filter_text("")
            popup = self.completer_widget.popup()
            if popup is not None and hasattr(popup, "isVisible") and popup.isVisible():
                popup = self.completer_widget.popup()
                if hasattr(popup, "hide") and callable(getattr(popup, "hide", None)):
                    popup.hide()
```

</details>

## 🏛️ Class `SmartFilterProxyModel`

```python
class SmartFilterProxyModel(QSortFilterProxyModel)
```

Custom proxy model for smart filtering.

Implements smart filtering logic:

- First shows items that start with the filter text (case-insensitive)
- Then shows items that contain the filter text in the middle (if length >= 2)
- Case-insensitive matching

<details>
<summary>Code:</summary>

```python
class SmartFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        """Determine if a row should be accepted by the filter."""
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        # Always accept items that start with filter text
        if text.startswith(filter_lower):
            return True

        # For filter text with MIN_FILTER_LENGTH+ chars, also accept items containing it anywhere
        min_filter_length = 2
        return len(filter_lower) >= min_filter_length and filter_lower in text

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort so that items starting with filter text appear first."""
        if not self.filter_text:
            # Default: alphabetical order (case-insensitive)
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

            if left_data is None or right_data is None:
                return False

            return str(left_data).lower() < str(right_data).lower()

        filter_lower = self.filter_text.lower()

        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_text = str(left_data).lower()
        right_text = str(right_data).lower()

        left_startswith = left_text.startswith(filter_lower)
        right_startswith = right_text.startswith(filter_lower)

        # Prioritize items that start with the filter text
        if left_startswith != right_startswith:
            return left_startswith

        # If both (or neither) start, sort alphabetically
        return left_text < right_text

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the proxy model.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
```

</details>

### ⚙️ Method `filterAcceptsRow`

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool
```

Determine if a row should be accepted by the filter.

<details>
<summary>Code:</summary>

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        # Always accept items that start with filter text
        if text.startswith(filter_lower):
            return True

        # For filter text with MIN_FILTER_LENGTH+ chars, also accept items containing it anywhere
        min_filter_length = 2
        return len(filter_lower) >= min_filter_length and filter_lower in text
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Sort so that items starting with filter text appear first.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if not self.filter_text:
            # Default: alphabetical order (case-insensitive)
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

            if left_data is None or right_data is None:
                return False

            return str(left_data).lower() < str(right_data).lower()

        filter_lower = self.filter_text.lower()

        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_text = str(left_data).lower()
        right_text = str(right_data).lower()

        left_startswith = left_text.startswith(filter_lower)
        right_startswith = right_text.startswith(filter_lower)

        # Prioritize items that start with the filter text
        if left_startswith != right_startswith:
            return left_startswith

        # If both (or neither) start, sort alphabetically
        return left_text < right_text
```

</details>

### ⚙️ Method `set_filter_text`

```python
def set_filter_text(self, text: str) -> None
```

Set the filter text and trigger re-filtering.

<details>
<summary>Code:</summary>

```python
def set_filter_text(self, text: str) -> None:
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

## 🔧 Function `apply_smart_filtering`

```python
def apply_smart_filtering(combobox: QComboBox) -> None
```

Apply smart filtering to an existing QComboBox.

This function converts a regular QComboBox into one with smart filtering:

- Shows matching items as you type
- Case-insensitive filtering
- Items starting with typed text appear first
- Items containing typed text (>= 2 chars) appear after
- Dropdown opens automatically when typing
- Allows entering custom text not in the list

Args:

- `combobox` (`QComboBox`): The QComboBox to enhance with smart filtering

Example:

```python
combo = QComboBox()
combo.addItems(["Apple", "Banana", "Cherry"])
apply_smart_filtering(combo)
```

<details>
<summary>Code:</summary>

```python
def apply_smart_filtering(combobox: QComboBox) -> None:
    # Make it editable if not already
    if not combobox.isEditable():
        combobox.setEditable(True)

    # Allow custom text entry
    combobox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

    # Get existing items and sort them
    items = [combobox.itemText(i) for i in range(combobox.count())]
    items_sorted = sorted(items, key=str.lower)

    # Setup model and proxy
    string_model = QStringListModel(items_sorted)
    proxy_model = SmartFilterProxyModel(combobox)
    proxy_model.setSourceModel(string_model)

    # Setup completer
    completer = QCompleter(proxy_model, combobox)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)

    combobox.setCompleter(completer)

    # Re-populate combobox with sorted items
    combobox.clear()
    combobox.addItems(items_sorted)

    # Store references to prevent garbage collection and maintain smart filtering state
    combobox.smart_filter_model = string_model
    combobox.smart_filter_proxy = proxy_model
    combobox.smart_filter_completer = completer
    combobox.smart_filter_items = items_sorted
    combobox.smart_filter_is_programmatic = False

    # Disconnect any existing text edited signals to avoid duplicates
    with contextlib.suppress(RuntimeError):
        line_edit = combobox.lineEdit()
        if line_edit is not None and hasattr(line_edit, "textEdited"):
            with contextlib.suppress(TypeError, RuntimeError):
                line_edit.textEdited.disconnect()

    # Connect signals
    def on_text_edited(text: str) -> None:
        if hasattr(combobox, "smart_filter_is_programmatic") and combobox.smart_filter_is_programmatic:
            return

        proxy_model.set_filter_text(text)

        if text:
            completer.setCompletionPrefix(text)
            completer.complete()
        else:
            proxy_model.set_filter_text("")
            popup = completer.popup()
            if popup is not None and hasattr(popup, "isVisible") and popup.isVisible() and hasattr(popup, "hide"):
                popup.hide()

    def on_completion_activated(text: str) -> None:
        combobox.smart_filter_is_programmatic = True
        combobox.setCurrentText(text)
        combobox.smart_filter_is_programmatic = False

    line_edit = combobox.lineEdit()
    if line_edit is not None and hasattr(line_edit, "textEdited"):
        line_edit.textEdited.connect(on_text_edited)
    completer.activated.connect(on_completion_activated)
```

</details>
