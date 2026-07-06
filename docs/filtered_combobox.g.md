---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `filtered_combobox.py`

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
    proxy_model = _SmartFilterProxyModel(combobox)
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
