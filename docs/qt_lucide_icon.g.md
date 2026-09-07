---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_lucide_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_lucide_action`](#-function-add_lucide_action)
- [🔧 Function `apply_leading_chrome_button_icon`](#-function-apply_leading_chrome_button_icon)
- [🔧 Function `apply_leading_chrome_buttons`](#-function-apply_leading_chrome_buttons)
- [🔧 Function `apply_leading_chrome_icon`](#-function-apply_leading_chrome_icon)
- [🔧 Function `apply_leading_chrome_icons`](#-function-apply_leading_chrome_icons)
- [🔧 Function `apply_lucide_action_icon`](#-function-apply_lucide_action_icon)
- [🔧 Function `apply_lucide_button_icon`](#-function-apply_lucide_button_icon)
- [🔧 Function `apply_lucide_dialog_buttons`](#-function-apply_lucide_dialog_buttons)
- [🔧 Function `create_ai_lucide_icon`](#-function-create_ai_lucide_icon)
- [🔧 Function `create_lucide_icon`](#-function-create_lucide_icon)
- [🔧 Function `lucide_color_for`](#-function-lucide_color_for)
- [🔧 Function `lucide_name_for_chrome_emoji`](#-function-lucide_name_for_chrome_emoji)
- [🔧 Function `lucide_svg_path`](#-function-lucide_svg_path)
- [🔧 Function `make_ai_lucide_push_button`](#-function-make_ai_lucide_push_button)
- [🔧 Function `make_lucide_push_button`](#-function-make_lucide_push_button)
- [🔧 Function `set_action_text_with_lucide_icon`](#-function-set_action_text_with_lucide_icon)
- [🔧 Function `style_accept_button`](#-function-style_accept_button)
- [🔧 Function `style_cancel_button`](#-function-style_cancel_button)

</details>

## 🔧 Function `add_lucide_action`

```python
def add_lucide_action(menu: QMenu, label: str, name: str, *, icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE) -> QAction
```

Add a menu action with a Lucide `QIcon` and plain `label` text.

<details>
<summary>Code:</summary>

```python
def add_lucide_action(
    menu: QMenu,
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> QAction:
    action = menu.addAction(label)
    apply_lucide_action_icon(action, name, icon_size=icon_size)
    return action
```

</details>

## 🔧 Function `apply_leading_chrome_button_icon`

```python
def apply_leading_chrome_button_icon(button: QAbstractButton, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> bool
```

Move a leading chrome emoji from `button` text onto a Lucide `QIcon`.

Returns `True` when a mapped emoji prefix was converted.

<details>
<summary>Code:</summary>

```python
def apply_leading_chrome_button_icon(
    button: QAbstractButton,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> bool:
    emoji, rest = split_leading_emoji(button.text())
    if not emoji:
        return False
    name = lucide_name_for_chrome_emoji(emoji)
    if name is None:
        logger.warning("No Lucide mapping for chrome emoji %r", emoji)
        return False
    if name == "clipboard-list" and rest.casefold().startswith("copy"):
        name = COPY_BUTTON_ICON
    color = AI_BUTTON_ICON_COLOR if _is_ai_chrome_emoji(emoji) else None
    apply_lucide_button_icon(button, name, icon_size=icon_size, color=color)
    button.setText(rest)
    return True
```

</details>

## 🔧 Function `apply_leading_chrome_buttons`

```python
def apply_leading_chrome_buttons(root: QWidget, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> None
```

Convert leading chrome emoji prefixes on push and tool buttons under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_leading_chrome_buttons(
    root: QWidget,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    for button in root.findChildren(QAbstractButton):
        if isinstance(button, (QPushButton, QToolButton)):
            apply_leading_chrome_button_icon(button, icon_size=icon_size)
```

</details>

## 🔧 Function `apply_leading_chrome_icon`

```python
def apply_leading_chrome_icon(action: QAction, *, icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE) -> bool
```

Move a leading chrome emoji from `action` text onto a Lucide `QIcon`.

Returns `True` when a mapped emoji prefix was converted.

<details>
<summary>Code:</summary>

```python
def apply_leading_chrome_icon(
    action: QAction,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> bool:
    emoji, rest = split_leading_emoji(action.text())
    if not emoji:
        return False
    name = lucide_name_for_chrome_emoji(emoji)
    if name is None:
        logger.warning("No Lucide mapping for chrome emoji %r", emoji)
        return False
    if name == "clipboard-list" and rest.casefold().startswith("copy"):
        name = COPY_BUTTON_ICON
    color = AI_BUTTON_ICON_COLOR if _is_ai_chrome_emoji(emoji) else None
    apply_lucide_action_icon(action, name, icon_size=icon_size, color=color)
    action.setText(rest)
    return True
```

</details>

## 🔧 Function `apply_leading_chrome_icons`

```python
def apply_leading_chrome_icons(menu: QMenu | QMenuBar, *, icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE) -> None
```

Convert leading chrome emoji prefixes on `menu` actions into Lucide icons.

<details>
<summary>Code:</summary>

```python
def apply_leading_chrome_icons(
    menu: QMenu | QMenuBar,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> None:
    for action in menu.actions():
        if action.isSeparator():
            continue
        apply_leading_chrome_icon(action, icon_size=icon_size)
        submenu = action.menu()
        if isinstance(submenu, QMenu):
            apply_leading_chrome_icons(submenu, icon_size=icon_size)
```

</details>

## 🔧 Function `apply_lucide_action_icon`

```python
def apply_lucide_action_icon(action: QAction, name: str, *, icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE, color: QColor | str | None = None) -> None
```

Set a Lucide icon on `action` without changing its text.

<details>
<summary>Code:</summary>

```python
def apply_lucide_action_icon(
    action: QAction,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
    color: QColor | str | None = None,
) -> None:
    if name:
        action.setIcon(create_lucide_icon(name, icon_size, color=color))
```

</details>

## 🔧 Function `apply_lucide_button_icon`

```python
def apply_lucide_button_icon(button: QAbstractButton, name: str, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE, color: QColor | str | None = None) -> None
```

Set a Lucide icon on an existing button.

<details>
<summary>Code:</summary>

```python
def apply_lucide_button_icon(
    button: QAbstractButton,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
) -> None:
    button.setIcon(create_lucide_icon(name, icon_size, color=color))
    button.setIconSize(QSize(icon_size, icon_size))
    button.setProperty(_LUCIDE_NAME_PROP, name)
```

</details>

## 🔧 Function `apply_lucide_dialog_buttons`

```python
def apply_lucide_dialog_buttons(buttons: QDialogButtonBox, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> None
```

Set Lucide icons on standard `QDialogButtonBox` buttons when present.

Also paints OK / Apply / Save / Yes green and Cancel / No / Reject red,
with white icons on those filled backgrounds.

<details>
<summary>Code:</summary>

```python
def apply_lucide_dialog_buttons(
    buttons: QDialogButtonBox,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    for standard_button, name in (
        (QDialogButtonBox.StandardButton.Ok, OK_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Apply, APPLY_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Cancel, CANCEL_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Save, SAVE_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Close, CLOSE_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Yes, OK_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.No, CANCEL_BUTTON_ICON),
    ):
        button = buttons.button(standard_button)
        if button is not None:
            apply_lucide_button_icon(button, name, icon_size=icon_size)
    for button in buttons.buttons():
        role = buttons.buttonRole(button)
        if role in (
            QDialogButtonBox.ButtonRole.AcceptRole,
            QDialogButtonBox.ButtonRole.ApplyRole,
            QDialogButtonBox.ButtonRole.YesRole,
        ):
            style_accept_button(button, icon_size=icon_size)
        elif role in (
            QDialogButtonBox.ButtonRole.RejectRole,
            QDialogButtonBox.ButtonRole.NoRole,
        ):
            style_cancel_button(button, icon_size=icon_size)
```

</details>

## 🔧 Function `create_ai_lucide_icon`

```python
def create_ai_lucide_icon(size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> QIcon
```

Create the shared AI chrome icon (`sparkles` in `#2e86b7`).

<details>
<summary>Code:</summary>

```python
def create_ai_lucide_icon(size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> QIcon:
    return create_lucide_icon(AI_BUTTON_ICON, size, color=AI_BUTTON_ICON_COLOR)
```

</details>

## 🔧 Function `create_lucide_icon`

```python
def create_lucide_icon(name: str, size: int = 64, *, color: QColor | str | None = None, device_pixel_ratio: float | None = None) -> QIcon
```

Create a square `QIcon` from a Lucide SVG ID.

When `color` is omitted, uses the CodeStyle semantic color for `name`.
Unknown names log a warning and return an empty icon.

<details>
<summary>Code:</summary>

```python
def create_lucide_icon(
    name: str,
    size: int = 64,
    *,
    color: QColor | str | None = None,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    ratio = device_pixel_ratio if device_pixel_ratio is not None else _lucide_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    paint_color = QColor(color) if color is not None else QColor(lucide_color_for(name))
    cache_key = (name, size, paint_color.name(QColor.NameFormat.HexArgb), ratio)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached

    svg_bytes = _lucide_svg_bytes(name, paint_color)
    if svg_bytes is None:
        return QIcon()

    physical = max(1, round(size * ratio))
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    if not renderer.isValid():
        logger.warning("Lucide SVG for `%s` is invalid", name)
        return QIcon()

    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    renderer.render(painter, QRectF(0.0, 0.0, float(physical), float(physical)))
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    _CACHE[cache_key] = icon
    return icon
```

</details>

## 🔧 Function `lucide_color_for`

```python
def lucide_color_for(name: str) -> str
```

Return the CodeStyle hex color for Lucide ID `name` (or dark default).

<details>
<summary>Code:</summary>

```python
def lucide_color_for(name: str) -> str:
    return LUCIDE_ICON_COLORS.get(name, LUCIDE_COLOR_DARK)
```

</details>

## 🔧 Function `lucide_name_for_chrome_emoji`

```python
def lucide_name_for_chrome_emoji(emoji: str) -> str | None
```

Return the Lucide ID for a chrome emoji, or `None` when unmapped.

<details>
<summary>Code:</summary>

```python
def lucide_name_for_chrome_emoji(emoji: str) -> str | None:
    if emoji in CHROME_EMOJI_TO_LUCIDE:
        return CHROME_EMOJI_TO_LUCIDE[emoji]
    stripped = emoji.replace("\ufe0f", "").replace("\u200d", "")
    return CHROME_EMOJI_TO_LUCIDE.get(stripped)
```

</details>

## 🔧 Function `lucide_svg_path`

```python
def lucide_svg_path(name: str) -> Path | None
```

Return the SVG path for `name`, or `None` when the ID is invalid or missing.

<details>
<summary>Code:</summary>

```python
def lucide_svg_path(name: str) -> Path | None:
    if not _ICON_NAME_RE.fullmatch(name):
        return None
    path = _lucide_dir() / f"{name}.svg"
    if not path.is_file():
        return None
    return path
```

</details>

## 🔧 Function `make_ai_lucide_push_button`

```python
def make_ai_lucide_push_button(label: str, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE, parent: QWidget | None = None) -> QPushButton
```

Create a push button with the shared AI `sparkles` icon.

<details>
<summary>Code:</summary>

```python
def make_ai_lucide_push_button(
    label: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    parent: QWidget | None = None,
) -> QPushButton:
    return make_lucide_push_button(
        label,
        AI_BUTTON_ICON,
        icon_size=icon_size,
        color=AI_BUTTON_ICON_COLOR,
        parent=parent,
    )
```

</details>

## 🔧 Function `make_lucide_push_button`

```python
def make_lucide_push_button(label: str, name: str, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE, color: QColor | str | None = None, parent: QWidget | None = None) -> QPushButton
```

Create a push button with a Lucide icon.

Labels that are Cancel (or start with `Cancel`) get the shared red chrome
and a white icon on that fill.

<details>
<summary>Code:</summary>

```python
def make_lucide_push_button(
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(label, parent)
    apply_lucide_button_icon(button, name, icon_size=icon_size, color=color)
    folded = label.casefold()
    if folded == "cancel" or folded.startswith("cancel "):
        style_cancel_button(button, icon_size=icon_size)
    return button
```

</details>

## 🔧 Function `set_action_text_with_lucide_icon`

```python
def set_action_text_with_lucide_icon(action: QAction, text: str, name: str | None = None, *, icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE) -> None
```

Set action text and a Lucide icon.

When `name` is omitted, a leading chrome emoji on `text` is mapped to Lucide
and stripped from the visible label.

<details>
<summary>Code:</summary>

```python
def set_action_text_with_lucide_icon(
    action: QAction,
    text: str,
    name: str | None = None,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> None:
    action.setText(text)
    if name:
        apply_lucide_action_icon(action, name, icon_size=icon_size)
        return
    apply_leading_chrome_icon(action, icon_size=icon_size)
```

</details>

## 🔧 Function `style_accept_button`

```python
def style_accept_button(button: QAbstractButton, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> None
```

Paint an accept action (OK / Apply / Save) with the shared green chrome.

<details>
<summary>Code:</summary>

```python
def style_accept_button(
    button: QAbstractButton,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    button.setStyleSheet(ACCEPT_BUTTON_STYLE)
    _recolor_filled_button_icon(button, icon_size=icon_size)
```

</details>

## 🔧 Function `style_cancel_button`

```python
def style_cancel_button(button: QAbstractButton, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> None
```

Paint a cancel/reject/delete action with the shared red chrome.

<details>
<summary>Code:</summary>

```python
def style_cancel_button(
    button: QAbstractButton,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    button.setStyleSheet(CANCEL_BUTTON_STYLE)
    _recolor_filled_button_icon(button, icon_size=icon_size)
```

</details>
