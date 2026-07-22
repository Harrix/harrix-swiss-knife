---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `cli_menu.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CliContextMenu`](#%EF%B8%8F-class-clicontextmenu)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
- [🔧 Function `build_cli_copy_command`](#-function-build_cli_copy_command)
- [🔧 Function `copy_cli_command_to_clipboard`](#-function-copy_cli_command_to_clipboard)
- [🔧 Function `copy_text_to_clipboard`](#-function-copy_text_to_clipboard)
- [🔧 Function `format_copy_cli_menu_label`](#-function-format_copy_cli_menu_label)
- [🔧 Function `get_cli_copy_command`](#-function-get_cli_copy_command)
- [🔧 Function `show_copy_cli_menu`](#-function-show_copy_cli_menu)

</details>

## 🏛️ Class `CliContextMenu`

```python
class CliContextMenu(QMenu)
```

QMenu that offers Copy CLI command on right-click for CLI-enabled actions.

<details>
<summary>Code:</summary>

```python
class CliContextMenu(QMenu):

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """On right-click over a CLI action, show the copy-command context menu."""
        if event.button() == Qt.MouseButton.RightButton:
            action = self.actionAt(event.pos())
            cmd = get_cli_copy_command(action)
            if cmd is not None:
                show_copy_cli_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    cli_copy_command=cmd,
                )
                event.accept()
                return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

On right-click over a CLI action, show the copy-command context menu.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.RightButton:
            action = self.actionAt(event.pos())
            cmd = get_cli_copy_command(action)
            if cmd is not None:
                show_copy_cli_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    cli_copy_command=cmd,
                )
                event.accept()
                return
        super().mouseReleaseEvent(event)
```

</details>

## 🔧 Function `build_cli_copy_command`

```python
def build_cli_copy_command(hint: str) -> str
```

Build a full CLI invocation string for clipboard and tooltips.

<details>
<summary>Code:</summary>

```python
def build_cli_copy_command(hint: str) -> str:
    stripped = hint.strip()
    if stripped:
        return f"{CLI_EXECUTABLE} {stripped}"
    return CLI_EXECUTABLE
```

</details>

## 🔧 Function `copy_cli_command_to_clipboard`

```python
def copy_cli_command_to_clipboard(command: str) -> None
```

Copy a full CLI command string to the system clipboard.

<details>
<summary>Code:</summary>

```python
def copy_cli_command_to_clipboard(command: str) -> None:
    copy_text_to_clipboard(command)
```

</details>

## 🔧 Function `copy_text_to_clipboard`

```python
def copy_text_to_clipboard(text: str) -> None
```

Copy text to the system clipboard.

<details>
<summary>Code:</summary>

```python
def copy_text_to_clipboard(text: str) -> None:
    clipboard = QGuiApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(text, QClipboard.Mode.Clipboard)
```

</details>

## 🔧 Function `format_copy_cli_menu_label`

```python
def format_copy_cli_menu_label(cli_copy_command: str) -> str
```

Build context menu item text: prefix, colon, and the command to copy.

<details>
<summary>Code:</summary>

```python
def format_copy_cli_menu_label(cli_copy_command: str) -> str:
    return f"{COPY_CLI_MENU_PREFIX}{cli_copy_command}"
```

</details>

## 🔧 Function `get_cli_copy_command`

```python
def get_cli_copy_command(action: QAction | None) -> str | None
```

Return the CLI copy string stored on a menu action, if any.

<details>
<summary>Code:</summary>

```python
def get_cli_copy_command(action: QAction | None) -> str | None:
    if action is None:
        return None
    cmd = getattr(action, "cli_copy_command", None)
    if isinstance(cmd, str) and cmd:
        return cmd
    return None
```

</details>

## 🔧 Function `show_copy_cli_menu`

```python
def show_copy_cli_menu() -> None
```

Show a small context menu to copy a CLI command to the clipboard.

<details>
<summary>Code:</summary>

```python
def show_copy_cli_menu(*, parent: QWidget | None, global_pos: QPoint, cli_copy_command: str) -> None:
    menu = QMenu(parent)
    copy_action = menu.addAction(format_copy_cli_menu_label(cli_copy_command))
    copy_action.triggered.connect(lambda: copy_cli_command_to_clipboard(cli_copy_command))
    menu.exec_(global_pos)
```

</details>
