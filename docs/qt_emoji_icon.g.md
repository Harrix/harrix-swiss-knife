---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_emoji_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_emoji_action`](#-function-add_emoji_action)
- [🔧 Function `apply_emoji_action_icon`](#-function-apply_emoji_action_icon)
- [🔧 Function `apply_emoji_dialog_buttons`](#-function-apply_emoji_dialog_buttons)
- [🔧 Function `apply_leading_emoji_icon`](#-function-apply_leading_emoji_icon)
- [🔧 Function `apply_leading_emoji_icons`](#-function-apply_leading_emoji_icons)
- [🔧 Function `create_emoji_icon`](#-function-create_emoji_icon)
- [🔧 Function `create_emoji_row_icon`](#-function-create_emoji_row_icon)
- [🔧 Function `make_emoji_push_button`](#-function-make_emoji_push_button)
- [🔧 Function `paint_centered_emoji`](#-function-paint_centered_emoji)
- [🔧 Function `set_action_text_with_emoji_icon`](#-function-set_action_text_with_emoji_icon)
- [🔧 Function `split_leading_emoji`](#-function-split_leading_emoji)

</details>

## 🔧 Function `add_emoji_action`

```python
def add_emoji_action(menu: QMenu, label: str, emoji: str, *, icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE) -> QAction
```

Add a menu action with [`emoji`](apps/common/emoji_picker_dialog.g.md#%EF%B8%8F-method-emoji) as a `QIcon` and `label` as the text.

<details>
<summary>Code:</summary>

```python
def add_emoji_action(
    menu: QMenu,
    label: str,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> QAction:
    action = menu.addAction(label)
    apply_emoji_action_icon(action, emoji, icon_size=icon_size)
    return action
```

</details>

## 🔧 Function `apply_emoji_action_icon`

```python
def apply_emoji_action_icon(action: QAction, emoji: str, *, icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE) -> None
```

Set [`emoji`](apps/common/emoji_picker_dialog.g.md#%EF%B8%8F-method-emoji) as the action icon without changing its text.

<details>
<summary>Code:</summary>

```python
def apply_emoji_action_icon(
    action: QAction,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> None:
    if emoji:
        action.setIcon(
            create_emoji_icon(
                emoji,
                icon_size,
                align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            ),
        )
```

</details>

## 🔧 Function `apply_emoji_dialog_buttons`

```python
def apply_emoji_dialog_buttons(buttons: QDialogButtonBox, *, icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE) -> None
```

Set emoji icons on standard QDialogButtonBox buttons when present.

<details>
<summary>Code:</summary>

```python
def apply_emoji_dialog_buttons(
    buttons: QDialogButtonBox,
    *,
    icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE,
) -> None:
    for standard_button, emoji in (
        (QDialogButtonBox.StandardButton.Ok, OK_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Cancel, CANCEL_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Save, SAVE_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Close, CLOSE_BUTTON_EMOJI),
    ):
        button = buttons.button(standard_button)
        if button is not None:
            button.setIcon(create_emoji_icon(emoji, icon_size))
            button.setIconSize(QSize(icon_size, icon_size))
```

</details>

## 🔧 Function `apply_leading_emoji_icon`

```python
def apply_leading_emoji_icon(action: QAction, *, icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE) -> bool
```

Move a leading emoji from `action` text onto its `QIcon`.

Returns:

- `bool`: `True` when an emoji prefix was converted.

<details>
<summary>Code:</summary>

```python
def apply_leading_emoji_icon(
    action: QAction,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> bool:
    emoji, rest = split_leading_emoji(action.text())
    if not emoji:
        return False
    apply_emoji_action_icon(action, emoji, icon_size=icon_size)
    action.setText(rest)
    return True
```

</details>

## 🔧 Function `apply_leading_emoji_icons`

```python
def apply_leading_emoji_icons(menu: QMenu | QMenuBar, *, icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE) -> None
```

Convert leading emoji prefixes on `menu` actions into `QIcon`s.

<details>
<summary>Code:</summary>

```python
def apply_leading_emoji_icons(
    menu: QMenu | QMenuBar,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> None:
    for action in menu.actions():
        if action.isSeparator():
            continue
        apply_leading_emoji_icon(action, icon_size=icon_size)
        submenu = action.menu()
        if isinstance(submenu, QMenu):
            apply_leading_emoji_icons(submenu, icon_size=icon_size)
```

</details>

## 🔧 Function `create_emoji_icon`

```python
def create_emoji_icon(emoji: str, size: int = 64, *, align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter, device_pixel_ratio: float | None = None) -> QIcon
```

Create a square `QIcon` for an emoji, scaled to avoid clipping.

The pixmap is rasterized at the screen device-pixel ratio so icons stay
sharp on HiDPI displays such as 4K.

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(
    emoji: str,
    size: int = 64,
    *,
    align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    ratio = device_pixel_ratio if device_pixel_ratio is not None else _emoji_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    physical = max(1, round(size * ratio))
    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    paint_centered_emoji(
        painter,
        emoji,
        QRectF(0.0, 0.0, float(physical), float(physical)),
        fill=0.90,
        align=align,
    )
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    return icon
```

</details>

## 🔧 Function `create_emoji_row_icon`

```python
def create_emoji_row_icon(emojis: list[str], size: int = 64, *, gap: int = 2, device_pixel_ratio: float | None = None) -> QIcon
```

Create a left-aligned row of emoji icons, or a single square icon.

Used when a list item needs more than one marker (for example a catalog
food item that is also a drink).

<details>
<summary>Code:</summary>

```python
def create_emoji_row_icon(
    emojis: list[str],
    size: int = 64,
    *,
    gap: int = 2,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    cleaned = [emoji for emoji in emojis if emoji]
    if not cleaned:
        return QIcon()
    if len(cleaned) == 1:
        return create_emoji_icon(cleaned[0], size, device_pixel_ratio=device_pixel_ratio)

    ratio = device_pixel_ratio if device_pixel_ratio is not None else _emoji_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    logical_width = size * len(cleaned) + gap * (len(cleaned) - 1)
    physical_h = max(1, round(size * ratio))
    physical_w = max(1, round(logical_width * ratio))
    physical_gap = max(0, round(gap * ratio))
    pixmap = QPixmap(physical_w, physical_h)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    x = 0.0
    for emoji in cleaned:
        paint_centered_emoji(
            painter,
            emoji,
            QRectF(x, 0.0, float(physical_h), float(physical_h)),
            fill=0.90,
        )
        x += physical_h + physical_gap
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    return icon
```

</details>

## 🔧 Function `make_emoji_push_button`

```python
def make_emoji_push_button(label: str, emoji: str, *, icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE, parent: QWidget | None = None) -> QPushButton
```

Create a push button with an emoji icon.

<details>
<summary>Code:</summary>

```python
def make_emoji_push_button(
    label: str,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE,
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(label, parent)
    button.setIcon(create_emoji_icon(emoji, icon_size))
    button.setIconSize(QSize(icon_size, icon_size))
    return button
```

</details>

## 🔧 Function `paint_centered_emoji`

```python
def paint_centered_emoji(painter: QPainter, emoji: str, rect: QRectF, *, fill: float = 0.9, align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter) -> None
```

Draw `[`emoji`](apps/common/emoji_picker_dialog.g.md#%EF%B8%8F-method-emoji)` in ``rect``, scaled to ``fill`` of the shorter side.

<details>
<summary>Code:</summary>

```python
def paint_centered_emoji(
    painter: QPainter,
    emoji: str,
    rect: QRectF,
    *,
    fill: float = 0.90,
    align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> None:
    if not emoji:
        return
    painter.save()
    painter.setPen(Qt.GlobalColor.black)
    size = min(rect.width(), rect.height())
    target = size * fill
    base_font = QFont()
    base_font.setPointSizeF(max(1.0, size))
    bounds = QFontMetricsF(base_font).tightBoundingRect(emoji)
    rect_w = max(bounds.width(), 1.0)
    rect_h = max(bounds.height(), 1.0)
    scale = (target / rect_h) if rect_h > rect_w else (target / rect_w)
    font = QFont(base_font)
    font.setPointSizeF(max(1.0, base_font.pointSizeF() * scale))
    painter.setFont(font)
    fitted = QFontMetricsF(font).tightBoundingRect(emoji)
    inset = 1.0
    if align & Qt.AlignmentFlag.AlignLeft:
        x = rect.x() + inset
    elif align & Qt.AlignmentFlag.AlignRight:
        x = rect.x() + rect.width() - fitted.width() - inset
    else:
        x = rect.x() + (rect.width() - fitted.width()) / 2.0
    if align & Qt.AlignmentFlag.AlignTop:
        y = rect.y() + inset
    elif align & Qt.AlignmentFlag.AlignBottom:
        y = rect.y() + rect.height() - fitted.height() - inset
    else:
        y = rect.y() + (rect.height() - fitted.height()) / 2.0
    painter.drawText(QPointF(x - fitted.left(), y - fitted.top()), emoji)
    painter.restore()
```

</details>

## 🔧 Function `set_action_text_with_emoji_icon`

```python
def set_action_text_with_emoji_icon(action: QAction, text: str, *, icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE) -> None
```

Set action text and move a leading emoji onto the icon when present.

<details>
<summary>Code:</summary>

```python
def set_action_text_with_emoji_icon(
    action: QAction,
    text: str,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> None:
    action.setText(text)
    apply_leading_emoji_icon(action, icon_size=icon_size)
```

</details>

## 🔧 Function `split_leading_emoji`

```python
def split_leading_emoji(text: str) -> tuple[str, str]
```

Split `emoji rest` menu text into `(emoji, rest)`.

Returns `("", text)` when the first token is not an emoji.

<details>
<summary>Code:</summary>

```python
def split_leading_emoji(text: str) -> tuple[str, str]:
    raw = text.strip()
    if not raw:
        return "", text
    first, _sep, rest = raw.partition(" ")
    if _is_emoji_token(first):
        return first, rest
    return "", text
```

</details>
