---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `quick_launcher.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnQuickLauncher`](#%EF%B8%8F-class-onquicklauncher)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnQuickLauncher`

```python
class OnQuickLauncher(ActionBase)
```

Show or hide the Quick launcher overlay.

<details>
<summary>Code:</summary>

```python
class OnQuickLauncher(ActionBase):

    icon = "⚡"
    title = "Quick launcher"
    description = "Search and run favorite Harrix Swiss Knife commands."
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("opening quick launcher")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Toggle the Quick launcher overlay."""
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        context.toggle()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Toggle the Quick launcher overlay.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        context.toggle()
```

</details>
