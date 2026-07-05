---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `convert_path_to_windows.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnConvertPathToWindows`](#️-class-onconvertpathtowindows)
  - [⚙️ Method `execute`](#️-method-execute)
- [🔧 Function `_to_windows_path`](#-function-_to_windows_path)

</details>

## 🏛️ Class `OnConvertPathToWindows`

```python
class OnConvertPathToWindows(ActionBase)
```

Convert clipboard path with forward slashes to Windows backslash format.

<details>
<summary>Code:</summary>

```python
class OnConvertPathToWindows(ActionBase):

    icon = "🪟"
    title = "Convert path to Windows from clipboard"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("converting path to Windows format")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Read path from clipboard, convert slashes, and copy result back."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        windows_path = _to_windows_path(input_text)
        clipboard.setText(windows_path, QClipboard.Mode.Clipboard)
        self.show_toast("✅ Windows path copied to clipboard.", duration=4000)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Read path from clipboard, convert slashes, and copy result back.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        windows_path = _to_windows_path(input_text)
        clipboard.setText(windows_path, QClipboard.Mode.Clipboard)
        self.show_toast("✅ Windows path copied to clipboard.", duration=4000)
```

</details>

## 🔧 Function `_to_windows_path`

```python
def _to_windows_path(text: str) -> str
```

Normalize path text for Windows: trim, strip quotes, replace `/` with `\\`.

<details>
<summary>Code:</summary>

```python
def _to_windows_path(text: str) -> str:
    return text.strip().strip('"').strip("'").replace("/", "\\")
```

</details>
