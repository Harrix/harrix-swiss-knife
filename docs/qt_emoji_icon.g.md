---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_emoji_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_emoji_dialog_buttons`](#-function-apply_emoji_dialog_buttons)
- [🔧 Function `create_emoji_icon`](#-function-create_emoji_icon)
- [🔧 Function `make_emoji_push_button`](#-function-make_emoji_push_button)
- [🔧 Function `paint_centered_emoji`](#-function-paint_centered_emoji)

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
```

</details>

## 🔧 Function `create_emoji_icon`

```python
def create_emoji_icon(emoji: str, size: int = 64) -> QIcon
```

Create a square `QIcon` for an emoji, scaled to avoid clipping.

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(emoji: str, size: int = 64) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    paint_centered_emoji(painter, emoji, QRectF(0.0, 0.0, float(size), float(size)), fill=0.90)
    painter.end()

    return QIcon(pixmap)
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
    return button
```

</details>

## 🔧 Function `paint_centered_emoji`

```python
def paint_centered_emoji(painter: QPainter, emoji: str, rect: QRectF, *, fill: float = 0.9) -> None
```

Draw ``emoji`` centered in ``rect``, scaled to ``fill`` of the shorter side.

<details>
<summary>Code:</summary>

```python
def paint_centered_emoji(
    painter: QPainter,
    emoji: str,
    rect: QRectF,
    *,
    fill: float = 0.90,
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
    x = rect.x() + (rect.width() - fitted.width()) / 2.0
    y = rect.y() + (rect.height() - fitted.height()) / 2.0
    painter.drawText(QPointF(x - fitted.left(), y - fitted.top()), emoji)
    painter.restore()
```

</details>
