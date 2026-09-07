---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `annotations.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `Annotation`](#%EF%B8%8F-class-annotation)
- [🏛️ Class `AnnotationDocument`](#%EF%B8%8F-class-annotationdocument)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `annotations (property)`](#%EF%B8%8F-method-annotations-property)
  - [⚙️ Method `append_draft_point`](#%EF%B8%8F-method-append_draft_point)
  - [⚙️ Method `apply_crop`](#%EF%B8%8F-method-apply_crop)
  - [⚙️ Method `base_image (property)`](#%EF%B8%8F-method-base_image-property)
  - [⚙️ Method `begin_draft`](#%EF%B8%8F-method-begin_draft)
  - [⚙️ Method `can_undo (property)`](#%EF%B8%8F-method-can_undo-property)
  - [⚙️ Method `cancel_draft`](#%EF%B8%8F-method-cancel_draft)
  - [⚙️ Method `commit_draft`](#%EF%B8%8F-method-commit_draft)
  - [⚙️ Method `delete_at`](#%EF%B8%8F-method-delete_at)
  - [⚙️ Method `draft (property)`](#%EF%B8%8F-method-draft-property)
  - [⚙️ Method `render`](#%EF%B8%8F-method-render)
  - [⚙️ Method `save_undo_checkpoint`](#%EF%B8%8F-method-save_undo_checkpoint)
  - [⚙️ Method `set_draft_text`](#%EF%B8%8F-method-set_draft_text)
  - [⚙️ Method `undo`](#%EF%B8%8F-method-undo)
  - [⚙️ Method `update_annotation_points`](#%EF%B8%8F-method-update_annotation_points)
  - [⚙️ Method `update_draft_points`](#%EF%B8%8F-method-update_draft_points)
- [🏛️ Class `AnnotationStyle`](#%EF%B8%8F-class-annotationstyle)
- [🏛️ Class `AnnotationTool`](#%EF%B8%8F-class-annotationtool)
- [🔧 Function `constrain_shape_end`](#-function-constrain_shape_end)
- [🔧 Function `paint_annotation`](#-function-paint_annotation)
- [🔧 Function `text_annotation_rect`](#-function-text_annotation_rect)

</details>

## 🏛️ Class `Annotation`

```python
class Annotation
```

One drawable mark in image coordinates.

<details>
<summary>Code:</summary>

```python
class Annotation:

    tool: AnnotationTool
    points: list[QPointF]
    style: AnnotationStyle
    text: str = ""
