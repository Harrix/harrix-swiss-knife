---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `line_edit.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LineEditSpellController`](#%EF%B8%8F-class-lineeditspellcontroller)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `detach`](#%EF%B8%8F-method-detach)
  - [⚙️ Method `misspellings`](#%EF%B8%8F-method-misspellings)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)

</details>

## 🏛️ Class `LineEditSpellController`

```python
class LineEditSpellController(QObject)
```

Debounced misspelling ranges and post-paint wave underlines for a line edit.

<details>
<summary>Code:</summary>

```python
class LineEditSpellController(QObject):

    def __init__(self, line_edit: QLineEdit, engine: SpellEngine | None = None) -> None:
        """Attach to `line_edit`; owns a debounce timer for `textChanged`."""
        super().__init__(line_edit)
        self._line_edit = line_edit
        self._engine = engine if engine is not None else get_spell_engine()
        self._misspellings: list[tuple[int, int]] = []
        self._original_paint = line_edit.paintEvent
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(self._recompute)
        line_edit.textChanged.connect(self._schedule)
        line_edit.paintEvent = self._paint_event  # type: ignore[method-assign]
        self._recompute()

    def detach(self) -> None:
        """Restore the original `paintEvent` and stop listening."""
        self._timer.stop()
        with contextlib.suppress(TypeError, RuntimeError):
            self._line_edit.textChanged.disconnect(self._schedule)
        self._line_edit.paintEvent = self._original_paint  # type: ignore[method-assign]
        self._misspellings.clear()
        self._line_edit.update()

    def misspellings(self) -> list[tuple[int, int]]:
        """Return current `[start, end)` misspelled spans."""
        return list(self._misspellings)

    def refresh(self) -> None:
        """Recompute misspellings immediately (e.g. after Add to dictionary)."""
        self._timer.stop()
        self._recompute()

    def _draw_underlines(self, painter: QPainter) -> None:
        line_edit = self._line_edit
        text = line_edit.text()
        if not text:
            return
        option = QStyleOptionFrame()
        line_edit.initStyleOption(option)
        contents = line_edit.style().subElementRect(QStyle.SubElement.SE_LineEditContents, option, line_edit)
        margins = line_edit.textMargins()
        left = contents.left() + margins.left()
        fm = line_edit.fontMetrics()
        scroll_x = _line_edit_scroll_x(line_edit, contents.x() + margins.left())
        underline_y = _line_edit_underline_y(line_edit, contents, margins.top(), margins.bottom(), fm)
        painter.setClipRect(contents)
        painter.setPen(QPen(_WAVE_COLOR, 1))
        for start, end in self._misspellings:
            x1 = left + fm.horizontalAdvance(text[:start]) - scroll_x
            x2 = left + fm.horizontalAdvance(text[:end]) - scroll_x
            if x2 <= contents.left() or x1 >= contents.right():
                continue
            x1 = max(x1, float(contents.left()))
            x2 = min(x2, float(contents.right()))
            _draw_wave(painter, x1, x2, float(underline_y))

    def _paint_event(self, event: object) -> None:
        self._original_paint(event)
        if not self._misspellings:
            return
        painter = QPainter(self._line_edit)
        if not painter.isActive():
            return
        try:
            self._draw_underlines(painter)
        finally:
            painter.end()

    def _recompute(self) -> None:
        text = self._line_edit.text()
        engine = self._engine
        spans = [(start, end) for start, end, word in iter_word_spans(text) if not engine.lookup(word)]
        self._misspellings = spans
        self._line_edit.update()

    def _schedule(self, _text: str = "") -> None:
        self._timer.start()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, line_edit: QLineEdit, engine: SpellEngine | None = None) -> None
```

Attach to `line_edit`; owns a debounce timer for `textChanged`.

<details>
<summary>Code:</summary>

```python
def __init__(self, line_edit: QLineEdit, engine: SpellEngine | None = None) -> None:
        super().__init__(line_edit)
        self._line_edit = line_edit
        self._engine = engine if engine is not None else get_spell_engine()
        self._misspellings: list[tuple[int, int]] = []
        self._original_paint = line_edit.paintEvent
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(self._recompute)
        line_edit.textChanged.connect(self._schedule)
        line_edit.paintEvent = self._paint_event  # type: ignore[method-assign]
        self._recompute()
```

</details>

### ⚙️ Method `detach`

```python
def detach(self) -> None
```

Restore the original `paintEvent` and stop listening.

<details>
<summary>Code:</summary>

```python
def detach(self) -> None:
        self._timer.stop()
        with contextlib.suppress(TypeError, RuntimeError):
            self._line_edit.textChanged.disconnect(self._schedule)
        self._line_edit.paintEvent = self._original_paint  # type: ignore[method-assign]
        self._misspellings.clear()
        self._line_edit.update()
```

</details>

### ⚙️ Method `misspellings`

```python
def misspellings(self) -> list[tuple[int, int]]
```

Return current `[start, end)` misspelled spans.

<details>
<summary>Code:</summary>

```python
def misspellings(self) -> list[tuple[int, int]]:
        return list(self._misspellings)
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self) -> None
```

Recompute misspellings immediately (e.g. after Add to dictionary).

<details>
<summary>Code:</summary>

```python
def refresh(self) -> None:
        self._timer.stop()
        self._recompute()
```

</details>
