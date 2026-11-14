---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `year_heatmap.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HeatmapCell`](#%EF%B8%8F-class-heatmapcell)
- [🏛️ Class `YearHeatmap`](#%EF%B8%8F-class-yearheatmap)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_calendar`](#%EF%B8%8F-method-set_calendar)
  - [⚙️ Method `set_selected`](#%EF%B8%8F-method-set_selected)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `YearHeatmapStack`](#%EF%B8%8F-class-yearheatmapstack)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `set_selected`](#%EF%B8%8F-method-set_selected-1)
  - [⚙️ Method `set_years`](#%EF%B8%8F-method-set_years)
- [🔧 Function `heatmap_column_count`](#-function-heatmap_column_count)
- [🔧 Function `heatmap_hairline`](#-function-heatmap_hairline)

</details>

## 🏛️ Class `HeatmapCell`

```python
class HeatmapCell
```

One painted day.

<details>
<summary>Code:</summary>

```python
class HeatmapCell:

    day: date
    rect: QRect
    color: str | None
    mark: str
    tip: str
```

</details>

## 🏛️ Class `YearHeatmap`

```python
class YearHeatmap(QWidget)
```

Square-cell calendar for one date range, with a legend that does not stretch.

<details>
<summary>Code:</summary>

```python
class YearHeatmap(QWidget):

    day_clicked = Signal(object)

    def __init__(self, parent: QWidget | None = None, *, show_legend: bool = True) -> None:
        """Build an empty calendar. `set_calendar` supplies the days."""
        super().__init__(parent)
        self.week_starts_on = HEATMAP_WEEK_STARTS_ON
        self.selected_days: set[date] = set()
        self._start: date | None = None
        self._end: date | None = None
        self._colors: dict[date, str | None] = {}
        self._marks: dict[date, str] = {}
        self._tips: dict[date, str] = {}
        self._layout_guard = False
        self._relayout_pending = False
        self._show_legend = show_legend

        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._grid = _Grid(self)
        self._scroll.setWidget(self._grid)
        self._scroll.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self._legend = _Legend(self)
        self._legend.setVisible(show_legend)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._scroll)
        layout.addWidget(self._legend)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        bind_theme(self, self._relayout)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Stay as wide as the column allows. The grid scrolls inside itself."""
        return QSize(0, self._content_height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit square cells to the new width."""
        super().resizeEvent(event)
        self._relayout()
        if self._relayout_pending:
            return
        self._relayout_pending = True
        QTimer.singleShot(0, self._relayout_after_resize)

    def set_calendar(
        self,
        start: date,
        end: date,
        colors: dict[date, str | None],
        *,
        legend: Sequence[tuple[str, str]],
        marks: dict[date, str] | None = None,
        tooltips: dict[date, str] | None = None,
        selected: set[date] | None = None,
        week_starts_on: int | None = None,
    ) -> None:
        """Replace the visible range. `None` colors are no-record outlines."""
        self._start = start
        self._end = end
        self._colors = colors
        self._marks = dict(marks or {})
        self._tips = dict(tooltips or {})
        self.selected_days = set(selected or ())
        if week_starts_on is not None:
            self.week_starts_on = week_starts_on
        self._legend.set_items(legend)
        self._relayout()

    def set_selected(self, days: set[date]) -> None:
        """Move the contrast outline without rebuilding the calendar."""
        self.selected_days = set(days)
        self._grid.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Report the calendar height without adopting the scrolled grid width."""
        return QSize(_FALLBACK_WIDTH, self._content_height())

    def _content_height(self) -> int:
        layout = self.layout()
        spacing = layout.spacing() if layout is not None else 0
        legend_h = self._legend.sizeHint().height() if self._show_legend else 0
        scroll_h = self._scroll.height()
        if scroll_h < _MONTH_LABEL_H + _CELL_MIN:
            scroll_h = _MONTH_LABEL_H + 7 * (_CELL_MIN + _CELL_GAP) + _PAD * 2
        return scroll_h + legend_h + spacing

    def _relayout(self) -> None:
        if self._layout_guard or self._start is None or self._end is None:
            return
        self._layout_guard = True
        try:
            months = habit_heatmap_month_ranges(self._start, self._end)
            columns = [
                habit_heatmap_month_column_count(month_start, month_end, week_starts_on=self.week_starts_on)
                for month_start, month_end in months
            ]
            viewport = max(self.width(), self._scroll.viewport().width())
            if viewport < _VIEWPORT_FALLBACK:
                viewport = _FALLBACK_WIDTH
            cell, _scrolling = _cell_size(viewport, sum(columns), len(months))
            cells, month_labels, width, height = _place_cells(
                self._start,
                self._end,
                cell=cell,
                colors=self._colors,
                marks=self._marks,
                tips=self._tips,
                week_starts_on=self.week_starts_on,
            )
            self._grid.set_scene(cells, month_labels, width, height)
            bar = self._scroll.horizontalScrollBar().sizeHint().height() if width > viewport + 1 else 0
            self._scroll.setFixedHeight(height + bar)
            self.updateGeometry()
        finally:
            self._layout_guard = False

    def _relayout_after_resize(self) -> None:
        self._relayout_pending = False
        self._relayout()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, show_legend: bool = True) -> None
```

Build an empty calendar. [`set_calendar`](#%EF%B8%8F-method-set_calendar) supplies the days.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, show_legend: bool = True) -> None:
        super().__init__(parent)
        self.week_starts_on = HEATMAP_WEEK_STARTS_ON
        self.selected_days: set[date] = set()
        self._start: date | None = None
        self._end: date | None = None
        self._colors: dict[date, str | None] = {}
        self._marks: dict[date, str] = {}
        self._tips: dict[date, str] = {}
        self._layout_guard = False
        self._relayout_pending = False
        self._show_legend = show_legend

        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._grid = _Grid(self)
        self._scroll.setWidget(self._grid)
        self._scroll.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self._legend = _Legend(self)
        self._legend.setVisible(show_legend)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._scroll)
        layout.addWidget(self._legend)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        bind_theme(self, self._relayout)
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Stay as wide as the column allows. The grid scrolls inside itself.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(0, self._content_height())
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Refit square cells to the new width.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._relayout()
        if self._relayout_pending:
            return
        self._relayout_pending = True
        QTimer.singleShot(0, self._relayout_after_resize)
```

</details>

### ⚙️ Method `set_calendar`

```python
def set_calendar(self, start: date, end: date, colors: dict[date, str | None], *, legend: Sequence[tuple[str, str]], marks: dict[date, str] | None = None, tooltips: dict[date, str] | None = None, selected: set[date] | None = None, week_starts_on: int | None = None) -> None
```

Replace the visible range. `None` colors are no-record outlines.

<details>
<summary>Code:</summary>

```python
def set_calendar(
        self,
        start: date,
        end: date,
        colors: dict[date, str | None],
        *,
        legend: Sequence[tuple[str, str]],
        marks: dict[date, str] | None = None,
        tooltips: dict[date, str] | None = None,
        selected: set[date] | None = None,
        week_starts_on: int | None = None,
    ) -> None:
        self._start = start
        self._end = end
        self._colors = colors
        self._marks = dict(marks or {})
        self._tips = dict(tooltips or {})
        self.selected_days = set(selected or ())
        if week_starts_on is not None:
            self.week_starts_on = week_starts_on
        self._legend.set_items(legend)
        self._relayout()
```

</details>

### ⚙️ Method `set_selected`

```python
def set_selected(self, days: set[date]) -> None
```

Move the contrast outline without rebuilding the calendar.

<details>
<summary>Code:</summary>

```python
def set_selected(self, days: set[date]) -> None:
        self.selected_days = set(days)
        self._grid.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Report the calendar height without adopting the scrolled grid width.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_FALLBACK_WIDTH, self._content_height())
```

</details>

## 🏛️ Class `YearHeatmapStack`

```python
class YearHeatmapStack(QWidget)
```

Many year calendars stacked newest-first, with vertical scroll and one legend.

<details>
<summary>Code:</summary>

```python
class YearHeatmapStack(QWidget):

    day_clicked = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build an empty stack. Call `set_years` to fill it."""
        super().__init__(parent)
        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._body = QWidget(self._scroll)
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(12)
        self._scroll.setWidget(self._body)
        self._legend = _Legend(self)
        self._rows: list[tuple[QLabel, YearHeatmap]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._scroll, stretch=1)
        layout.addWidget(self._legend, stretch=0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_selected(self, days: set[date]) -> None:
        """Update selection outlines on every visible year band."""
        for _label, heatmap in self._rows:
            heatmap.set_selected(days)

    def set_years(
        self,
        years: Sequence[tuple[int, date, date]],
        colors: dict[date, str | None],
        *,
        legend: Sequence[tuple[str, str]],
        marks: dict[date, str] | None = None,
        tooltips: dict[date, str] | None = None,
        selected: set[date] | None = None,
        week_starts_on: int | None = None,
    ) -> None:
        """Stack year calendars newest-first; each band is labeled with its year."""
        self._clear_rows()
        self._legend.set_items(legend)
        for year, start, end in years:
            label = QLabel(str(year), self._body)
            font = label.font()
            font.setBold(True)
            label.setFont(font)
            self._body_layout.addWidget(label, stretch=0)
            heatmap = YearHeatmap(self._body, show_legend=False)
            heatmap.day_clicked.connect(self.day_clicked.emit)
            heatmap.set_calendar(
                start,
                end,
                colors,
                legend=(),
                marks=marks,
                tooltips=tooltips,
                selected=selected,
                week_starts_on=week_starts_on,
            )
            self._body_layout.addWidget(heatmap, stretch=0)
            self._rows.append((label, heatmap))
        self._body_layout.addStretch(1)
        self.updateGeometry()

    def _clear_rows(self) -> None:
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self._rows.clear()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build an empty stack. Call `set_years` to fill it.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._body = QWidget(self._scroll)
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(12)
        self._scroll.setWidget(self._body)
        self._legend = _Legend(self)
        self._rows: list[tuple[QLabel, YearHeatmap]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._scroll, stretch=1)
        layout.addWidget(self._legend, stretch=0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
```

</details>

### ⚙️ Method `set_selected`

```python
def set_selected(self, days: set[date]) -> None
```

Update selection outlines on every visible year band.

<details>
<summary>Code:</summary>

```python
def set_selected(self, days: set[date]) -> None:
        for _label, heatmap in self._rows:
            heatmap.set_selected(days)
```

</details>

### ⚙️ Method `set_years`

```python
def set_years(self, years: Sequence[tuple[int, date, date]], colors: dict[date, str | None], *, legend: Sequence[tuple[str, str]], marks: dict[date, str] | None = None, tooltips: dict[date, str] | None = None, selected: set[date] | None = None, week_starts_on: int | None = None) -> None
```

Stack year calendars newest-first; each band is labeled with its year.

<details>
<summary>Code:</summary>

```python
def set_years(
        self,
        years: Sequence[tuple[int, date, date]],
        colors: dict[date, str | None],
        *,
        legend: Sequence[tuple[str, str]],
        marks: dict[date, str] | None = None,
        tooltips: dict[date, str] | None = None,
        selected: set[date] | None = None,
        week_starts_on: int | None = None,
    ) -> None:
        self._clear_rows()
        self._legend.set_items(legend)
        for year, start, end in years:
            label = QLabel(str(year), self._body)
            font = label.font()
            font.setBold(True)
            label.setFont(font)
            self._body_layout.addWidget(label, stretch=0)
            heatmap = YearHeatmap(self._body, show_legend=False)
            heatmap.day_clicked.connect(self.day_clicked.emit)
            heatmap.set_calendar(
                start,
                end,
                colors,
                legend=(),
                marks=marks,
                tooltips=tooltips,
                selected=selected,
                week_starts_on=week_starts_on,
            )
            self._body_layout.addWidget(heatmap, stretch=0)
            self._rows.append((label, heatmap))
        self._body_layout.addStretch(1)
        self.updateGeometry()
```

</details>

## 🔧 Function `heatmap_column_count`

```python
def heatmap_column_count(start: date, end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int
```

Return week columns for `[start, end]`, without assuming 52 columns.

<details>
<summary>Code:</summary>

```python
def heatmap_column_count(start: date, end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int:
    return sum(
        habit_heatmap_month_column_count(month_start, month_end, week_starts_on=week_starts_on)
        for month_start, month_end in habit_heatmap_month_ranges(start, end)
    )
```

</details>

## 🔧 Function `heatmap_hairline`

```python
def heatmap_hairline() -> str
```

Return the outline used for days with no record.

<details>
<summary>Code:</summary>

```python
def heatmap_hairline() -> str:
    palette = FluentTheme.instance().palette()
    return chart_tint(chart_surface(), palette.text_secondary, 0.28).name()
```

</details>
