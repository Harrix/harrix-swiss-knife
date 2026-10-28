---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `views.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentCardGrid`](#%EF%B8%8F-class-fluentcardgrid)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_card`](#%EF%B8%8F-method-add_card)
  - [⚙️ Method `cards`](#%EF%B8%8F-method-cards)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `count`](#%EF%B8%8F-method-count)
  - [⚙️ Method `flow_layout`](#%EF%B8%8F-method-flow_layout)
- [🏛️ Class `FluentGraphicsItem`](#%EF%B8%8F-class-fluentgraphicsitem)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
- [🏛️ Class `FluentGraphicsLineItem`](#%EF%B8%8F-class-fluentgraphicslineitem)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `update_position`](#%EF%B8%8F-method-update_position)
- [🏛️ Class `FluentGraphicsScene`](#%EF%B8%8F-class-fluentgraphicsscene)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `drawBackground`](#%EF%B8%8F-method-drawbackground)
  - [⚙️ Method `set_colors`](#%EF%B8%8F-method-set_colors)
- [🏛️ Class `FluentGraphicsView`](#%EF%B8%8F-class-fluentgraphicsview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
- [🏛️ Class `FluentListView`](#%EF%B8%8F-class-fluentlistview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-1)
- [🏛️ Class `FluentListWidget`](#%EF%B8%8F-class-fluentlistwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-2)
- [🏛️ Class `FluentPromotionView`](#%EF%B8%8F-class-fluentpromotionview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)
  - [⚙️ Method `add_pixmap`](#%EF%B8%8F-method-add_pixmap)
  - [⚙️ Method `current`](#%EF%B8%8F-method-current)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `next_page`](#%EF%B8%8F-method-next_page)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `set_current`](#%EF%B8%8F-method-set_current)
- [🏛️ Class `FluentScrollArea`](#%EF%B8%8F-class-fluentscrollarea)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-8)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-3)
  - [⚙️ Method `setWidget`](#%EF%B8%8F-method-setwidget)
- [🏛️ Class `FluentScrollBar`](#%EF%B8%8F-class-fluentscrollbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-9)
- [🏛️ Class `FluentScrollPage`](#%EF%B8%8F-class-fluentscrollpage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-10)
  - [⚙️ Method `add_section`](#%EF%B8%8F-method-add_section)
  - [⚙️ Method `scroll_to`](#%EF%B8%8F-method-scroll_to)
- [🏛️ Class `FluentScrollPageArea`](#%EF%B8%8F-class-fluentscrollpagearea)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-11)
  - [⚙️ Method `add_page`](#%EF%B8%8F-method-add_page)
  - [⚙️ Method `page`](#%EF%B8%8F-method-page)
  - [⚙️ Method `show_page`](#%EF%B8%8F-method-show_page)
- [🏛️ Class `FluentTableView`](#%EF%B8%8F-class-fluenttableview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-12)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-4)
- [🏛️ Class `FluentTableWidget`](#%EF%B8%8F-class-fluenttablewidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-13)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-5)
- [🏛️ Class `FluentTreeView`](#%EF%B8%8F-class-fluenttreeview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-14)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-6)
- [🏛️ Class `FluentTreeWidget`](#%EF%B8%8F-class-fluenttreewidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-15)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-7)
- [🏛️ Class `FluentVirtualList`](#%EF%B8%8F-class-fluentvirtuallist)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-16)
  - [⚙️ Method `set_rows`](#%EF%B8%8F-method-set_rows)
- [🏛️ Class `SmoothScroller`](#%EF%B8%8F-class-smoothscroller)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-17)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `scroll_by_wheel`](#%EF%B8%8F-method-scroll_by_wheel)

</details>

## 🏛️ Class `FluentCardGrid`

```python
class FluentCardGrid(QWidget)
```

Wrapping grid of fixed-size cards on a [`FlowLayout`](../../qt_flow_layout.g.md#%EF%B8%8F-class-flowlayout) (height follows width).

<details>
<summary>Code:</summary>

```python
class FluentCardGrid(QWidget):

    def __init__(self, parent: QWidget | None = None, *, spacing: int = CARD_GRID_SPACING) -> None:
        """Create an empty card grid."""
        super().__init__(parent)
        self._layout = FlowLayout(self, margin=0, h_spacing=spacing, v_spacing=spacing)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def add_card(self, card: QWidget) -> None:
        """Append a card."""
        card.setParent(self)
        self._layout.addWidget(card)
        card.show()

    def cards(self) -> list[QWidget]:
        """Return the cards in order."""
        result: list[QWidget] = []
        for index in range(self._layout.count()):
            item = self._layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is not None:
                result.append(widget)
        return result

    def clear(self) -> None:
        """Remove and delete every card."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()

    def count(self) -> int:
        """Return the number of cards."""
        return self._layout.count()

    def flow_layout(self) -> FlowLayout:
        """Return the underlying flow layout."""
        return self._layout
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, spacing: int = CARD_GRID_SPACING) -> None
```

Create an empty card grid.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, spacing: int = CARD_GRID_SPACING) -> None:
        super().__init__(parent)
        self._layout = FlowLayout(self, margin=0, h_spacing=spacing, v_spacing=spacing)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
```

</details>

### ⚙️ Method `add_card`

```python
def add_card(self, card: QWidget) -> None
```

Append a card.

<details>
<summary>Code:</summary>

```python
def add_card(self, card: QWidget) -> None:
        card.setParent(self)
        self._layout.addWidget(card)
        card.show()
```

</details>

### ⚙️ Method `cards`

```python
def cards(self) -> list[QWidget]
```

Return the cards in order.

<details>
<summary>Code:</summary>

```python
def cards(self) -> list[QWidget]:
        result: list[QWidget] = []
        for index in range(self._layout.count()):
            item = self._layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is not None:
                result.append(widget)
        return result
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Remove and delete every card.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
```

</details>

### ⚙️ Method `count`

```python
def count(self) -> int
```

Return the number of cards.

<details>
<summary>Code:</summary>

```python
def count(self) -> int:
        return self._layout.count()
```

</details>

### ⚙️ Method `flow_layout`

```python
def flow_layout(self) -> FlowLayout
```

Return the underlying flow layout.

<details>
<summary>Code:</summary>

```python
def flow_layout(self) -> FlowLayout:
        return self._layout
```

</details>

## 🏛️ Class `FluentGraphicsItem`

```python
class FluentGraphicsItem(QGraphicsRectItem)
```

Rounded, selectable, movable node item with a title.

<details>
<summary>Code:</summary>

```python
class FluentGraphicsItem(QGraphicsRectItem):

    def __init__(self, title: str, rect: QRectF | None = None, *, accent: QColor | None = None) -> None:
        """Create a node item."""
        super().__init__(rect or QRectF(0, 0, 160, 64))
        self.title = title
        self._accent = accent or QColor("#005fb8")
        flags = QGraphicsRectItem.GraphicsItemFlag
        self.setFlags(flags.ItemIsMovable | flags.ItemIsSelectable | flags.ItemSendsGeometryChanges)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
        """Paint a card-like node; the selected node gets an accent border."""
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        stroke = self._accent if self.isSelected() else QColor(0, 0, 0, 40)
        paint_surface(
            painter,
            self.rect(),
            QColor(255, 255, 255, 235),
            stroke,
            RADIUS_CARD,
            stroke_width=2 if self.isSelected() else 1,
        )
        painter.fillRect(
            QRectF(self.rect().left() + 8, self.rect().top() + 10, 3, self.rect().height() - 20), self._accent
        )
        painter.setPen(QColor(0, 0, 0, 228))
        painter.drawText(
            self.rect().adjusted(20, 0, -8, 0),
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            self.title,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, rect: QRectF | None = None, *, accent: QColor | None = None) -> None
```

Create a node item.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, rect: QRectF | None = None, *, accent: QColor | None = None) -> None:
        super().__init__(rect or QRectF(0, 0, 160, 64))
        self.title = title
        self._accent = accent or QColor("#005fb8")
        flags = QGraphicsRectItem.GraphicsItemFlag
        self.setFlags(flags.ItemIsMovable | flags.ItemIsSelectable | flags.ItemSendsGeometryChanges)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None
```

Paint a card-like node; the selected node gets an accent border.

<details>
<summary>Code:</summary>

```python
def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        stroke = self._accent if self.isSelected() else QColor(0, 0, 0, 40)
        paint_surface(
            painter,
            self.rect(),
            QColor(255, 255, 255, 235),
            stroke,
            RADIUS_CARD,
            stroke_width=2 if self.isSelected() else 1,
        )
        painter.fillRect(
            QRectF(self.rect().left() + 8, self.rect().top() + 10, 3, self.rect().height() - 20), self._accent
        )
        painter.setPen(QColor(0, 0, 0, 228))
        painter.drawText(
            self.rect().adjusted(20, 0, -8, 0),
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            self.title,
        )
```

</details>

## 🏛️ Class `FluentGraphicsLineItem`

```python
class FluentGraphicsLineItem(QGraphicsLineItem)
```

Connector line between two [`FluentGraphicsItem`](#%EF%B8%8F-class-fluentgraphicsitem) nodes that follows them.

<details>
<summary>Code:</summary>

```python
class FluentGraphicsLineItem(QGraphicsLineItem):

    def __init__(self, source: QGraphicsRectItem, target: QGraphicsRectItem, *, color: QColor | None = None) -> None:
        """Create a connector."""
        super().__init__()
        self._source = source
        self._target = target
        pen = QPen(color or QColor(0, 0, 0, 110), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-1)
        self.update_position()

    def update_position(self) -> None:
        """Re-anchor the line to the node centers."""
        start = self._source.sceneBoundingRect().center()
        end = self._target.sceneBoundingRect().center()
        self.setLine(start.x(), start.y(), end.x(), end.y())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, source: QGraphicsRectItem, target: QGraphicsRectItem, *, color: QColor | None = None) -> None
```

Create a connector.

<details>
<summary>Code:</summary>

```python
def __init__(self, source: QGraphicsRectItem, target: QGraphicsRectItem, *, color: QColor | None = None) -> None:
        super().__init__()
        self._source = source
        self._target = target
        pen = QPen(color or QColor(0, 0, 0, 110), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-1)
        self.update_position()
```

</details>

### ⚙️ Method `update_position`

```python
def update_position(self) -> None
```

Re-anchor the line to the node centers.

<details>
<summary>Code:</summary>

```python
def update_position(self) -> None:
        start = self._source.sceneBoundingRect().center()
        end = self._target.sceneBoundingRect().center()
        self.setLine(start.x(), start.y(), end.x(), end.y())
```

</details>

## 🏛️ Class `FluentGraphicsScene`

```python
class FluentGraphicsScene(QGraphicsScene)
```

Graphics scene with a theme-colored dotted grid background.

<details>
<summary>Code:</summary>

```python
class FluentGraphicsScene(QGraphicsScene):

    def __init__(self, parent: QObject | None = None, *, grid: int = 20) -> None:
        """Create a scene with a `grid` px dot pitch (`0` = no grid)."""
        super().__init__(parent)
        self._grid = grid
        self._dot = QColor(0, 0, 0, 40)
        self._background = QColor(0, 0, 0, 0)

    def drawBackground(self, painter: QPainter, rect: QRectF | QRect, /) -> None:  # noqa: N802
        """Paint the fill and grid dots."""
        rect = QRectF(rect)
        painter.fillRect(rect, self._background)
        if self._grid <= 0:
            return
        painter.setPen(QPen(self._dot, 1.5))
        left = int(rect.left()) - int(rect.left()) % self._grid
        top = int(rect.top()) - int(rect.top()) % self._grid
        for x in range(left, int(rect.right()) + 1, self._grid):
            for y in range(top, int(rect.bottom()) + 1, self._grid):
                painter.drawPoint(x, y)

    def set_colors(self, background: QColor, dot: QColor) -> None:
        """Change fill and grid colors."""
        self._background, self._dot = background, dot
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, *, grid: int = 20) -> None
```

Create a scene with a `grid` px dot pitch (`0` = no grid).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, *, grid: int = 20) -> None:
        super().__init__(parent)
        self._grid = grid
        self._dot = QColor(0, 0, 0, 40)
        self._background = QColor(0, 0, 0, 0)
```

</details>

### ⚙️ Method `drawBackground`

```python
def drawBackground(self, painter: QPainter, rect: QRectF | QRect, /) -> None
```

Paint the fill and grid dots.

<details>
<summary>Code:</summary>

```python
def drawBackground(self, painter: QPainter, rect: QRectF | QRect, /) -> None:  # noqa: N802
        rect = QRectF(rect)
        painter.fillRect(rect, self._background)
        if self._grid <= 0:
            return
        painter.setPen(QPen(self._dot, 1.5))
        left = int(rect.left()) - int(rect.left()) % self._grid
        top = int(rect.top()) - int(rect.top()) % self._grid
        for x in range(left, int(rect.right()) + 1, self._grid):
            for y in range(top, int(rect.bottom()) + 1, self._grid):
                painter.drawPoint(x, y)
```

</details>

### ⚙️ Method `set_colors`

```python
def set_colors(self, background: QColor, dot: QColor) -> None
```

Change fill and grid colors.

<details>
<summary>Code:</summary>

```python
def set_colors(self, background: QColor, dot: QColor) -> None:
        self._background, self._dot = background, dot
        self.update()
```

</details>

## 🏛️ Class `FluentGraphicsView`

```python
class FluentGraphicsView(QGraphicsView)
```

Graphics view with antialiasing, wheel zoom (Ctrl), and pan by middle drag.

<details>
<summary>Code:</summary>

```python
class FluentGraphicsView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene | None = None, parent: QWidget | None = None) -> None:
        """Create a graphics view."""
        super().__init__(parent)
        self.setScene(scene or FluentGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, enabled=True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-color the background and grid."""
        palette = palette_for(self)
        scene = self.scene()
        if isinstance(scene, FluentGraphicsScene):
            scene.set_colors(
                palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg,
                with_alpha(palette.text_primary, 40),
            )
        self.setStyleSheet(
            f"QGraphicsView {{ border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CARD}px; }}\n"
            f"{scroll_bar_qss(palette)}"
        )

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom with Ctrl+wheel, scroll otherwise."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, scene: QGraphicsScene | None = None, parent: QWidget | None = None) -> None
```

Create a graphics view.

<details>
<summary>Code:</summary>

```python
def __init__(self, scene: QGraphicsScene | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setScene(scene or FluentGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, enabled=True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-color the background and grid.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        scene = self.scene()
        if isinstance(scene, FluentGraphicsScene):
            scene.set_colors(
                palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg,
                with_alpha(palette.text_primary, 40),
            )
        self.setStyleSheet(
            f"QGraphicsView {{ border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CARD}px; }}\n"
            f"{scroll_bar_qss(palette)}"
        )
```

</details>

### ⚙️ Method `wheelEvent`

```python
def wheelEvent(self, event: QWheelEvent) -> None
```

Zoom with Ctrl+wheel, scroll otherwise.

<details>
<summary>Code:</summary>

```python
def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)
```

</details>

## 🏛️ Class `FluentListView`

```python
class FluentListView(QListView)
```

Model-based list view with Fluent item chrome.

<details>
<summary>Code:</summary>

```python
class FluentListView(QListView):

    def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        """Create a list view."""
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListView")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint items, then the accent pill next to the current item."""
        super().paintEvent(event)
        _paint_selection_indicator(self)

    def refresh_theme(self) -> None:
        """Re-apply item chrome."""
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListView#{self.objectName()}", transparent=self._transparent)
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None
```

Create a list view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListView")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint items, then the accent pill next to the current item.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        _paint_selection_indicator(self)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply item chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListView#{self.objectName()}", transparent=self._transparent)
        )
```

</details>

## 🏛️ Class `FluentListWidget`

```python
class FluentListWidget(QListWidget)
```

List widget with rounded hover/selection, accent indicator, and smooth scrolling.

<details>
<summary>Code:</summary>

```python
class FluentListWidget(QListWidget):

    def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        """Create a list widget."""
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListWidget")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint items, then the accent pill next to the current item."""
        super().paintEvent(event)
        _paint_selection_indicator(self)

    def refresh_theme(self) -> None:
        """Re-apply item chrome."""
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListWidget#{self.objectName()}", transparent=self._transparent)
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None
```

Create a list widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListWidget")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint items, then the accent pill next to the current item.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        _paint_selection_indicator(self)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply item chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListWidget#{self.objectName()}", transparent=self._transparent)
        )
```

</details>

## 🏛️ Class `FluentPromotionView`

```python
class FluentPromotionView(QWidget)
```

Auto-advancing image carousel with page dots and rounded corners.

<details>
<summary>Code:</summary>

```python
class FluentPromotionView(QWidget):

    current_changed = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        pixmaps: Sequence[QPixmap] = (),
        interval_ms: int = _CAROUSEL_INTERVAL_MS,
    ) -> None:
        """Create a carousel."""
        super().__init__(parent)
        self._pixmaps = list(pixmaps)
        self._current = 0
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.next_page)
        if self._pixmaps:
            self._timer.start()
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bind_theme(self, self.update)

    def add_pixmap(self, pixmap: QPixmap) -> None:
        """Append a slide."""
        self._pixmaps.append(pixmap)
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def current(self) -> int:
        """Return the shown slide index."""
        return self._current

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Jump to the slide whose dot was clicked."""
        position = event.position()
        for index, dot in enumerate(self._dot_rects()):
            if dot.adjusted(-4, -4, 4, 4).contains(position):
                self.set_current(index)
                return

    def next_page(self) -> None:
        """Show the next slide (wraps around)."""
        if self._pixmaps:
            self.set_current((self._current + 1) % len(self._pixmaps))

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the clipped slide and the page dots."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmaps:
            pixmap = self._pixmaps[self._current]
            scaled = pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(
                int((self.width() - scaled.width()) / 2), int((self.height() - scaled.height()) / 2), scaled
            )
        else:
            painter.fillRect(rect, palette.subtle_hover)
        painter.setClipping(False)
        for index, dot in enumerate(self._dot_rects()):
            color = QColor(255, 255, 255, 240 if index == self._current else 130)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(dot, dot.height() / 2, dot.height() / 2)
        painter.end()

    def set_current(self, index: int) -> None:
        """Show slide `index`."""
        if not self._pixmaps:
            return
        index %= len(self._pixmaps)
        if index == self._current:
            return
        self._current = index
        self.update()
        self.current_changed.emit(index)

    def _dot_rects(self) -> list[QRectF]:
        count = len(self._pixmaps)
        if count <= 1:
            return []
        widths = [16.0 if index == self._current else 6.0 for index in range(count)]
        total = sum(widths) + (count - 1) * 6
        x = (self.width() - total) / 2
        rects = []
        for width in widths:
            rects.append(QRectF(x, self.height() - 16, width, 6))
            x += width + 6
        return rects
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, pixmaps: Sequence[QPixmap] = (), interval_ms: int = _CAROUSEL_INTERVAL_MS) -> None
```

Create a carousel.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        pixmaps: Sequence[QPixmap] = (),
        interval_ms: int = _CAROUSEL_INTERVAL_MS,
    ) -> None:
        super().__init__(parent)
        self._pixmaps = list(pixmaps)
        self._current = 0
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.next_page)
        if self._pixmaps:
            self._timer.start()
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `add_pixmap`

```python
def add_pixmap(self, pixmap: QPixmap) -> None
```

Append a slide.

<details>
<summary>Code:</summary>

```python
def add_pixmap(self, pixmap: QPixmap) -> None:
        self._pixmaps.append(pixmap)
        if not self._timer.isActive():
            self._timer.start()
        self.update()
```

</details>

### ⚙️ Method `current`

```python
def current(self) -> int
```

Return the shown slide index.

<details>
<summary>Code:</summary>

```python
def current(self) -> int:
        return self._current
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Jump to the slide whose dot was clicked.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        position = event.position()
        for index, dot in enumerate(self._dot_rects()):
            if dot.adjusted(-4, -4, 4, 4).contains(position):
                self.set_current(index)
                return
```

</details>

### ⚙️ Method `next_page`

```python
def next_page(self) -> None
```

Show the next slide (wraps around).

<details>
<summary>Code:</summary>

```python
def next_page(self) -> None:
        if self._pixmaps:
            self.set_current((self._current + 1) % len(self._pixmaps))
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the clipped slide and the page dots.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmaps:
            pixmap = self._pixmaps[self._current]
            scaled = pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(
                int((self.width() - scaled.width()) / 2), int((self.height() - scaled.height()) / 2), scaled
            )
        else:
            painter.fillRect(rect, palette.subtle_hover)
        painter.setClipping(False)
        for index, dot in enumerate(self._dot_rects()):
            color = QColor(255, 255, 255, 240 if index == self._current else 130)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(dot, dot.height() / 2, dot.height() / 2)
        painter.end()
```

</details>

### ⚙️ Method `set_current`

```python
def set_current(self, index: int) -> None
```

Show slide `index`.

<details>
<summary>Code:</summary>

```python
def set_current(self, index: int) -> None:
        if not self._pixmaps:
            return
        index %= len(self._pixmaps)
        if index == self._current:
            return
        self._current = index
        self.update()
        self.current_changed.emit(index)
```

</details>

## 🏛️ Class `FluentScrollArea`

```python
class FluentScrollArea(QScrollArea)
```

Transparent scroll area with thin Fluent scrollbars and smooth wheel scrolling.

<details>
<summary>Code:</summary>

```python
class FluentScrollArea(QScrollArea):

    def __init__(self, parent: QWidget | None = None, *, smooth: bool = True) -> None:
        """Create a scroll area (`widgetResizable` is on)."""
        super().__init__(parent)
        self.setWidgetResizable(True)
        _prepare_scroll_area(self, smooth=smooth)
        self.setObjectName(self.objectName() or "FluentScrollArea")
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply transparent background and scrollbar chrome."""
        palette = palette_for(self)
        self.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}\n{scroll_bar_qss(palette)}")
        self.viewport().setAutoFillBackground(False)
        content = self.widget()
        if content is not None:
            content.setAutoFillBackground(False)

    def setWidget(self, widget: QWidget) -> None:  # noqa: N802
        """Set the content widget (kept transparent)."""
        super().setWidget(widget)
        widget.setAutoFillBackground(False)
        widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, smooth: bool = True) -> None
```

Create a scroll area (`widgetResizable` is on).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, smooth: bool = True) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        _prepare_scroll_area(self, smooth=smooth)
        self.setObjectName(self.objectName() or "FluentScrollArea")
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply transparent background and scrollbar chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}\n{scroll_bar_qss(palette)}")
        self.viewport().setAutoFillBackground(False)
        content = self.widget()
        if content is not None:
            content.setAutoFillBackground(False)
```

</details>

### ⚙️ Method `setWidget`

```python
def setWidget(self, widget: QWidget) -> None
```

Set the content widget (kept transparent).

<details>
<summary>Code:</summary>

```python
def setWidget(self, widget: QWidget) -> None:  # noqa: N802
        super().setWidget(widget)
        widget.setAutoFillBackground(False)
        widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
```

</details>

## 🏛️ Class `FluentScrollBar`

```python
class FluentScrollBar(QScrollBar)
```

Stand-alone thin rounded scrollbar.

<details>
<summary>Code:</summary>

```python
class FluentScrollBar(QScrollBar):

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Vertical, parent: QWidget | None = None) -> None:
        """Create a scrollbar."""
        super().__init__(orientation, parent)
        bind_theme(self, lambda: self.setStyleSheet(scroll_bar_qss(palette_for(self))))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Vertical, parent: QWidget | None = None) -> None
```

Create a scrollbar.

<details>
<summary>Code:</summary>

```python
def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Vertical, parent: QWidget | None = None) -> None:
        super().__init__(orientation, parent)
        bind_theme(self, lambda: self.setStyleSheet(scroll_bar_qss(palette_for(self))))
```

</details>

## 🏛️ Class `FluentScrollPage`

```python
class FluentScrollPage(FluentScrollArea)
```

Scroll area whose content is a vertical stack of page sections.

<details>
<summary>Code:</summary>

```python
class FluentScrollPage(FluentScrollArea):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a scroll page with an empty content widget."""
        super().__init__(parent)
        self._content = QWidget(self)
        self._content.setObjectName("FluentScrollPageContent")
        self.content_layout = QVBoxLayout(self._content)
        self.content_layout.setContentsMargins(36, 20, 36, 36)
        self.content_layout.setSpacing(SPACE_S * 2)
        self.content_layout.addStretch(1)
        self.setWidget(self._content)

    def add_section(self, widget: QWidget) -> None:
        """Append a section before the trailing stretch."""
        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)

    def scroll_to(self, widget: QWidget) -> None:
        """Scroll so `widget` is at the top of the viewport."""
        top = widget.mapTo(self._content, widget.rect().topLeft()).y()
        bar = self.verticalScrollBar()
        animation = QPropertyAnimation(bar, b"value", self)
        animation.setDuration(ANIMATION_NORMAL * 2)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(bar.value())
        animation.setEndValue(min(bar.maximum(), top))
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a scroll page with an empty content widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._content = QWidget(self)
        self._content.setObjectName("FluentScrollPageContent")
        self.content_layout = QVBoxLayout(self._content)
        self.content_layout.setContentsMargins(36, 20, 36, 36)
        self.content_layout.setSpacing(SPACE_S * 2)
        self.content_layout.addStretch(1)
        self.setWidget(self._content)
```

</details>

### ⚙️ Method `add_section`

```python
def add_section(self, widget: QWidget) -> None
```

Append a section before the trailing stretch.

<details>
<summary>Code:</summary>

```python
def add_section(self, widget: QWidget) -> None:
        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
```

</details>

### ⚙️ Method `scroll_to`

```python
def scroll_to(self, widget: QWidget) -> None
```

Scroll so `widget` is at the top of the viewport.

<details>
<summary>Code:</summary>

```python
def scroll_to(self, widget: QWidget) -> None:
        top = widget.mapTo(self._content, widget.rect().topLeft()).y()
        bar = self.verticalScrollBar()
        animation = QPropertyAnimation(bar, b"value", self)
        animation.setDuration(ANIMATION_NORMAL * 2)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(bar.value())
        animation.setEndValue(min(bar.maximum(), top))
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
```

</details>

## 🏛️ Class `FluentScrollPageArea`

```python
class FluentScrollPageArea(QStackedWidget)
```

Stack of [`FluentScrollPage`](#%EF%B8%8F-class-fluentscrollpage) pages switched by key.

<details>
<summary>Code:</summary>

```python
class FluentScrollPageArea(QStackedWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty page stack."""
        super().__init__(parent)
        self._pages: dict[str, FluentScrollPage] = {}

    def add_page(self, key: str) -> FluentScrollPage:
        """Create and register a page under `key`."""
        page = FluentScrollPage(self)
        self._pages[key] = page
        self.addWidget(page)
        return page

    def page(self, key: str) -> FluentScrollPage | None:
        """Return the page registered under `key`."""
        return self._pages.get(key)

    def show_page(self, key: str) -> None:
        """Switch to the page registered under `key`."""
        page = self._pages.get(key)
        if page is not None:
            self.setCurrentWidget(page)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty page stack.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pages: dict[str, FluentScrollPage] = {}
```

</details>

### ⚙️ Method `add_page`

```python
def add_page(self, key: str) -> FluentScrollPage
```

Create and register a page under `key`.

<details>
<summary>Code:</summary>

```python
def add_page(self, key: str) -> FluentScrollPage:
        page = FluentScrollPage(self)
        self._pages[key] = page
        self.addWidget(page)
        return page
```

</details>

### ⚙️ Method `page`

```python
def page(self, key: str) -> FluentScrollPage | None
```

Return the page registered under `key`.

<details>
<summary>Code:</summary>

```python
def page(self, key: str) -> FluentScrollPage | None:
        return self._pages.get(key)
```

</details>

### ⚙️ Method `show_page`

```python
def show_page(self, key: str) -> None
```

Switch to the page registered under `key`.

<details>
<summary>Code:</summary>

```python
def show_page(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None:
            self.setCurrentWidget(page)
```

</details>

## 🏛️ Class `FluentTableView`

```python
class FluentTableView(QTableView)
```

Model-based table view with Fluent chrome.

<details>
<summary>Code:</summary>

```python
class FluentTableView(QTableView):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a table view."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTableView")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply table chrome."""
        self.setStyleSheet(_table_qss(self, f"QTableView#{self.objectName()}"))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a table view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTableView")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply table chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(_table_qss(self, f"QTableView#{self.objectName()}"))
```

</details>

## 🏛️ Class `FluentTableWidget`

```python
class FluentTableWidget(QTableWidget)
```

Table widget with hairline rows, no grid, and Fluent headers.

<details>
<summary>Code:</summary>

```python
class FluentTableWidget(QTableWidget):

    def __init__(self, rows: int = 0, columns: int = 0, parent: QWidget | None = None) -> None:
        """Create a table widget."""
        super().__init__(rows, columns, parent)
        self.setObjectName(self.objectName() or "FluentTableWidget")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply table chrome."""
        selector = f"QTableWidget#{self.objectName()}"
        self.setStyleSheet(_table_qss(self, selector))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, rows: int = 0, columns: int = 0, parent: QWidget | None = None) -> None
```

Create a table widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, rows: int = 0, columns: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(rows, columns, parent)
        self.setObjectName(self.objectName() or "FluentTableWidget")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply table chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        selector = f"QTableWidget#{self.objectName()}"
        self.setStyleSheet(_table_qss(self, selector))
```

</details>

## 🏛️ Class `FluentTreeView`

```python
class FluentTreeView(QTreeView)
```

Model-based tree view with Fluent chrome.

<details>
<summary>Code:</summary>

```python
class FluentTreeView(QTreeView):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a tree view."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeView")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tree chrome."""
        self.setStyleSheet(_tree_qss(self, f"QTreeView#{self.objectName()}"))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a tree view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeView")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply tree chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(_tree_qss(self, f"QTreeView#{self.objectName()}"))
```

</details>

## 🏛️ Class `FluentTreeWidget`

```python
class FluentTreeWidget(QTreeWidget)
```

Tree widget with rounded rows and Lucide branch chevrons.

<details>
<summary>Code:</summary>

```python
class FluentTreeWidget(QTreeWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a tree widget."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeWidget")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tree chrome."""
        self.setStyleSheet(_tree_qss(self, f"QTreeWidget#{self.objectName()}"))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a tree widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeWidget")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply tree chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(_tree_qss(self, f"QTreeWidget#{self.objectName()}"))
```

</details>

## 🏛️ Class `FluentVirtualList`

```python
class FluentVirtualList(FluentListView)
```

List of up to millions of rows: text is produced lazily by a callback.

<details>
<summary>Code:</summary>

```python
class FluentVirtualList(FluentListView):

    def __init__(
        self, parent: QWidget | None = None, *, count: int = 0, provider: Callable[[int], str] | None = None
    ) -> None:
        """Create a virtual list.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `count` (`int`): Number of rows.
        - `provider` (`Callable[[int], str] | None`): Returns the text of a row.

        """
        super().__init__(parent)
        self._model = _StringListModel(provider or str, count, self)
        self.setModel(self._model)
        self.setUniformItemSizes(True)
        self.setLayoutMode(QListView.LayoutMode.Batched)
        self.setBatchSize(200)

    def set_rows(self, count: int, provider: Callable[[int], str]) -> None:
        """Replace the row count and text provider."""
        self._model.reset(provider, count)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, count: int = 0, provider: Callable[[int], str] | None = None) -> None
```

Create a virtual list.

Args:

- `parent` (`QWidget | None`): Optional parent.
- `count` (`int`): Number of rows.
- `provider` (`Callable[[int], str] | None`): Returns the text of a row.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, parent: QWidget | None = None, *, count: int = 0, provider: Callable[[int], str] | None = None
    ) -> None:
        super().__init__(parent)
        self._model = _StringListModel(provider or str, count, self)
        self.setModel(self._model)
        self.setUniformItemSizes(True)
        self.setLayoutMode(QListView.LayoutMode.Batched)
        self.setBatchSize(200)
```

</details>

### ⚙️ Method `set_rows`

```python
def set_rows(self, count: int, provider: Callable[[int], str]) -> None
```

Replace the row count and text provider.

<details>
<summary>Code:</summary>

```python
def set_rows(self, count: int, provider: Callable[[int], str]) -> None:
        self._model.reset(provider, count)
```

</details>

## 🏛️ Class `SmoothScroller`

```python
class SmoothScroller(QObject)
```

Animate wheel scrolling of a `QAbstractScrollArea` instead of jumping.

<details>
<summary>Code:</summary>

```python
class SmoothScroller(QObject):

    def __init__(self, area: QAbstractScrollArea, *, orientation: Qt.Orientation = Qt.Orientation.Vertical) -> None:
        """Install smooth wheel scrolling on `area`."""
        super().__init__(area)
        self._area = area
        self._orientation = orientation
        bar = self._bar()
        self._animation = QPropertyAnimation(bar, b"value", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._target = bar.value()
        self._viewport = area.viewport()
        self._viewport.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Turn wheel events into an animated scroll."""
        if watched is self._viewport and event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                return False
            return self.scroll_by_wheel(event)
        return False

    def scroll_by_wheel(self, event: QWheelEvent) -> bool:
        """Scroll for one wheel event; return whether it was consumed."""
        bar = self._bar()
        if bar.maximum() <= bar.minimum():
            return False
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not event.pixelDelta().isNull():
            bar.setValue(bar.value() - (event.pixelDelta().y() or event.pixelDelta().x()))
            self._target = bar.value()
            return True
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._target = bar.value()
        step = bar.singleStep() * 3 if bar.singleStep() > 1 else _WHEEL_STEP_PX
        self._target = max(bar.minimum(), min(bar.maximum(), self._target - round(delta / _WHEEL_STEP_PX * step)))
        self._animation.stop()
        self._animation.setStartValue(bar.value())
        self._animation.setEndValue(self._target)
        self._animation.start()
        return True

    def _bar(self) -> QScrollBar:
        if self._orientation == Qt.Orientation.Horizontal:
            return self._area.horizontalScrollBar()
        return self._area.verticalScrollBar()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, area: QAbstractScrollArea, *, orientation: Qt.Orientation = Qt.Orientation.Vertical) -> None
```

Install smooth wheel scrolling on `area`.

<details>
<summary>Code:</summary>

```python
def __init__(self, area: QAbstractScrollArea, *, orientation: Qt.Orientation = Qt.Orientation.Vertical) -> None:
        super().__init__(area)
        self._area = area
        self._orientation = orientation
        bar = self._bar()
        self._animation = QPropertyAnimation(bar, b"value", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._target = bar.value()
        self._viewport = area.viewport()
        self._viewport.installEventFilter(self)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Turn wheel events into an animated scroll.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._viewport and event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                return False
            return self.scroll_by_wheel(event)
        return False
```

</details>

### ⚙️ Method `scroll_by_wheel`

```python
def scroll_by_wheel(self, event: QWheelEvent) -> bool
```

Scroll for one wheel event; return whether it was consumed.

<details>
<summary>Code:</summary>

```python
def scroll_by_wheel(self, event: QWheelEvent) -> bool:
        bar = self._bar()
        if bar.maximum() <= bar.minimum():
            return False
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not event.pixelDelta().isNull():
            bar.setValue(bar.value() - (event.pixelDelta().y() or event.pixelDelta().x()))
            self._target = bar.value()
            return True
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._target = bar.value()
        step = bar.singleStep() * 3 if bar.singleStep() > 1 else _WHEEL_STEP_PX
        self._target = max(bar.minimum(), min(bar.maximum(), self._target - round(delta / _WHEEL_STEP_PX * step)))
        self._animation.stop()
        self._animation.setStartValue(bar.value())
        self._animation.setEndValue(self._target)
        self._animation.start()
        return True
```

</details>
