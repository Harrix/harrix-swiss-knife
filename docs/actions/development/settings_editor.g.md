---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings_editor.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSettingsEditor`](#%EF%B8%8F-class-onsettingseditor)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🏛️ Class `SettingsEditorDialog`](#%EF%B8%8F-class-settingseditordialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `OnSettingsEditor`

```python
class OnSettingsEditor(ActionBase)
```

Open settings editor.

<details>
<summary>Code:</summary>

```python
class OnSettingsEditor(ActionBase):

    icon = "⚙️"
    title = "Settings Editor"
    description = "Edit config.json in a VS Code style settings editor."

    @ActionBase.handle_exceptions("settings editor")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the settings editor action."""
        dialog = SettingsEditorDialog()
        dialog.exec()
        self.add_line("Settings editor closed.")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the settings editor action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        dialog = SettingsEditorDialog()
        dialog.exec()
        self.add_line("Settings editor closed.")
        self.show_result()
```

</details>

## 🏛️ Class `SettingsEditorDialog`

```python
class SettingsEditorDialog(QDialog)
```

A VS Code style settings editor for `config.json`.

<details>
<summary>Code:</summary>

```python
class SettingsEditorDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the settings editor."""
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(900, 600)

        self.config_path = get_config_path_str()
        try:
            self.config_data = h.dev.config_load(self.config_path)
        except Exception:
            self.config_data = {}

        self.categories: dict[str, dict[str, Any]] = self._categorize_config(self.config_data)
        self.input_widgets: dict[str, QWidget] = {}

        self._setup_ui()

    def _categorize_config(self, data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        categories: dict[str, dict[str, Any]] = {"General": {}}
        for key, value in data.items():
            if isinstance(value, dict) and value:
                categories[key] = value
            else:
                categories["General"][key] = value
        return categories

    def _clear_layout(self, layout: Any) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_settings_layout(self) -> None:
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _on_category_changed(self, row: int) -> None:
        if self.search_input.text():
            self.search_input.clear()  # This will trigger _on_search and render the category
            return

        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()

        cat_name = self.list_categories.item(row).text()
        self._render_category(cat_name)

    def _on_save(self) -> None:
        self._save_current_category()

        new_config = dict(self.categories["General"])
        new_config.update({k: v for k, v in self.categories.items() if k != "General"})

        try:
            with Path(self.config_path).open("w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
                f.write("\n")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")

    def _on_search(self, text: str) -> None:
        search_term = text.lower()
        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()

        if not search_term:
            # If search is cleared, show current category
            row = self.list_categories.currentRow()
            if row >= 0:
                self._render_category(self.list_categories.item(row).text())
            return

        # Show matching settings across all categories
        for cat_name, settings in self.categories.items():
            matching_settings = {k: v for k, v in settings.items() if search_term in k.lower()}
            if matching_settings:
                title = QLabel(f"<h2>{cat_name}</h2>")
                self.settings_layout.addWidget(title)
                self._render_settings(cat_name, matching_settings)

    def _render_category(self, cat_name: str) -> None:
        title = QLabel(f"<h2>{cat_name}</h2>")
        self.settings_layout.addWidget(title)
        self._render_settings(cat_name, self.categories[cat_name])

    def _render_settings(self, cat_name: str, settings: dict[str, Any]) -> None:
        for key, value in settings.items():
            setting_layout = QVBoxLayout()
            label = QLabel(f"<b>{key}</b>")
            setting_layout.addWidget(label)

            widget_key = f"{cat_name}::{key}"

            if isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget
            elif isinstance(value, (int, float, str)):
                widget = QLineEdit(str(value))
                setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget
            else:
                # Lists or complex objects
                widget = QTextEdit()
                widget.setPlainText(json.dumps(value, indent=2, ensure_ascii=False))
                widget.setMaximumHeight(100)
                setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget

            self.settings_layout.addLayout(setting_layout)
            self.settings_layout.addSpacing(10)

    def _save_current_category(self) -> None:
        for widget_key, widget in self.input_widgets.items():
            cat_name, key = widget_key.split("::", 1)

            if isinstance(widget, QCheckBox):
                self.categories[cat_name][key] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                old_val = self.categories[cat_name][key]
                text = widget.text()
                if isinstance(old_val, int):
                    try:
                        self.categories[cat_name][key] = int(text)
                    except ValueError:
                        self.categories[cat_name][key] = text
                elif isinstance(old_val, float):
                    try:
                        self.categories[cat_name][key] = float(text)
                    except ValueError:
                        self.categories[cat_name][key] = text
                else:
                    self.categories[cat_name][key] = text
            elif isinstance(widget, QTextEdit):
                import contextlib

                with contextlib.suppress(json.JSONDecodeError):
                    self.categories[cat_name][key] = json.loads(widget.toPlainText())

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search settings...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left pane: Categories
        self.list_categories = QListWidget()
        for cat in self.categories:
            self.list_categories.addItem(cat)
        self.list_categories.currentRowChanged.connect(self._on_category_changed)
        splitter.addWidget(self.list_categories)

        # Right pane: Settings
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.settings_container)
        splitter.addWidget(self.scroll_area)

        splitter.setSizes([200, 700])

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        if self.list_categories.count() > 0:
            self.list_categories.setCurrentRow(0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the settings editor.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(900, 600)

        self.config_path = get_config_path_str()
        try:
            self.config_data = h.dev.config_load(self.config_path)
        except Exception:
            self.config_data = {}

        self.categories: dict[str, dict[str, Any]] = self._categorize_config(self.config_data)
        self.input_widgets: dict[str, QWidget] = {}

        self._setup_ui()
```

</details>
