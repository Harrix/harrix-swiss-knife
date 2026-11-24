---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `commands.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCommands`](#%EF%B8%8F-class-oncommands)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnCommands`

```python
class OnCommands(ActionBase)
```

Show the Commands window with the tray command list and Fluent cards.

<details>
<summary>Code:</summary>

```python
class OnCommands(ActionBase):

    icon = "🗂️"
    title = "Commands"
    description = "Browse and run Harrix Swiss Knife commands as cards."
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("opening commands")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show or raise the command-cards window."""
        if show_command_window():
            return
        message_box.critical(None, "Commands", "Tray icon is not initialized.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Show or raise the command-cards window.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if show_command_window():
            return
        message_box.critical(None, "Commands", "Tray icon is not initialized.")
```

</details>
