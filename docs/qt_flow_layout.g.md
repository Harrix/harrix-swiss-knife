---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_flow_layout.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FlowLayout`](#%EF%B8%8F-class-flowlayout)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `addItem`](#%EF%B8%8F-method-additem)
  - [⚙️ Method `count`](#%EF%B8%8F-method-count)
  - [⚙️ Method `expandingDirections`](#%EF%B8%8F-method-expandingdirections)
  - [⚙️ Method `hasHeightForWidth`](#%EF%B8%8F-method-hasheightforwidth)
  - [⚙️ Method `heightForWidth`](#%EF%B8%8F-method-heightforwidth)
  - [⚙️ Method `itemAt`](#%EF%B8%8F-method-itemat)
  - [⚙️ Method `minimumSize`](#%EF%B8%8F-method-minimumsize)
  - [⚙️ Method `setGeometry`](#%EF%B8%8F-method-setgeometry)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `takeAt`](#%EF%B8%8F-method-takeat)

</details>

## 🏛️ Class `FlowLayout`

```python
class FlowLayout(QLayout)
```

Lay out child widgets in rows that wrap when the width is too small.

<details>
<summary>Code:</summary>

```python
class FlowLayout(QLayout):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        margin: int = -1,
        h_spacing: int = -1,
        v_spacing: int = -1,
    ) -> None:
        """Create an empty flow layout.

        Args:

        - `parent` (`QWidget | None`): Optional parent widget.
        - `margin` (`int`): Uniform contents margin; `-1` keeps the style default.
        - `h_spacing` (`int`): Horizontal gap; `-1` uses style spacing.
        - `v_spacing` (`int`): Vertical gap; `-1` uses style spacing.

        """
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem) -> None:  # noqa: N802
        """Append `item` to the flow."""
        self._items.append(item)

    def count(self) -> int:
        """Return the number of items."""
        return len(self._items)

    def expandingDirections(self) -> Qt.Orientation:  # noqa: N802
        """Flow layouts do not expand in either direction by themselves."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        """Height depends on the available width."""
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        """Return the height needed to lay out items in `width` pixels."""
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def itemAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        """Return the item at `index`, or `None`."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def minimumSize(self) -> QSize:  # noqa: N802
        """Return the size that fits the largest single child plus margins."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self._margins()
        size += QSize(left + right, top + bottom)
        return size

    def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        """Position children inside `rect`."""
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Prefer the minimum size that can fit every child."""
        return self.minimumSize()

    def takeAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        """Remove and return the item at `index`."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        left, top, right, bottom = self._margins()
        effective = rect.adjusted(left, top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        line_height = 0
        space_x = self._horizontal_spacing()
        space_y = self._vertical_spacing()

        for item in self._items:
            widget = item.widget()
            space_x_eff = space_x
            space_y_eff = space_y
            if widget is not None:
                style = widget.style()
                space_x_eff = style.layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal,
                )
                space_y_eff = style.layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical,
                )
                if self._h_spacing >= 0:
                    space_x_eff = self._h_spacing
                if self._v_spacing >= 0:
                    space_y_eff = self._v_spacing

            next_x = x + item.sizeHint().width() + space_x_eff
            if next_x - space_x_eff > effective.right() and line_height > 0:
                x = effective.x()
                y = y + line_height + space_y_eff
                next_x = x + item.sizeHint().width() + space_x_eff
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom

    def _horizontal_spacing(self) -> int:
        if self._h_spacing >= 0:
            return self._h_spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def _margins(self) -> tuple[int, int, int, int]:
        return cast("tuple[int, int, int, int]", self.getContentsMargins())

    def _smart_spacing(self, metric: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent.style().pixelMetric(metric, None, parent)
        return self.spacing()

    def _vertical_spacing(self) -> int:
        if self._v_spacing >= 0:
            return self._v_spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, margin: int = -1, h_spacing: int = -1, v_spacing: int = -1) -> None
```

Create an empty flow layout.

Args:

- `parent` (`QWidget | None`): Optional parent widget.
- `margin` (`int`): Uniform contents margin; `-1` keeps the style default.
- `h_spacing` (`int`): Horizontal gap; `-1` uses style spacing.
- `v_spacing` (`int`): Vertical gap; `-1` uses style spacing.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        margin: int = -1,
        h_spacing: int = -1,
        v_spacing: int = -1,
    ) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)
```

</details>

### ⚙️ Method `addItem`

```python
def addItem(self, item: QLayoutItem) -> None
```

Append `item` to the flow.

<details>
<summary>Code:</summary>

```python
def addItem(self, item: QLayoutItem) -> None:  # noqa: N802
        self._items.append(item)
```

</details>

### ⚙️ Method `count`

```python
def count(self) -> int
```

Return the number of items.

<details>
<summary>Code:</summary>

```python
def count(self) -> int:
        return len(self._items)
```

</details>

### ⚙️ Method `expandingDirections`

```python
def expandingDirections(self) -> Qt.Orientation
```

Flow layouts do not expand in either direction by themselves.

<details>
<summary>Code:</summary>

```python
def expandingDirections(self) -> Qt.Orientation:  # noqa: N802
        return Qt.Orientation(0)
```

</details>

### ⚙️ Method `hasHeightForWidth`

```python
def hasHeightForWidth(self) -> bool
```

Height depends on the available width.

<details>
<summary>Code:</summary>

```python
def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True
```

</details>

### ⚙️ Method `heightForWidth`

```python
def heightForWidth(self, width: int) -> int
```

Return the height needed to lay out items in `width` pixels.

<details>
<summary>Code:</summary>

```python
def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)
```

</details>

### ⚙️ Method `itemAt`

```python
def itemAt(self, index: int) -> QLayoutItem | None
```

Return the item at `index`, or `None`.

<details>
<summary>Code:</summary>

```python
def itemAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
```

</details>

### ⚙️ Method `minimumSize`

```python
def minimumSize(self) -> QSize
```

Return the size that fits the largest single child plus margins.

<details>
<summary>Code:</summary>

```python
def minimumSize(self) -> QSize:  # noqa: N802
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self._margins()
        size += QSize(left + right, top + bottom)
        return size
```

</details>

### ⚙️ Method `setGeometry`

```python
def setGeometry(self, rect: QRect) -> None
```

Position children inside `rect`.

<details>
<summary>Code:</summary>

```python
def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Prefer the minimum size that can fit every child.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return self.minimumSize()
```

</details>

### ⚙️ Method `takeAt`

```python
def takeAt(self, index: int) -> QLayoutItem | None
```

Remove and return the item at `index`.

<details>
<summary>Code:</summary>

```python
def takeAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
```

</details>