```

</details>

## 🏛️ Class `AnnotationDocument`

```python
class AnnotationDocument
```

Editable screenshot with a list of annotations and undo history.

<details>
<summary>Code:</summary>

```python
class AnnotationDocument:

    def __init__(self, image: QImage) -> None:
        """Start from a copy of `image` with an empty annotation list."""
        self._base = image.copy()
        self._annotations: list[Annotation] = []
        self._history: list[_HistoryEntry] = []
        self._draft: Annotation | None = None

    @property
    def annotations(self) -> list[Annotation]:
        """Committed annotations (image coordinates)."""
        return self._annotations

    def append_draft_point(self, point: QPointF) -> None:
        """Add a freehand point to the draft."""
        if self._draft is None:
            return
        self._draft.points.append(QPointF(point))

    def apply_crop(self, rect: QRectF) -> bool:
        """Crop the composite to `rect` (image coords) and clear annotations."""
        bounds = QRectF(self._base.rect()).intersected(rect.normalized())
        if bounds.width() < _MIN_CROP_SIZE or bounds.height() < _MIN_CROP_SIZE:
            return False
        composite = self.render()
        cropped = composite.copy(bounds.toRect())
        if cropped.isNull():
            return False
        self._push_history()
        self._base = cropped
        self._annotations = []
        self._draft = None
        return True

    @property
    def base_image(self) -> QImage:
        """Underlying image without the current draft."""
        return self._base

    def begin_draft(self, annotation: Annotation) -> None:
        """Start a new in-progress annotation."""
        self._draft = annotation

    @property
    def can_undo(self) -> bool:
        """Whether `undo` can restore a previous state."""
        return bool(self._history)

    def cancel_draft(self) -> None:
        """Discard the in-progress annotation."""
        self._draft = None

    def commit_draft(self) -> bool:
        """Commit the draft if it is drawable; return whether anything was added."""
        draft = self._draft
        self._draft = None
        if draft is None or not _is_meaningful(draft):
            return False
        self._push_history()
        self._annotations.append(draft)
        return True

    def delete_at(self, index: int) -> bool:
        """Remove the annotation at `index` and record undo. Return whether it was deleted."""
        if index < 0 or index >= len(self._annotations):
            return False
        self._push_history()
        del self._annotations[index]
        return True

    @property
    def draft(self) -> Annotation | None:
        """In-progress annotation while the mouse is dragged."""
        return self._draft

    def render(self, *, include_draft: bool = True) -> QImage:
        """Return base image with committed annotations painted.

        When `include_draft` is `True`, also paint the in-progress annotation.

        """
        result = self._base.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        for item in self._annotations:
            paint_annotation(painter, item)
        if include_draft and self._draft is not None:
            paint_annotation(painter, self._draft)
        painter.end()
        return result

    def save_undo_checkpoint(self) -> None:
        """Snapshot the current document so the next mutation can be undone."""
        self._push_history()

    def set_draft_text(self, text: str) -> None:
        """Set text on the current draft (for the text tool)."""
        if self._draft is not None:
            self._draft.text = text

    def undo(self) -> bool:
        """Restore the previous document state."""
        if not self._history:
            return False
        entry = self._history.pop()
        self._base = entry.base
        self._annotations = entry.annotations
        self._draft = None
        return True

    def update_annotation_points(self, index: int, points: Sequence[QPointF]) -> None:
        """Replace points of a committed annotation (image coordinates)."""
        if index < 0 or index >= len(self._annotations):
            return
        self._annotations[index].points = [QPointF(p) for p in points]

    def update_draft_points(self, points: Sequence[QPointF]) -> None:
        """Replace draft points (image coordinates)."""
        if self._draft is None:
            return
        self._draft.points = [QPointF(p) for p in points]

    def _push_history(self) -> None:
        self._history.append(
            _HistoryEntry(
                base=self._base.copy(),
                annotations=[_clone_annotation(item) for item in self._annotations],
            )
        )
        if len(self._history) > _MAX_UNDO:
            del self._history[0]
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, image: QImage) -> None
```

Start from a copy of `image` with an empty annotation list.

<details>
<summary>Code:</summary>

```python
def __init__(self, image: QImage) -> None:
        self._base = image.copy()
        self._annotations: list[Annotation] = []
        self._history: list[_HistoryEntry] = []
        self._draft: Annotation | None = None
```

</details>

### ⚙️ Method `annotations (property)`

```python
def annotations(self) -> list[Annotation]
```

Committed annotations (image coordinates).

<details>
<summary>Code:</summary>

```python
def annotations(self) -> list[Annotation]:
        return self._annotations
```

</details>

### ⚙️ Method `append_draft_point`

```python
def append_draft_point(self, point: QPointF) -> None
```

Add a freehand point to the draft.

<details>
<summary>Code:</summary>

```python
def append_draft_point(self, point: QPointF) -> None:
        if self._draft is None:
            return
        self._draft.points.append(QPointF(point))
```

</details>

### ⚙️ Method `apply_crop`

```python
def apply_crop(self, rect: QRectF) -> bool
```

Crop the composite to `rect` (image coords) and clear annotations.

<details>
<summary>Code:</summary>

```python
def apply_crop(self, rect: QRectF) -> bool:
        bounds = QRectF(self._base.rect()).intersected(rect.normalized())
        if bounds.width() < _MIN_CROP_SIZE or bounds.height() < _MIN_CROP_SIZE:
            return False
        composite = self.render()
        cropped = composite.copy(bounds.toRect())
        if cropped.isNull():
            return False
        self._push_history()
        self._base = cropped
        self._annotations = []
        self._draft = None
        return True
```

</details>

### ⚙️ Method `base_image (property)`

```python
def base_image(self) -> QImage
```

Underlying image without the current draft.

<details>
<summary>Code:</summary>

```python
def base_image(self) -> QImage:
        return self._base
