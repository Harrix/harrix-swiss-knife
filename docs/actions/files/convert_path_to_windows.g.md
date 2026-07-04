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

Convert a path with forward slashes to Windows backslash format.

<details>
<summary>Code:</summary>

```python
class OnConvertPathToWindows(ActionBase):

    icon = "🪟"
    title = "Convert path to Windows"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("converting path to Windows format")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show path dialog, convert slashes, and copy result to clipboard."""
        clipboard = QApplication.clipboard()
        default_path = ""
        if clipboard is not None:
            default_path = clipboard.text(QClipboard.Mode.Clipboard) or ""

        path = self.dialogs.get_text_input("Convert path to Windows", "Enter path:", default_path)
        if path is None:
            return

        windows_path = _to_windows_path(path)
        self.text_to_clipboard(windows_path)
        self.add_line(windows_path)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Show path dialog, convert slashes, and copy result to clipboard.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        clipboard = QApplication.clipboard()
        default_path = ""
        if clipboard is not None:
            default_path = clipboard.text(QClipboard.Mode.Clipboard) or ""

        path = self.dialogs.get_text_input("Convert path to Windows", "Enter path:", default_path)
        if path is None:
            return

        windows_path = _to_windows_path(path)
        self.text_to_clipboard(windows_path)
        self.add_line(windows_path)
        self.show_result()
```

</details>

## 🔧 Function `_to_windows_path`

```python
def _to_windows_path(text: str) -> str
```

Normalize path text for Windows: trim, strip quotes, replace `/` with `\`.

<details>
<summary>Code:</summary>

```python
def _to_windows_path(text: str) -> str:
    return text.strip().strip('"').strip("'").replace("/", "\\")
```

</details>
