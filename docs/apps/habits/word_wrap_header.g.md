---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `word_wrap_header.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `WordWrapHeaderView`](#%EF%B8%8F-class-wordwrapheaderview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
  - [⚙️ Method `paintSection`](#%EF%B8%8F-method-paintsection)
  - [⚙️ Method `refresh_wrapped_height`](#%EF%B8%8F-method-refresh_wrapped_height)
  - [⚙️ Method `sectionSizeFromContents`](#%EF%B8%8F-method-sectionsizefromcontents)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🔧 Function `wrapped_header_text_size`](#-function-wrapped_header_text_size)

</details>

## 🏛️ Class `WordWrapHeaderView`

```python
class WordWrapHeaderView(QHeaderView)
```

`QHeaderView` that paints and sizes section titles with word wrap.

<details>
<summary>Code:</summary>

```python
class WordWrapHeaderView(QHeaderView):

    def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = None,
        *,
        wrap_width: int | None = None,
        wrap_first_section: bool = False,
    ) -> None:
        super().__init__(orientation, parent)
        self._wrap_width = wrap_width
        self._wrap_first_section = wrap_first_section
        self._updating_height = False
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.sectionResized.connect(self._on_section_resized)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Use the wrapped height as the minimum header size."""
        return self.sizeHint()

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        """Paint the section chrome, then draw the title with wrapping."""
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        self.initStyleOptionForIndex(option, logical_index)
        option.rect = rect
        option.text = ""
        style = self.style()
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_Header, option, painter, self)

        text = self._section_text(logical_index)
        if not text:
            return

        painter.save()
        painter.setPen(option.palette.color(QPalette.ColorRole.ButtonText))
        painter.drawText(rect.adjusted(_TEXT_INSET, 2, -_TEXT_INSET, -2), int(HEADER_TEXT_FLAGS), text)
        painter.restore()

    def refresh_wrapped_height(self) -> None:
        """Recalculate header height from the current section widths."""
        if self._updating_height:
            return
        self._updating_height = True
        try:
            self.updateGeometries()
        finally:
            self._updating_height = False

    def sectionSizeFromContents(self, logical_index: int) -> QSize:  # noqa: N802
        """Prefer a compact wrapped width for habit columns."""
        if not self._should_wrap_section(logical_index) or self._wrap_width is None:
            return super().sectionSizeFromContents(logical_index)
        return wrapped_header_text_size(self._section_text(logical_index), self._wrap_width, self.fontMetrics())

    def sizeHint(self) -> QSize:  # noqa: N802
        """Grow vertically so wrapped titles stay visible."""
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), self._max_wrapped_height()))

    def _max_wrapped_height(self) -> int:
        if self.count() == 0:
            return 0
        max_height = 0
        for logical_index in range(self.count()):
            width = self.sectionSize(logical_index)
            if width <= 0 and self._wrap_width is not None and self._should_wrap_section(logical_index):
                width = self._wrap_width
            if width <= 0:
                continue
            max_height = max(
                max_height,
                wrapped_header_text_size(self._section_text(logical_index), width, self.fontMetrics()).height(),
            )
        return max_height

    def _on_section_resized(self, _logical_index: int, _old_size: int, _new_size: int) -> None:
        self.refresh_wrapped_height()

    def _section_text(self, logical_index: int) -> str:
        model = self.model()
        if model is None:
            return ""
        value = model.headerData(logical_index, self.orientation(), Qt.ItemDataRole.DisplayRole)
        return "" if value is None else str(value)

    def _should_wrap_section(self, logical_index: int) -> bool:
        return self._wrap_first_section or logical_index > 0
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None, *, wrap_width: int | None = None, wrap_first_section: bool = False) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = None,
        *,
        wrap_width: int | None = None,
        wrap_first_section: bool = False,
    ) -> None:
        super().__init__(orientation, parent)
        self._wrap_width = wrap_width
        self._wrap_first_section = wrap_first_section
        self._updating_height = False
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.sectionResized.connect(self._on_section_resized)
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Use the wrapped height as the minimum header size.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()
```

</details>

### ⚙️ Method `paintSection`

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None
```

Paint the section chrome, then draw the title with wrapping.

<details>
<summary>Code:</summary>

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        self.initStyleOptionForIndex(option, logical_index)
        option.rect = rect
        option.text = ""
        style = self.style()
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_Header, option, painter, self)

        text = self._section_text(logical_index)
        if not text:
            return

        painter.save()
        painter.setPen(option.palette.color(QPalette.ColorRole.ButtonText))
        painter.drawText(rect.adjusted(_TEXT_INSET, 2, -_TEXT_INSET, -2), int(HEADER_TEXT_FLAGS), text)
        painter.restore()
```

</details>

### ⚙️ Method `refresh_wrapped_height`

```python
def refresh_wrapped_height(self) -> None
```

Recalculate header height from the current section widths.

<details>
<summary>Code:</summary>

```python
def refresh_wrapped_height(self) -> None:
        if self._updating_height:
            return
        self._updating_height = True
        try:
            self.updateGeometries()
        finally:
            self._updating_height = False
```

</details>

### ⚙️ Method `sectionSizeFromContents`

```python
def sectionSizeFromContents(self, logical_index: int) -> QSize
```

Prefer a compact wrapped width for habit columns.

<details>
<summary>Code:</summary>

```python
def sectionSizeFromContents(self, logical_index: int) -> QSize:  # noqa: N802
        if not self._should_wrap_section(logical_index) or self._wrap_width is None:
            return super().sectionSizeFromContents(logical_index)
        return wrapped_header_text_size(self._section_text(logical_index), self._wrap_width, self.fontMetrics())
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Grow vertically so wrapped titles stay visible.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), self._max_wrapped_height()))
```

</details>

## 🔧 Function `wrapped_header_text_size`

```python
def wrapped_header_text_size(text: str, width: int, font_metrics: QFontMetrics, *, padding: int = _TEXT_PADDING) -> QSize
```

Return the size of `text` wrapped into `width` pixels.

<details>
<summary>Code:</summary>

```python
def wrapped_header_text_size(
    text: str,
    width: int,
    font_metrics: QFontMetrics,
    *,
    padding: int = _TEXT_PADDING,
) -> QSize:
    inner_width = max(width - padding, 1)
    bounds = font_metrics.boundingRect(0, 0, inner_width, 10_000, int(HEADER_TEXT_FLAGS), text)
    return QSize(max(width, bounds.width() + padding), bounds.height() + padding)
```

</details>