```

</details>

### ⚙️ Method `begin_draft`

```python
def begin_draft(self, annotation: Annotation) -> None
```

Start a new in-progress annotation.

<details>
<summary>Code:</summary>

```python
def begin_draft(self, annotation: Annotation) -> None:
        self._draft = annotation
```

</details>

### ⚙️ Method `can_undo (property)`

```python
def can_undo(self) -> bool
```

Whether [`undo`](#%EF%B8%8F-method-undo) can restore a previous state.

<details>
<summary>Code:</summary>

```python
def can_undo(self) -> bool:
        return bool(self._history)
```

</details>

### ⚙️ Method `cancel_draft`

```python
def cancel_draft(self) -> None
```

Discard the in-progress annotation.

<details>
<summary>Code:</summary>

```python
def cancel_draft(self) -> None:
        self._draft = None
```

</details>

### ⚙️ Method `commit_draft`

```python
def commit_draft(self) -> bool
```

Commit the draft if it is drawable; return whether anything was added.

<details>
<summary>Code:</summary>

```python
def commit_draft(self) -> bool:
        draft = self._draft
        self._draft = None
        if draft is None or not _is_meaningful(draft):
            return False
        self._push_history()
        self._annotations.append(draft)
        return True
```

</details>

### ⚙️ Method `delete_at`

```python
def delete_at(self, index: int) -> bool
```

Remove the annotation at `index` and record undo. Return whether it was deleted.

<details>
<summary>Code:</summary>

```python
def delete_at(self, index: int) -> bool:
        if index < 0 or index >= len(self._annotations):
            return False
        self._push_history()
        del self._annotations[index]
        return True
```

</details>

### ⚙️ Method `draft (property)`

```python
def draft(self) -> Annotation | None
```

In-progress annotation while the mouse is dragged.

<details>
<summary>Code:</summary>

```python
def draft(self) -> Annotation | None:
        return self._draft
```

</details>

### ⚙️ Method `render`

```python
def render(self, *, include_draft: bool = True) -> QImage
```

Return base image with committed annotations painted.

When `include_draft` is `True`, also paint the in-progress annotation.

<details>
<summary>Code:</summary>

```python
def render(self, *, include_draft: bool = True) -> QImage:
        result = self._base.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        for item in self._annotations:
            paint_annotation(painter, item)
        if include_draft and self._draft is not None:
            paint_annotation(painter, self._draft)
        painter.end()
        return result
```

</details>

### ⚙️ Method `save_undo_checkpoint`

```python
def save_undo_checkpoint(self) -> None
```

Snapshot the current document so the next mutation can be undone.

<details>
<summary>Code:</summary>

```python
def save_undo_checkpoint(self) -> None:
        self._push_history()
```

</details>

### ⚙️ Method `set_draft_text`

```python
def set_draft_text(self, text: str) -> None
```

Set text on the current draft (for the text tool).

<details>
<summary>Code:</summary>

```python
def set_draft_text(self, text: str) -> None:
        if self._draft is not None:
            self._draft.text = text
```

</details>

### ⚙️ Method `undo`

```python
def undo(self) -> bool
```

Restore the previous document state.

<details>
<summary>Code:</summary>

```python
def undo(self) -> bool:
        if not self._history:
            return False
        entry = self._history.pop()
        self._base = entry.base
        self._annotations = entry.annotations
        self._draft = None
        return True
```

</details>

### ⚙️ Method `update_annotation_points`

```python
def update_annotation_points(self, index: int, points: Sequence[QPointF]) -> None
```

Replace points of a committed annotation (image coordinates).

<details>
<summary>Code:</summary>

```python
def update_annotation_points(self, index: int, points: Sequence[QPointF]) -> None:
        if index < 0 or index >= len(self._annotations):
            return
        self._annotations[index].points = [QPointF(p) for p in points]
```

</details>

### ⚙️ Method `update_draft_points`

```python
def update_draft_points(self, points: Sequence[QPointF]) -> None
```

Replace draft points (image coordinates).

<details>
<summary>Code:</summary>

```python
def update_draft_points(self, points: Sequence[QPointF]) -> None:
        if self._draft is None:
            return
        self._draft.points = [QPointF(p) for p in points]
