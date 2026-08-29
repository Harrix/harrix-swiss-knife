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
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(dialog)
        dialog.exec()
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
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(dialog)
        dialog.exec()
```

</details>
