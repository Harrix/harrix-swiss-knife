---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_edit_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoryEditDialog`](#%EF%B8%8F-class-categoryeditdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)

</details>

## 🏛️ Class `CategoryEditDialog`

```python
class CategoryEditDialog(QDialog)
```

Dialog for editing category name, local name, type, and icon.

<details>
<summary>Code:</summary>

```python
class CategoryEditDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        category_data: dict | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `category_data` (`dict | None`): Category fields (`id`, `name`, `type`, `icon`, `name_local`).
        - `app_config` (`dict[str, Any] | None`): App config for BotHub translation.
        - `bothub_state` (`BothubRequestState | None`): Shared in-flight BotHub request state.

        """
        super().__init__(parent)
        self.category_data = category_data or {}
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self.result_data: dict = {}

        self.setWindowTitle("Edit Category")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(400)

        self._setup_ui()
        self._populate_data()

    def get_result(self) -> dict:
        """Return dialog result with `action` and category fields."""
        return self.result_data

    def _on_delete(self) -> None:
        """Confirm and accept a delete action."""
        name = self.category_data.get("name", "")
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete category '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.result_data = {"action": "delete", "id": self.category_data.get("id")}
            self.accept()

    def _on_save(self) -> None:
        """Validate fields and accept a save action."""
        name = self.name_edit.text().strip()
        if not name:
            message_box.warning(self, "Error", "Category name cannot be empty")
            return

        self.result_data = {
            "action": "save",
            "id": self.category_data.get("id"),
            "name": name,
            "type": self.type_combo.currentIndex(),
            "icon": self.icon_edit.text().strip(),
            "name_local": self.name_local_edit.text().strip(),
        }
        self.accept()

    def _on_translate_clicked(self) -> None:
        request_category_name_local_translation(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self.name_edit,
            name_local_edit=self.name_local_edit,
            translate_button=self.translate_button,
        )

    def _populate_data(self) -> None:
        """Fill widgets from `category_data`."""
        self.name_edit.setText(str(self.category_data.get("name", "")))
        category_type = int(self.category_data.get("type", 0) or 0)
        self.type_combo.setCurrentIndex(0 if category_type == 0 else 1)
        self.icon_edit.setText(str(self.category_data.get("icon", "") or ""))
        self.name_local_edit.setText(str(self.category_data.get("name_local", "") or ""))
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def _setup_ui(self) -> None:
        """Build dialog controls."""
        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Category name")
        name_layout.addWidget(self.name_edit, 1)
        layout.addLayout(name_layout)

        name_local_layout = QHBoxLayout()
        name_local_layout.addWidget(QLabel("Local:"))
        self.name_local_edit = QLineEdit()
        self.name_local_edit.setPlaceholderText("Local name")
        name_local_layout.addWidget(self.name_local_edit, 1)
        self.translate_button = make_emoji_push_button("", "🤖")
        self.translate_button.setToolTip("Translate name to local language with AI")
        self.translate_button.setFixedWidth(36)
        self.translate_button.clicked.connect(self._on_translate_clicked)
        name_local_layout.addWidget(self.translate_button)
        layout.addLayout(name_local_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        type_layout.addWidget(self.type_combo, 1)
        layout.addLayout(type_layout)

        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("Emoji or short icon")
        icon_layout.addWidget(self.icon_edit, 1)
        layout.addLayout(icon_layout)

        button_layout = QHBoxLayout()
        self.delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = make_emoji_push_button("Save", SAVE_BUTTON_EMOJI)
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, category_data: dict | None = None, *, app_config: dict[str, Any] | None = None, bothub_state: BothubRequestState | None = None) -> None
```

Initialize the dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `category_data` (`dict | None`): Category fields (`id`, `name`, `type`, `icon`, `name_local`).
- `app_config` (`dict[str, Any] | None`): App config for BotHub translation.
- `bothub_state` (`BothubRequestState | None`): Shared in-flight BotHub request state.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        category_data: dict | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        super().__init__(parent)
        self.category_data = category_data or {}
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self.result_data: dict = {}

        self.setWindowTitle("Edit Category")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(400)

        self._setup_ui()
        self._populate_data()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> dict
```

Return dialog result with `action` and category fields.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> dict:
        return self.result_data
```

</details>
