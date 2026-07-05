---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_emoji_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `create_emoji_icon`](#-function-create_emoji_icon)
- [🔧 Function `make_emoji_push_button`](#-function-make_emoji_push_button)

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

    target = float(size) * 0.90
    base_font = QFont()
    base_font.setPointSizeF(float(size))

    metrics = QFontMetricsF(base_font)
    rect = metrics.tightBoundingRect(emoji)
    rect_w = max(rect.width(), 1.0)
    rect_h = max(rect.height(), 1.0)

    # If the glyph is taller than wide, fit by height; otherwise fit by width.
    scale = (target / rect_h) if (rect_h > rect_w) else (target / rect_w)

    font = QFont(base_font)
    font.setPointSizeF(max(1.0, base_font.pointSizeF() * scale))
    painter.setFont(font)

    metrics2 = QFontMetricsF(font)
    rect2 = metrics2.tightBoundingRect(emoji)

    x = (float(size) - rect2.width()) / 2.0
    y = (float(size) - rect2.height()) / 2.0
    baseline = QPointF(x - rect2.left(), y - rect2.top())

    painter.drawText(baseline, emoji)
    painter.end()

    return QIcon(pixmap)
```

</details>

## 🔧 Function `make_emoji_push_button`

```python
def make_emoji_push_button(label: str, emoji: str) -> QPushButton
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