```

</details>

## 🏛️ Class `AnnotationStyle`

```python
class AnnotationStyle
```

Stroke / text style shared by annotation tools.

<details>
<summary>Code:</summary>

```python
class AnnotationStyle:

    color: QColor = field(default_factory=lambda: QColor("#de2b26"))
    width: float = 3.0
    font_family: str = ""
    font_size: float = 26.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    align: str = "left"
    background_fill: bool = False
```

</details>

## 🏛️ Class `AnnotationTool`

```python
class AnnotationTool(Enum)
```

Active drawing tool in the screenshot preview.

<details>
<summary>Code:</summary>

```python
class AnnotationTool(Enum):

    NONE = "none"
    ARROW = "arrow"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    LINE = "line"
    PEN = "pen"
    TEXT = "text"
    CROP = "crop"
    EYEDROPPER = "eyedropper"
```

</details>

## 🔧 Function `constrain_shape_end`

```python
def constrain_shape_end(tool: AnnotationTool, start: QPointF, end: QPointF, *, shift: bool) -> QPointF
```

Return the free or Shift-constrained end point for [`tool`](preview_canvas.g.md#%EF%B8%8F-method-tool-property).

Shift snaps arrows and lines to 0°/45°/90° steps and makes rectangles
and ellipses square or circular, keeping the start corner fixed.

<details>
<summary>Code:</summary>

```python
def constrain_shape_end(tool: AnnotationTool, start: QPointF, end: QPointF, *, shift: bool) -> QPointF:
    if not shift:
        return QPointF(end)
    if tool in _LINE_SHIFT_TOOLS:
        return _snap_end_to_45_degrees(start, end)
    if tool in _SQUARE_SHIFT_TOOLS:
        return _snap_end_to_square(start, end)
    return QPointF(end)
```

</details>

## 🔧 Function `paint_annotation`

```python
def paint_annotation(painter: QPainter, annotation: Annotation) -> None
```

Draw `annotation` onto `painter` in image coordinates.

<details>
<summary>Code:</summary>

```python
def paint_annotation(painter: QPainter, annotation: Annotation) -> None:
    points = annotation.points
    if not points:
        return
    pen = QPen(annotation.style.color)
    pen.setWidthF(max(1.0, annotation.style.width))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    tool = annotation.tool
    if tool == AnnotationTool.PEN:
        if len(points) == 1:
            painter.drawPoint(points[0])
        else:
            painter.drawPolyline(QPolygonF(points))
        return
    if tool == AnnotationTool.TEXT:
        _paint_text_annotation(painter, annotation)
        return
    if len(points) < _MIN_SHAPE_POINTS:
        return
    start, end = points[0], points[-1]
    if tool == AnnotationTool.LINE:
        painter.drawLine(start, end)
        return
    if tool == AnnotationTool.ARROW:
        _draw_filled_arrow(painter, start, end, annotation.style.color, annotation.style.width)
        return
    rect = QRectF(start, end).normalized()
    if tool == AnnotationTool.RECTANGLE:
        painter.drawRect(rect)
        return
    if tool == AnnotationTool.ELLIPSE:
        painter.drawEllipse(rect)
        return
    if tool == AnnotationTool.CROP:
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(rect)
```

</details>

## 🔧 Function `text_annotation_rect`

```python
def text_annotation_rect(annotation: Annotation) -> QRectF
```

Return the axis-aligned text box for `annotation` in image coordinates.

<details>
<summary>Code:</summary>

```python
def text_annotation_rect(annotation: Annotation) -> QRectF:
    points = annotation.points
    if not points:
        return QRectF()
    if len(points) >= _MIN_SHAPE_POINTS:
        return QRectF(points[0], points[-1]).normalized()
    # Legacy single-point text: size from font metrics.
    from harrix_swiss_knife.screenshot.text_style import annotation_qfont  # noqa: PLC0415

    origin = points[0]
    metrics = QFontMetricsF(annotation_qfont(annotation.style))
    text = annotation.text or "…"
    width = max(metrics.horizontalAdvance(text), 8.0)
    height = max(metrics.height(), 10.0)
    return QRectF(origin.x(), origin.y() - metrics.ascent(), width, height)
```

</details>
