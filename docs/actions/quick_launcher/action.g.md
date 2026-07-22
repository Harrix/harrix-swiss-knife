---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action.py`

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

Show quick launcher overlay; configure global hotkey on first run (Windows).

<details>
<summary>Code:</summary>

```python
class OnQuickLauncher(ActionBase):

    icon = "⚡"
    title = "Quick launcher…"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("opening quick launcher")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Configure hotkey if needed, then toggle the quick launcher overlay."""
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        hotkey = load_quick_launcher_hotkey()
        if not hotkey:
            dialog = HotkeyCaptureDialog()
            captured: dict[str, str] = {"value": ""}

            def on_captured(value: str) -> None:
                captured["value"] = value

            dialog.hotkey_captured.connect(on_captured)
            if dialog.exec() != dialog.DialogCode.Accepted or not captured["value"].strip():
                return

            hotkey = captured["value"].strip()
            save_quick_launcher_hotkey(hotkey)

            if context.hotkey_manager is not None and not context.hotkey_manager.register(hotkey):
                QMessageBox.warning(
                    None,
                    "Quick launcher hotkey",
                    "Could not register the hotkey. Choose another combination from the tray menu.",
                )

        elif context.hotkey_manager is not None and not context.hotkey_manager.registered_hotkey:
            context.hotkey_manager.register(hotkey)

        context.toggle()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Configure hotkey if needed, then toggle the quick launcher overlay.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        hotkey = load_quick_launcher_hotkey()
        if not hotkey:
            dialog = HotkeyCaptureDialog()
            captured: dict[str, str] = {"value": ""}

            def on_captured(value: str) -> None:
                captured["value"] = value

            dialog.hotkey_captured.connect(on_captured)
            if dialog.exec() != dialog.DialogCode.Accepted or not captured["value"].strip():
                return

            hotkey = captured["value"].strip()
            save_quick_launcher_hotkey(hotkey)

            if context.hotkey_manager is not None and not context.hotkey_manager.register(hotkey):
                QMessageBox.warning(
                    None,
                    "Quick launcher hotkey",
                    "Could not register the hotkey. Choose another combination from the tray menu.",
                )

        elif context.hotkey_manager is not None and not context.hotkey_manager.registered_hotkey:
            context.hotkey_manager.register(hotkey)

        context.toggle()
```

</details>
