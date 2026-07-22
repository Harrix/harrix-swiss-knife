---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ClickableCategoryLabel`](#%EF%B8%8F-class-clickablecategorylabel)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)

</details>

## 🏛️ Class `ClickableCategoryLabel`

```python
class ClickableCategoryLabel(QLabel)
```

QLabel with dropdown arrow indicator on the right side.

<details>
<summary>Code:</summary>

```python
class ClickableCategoryLabel(QLabel):

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Override paintEvent to draw dropdown arrow."""
        super().paintEvent(event)

        # Draw dropdown arrow on the right side
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get arrow size and position
        arrow_size = 8
        margin = 4
        rect = self.rect()
        arrow_x = rect.width() - arrow_size - margin
        arrow_y = rect.height() // 2

        # Get text color for arrow
        text_color = self.palette().color(self.palette().ColorRole.WindowText)
        painter.setPen(text_color)
        painter.setBrush(text_color)

        # Draw triangle pointing down
        points = [
            QPoint(arrow_x, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size // 2, arrow_y + arrow_size // 2),
        ]
        painter.drawPolygon(points)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Override paintEvent to draw dropdown arrow.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)

        # Draw dropdown arrow on the right side
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get arrow size and position
        arrow_size = 8
        margin = 4
        rect = self.rect()
        arrow_x = rect.width() - arrow_size - margin
        arrow_y = rect.height() // 2

        # Get text color for arrow
        text_color = self.palette().color(self.palette().ColorRole.WindowText)
        painter.setPen(text_color)
        painter.setBrush(text_color)

        # Draw triangle pointing down
        points = [
            QPoint(arrow_x, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size // 2, arrow_y + arrow_size // 2),
        ]
        painter.drawPolygon(points)
```

</details>
