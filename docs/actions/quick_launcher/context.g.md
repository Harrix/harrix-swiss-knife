---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `context.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `QuickLauncherContext`](#%EF%B8%8F-class-quicklaunchercontext)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `action_classes`](#%EF%B8%8F-method-action_classes)
  - [⚙️ Method `toggle`](#%EF%B8%8F-method-toggle)
- [🔧 Function `get_quick_launcher_context`](#-function-get_quick_launcher_context)
- [🔧 Function `set_quick_launcher_context`](#-function-set_quick_launcher_context)

</details>

## 🏛️ Class `QuickLauncherContext`

```python
class QuickLauncherContext
```

Holds quick launcher dependencies for menu action and global hotkey.

<details>
<summary>Code:</summary>

```python
class QuickLauncherContext:

    def __init__(
        self,
        *,
        output_bus: ActionOutputBus | None,
        hotkey_manager: GlobalHotkeyManager | None,
        menu_structure_provider: Callable[[], list[Any]],
        parent: QWidget | None = None,
    ) -> None:
        """Store dependencies used by the tray action and global hotkey handler."""
        self.output_bus = output_bus
        self.hotkey_manager = hotkey_manager
        self._menu_structure_provider = menu_structure_provider
        self.parent = parent

    def action_classes(self) -> list[type[ActionBase]]:
        """Return quick-launcher action classes from the current menu structure."""
        actions = collect_quick_launcher_actions(self._menu_structure_provider())
        if load_quick_launcher_markdown_in_panel():
            actions = [action_cls for action_cls in actions if action_cls.__name__ != "OnNewMarkdown"]
        return actions

    def toggle(self) -> None:
        """Toggle the quick launcher overlay."""
        QuickLauncherDialog.toggle(
            parent=self.parent,
            output_bus=self.output_bus,
            action_classes=self.action_classes(),
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Store dependencies used by the tray action and global hotkey handler.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        output_bus: ActionOutputBus | None,
        hotkey_manager: GlobalHotkeyManager | None,
        menu_structure_provider: Callable[[], list[Any]],
        parent: QWidget | None = None,
    ) -> None:
        self.output_bus = output_bus
        self.hotkey_manager = hotkey_manager
        self._menu_structure_provider = menu_structure_provider
        self.parent = parent
```

</details>

### ⚙️ Method `action_classes`

```python
def action_classes(self) -> list[type[ActionBase]]
```

Return quick-launcher action classes from the current menu structure.

<details>
<summary>Code:</summary>

```python
def action_classes(self) -> list[type[ActionBase]]:
        actions = collect_quick_launcher_actions(self._menu_structure_provider())
        if load_quick_launcher_markdown_in_panel():
            actions = [action_cls for action_cls in actions if action_cls.__name__ != "OnNewMarkdown"]
        return actions
```

</details>

### ⚙️ Method `toggle`

```python
def toggle(self) -> None
```

Toggle the quick launcher overlay.

<details>
<summary>Code:</summary>

```python
def toggle(self) -> None:
        QuickLauncherDialog.toggle(
            parent=self.parent,
            output_bus=self.output_bus,
            action_classes=self.action_classes(),
        )
```

</details>

## 🔧 Function `get_quick_launcher_context`

```python
def get_quick_launcher_context() -> QuickLauncherContext | None
```

Return the process-wide quick launcher context, if initialized.

<details>
<summary>Code:</summary>

```python
def get_quick_launcher_context() -> QuickLauncherContext | None:
    return _context
```

</details>

## 🔧 Function `set_quick_launcher_context`

```python
def set_quick_launcher_context(context: QuickLauncherContext | None) -> None
```

Set the process-wide quick launcher context.

<details>
<summary>Code:</summary>

```python
def set_quick_launcher_context(context: QuickLauncherContext | None) -> None:
    global _context  # noqa: PLW0603
    _context = context
```

</details>
