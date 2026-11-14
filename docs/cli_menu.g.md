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
- [🔧 Function `format_copy_action_class_menu_label`](#-function-format_copy_action_class_menu_label)
- [🔧 Function `format_copy_action_name_menu_label`](#-function-format_copy_action_name_menu_label)
- [🔧 Function `format_copy_action_path_menu_label`](#-function-format_copy_action_path_menu_label)
- [🔧 Function `format_copy_cli_menu_label`](#-function-format_copy_cli_menu_label)
- [🔧 Function `get_action_identity_parts`](#-function-get_action_identity_parts)
- [🔧 Function `get_action_identity_text`](#-function-get_action_identity_text)
- [🔧 Function `get_cli_copy_command`](#-function-get_cli_copy_command)
- [🔧 Function `is_tracker_launcher_action`](#-function-is_tracker_launcher_action)
- [🔧 Function `iter_tracker_launcher_actions`](#-function-iter_tracker_launcher_actions)
- [🔧 Function `show_action_class_context_menu`](#-function-show_action_class_context_menu)
- [🔧 Function `show_action_identity_context_menu`](#-function-show_action_identity_context_menu)
- [🔧 Function `show_action_item_context_menu`](#-function-show_action_item_context_menu)
- [🔧 Function `show_open_all_trackers_menu`](#-function-show_open_all_trackers_menu)
- [🔧 Function `trigger_all_tracker_launchers`](#-function-trigger_all_tracker_launchers)
- [🔧 Function `truncate_action_name_preview`](#-function-truncate_action_name_preview)

</details>

## 🏛️ Class `CliContextMenu`

```python
class CliContextMenu(FluentMenu)
```

Tray menu: middle-click copies identity; right-click on trackers opens all four.

<details>
<summary>Code:</summary>

```python
class CliContextMenu(FluentMenu):

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle middle-click identity copy and right-click open-all for trackers."""
        action = self.actionAt(event.position().toPoint())
        if action is not None and not action.isSeparator() and action.menu() is None:
            if event.button() == Qt.MouseButton.MiddleButton:
                show_action_item_context_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    action=action,
                )
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton and is_tracker_launcher_action(action):
                show_open_all_trackers_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    host_menu=self,
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

Handle middle-click identity copy and right-click open-all for trackers.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        action = self.actionAt(event.position().toPoint())
        if action is not None and not action.isSeparator() and action.menu() is None:
            if event.button() == Qt.MouseButton.MiddleButton:
                show_action_item_context_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    action=action,
                )
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton and is_tracker_launcher_action(action):
                show_open_all_trackers_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    host_menu=self,
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

## 🔧 Function `format_copy_action_class_menu_label`

```python
def format_copy_action_class_menu_label(class_name: str) -> str
```

Build context menu item text: prefix, colon, and the class name to copy.

<details>
<summary>Code:</summary>

```python
def format_copy_action_class_menu_label(class_name: str) -> str:
    return f"{COPY_ACTION_CLASS_MENU_PREFIX}{class_name}"
```

</details>

## 🔧 Function `format_copy_action_name_menu_label`

```python
def format_copy_action_name_menu_label(name: str) -> str
```

Build context menu item text: prefix, colon, and a shortened name preview.

<details>
<summary>Code:</summary>

```python
def format_copy_action_name_menu_label(name: str) -> str:
    return f"{COPY_ACTION_NAME_MENU_PREFIX}{truncate_action_name_preview(name)}"
```

</details>

## 🔧 Function `format_copy_action_path_menu_label`

```python
def format_copy_action_path_menu_label(path: str) -> str
```

Build context menu item text: prefix, colon, and the path to copy.

<details>
<summary>Code:</summary>

```python
def format_copy_action_path_menu_label(path: str) -> str:
    return f"{COPY_ACTION_PATH_MENU_PREFIX}{path}"
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

## 🔧 Function `get_action_identity_parts`

```python
def get_action_identity_parts(action: QAction | None) -> ActionIdentityParts | None
```

Return name/class/path parts stored on a menu action, if any.

<details>
<summary>Code:</summary>

```python
def get_action_identity_parts(action: QAction | None) -> ActionIdentityParts | None:
    if action is None:
        return None
    parts = getattr(action, "action_identity_parts", None)
    if isinstance(parts, ActionIdentityParts):
        return parts
    return None
```

</details>

## 🔧 Function `get_action_identity_text`

```python
def get_action_identity_text(action: QAction | None) -> str | None
```

Return the name/class/path snippet stored on a menu action, if any.

<details>
<summary>Code:</summary>

```python
def get_action_identity_text(action: QAction | None) -> str | None:
    if action is None:
        return None
    text = getattr(action, "action_identity_text", None)
    if isinstance(text, str) and text:
        return text
    parts = get_action_identity_parts(action)
    if parts is None:
        return None
    return f"{parts.name}\n{parts.class_name}\n{parts.path}"
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

## 🔧 Function `is_tracker_launcher_action`

```python
def is_tracker_launcher_action(action: QAction | None) -> bool
```

Return whether `action` is one of the four tray tracker launchers.

<details>
<summary>Code:</summary>

```python
def is_tracker_launcher_action(action: QAction | None) -> bool:
    parts = get_action_identity_parts(action)
    return parts is not None and parts.class_name in TRACKER_LAUNCHER_CLASS_NAMES
```

</details>

## 🔧 Function `iter_tracker_launcher_actions`

```python
def iter_tracker_launcher_actions(menu: QMenu) -> Iterable[QAction]
```

Yield Finance/Fitness/Food/Habits leaf actions from [`menu`](qt_split_menu_button.g.md#%EF%B8%8F-method-menu) in menu order.

<details>
<summary>Code:</summary>

```python
def iter_tracker_launcher_actions(menu: QMenu) -> Iterable[QAction]:
    for action in menu.actions():
        if is_tracker_launcher_action(action):
            yield action
```

</details>

## 🔧 Function `show_action_class_context_menu`

```python
def show_action_class_context_menu(*, parent: QWidget | None, global_pos: QPoint, action_cls: type, host_widget: QWidget | None = None) -> None
```

Show copy name/class/path (and CLI when available) for an action class.

<details>
<summary>Code:</summary>

```python
def show_action_class_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action_cls: type,
    host_widget: QWidget | None = None,
) -> None:
    identity_parts = action_identity_parts(action_cls)
    identity_text = format_action_identity_text(action_cls)
    cli_copy_command: str | None = None
    if getattr(action_cls, "cli_available", False):
        cli_copy_command = build_cli_copy_command(str(getattr(action_cls, "cli_hint", "") or ""))
    show_action_identity_context_menu(
        parent=parent,
        global_pos=global_pos,
        identity_text=identity_text,
        identity_parts=identity_parts,
        cli_copy_command=cli_copy_command,
        host_widget=host_widget,
    )
```

</details>

## 🔧 Function `show_action_identity_context_menu`

```python
def show_action_identity_context_menu(*, parent: QWidget | None, global_pos: QPoint, identity_text: str | None = None, identity_parts: ActionIdentityParts | None = None, cli_copy_command: str | None = None, host_widget: QWidget | None = None) -> None
```

Show a context menu to copy action identity fields and optional CLI command.

<details>
<summary>Code:</summary>

```python
def show_action_identity_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    identity_text: str | None = None,
    identity_parts: ActionIdentityParts | None = None,
    cli_copy_command: str | None = None,
    host_widget: QWidget | None = None,
) -> None:
    if identity_text is None and identity_parts is None and cli_copy_command is None and host_widget is None:
        return

    menu = FluentMenu("", parent)
    if identity_text is not None:
        copy_identity = menu.addAction(COPY_ACTION_IDENTITY_MENU_LABEL)
        copy_identity.triggered.connect(
            lambda *_args, text=identity_text: copy_text_to_clipboard(text),
        )
    if identity_parts is not None:
        copy_name = menu.addAction(format_copy_action_name_menu_label(identity_parts.name))
        copy_name.triggered.connect(
            lambda *_args, text=identity_parts.name: copy_text_to_clipboard(text),
        )
        copy_class = menu.addAction(format_copy_action_class_menu_label(identity_parts.class_name))
        copy_class.triggered.connect(
            lambda *_args, text=identity_parts.class_name: copy_text_to_clipboard(text),
        )
        copy_path = menu.addAction(format_copy_action_path_menu_label(identity_parts.path))
        copy_path.triggered.connect(
            lambda *_args, text=identity_parts.path: copy_text_to_clipboard(text),
        )
    if cli_copy_command is not None:
        if not menu.isEmpty():
            menu.addSeparator()
        copy_cli = menu.addAction(format_copy_cli_menu_label(cli_copy_command))
        copy_cli.triggered.connect(
            lambda *_args, cmd=cli_copy_command: copy_cli_command_to_clipboard(cmd),
        )
    if host_widget is not None:
        if not menu.isEmpty():
            menu.addSeparator()
        add_widget_identity_actions(menu, host_widget)
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)
```

</details>

## 🔧 Function `show_action_item_context_menu`

```python
def show_action_item_context_menu(*, parent: QWidget | None, global_pos: QPoint, action: QAction, host_widget: QWidget | None = None) -> None
```

Show a context menu to copy action identity and, when present, the CLI command.

<details>
<summary>Code:</summary>

```python
def show_action_item_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action: QAction,
    host_widget: QWidget | None = None,
) -> None:
    show_action_identity_context_menu(
        parent=parent,
        global_pos=global_pos,
        identity_text=get_action_identity_text(action),
        identity_parts=get_action_identity_parts(action),
        cli_copy_command=get_cli_copy_command(action),
        host_widget=host_widget,
    )
```

</details>

## 🔧 Function `show_open_all_trackers_menu`

```python
def show_open_all_trackers_menu(*, parent: QWidget | None, global_pos: QPoint, host_menu: QMenu) -> None
```

Show a one-item menu that opens Finance, Fitness, Food, and Habits.

<details>
<summary>Code:</summary>

```python
def show_open_all_trackers_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    host_menu: QMenu,
) -> None:
    menu = FluentMenu("", parent)
    open_all = menu.addAction(OPEN_ALL_TRACKERS_MENU_LABEL)
    open_all.triggered.connect(lambda *_args, source=host_menu: trigger_all_tracker_launchers(source))
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)
```

</details>

## 🔧 Function `trigger_all_tracker_launchers`

```python
def trigger_all_tracker_launchers(menu: QMenu) -> None
```

Trigger every tracker launcher QAction found on [`menu`](qt_split_menu_button.g.md#%EF%B8%8F-method-menu).

<details>
<summary>Code:</summary>

```python
def trigger_all_tracker_launchers(menu: QMenu) -> None:
    for action in iter_tracker_launcher_actions(menu):
        action.trigger()
```

</details>

## 🔧 Function `truncate_action_name_preview`

```python
def truncate_action_name_preview(name: str, max_len: int = COPY_ACTION_NAME_PREVIEW_MAX_LEN) -> str
```

Return `name` unchanged, or a prefix ending with `…` when it is too long.

<details>
<summary>Code:</summary>

```python
def truncate_action_name_preview(name: str, max_len: int = COPY_ACTION_NAME_PREVIEW_MAX_LEN) -> str:
    if max_len <= 0:
        return _ELLIPSIS
    if len(name) <= max_len:
        return name
    return name[:max_len].rstrip() + _ELLIPSIS
```

</details>
