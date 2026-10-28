---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `editors.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BubbleSide`](#%EF%B8%8F-class-bubbleside)
- [🏛️ Class `FluentChatBubble`](#%EF%B8%8F-class-fluentchatbubble)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `text`](#%EF%B8%8F-method-text)
- [🏛️ Class `FluentCodeEditor`](#%EF%B8%8F-class-fluentcodeeditor)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `line_number_width`](#%EF%B8%8F-method-line_number_width)
  - [⚙️ Method `paint_line_numbers`](#%EF%B8%8F-method-paint_line_numbers)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_language`](#%EF%B8%8F-method-set_language)
- [🏛️ Class `FluentDashboardGauge`](#%EF%B8%8F-class-fluentdashboardgauge)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_value`](#%EF%B8%8F-method-set_value)
  - [⚙️ Method `value`](#%EF%B8%8F-method-value)
- [🏛️ Class `FluentLogView`](#%EF%B8%8F-class-fluentlogview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `append_record`](#%EF%B8%8F-method-append_record)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-1)
- [🏛️ Class `FluentMarkdownViewer`](#%EF%B8%8F-class-fluentmarkdownviewer)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `markdown`](#%EF%B8%8F-method-markdown)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-2)
  - [⚙️ Method `set_markdown`](#%EF%B8%8F-method-set_markdown)
- [🏛️ Class `FluentTerminalWidget`](#%EF%B8%8F-class-fluentterminalwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `append_text`](#%EF%B8%8F-method-append_text)
  - [⚙️ Method `is_running`](#%EF%B8%8F-method-is_running)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-3)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)

</details>

## 🏛️ Class `BubbleSide`

```python
class BubbleSide(Enum)
```

Which side a chat bubble belongs to.

<details>
<summary>Code:</summary>

```python
class BubbleSide(Enum):

    INCOMING = "incoming"
    OUTGOING = "outgoing"
```

</details>

## 🏛️ Class `FluentChatBubble`

```python
class FluentChatBubble(QWidget)
```

Chat message: rounded bubble (accent for outgoing), sender, and time caption.

<details>
<summary>Code:</summary>

```python
class FluentChatBubble(QWidget):

    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        side: BubbleSide = BubbleSide.INCOMING,
        sender: str = "",
        time: str = "",
    ) -> None:
        """Create a chat bubble row."""
        super().__init__(parent)
        self._side = side
        row = QHBoxLayout(self)
        row.setContentsMargins(0, SPACE_XS, 0, SPACE_XS)
        self._bubble = _Bubble(text, side, self)
        column = QVBoxLayout()
        column.setSpacing(2)
        if sender:
            column.addWidget(CaptionLabel(sender, self))
        column.addWidget(self._bubble)
        if time:
            caption = CaptionLabel(time, self)
            caption.set_role(TextRole.TERTIARY)
            column.addWidget(
                caption, 0, Qt.AlignmentFlag.AlignRight if side == BubbleSide.OUTGOING else Qt.AlignmentFlag.AlignLeft
            )
        if side == BubbleSide.OUTGOING:
            row.addStretch(1)
            row.addLayout(column)
        else:
            row.addLayout(column)
            row.addStretch(1)

    def text(self) -> str:
        """Return the message text."""
        return self._bubble.label.text()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, parent: QWidget | None = None, *, side: BubbleSide = BubbleSide.INCOMING, sender: str = '', time: str = '') -> None
```

Create a chat bubble row.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        side: BubbleSide = BubbleSide.INCOMING,
        sender: str = "",
        time: str = "",
    ) -> None:
        super().__init__(parent)
        self._side = side
        row = QHBoxLayout(self)
        row.setContentsMargins(0, SPACE_XS, 0, SPACE_XS)
        self._bubble = _Bubble(text, side, self)
        column = QVBoxLayout()
        column.setSpacing(2)
        if sender:
            column.addWidget(CaptionLabel(sender, self))
        column.addWidget(self._bubble)
        if time:
            caption = CaptionLabel(time, self)
            caption.set_role(TextRole.TERTIARY)
            column.addWidget(
                caption, 0, Qt.AlignmentFlag.AlignRight if side == BubbleSide.OUTGOING else Qt.AlignmentFlag.AlignLeft
            )
        if side == BubbleSide.OUTGOING:
            row.addStretch(1)
            row.addLayout(column)
        else:
            row.addLayout(column)
            row.addStretch(1)
```

</details>

### ⚙️ Method `text`

```python
def text(self) -> str
```

Return the message text.

<details>
<summary>Code:</summary>

```python
def text(self) -> str:
        return self._bubble.label.text()
```

</details>

## 🏛️ Class `FluentCodeEditor`

```python
class FluentCodeEditor(QPlainTextEdit)
```

Monospace editor with line numbers, current-line highlight, and Pygments colors.

<details>
<summary>Code:</summary>

```python
class FluentCodeEditor(QPlainTextEdit):

    def __init__(self, parent: QWidget | None = None, *, language: str = "python") -> None:
        """Create a code editor (`language` is a Pygments lexer alias)."""
        super().__init__(parent)
        self.setFont(_monospace_font(self.font()))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._gutter = _LineNumberArea(self)
        self._highlighter = _PygmentsHighlighter(self.document(), language, dark=False)
        self.blockCountChanged.connect(self._update_margins)
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._highlight_line)
        self._update_margins()
        bind_theme(self, self.refresh_theme)

    def line_number_width(self) -> int:
        """Return the gutter width for the current line count."""
        digits = max(2, len(str(max(1, self.blockCount()))))
        return _GUTTER_PADDING * 2 + self.fontMetrics().horizontalAdvance("9") * digits

    def paint_line_numbers(self, event: QPaintEvent) -> None:
        """Paint the gutter (called by the line number area)."""
        palette = palette_for(self)
        painter = QPainter(self._gutter)
        painter.fillRect(event.rect(), Qt.GlobalColor.transparent)
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        current = self.textCursor().blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                color = palette.text_primary if number == current else palette.text_tertiary
                painter.setPen(color)
                painter.drawText(
                    0,
                    top,
                    self._gutter.width() - _GUTTER_PADDING,
                    self.fontMetrics().height(),
                    int(Qt.AlignmentFlag.AlignRight),
                    str(number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            number += 1
        painter.end()

    def refresh_theme(self) -> None:
        """Re-apply chrome and token colors."""
        palette = palette_for(self)
        self.setStyleSheet(text_edit_qss(palette, "QPlainTextEdit"))
        self._highlighter.set_dark(dark=palette.dark)
        self._highlight_line()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the gutter aligned with the viewport."""
        super().resizeEvent(event)
        rect = self.contentsRect()
        self._gutter.setGeometry(QRect(rect.left(), rect.top(), self.line_number_width(), rect.height()))

    def set_language(self, language: str) -> None:
        """Switch the Pygments lexer."""
        self._highlighter.set_language(language)

    def _highlight_line(self) -> None:
        palette = palette_for(self)
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(with_alpha(palette.text_primary, 10))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)  # noqa: FBT003
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])
        self._gutter.update()

    def _update_gutter(self, rect: QRect, dy: int) -> None:
        if dy:
            self._gutter.scroll(0, dy)
        else:
            self._gutter.update(0, rect.y(), self._gutter.width(), rect.height())

    def _update_margins(self) -> None:
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, language: str = 'python') -> None
```

Create a code editor (`language` is a Pygments lexer alias).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, language: str = "python") -> None:
        super().__init__(parent)
        self.setFont(_monospace_font(self.font()))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._gutter = _LineNumberArea(self)
        self._highlighter = _PygmentsHighlighter(self.document(), language, dark=False)
        self.blockCountChanged.connect(self._update_margins)
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._highlight_line)
        self._update_margins()
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `line_number_width`

```python
def line_number_width(self) -> int
```

Return the gutter width for the current line count.

<details>
<summary>Code:</summary>

```python
def line_number_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return _GUTTER_PADDING * 2 + self.fontMetrics().horizontalAdvance("9") * digits
```

</details>

### ⚙️ Method `paint_line_numbers`

```python
def paint_line_numbers(self, event: QPaintEvent) -> None
```

Paint the gutter (called by the line number area).

<details>
<summary>Code:</summary>

```python
def paint_line_numbers(self, event: QPaintEvent) -> None:
        palette = palette_for(self)
        painter = QPainter(self._gutter)
        painter.fillRect(event.rect(), Qt.GlobalColor.transparent)
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        current = self.textCursor().blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                color = palette.text_primary if number == current else palette.text_tertiary
                painter.setPen(color)
                painter.drawText(
                    0,
                    top,
                    self._gutter.width() - _GUTTER_PADDING,
                    self.fontMetrics().height(),
                    int(Qt.AlignmentFlag.AlignRight),
                    str(number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            number += 1
        painter.end()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and token colors.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(text_edit_qss(palette, "QPlainTextEdit"))
        self._highlighter.set_dark(dark=palette.dark)
        self._highlight_line()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep the gutter aligned with the viewport.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        rect = self.contentsRect()
        self._gutter.setGeometry(QRect(rect.left(), rect.top(), self.line_number_width(), rect.height()))
```

</details>

### ⚙️ Method `set_language`

```python
def set_language(self, language: str) -> None
```

Switch the Pygments lexer.

<details>
<summary>Code:</summary>

```python
def set_language(self, language: str) -> None:
        self._highlighter.set_language(language)
```

</details>

## 🏛️ Class `FluentDashboardGauge`

```python
class FluentDashboardGauge(QWidget)
```

Arc gauge with a value, unit, and optional caution / critical thresholds.

<details>
<summary>Code:</summary>

```python
class FluentDashboardGauge(QWidget):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: float = 0.0,
        maximum: float = 100.0,
        unit: str = "",
        title: str = "",
        caution: float | None = None,
        critical: float | None = None,
    ) -> None:
        """Create a gauge."""
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._value = minimum
        self._unit = unit
        self._title = title
        self._caution = caution
        self._critical = critical
        self.setMinimumSize(160, 140)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint track, value arc, number, and title."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        side = min(self.width(), self.height() * 1.15)
        stroke = max(8.0, side / 14)
        rect = QRectF((self.width() - side) / 2 + stroke, stroke, side - 2 * stroke, side - 2 * stroke)
        start = 90 + _GAUGE_SPAN / 2
        track = QPen(palette.control_strong_stroke if not palette.dark else palette.control_strong_fill, stroke)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track)
        painter.drawArc(rect, int(start * 16), int(-_GAUGE_SPAN * 16))
        ratio = (
            0.0 if self._maximum <= self._minimum else (self._value - self._minimum) / (self._maximum - self._minimum)
        )
        pen = QPen(self._color(palette), stroke)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if ratio > 0:
            painter.drawArc(rect, int(start * 16), int(-_GAUGE_SPAN * ratio * 16))
        painter.setPen(palette.text_primary)
        painter.setFont(fluent_font(self.font(), TYPE_TITLE, weight=QFont.Weight.DemiBold))
        number = f"{self._value:g}{self._unit}"
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), number)
        if self._title:
            painter.setPen(palette.text_secondary)
            painter.setFont(fluent_font(self.font(), TYPE_CAPTION))
            bottom = rect.center().y() + rect.height() / 2 * math.cos(math.radians(_GAUGE_SPAN / 2 - 90)) * 0.2
            painter.drawText(
                QRectF(rect.left(), bottom + SPACE_L, rect.width(), 20), int(Qt.AlignmentFlag.AlignHCenter), self._title
            )
        painter.end()

    def set_value(self, value: float) -> None:
        """Set the gauge value (clamped)."""
        self._value = max(self._minimum, min(self._maximum, value))
        self.update()

    def value(self) -> float:
        """Return the gauge value."""
        return self._value

    def _color(self, palette: FluentPalette) -> QColor:
        if self._critical is not None and self._value >= self._critical:
            return palette.critical
        if self._caution is not None and self._value >= self._caution:
            return palette.caution
        return palette.accent
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, minimum: float = 0.0, maximum: float = 100.0, unit: str = '', title: str = '', caution: float | None = None, critical: float | None = None) -> None
```

Create a gauge.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: float = 0.0,
        maximum: float = 100.0,
        unit: str = "",
        title: str = "",
        caution: float | None = None,
        critical: float | None = None,
    ) -> None:
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._value = minimum
        self._unit = unit
        self._title = title
        self._caution = caution
        self._critical = critical
        self.setMinimumSize(160, 140)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint track, value arc, number, and title.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        side = min(self.width(), self.height() * 1.15)
        stroke = max(8.0, side / 14)
        rect = QRectF((self.width() - side) / 2 + stroke, stroke, side - 2 * stroke, side - 2 * stroke)
        start = 90 + _GAUGE_SPAN / 2
        track = QPen(palette.control_strong_stroke if not palette.dark else palette.control_strong_fill, stroke)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track)
        painter.drawArc(rect, int(start * 16), int(-_GAUGE_SPAN * 16))
        ratio = (
            0.0 if self._maximum <= self._minimum else (self._value - self._minimum) / (self._maximum - self._minimum)
        )
        pen = QPen(self._color(palette), stroke)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if ratio > 0:
            painter.drawArc(rect, int(start * 16), int(-_GAUGE_SPAN * ratio * 16))
        painter.setPen(palette.text_primary)
        painter.setFont(fluent_font(self.font(), TYPE_TITLE, weight=QFont.Weight.DemiBold))
        number = f"{self._value:g}{self._unit}"
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), number)
        if self._title:
            painter.setPen(palette.text_secondary)
            painter.setFont(fluent_font(self.font(), TYPE_CAPTION))
            bottom = rect.center().y() + rect.height() / 2 * math.cos(math.radians(_GAUGE_SPAN / 2 - 90)) * 0.2
            painter.drawText(
                QRectF(rect.left(), bottom + SPACE_L, rect.width(), 20), int(Qt.AlignmentFlag.AlignHCenter), self._title
            )
        painter.end()
```

</details>

### ⚙️ Method `set_value`

```python
def set_value(self, value: float) -> None
```

Set the gauge value (clamped).

<details>
<summary>Code:</summary>

```python
def set_value(self, value: float) -> None:
        self._value = max(self._minimum, min(self._maximum, value))
        self.update()
```

</details>

### ⚙️ Method `value`

```python
def value(self) -> float
```

Return the gauge value.

<details>
<summary>Code:</summary>

```python
def value(self) -> float:
        return self._value
```

</details>

## 🏛️ Class `FluentLogView`

```python
class FluentLogView(QWidget)
```

Colored log lines with a minimum-level filter; feed it from [`FluentLog`](../infra.g.md#%EF%B8%8F-class-fluentlog).

<details>
<summary>Code:</summary>

```python
class FluentLogView(QWidget):

    def __init__(self, parent: QWidget | None = None, *, log: FluentLog | None = None) -> None:
        """Create a log view (optionally connected to `log`)."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        row = QHBoxLayout()
        row.addWidget(CaptionLabel("Level", self))
        self.level_combo = FluentComboBox(self, items=[name for name, _level in _LOG_LEVELS])
        self.level_combo.setCurrentIndex(1)
        self.level_combo.currentIndexChanged.connect(self._refilter)
        row.addWidget(self.level_combo)
        row.addStretch(1)
        layout.addLayout(row)
        self.view = QTextBrowser(self)
        self.view.setFont(_monospace_font(self.font()))
        layout.addWidget(self.view, 1)
        self._records: list[tuple[int, str]] = []
        if log is not None:
            log.record_emitted.connect(self.append_record)
        bind_theme(self, self.refresh_theme)

    def append_record(self, level: int, text: str) -> None:
        """Add one log line."""
        self._records.append((level, text))
        if len(self._records) > _TERMINAL_MAX_BLOCKS:
            self._records = self._records[-_TERMINAL_MAX_BLOCKS:]
        if level >= self._min_level():
            self.view.append(self._line_html(level, text))

    def clear(self) -> None:
        """Remove every line."""
        self._records.clear()
        self.view.clear()

    def refresh_theme(self) -> None:
        """Re-apply colors and re-render lines."""
        palette = palette_for(self)
        self.view.setStyleSheet(
            f"QTextBrowser {{ background: {css(palette.card_bg)}; color: {css(palette.text_primary)};"
            f" border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; padding: 4px; }}\n"
            f"{scroll_bar_qss(palette)}",
        )
        self._refilter()

    def _line_html(self, level: int, text: str) -> str:
        palette = palette_for(self)
        if level >= logging.ERROR:
            color = palette.critical
        elif level >= logging.WARNING:
            color = palette.caution
        elif level <= logging.DEBUG:
            color = palette.text_tertiary
        else:
            color = palette.text_primary
        return f'<span style="color:{mix(palette.window_bg, color).name()}; white-space:pre">{html.escape(text)}</span>'

    def _min_level(self) -> int:
        return _LOG_LEVELS[max(0, self.level_combo.currentIndex())][1]

    def _refilter(self) -> None:
        self.view.clear()
        minimum = self._min_level()
        for level, text in self._records:
            if level >= minimum:
                self.view.append(self._line_html(level, text))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, log: FluentLog | None = None) -> None
```

Create a log view (optionally connected to `log`).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, log: FluentLog | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        row = QHBoxLayout()
        row.addWidget(CaptionLabel("Level", self))
        self.level_combo = FluentComboBox(self, items=[name for name, _level in _LOG_LEVELS])
        self.level_combo.setCurrentIndex(1)
        self.level_combo.currentIndexChanged.connect(self._refilter)
        row.addWidget(self.level_combo)
        row.addStretch(1)
        layout.addLayout(row)
        self.view = QTextBrowser(self)
        self.view.setFont(_monospace_font(self.font()))
        layout.addWidget(self.view, 1)
        self._records: list[tuple[int, str]] = []
        if log is not None:
            log.record_emitted.connect(self.append_record)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `append_record`

```python
def append_record(self, level: int, text: str) -> None
```

Add one log line.

<details>
<summary>Code:</summary>

```python
def append_record(self, level: int, text: str) -> None:
        self._records.append((level, text))
        if len(self._records) > _TERMINAL_MAX_BLOCKS:
            self._records = self._records[-_TERMINAL_MAX_BLOCKS:]
        if level >= self._min_level():
            self.view.append(self._line_html(level, text))
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Remove every line.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._records.clear()
        self.view.clear()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply colors and re-render lines.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.view.setStyleSheet(
            f"QTextBrowser {{ background: {css(palette.card_bg)}; color: {css(palette.text_primary)};"
            f" border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; padding: 4px; }}\n"
            f"{scroll_bar_qss(palette)}",
        )
        self._refilter()
```

</details>

## 🏛️ Class `FluentMarkdownViewer`

```python
class FluentMarkdownViewer(QTextBrowser)
```

Read-only Markdown view with Fluent typography, links, and code blocks.

<details>
<summary>Code:</summary>

```python
class FluentMarkdownViewer(QTextBrowser):

    def __init__(self, parent: QWidget | None = None, *, markdown: str = "") -> None:
        """Create a Markdown viewer."""
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setFrameShape(QTextBrowser.Shape.NoFrame)
        self._markdown = markdown
        bind_theme(self, self.refresh_theme)

    def markdown(self) -> str:
        """Return the shown Markdown source."""
        return self._markdown

    def refresh_theme(self) -> None:
        """Re-apply colors and re-render."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QTextBrowser {{ background: transparent; color: {css(palette.text_primary)}; border: none; }}\n"
            f"{scroll_bar_qss(palette)}"
        )
        code_bg = mix(palette.window_bg, palette.subtle_hover)
        self.document().setDefaultStyleSheet(
            f"a {{ color: {palette.accent_text.name()}; text-decoration: none; }}"
            f" code {{ background-color: {code_bg.name()}; font-family: Consolas, monospace; }}"
            f" pre {{ background-color: {code_bg.name()}; padding: 8px; }}"
            f" h1, h2, h3 {{ font-weight: 600; }}"
            f" blockquote {{ color: {mix(palette.window_bg, palette.text_secondary).name()}; }}",
        )
        self.set_markdown(self._markdown)

    def set_markdown(self, markdown: str) -> None:
        """Render Markdown text."""
        self._markdown = markdown
        self.setMarkdown(markdown)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, markdown: str = '') -> None
```

Create a Markdown viewer.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, markdown: str = "") -> None:
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setFrameShape(QTextBrowser.Shape.NoFrame)
        self._markdown = markdown
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `markdown`

```python
def markdown(self) -> str
```

Return the shown Markdown source.

<details>
<summary>Code:</summary>

```python
def markdown(self) -> str:
        return self._markdown
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply colors and re-render.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QTextBrowser {{ background: transparent; color: {css(palette.text_primary)}; border: none; }}\n"
            f"{scroll_bar_qss(palette)}"
        )
        code_bg = mix(palette.window_bg, palette.subtle_hover)
        self.document().setDefaultStyleSheet(
            f"a {{ color: {palette.accent_text.name()}; text-decoration: none; }}"
            f" code {{ background-color: {code_bg.name()}; font-family: Consolas, monospace; }}"
            f" pre {{ background-color: {code_bg.name()}; padding: 8px; }}"
            f" h1, h2, h3 {{ font-weight: 600; }}"
            f" blockquote {{ color: {mix(palette.window_bg, palette.text_secondary).name()}; }}",
        )
        self.set_markdown(self._markdown)
```

</details>

### ⚙️ Method `set_markdown`

```python
def set_markdown(self, markdown: str) -> None
```

Render Markdown text.

<details>
<summary>Code:</summary>

```python
def set_markdown(self, markdown: str) -> None:
        self._markdown = markdown
        self.setMarkdown(markdown)
```

</details>

## 🏛️ Class `FluentTerminalWidget`

```python
class FluentTerminalWidget(QWidget)
```

Minimal terminal: runs commands through the system shell and shows output.

<details>
<summary>Code:</summary>

```python
class FluentTerminalWidget(QWidget):

    command_finished = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, working_directory: str = "") -> None:
        """Create a terminal view."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(_TERMINAL_MAX_BLOCKS)
        self.output.setFont(_monospace_font(self.font()))
        self.input = FluentLineEdit(self, placeholder="Command", clearable=False)
        self.input.setFont(_monospace_font(self.font()))
        layout.addWidget(self.output, 1)
        layout.addWidget(self.input)
        self._process = QProcess(self)
        if working_directory:
            self._process.setWorkingDirectory(working_directory)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.finished.connect(self._on_finished)
        self.input.returnPressed.connect(self._run_input)
        bind_theme(self, self.refresh_theme)

    def append_text(self, text: str) -> None:
        """Append text to the output."""
        self.output.appendPlainText(text.rstrip("\n"))

    def is_running(self) -> bool:
        """Return whether a command is running."""
        return self._process.state() != QProcess.ProcessState.NotRunning

    def refresh_theme(self) -> None:
        """Re-apply terminal colors."""
        palette = palette_for(self)
        background = QColor("#1e1e1e") if palette.dark else QColor("#fbfbfb")
        self.output.setStyleSheet(
            f"QPlainTextEdit {{ background: {css(background)}; color: {css(palette.text_primary)};"
            f" border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; padding: 6px; }}\n"
            f"{scroll_bar_qss(palette)}",
        )

    def run(self, command: str) -> None:
        """Run `command` in the system shell."""
        if self.is_running() or not command.strip():
            return
        self.append_text(f"> {command}")
        if sys.platform == "win32":
            self._process.start("cmd.exe", ["/c", command])
        else:
            self._process.start("/bin/sh", ["-c", command])

    def stop(self) -> None:
        """Kill the running command."""
        if self.is_running():
            self._process.kill()

    def _on_finished(self, code: int, _status: QProcess.ExitStatus) -> None:
        self.append_text(f"[exit {code}]")
        self.command_finished.emit(code)

    def _read_stderr(self) -> None:
        self.append_text(_decode(bytes(self._process.readAllStandardError().data())))

    def _read_stdout(self) -> None:
        self.append_text(_decode(bytes(self._process.readAllStandardOutput().data())))

    def _run_input(self) -> None:
        command = self.input.text()
        self.input.clear()
        self.run(command)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, working_directory: str = '') -> None
```

Create a terminal view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, working_directory: str = "") -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(_TERMINAL_MAX_BLOCKS)
        self.output.setFont(_monospace_font(self.font()))
        self.input = FluentLineEdit(self, placeholder="Command", clearable=False)
        self.input.setFont(_monospace_font(self.font()))
        layout.addWidget(self.output, 1)
        layout.addWidget(self.input)
        self._process = QProcess(self)
        if working_directory:
            self._process.setWorkingDirectory(working_directory)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.finished.connect(self._on_finished)
        self.input.returnPressed.connect(self._run_input)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `append_text`

```python
def append_text(self, text: str) -> None
```

Append text to the output.

<details>
<summary>Code:</summary>

```python
def append_text(self, text: str) -> None:
        self.output.appendPlainText(text.rstrip("\n"))
```

</details>

### ⚙️ Method `is_running`

```python
def is_running(self) -> bool
```

Return whether a command is running.

<details>
<summary>Code:</summary>

```python
def is_running(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply terminal colors.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        background = QColor("#1e1e1e") if palette.dark else QColor("#fbfbfb")
        self.output.setStyleSheet(
            f"QPlainTextEdit {{ background: {css(background)}; color: {css(palette.text_primary)};"
            f" border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; padding: 6px; }}\n"
            f"{scroll_bar_qss(palette)}",
        )
```

</details>

### ⚙️ Method `run`

```python
def run(self, command: str) -> None
```

Run `command` in the system shell.

<details>
<summary>Code:</summary>

```python
def run(self, command: str) -> None:
        if self.is_running() or not command.strip():
            return
        self.append_text(f"> {command}")
        if sys.platform == "win32":
            self._process.start("cmd.exe", ["/c", command])
        else:
            self._process.start("/bin/sh", ["-c", command])
```

</details>

### ⚙️ Method `stop`

```python
def stop(self) -> None
```

Kill the running command.

<details>
<summary>Code:</summary>

```python
def stop(self) -> None:
        if self.is_running():
            self._process.kill()
```

</details>
