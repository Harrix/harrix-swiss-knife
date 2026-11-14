---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChartCard`](#%EF%B8%8F-class-chartcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `actions_layout`](#%EF%B8%8F-method-actions_layout)
  - [⚙️ Method `body_layout`](#%EF%B8%8F-method-body_layout)
  - [⚙️ Method `set_subtitle`](#%EF%B8%8F-method-set_subtitle)
  - [⚙️ Method `set_title`](#%EF%B8%8F-method-set_title)
- [🏛️ Class `ChartPage`](#%EF%B8%8F-class-chartpage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `set_main`](#%EF%B8%8F-method-set_main)
  - [⚙️ Method `set_toolbar`](#%EF%B8%8F-method-set_toolbar)
- [🏛️ Class `ChartSidebar`](#%EF%B8%8F-class-chartsidebar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `add_section`](#%EF%B8%8F-method-add_section)
  - [⚙️ Method `polish_list`](#%EF%B8%8F-method-polish_list)
- [🏛️ Class `KpiCard`](#%EF%B8%8F-class-kpicard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `set_metric`](#%EF%B8%8F-method-set_metric)
- [🏛️ Class `KpiRow`](#%EF%B8%8F-class-kpirow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `set_metrics`](#%EF%B8%8F-method-set_metrics)
- [🏛️ Class `KpiSpec`](#%EF%B8%8F-class-kpispec)
- [🏛️ Class `YearNavigator`](#%EF%B8%8F-class-yearnavigator)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `selection`](#%EF%B8%8F-method-selection)
  - [⚙️ Method `set_years`](#%EF%B8%8F-method-set_years)
  - [⚙️ Method `step`](#%EF%B8%8F-method-step)
  - [⚙️ Method `year`](#%EF%B8%8F-method-year)
- [🔧 Function `apply_chart_list_chrome`](#-function-apply_chart_list_chrome)
- [🔧 Function `kpi_row_limits`](#-function-kpi_row_limits)
- [🔧 Function `mark_chart_list_separator`](#-function-mark_chart_list_separator)

</details>

## 🏛️ Class `ChartCard`

```python
class ChartCard(FluentCard)
```

Bordered chart card with the title in the header, not inside Matplotlib.

<details>
<summary>Code:</summary>

```python
class ChartCard(FluentCard):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty card. Put the canvas in `body_layout`."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        root.setSpacing(SPACE_S)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        titles = QVBoxLayout()
        titles.setSpacing(SPACE_XS)
        self._title = FluentText("", self, style=TextStyle.BODY_STRONG)
        self._subtitle = CaptionLabel("", self)
        self._subtitle.hide()
        titles.addWidget(self._title)
        titles.addWidget(self._subtitle)
        header.addLayout(titles, stretch=1)
        self._actions = QHBoxLayout()
        self._actions.setSpacing(SPACE_S)
        header.addLayout(self._actions)
        root.addLayout(header)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)
        root.addLayout(self._body, stretch=1)

    def actions_layout(self) -> QHBoxLayout:
        """Return the header slot for a legend or Copy / Save actions."""
        return self._actions

    def body_layout(self) -> QVBoxLayout:
        """Return the layout that should hold the chart canvas."""
        return self._body

    def set_subtitle(self, text: str) -> None:
        """Set the muted line under the title (period, units). Empty hides it."""
        self._subtitle.setText(text)
        self._subtitle.setVisible(bool(text))

    def set_title(self, text: str) -> None:
        """Set the 14px semibold card title."""
        self._title.setText(text)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty card. Put the canvas in [`body_layout`](#%EF%B8%8F-method-body_layout).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        root.setSpacing(SPACE_S)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        titles = QVBoxLayout()
        titles.setSpacing(SPACE_XS)
        self._title = FluentText("", self, style=TextStyle.BODY_STRONG)
        self._subtitle = CaptionLabel("", self)
        self._subtitle.hide()
        titles.addWidget(self._title)
        titles.addWidget(self._subtitle)
        header.addLayout(titles, stretch=1)
        self._actions = QHBoxLayout()
        self._actions.setSpacing(SPACE_S)
        header.addLayout(self._actions)
        root.addLayout(header)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)
        root.addLayout(self._body, stretch=1)
```

</details>

### ⚙️ Method `actions_layout`

```python
def actions_layout(self) -> QHBoxLayout
```

Return the header slot for a legend or Copy / Save actions.

<details>
<summary>Code:</summary>

```python
def actions_layout(self) -> QHBoxLayout:
        return self._actions
```

</details>

### ⚙️ Method `body_layout`

```python
def body_layout(self) -> QVBoxLayout
```

Return the layout that should hold the chart canvas.

<details>
<summary>Code:</summary>

```python
def body_layout(self) -> QVBoxLayout:
        return self._body
```

</details>

### ⚙️ Method `set_subtitle`

```python
def set_subtitle(self, text: str) -> None
```

Set the muted line under the title (period, units). Empty hides it.

<details>
<summary>Code:</summary>

```python
def set_subtitle(self, text: str) -> None:
        self._subtitle.setText(text)
        self._subtitle.setVisible(bool(text))
```

</details>

### ⚙️ Method `set_title`

```python
def set_title(self, text: str) -> None
```

Set the 14px semibold card title.

<details>
<summary>Code:</summary>

```python
def set_title(self, text: str) -> None:
        self._title.setText(text)
```

</details>

## 🏛️ Class `ChartPage`

```python
class ChartPage(QWidget)
```

Sidebar plus toolbar, KPI row, main chart, and a bottom detail row.

The bottom row is about two fifths of the page and at least 240 px.
The page scrolls when the window is shorter than the content.

<details>
<summary>Code:</summary>

```python
class ChartPage(QWidget):

    def __init__(self, parent: QWidget | None = None, *, settings_key: str = "") -> None:
        """Build the empty shell. `settings_key` persists the sidebar width."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        outer.setSpacing(SPACE_M)

        self.sidebar = ChartSidebar(self)
        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.addWidget(self.sidebar)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget(scroll)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        column = QVBoxLayout(content)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(SPACE_M)

        self._toolbar_host = QVBoxLayout()
        self._toolbar_host.setContentsMargins(0, 0, 0, 0)
        column.addLayout(self._toolbar_host)

        self.kpi_row = KpiRow(content)
        column.addWidget(self.kpi_row)

        self._main_host = QVBoxLayout()
        self._main_host.setContentsMargins(0, 0, 0, 0)
        column.addLayout(self._main_host, stretch=3)

        self.bottom = QSplitter(Qt.Orientation.Horizontal, content)
        self.bottom.setChildrenCollapsible(False)
        self.bottom.setMinimumHeight(_BOTTOM_MIN_HEIGHT)
        column.addWidget(self.bottom, stretch=2)

        scroll.setWidget(content)
        self._splitter.addWidget(scroll)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        outer.addWidget(self._splitter)

        self._settings_key = settings_key
        self._apply_sidebar_width()
        if settings_key:
            self._splitter.splitterMoved.connect(self._save_sidebar_width)

    def set_main(self, widget: QWidget) -> None:
        """Replace the main chart widget."""
        self._swap(self._main_host, widget)

    def set_toolbar(self, widget: QWidget) -> None:
        """Replace the toolbar widget."""
        self._swap(self._toolbar_host, widget)

    def _apply_sidebar_width(self) -> None:
        default = [_SIDEBAR_DEFAULT, 1000]
        sizes = load_splitter_sizes(self._settings_key, default) if self._settings_key else list(default)
        width = max(_SIDEBAR_MIN, min(_SIDEBAR_MAX, sizes[0]))
        self._splitter.setSizes([width, max(sizes[1], 1)])

    def _save_sidebar_width(self, *_args: object) -> None:
        if not self._settings_key:
            return
        sizes = self._splitter.sizes()
        if len(sizes) < _SPLITTER_PANES:
            return
        width = max(_SIDEBAR_MIN, min(_SIDEBAR_MAX, sizes[0]))
        save_splitter_sizes(self._settings_key, [width, sizes[1]], [_SIDEBAR_DEFAULT, 1000])

    @staticmethod
    def _swap(layout: QVBoxLayout, widget: QWidget) -> None:
        while layout.count():
            item = layout.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        layout.addWidget(widget)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, settings_key: str = '') -> None
```

Build the empty shell. `settings_key` persists the sidebar width.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, settings_key: str = "") -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        outer.setSpacing(SPACE_M)

        self.sidebar = ChartSidebar(self)
        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.addWidget(self.sidebar)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget(scroll)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        column = QVBoxLayout(content)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(SPACE_M)

        self._toolbar_host = QVBoxLayout()
        self._toolbar_host.setContentsMargins(0, 0, 0, 0)
        column.addLayout(self._toolbar_host)

        self.kpi_row = KpiRow(content)
        column.addWidget(self.kpi_row)

        self._main_host = QVBoxLayout()
        self._main_host.setContentsMargins(0, 0, 0, 0)
        column.addLayout(self._main_host, stretch=3)

        self.bottom = QSplitter(Qt.Orientation.Horizontal, content)
        self.bottom.setChildrenCollapsible(False)
        self.bottom.setMinimumHeight(_BOTTOM_MIN_HEIGHT)
        column.addWidget(self.bottom, stretch=2)

        scroll.setWidget(content)
        self._splitter.addWidget(scroll)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        outer.addWidget(self._splitter)

        self._settings_key = settings_key
        self._apply_sidebar_width()
        if settings_key:
            self._splitter.splitterMoved.connect(self._save_sidebar_width)
```

</details>

### ⚙️ Method `set_main`

```python
def set_main(self, widget: QWidget) -> None
```

Replace the main chart widget.

<details>
<summary>Code:</summary>

```python
def set_main(self, widget: QWidget) -> None:
        self._swap(self._main_host, widget)
```

</details>

### ⚙️ Method `set_toolbar`

```python
def set_toolbar(self, widget: QWidget) -> None
```

Replace the toolbar widget.

<details>
<summary>Code:</summary>

```python
def set_toolbar(self, widget: QWidget) -> None:
        self._swap(self._toolbar_host, widget)
```

</details>

## 🏛️ Class `ChartSidebar`

```python
class ChartSidebar(QWidget)
```

Filter column: section titles without colons, lists elide with a tooltip.

<details>
<summary>Code:</summary>

```python
class ChartSidebar(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a sidebar clamped to 220-420 px."""
        super().__init__(parent)
        self.setMinimumWidth(_SIDEBAR_MIN)
        self.setMaximumWidth(_SIDEBAR_MAX)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        self._layout.setSpacing(SPACE_S)
        self._layout.addStretch(1)

    def add_section(self, title: str) -> QVBoxLayout:
        """Add a section title and return a layout for its controls.

        A trailing colon on `title` is dropped. The returned layout already
        contains the title label.

        """
        clean = title.strip().removesuffix(":").strip()
        block = QWidget(self)
        host = QVBoxLayout(block)
        host.setContentsMargins(0, 0, 0, 0)
        host.setSpacing(SPACE_XS)
        host.addWidget(FluentText(clean, block, style=TextStyle.BODY_STRONG))
        insert_at = max(self._layout.count() - 1, 0)
        self._layout.insertWidget(insert_at, block)
        return host

    def polish_list(self, view: QListView) -> None:
        """Elide long names, show the full text on hover, and use Fluent selection."""
        view.setTextElideMode(Qt.TextElideMode.ElideRight)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFrameShape(QFrame.Shape.NoFrame)
        tip = _ListElideTip(view)
        view.viewport().installEventFilter(tip)
        view.setProperty("_hsk_elide_tip", tip)
        apply_chart_list_chrome(view)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a sidebar clamped to 220-420 px.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(_SIDEBAR_MIN)
        self.setMaximumWidth(_SIDEBAR_MAX)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        self._layout.setSpacing(SPACE_S)
        self._layout.addStretch(1)
```

</details>

### ⚙️ Method `add_section`

```python
def add_section(self, title: str) -> QVBoxLayout
```

Add a section title and return a layout for its controls.

A trailing colon on `title` is dropped. The returned layout already
contains the title label.

<details>
<summary>Code:</summary>

```python
def add_section(self, title: str) -> QVBoxLayout:
        clean = title.strip().removesuffix(":").strip()
        block = QWidget(self)
        host = QVBoxLayout(block)
        host.setContentsMargins(0, 0, 0, 0)
        host.setSpacing(SPACE_XS)
        host.addWidget(FluentText(clean, block, style=TextStyle.BODY_STRONG))
        insert_at = max(self._layout.count() - 1, 0)
        self._layout.insertWidget(insert_at, block)
        return host
```

</details>

### ⚙️ Method `polish_list`

```python
def polish_list(self, view: QListView) -> None
```

Elide long names, show the full text on hover, and use Fluent selection.

<details>
<summary>Code:</summary>

```python
def polish_list(self, view: QListView) -> None:
        view.setTextElideMode(Qt.TextElideMode.ElideRight)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFrameShape(QFrame.Shape.NoFrame)
        tip = _ListElideTip(view)
        view.viewport().installEventFilter(tip)
        view.setProperty("_hsk_elide_tip", tip)
        apply_chart_list_chrome(view)
```

</details>

## 🏛️ Class `KpiCard`

```python
class KpiCard(FluentCard)
```

One metric: muted caption, large value, optional trend line and icon.

<details>
<summary>Code:</summary>

```python
class KpiCard(FluentCard):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty metric card."""
        super().__init__(parent)
        self._trend = "flat"
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(88)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_S, SPACE_M, SPACE_S)
        root.setSpacing(SPACE_XS)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._icon = QLabel(self)
        self._icon.setFixedSize(16, 16)
        self._icon.hide()
        self._caption = CaptionLabel("", self)
        header.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self._caption, stretch=1)
        root.addLayout(header)

        self._value = FluentText("", self, style=TextStyle.TITLE)
        root.addWidget(self._value)
        self._detail = CaptionLabel("", self)
        self._detail.hide()
        root.addWidget(self._detail)
        bind_theme(self, self._apply_trend_color)

    def set_metric(
        self,
        caption: str,
        value: str,
        *,
        detail: str = "",
        trend: str = "flat",
        icon: str = "",
    ) -> None:
        """Show one KPI. `trend` is `up`, `down`, or `flat`."""
        self._caption.setText(caption)
        self._value.setText(value)
        self._detail.setText(detail)
        self._detail.setVisible(bool(detail))
        self._trend = trend if trend in {"up", "down", "flat"} else "flat"
        if icon:
            palette = palette_for(self)
            qicon = create_lucide_icon(icon, 16, color=mix(palette.window_bg, palette.text_secondary))
            self._icon.setPixmap(qicon.pixmap(16, 16))
            self._icon.show()
        else:
            self._icon.hide()
        self._apply_trend_color()

    def _apply_trend_color(self) -> None:
        palette = palette_for(self)
        color = {
            "up": palette.success,
            "down": palette.critical,
            "flat": palette.text_secondary,
        }[self._trend]
        ink = mix(palette.window_bg, color)
        self._detail.setStyleSheet(f"QLabel {{ color: {css(ink)}; background: transparent; }}")
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty metric card.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trend = "flat"
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(88)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_S, SPACE_M, SPACE_S)
        root.setSpacing(SPACE_XS)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._icon = QLabel(self)
        self._icon.setFixedSize(16, 16)
        self._icon.hide()
        self._caption = CaptionLabel("", self)
        header.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self._caption, stretch=1)
        root.addLayout(header)

        self._value = FluentText("", self, style=TextStyle.TITLE)
        root.addWidget(self._value)
        self._detail = CaptionLabel("", self)
        self._detail.hide()
        root.addWidget(self._detail)
        bind_theme(self, self._apply_trend_color)
```

</details>

### ⚙️ Method `set_metric`

```python
def set_metric(self, caption: str, value: str, *, detail: str = '', trend: str = 'flat', icon: str = '') -> None
```

Show one KPI. `trend` is `up`, `down`, or `flat`.

<details>
<summary>Code:</summary>

```python
def set_metric(
        self,
        caption: str,
        value: str,
        *,
        detail: str = "",
        trend: str = "flat",
        icon: str = "",
    ) -> None:
        self._caption.setText(caption)
        self._value.setText(value)
        self._detail.setText(detail)
        self._detail.setVisible(bool(detail))
        self._trend = trend if trend in {"up", "down", "flat"} else "flat"
        if icon:
            palette = palette_for(self)
            qicon = create_lucide_icon(icon, 16, color=mix(palette.window_bg, palette.text_secondary))
            self._icon.setPixmap(qicon.pixmap(16, 16))
            self._icon.show()
        else:
            self._icon.hide()
        self._apply_trend_color()
```

</details>

## 🏛️ Class `KpiRow`

```python
class KpiRow(QWidget)
```

Three to six equal-width KPI cards.

<details>
<summary>Code:</summary>

```python
class KpiRow(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty row."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACE_M)
        self._cards: list[KpiCard] = []
        self.hide()

    def set_metrics(self, specs: list[KpiSpec]) -> None:
        """Replace the row. Extra specs beyond six are dropped."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._cards.clear()
        for spec in specs[:_KPI_MAX]:
            card = KpiCard(self)
            card.set_metric(spec.caption, spec.value, detail=spec.detail, trend=spec.trend, icon=spec.icon)
            self._layout.addWidget(card, stretch=1)
            self._cards.append(card)
        self.setVisible(len(self._cards) >= 1)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty row.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACE_M)
        self._cards: list[KpiCard] = []
        self.hide()
```

</details>

### ⚙️ Method `set_metrics`

```python
def set_metrics(self, specs: list[KpiSpec]) -> None
```

Replace the row. Extra specs beyond six are dropped.

<details>
<summary>Code:</summary>

```python
def set_metrics(self, specs: list[KpiSpec]) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._cards.clear()
        for spec in specs[:_KPI_MAX]:
            card = KpiCard(self)
            card.set_metric(spec.caption, spec.value, detail=spec.detail, trend=spec.trend, icon=spec.icon)
            self._layout.addWidget(card, stretch=1)
            self._cards.append(card)
        self.setVisible(len(self._cards) >= 1)
```

</details>

## 🏛️ Class `KpiSpec`

```python
class KpiSpec
```

One KPI card: caption, value, optional detail line and Lucide icon.

<details>
<summary>Code:</summary>

```python
class KpiSpec:

    caption: str
    value: str
    detail: str = ""
    trend: str = "flat"
    icon: str = ""
```

</details>

## 🏛️ Class `YearNavigator`

```python
class YearNavigator(QWidget)
```

Compact previous / next control for Last 365 days, years, and All years.

Items are Last 365 days, calendar years newest first, then All years.
The arrows move to the neighboring item.

<details>
<summary>Code:</summary>

```python
class YearNavigator(QWidget):

    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the control with Last 365 days and All years."""
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_S)
        self._previous = make_lucide_push_button("", "chevron-left")
        self._previous.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._previous.setStyleSheet(button_idle_qss())
        self._previous.clicked.connect(lambda: self.step(-1))
        self._combo = QComboBox(self)
        self._combo.setMinimumHeight(CONTROL_HEIGHT)
        self._combo.currentIndexChanged.connect(self._on_index)
        self._next = make_lucide_push_button("", "chevron-right")
        self._next.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._next.setStyleSheet(button_idle_qss())
        self._next.clicked.connect(lambda: self.step(1))
        layout.addWidget(self._previous)
        layout.addWidget(self._combo)
        layout.addWidget(self._next)
        self.set_years([])

    def selection(self) -> str:
        """Return `last_365`, `all`, or a four-digit year string."""
        data = self._combo.currentData()
        if data is None:
            return LAST_365_KEY
        return str(data)

    def set_years(self, years: list[int]) -> None:
        """Replace the year items. Order in the combo is newest first."""
        current = self.selection()
        unique = sorted({int(year) for year in years}, reverse=True)
        self._combo.blockSignals(True)  # noqa: FBT003
        self._combo.clear()
        self._combo.addItem("Last 365 days", LAST_365_KEY)
        for year in unique:
            self._combo.addItem(str(year), str(year))
        self._combo.addItem("All years", ALL_YEARS_KEY)
        restored = self._combo.findData(current)
        self._combo.setCurrentIndex(max(restored, 0))
        self._combo.blockSignals(False)  # noqa: FBT003
        self._sync_arrows()

    def step(self, delta: int) -> None:
        """Move to the neighboring item. `delta` is `-1` or `1`."""
        index = self._combo.currentIndex() + delta
        if 0 <= index < self._combo.count():
            self._combo.setCurrentIndex(index)

    def year(self) -> int | None:
        """Return the selected calendar year, or `None` for Last 365 days and All years."""
        key = self.selection()
        if key in {LAST_365_KEY, ALL_YEARS_KEY}:
            return None
        try:
            return int(key)
        except ValueError:
            return None

    def _on_index(self, _index: int) -> None:
        self._sync_arrows()
        self.changed.emit()

    def _sync_arrows(self) -> None:
        index = self._combo.currentIndex()
        self._previous.setEnabled(index > 0)
        self._next.setEnabled(index < self._combo.count() - 1)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create the control with Last 365 days and All years.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_S)
        self._previous = make_lucide_push_button("", "chevron-left")
        self._previous.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._previous.setStyleSheet(button_idle_qss())
        self._previous.clicked.connect(lambda: self.step(-1))
        self._combo = QComboBox(self)
        self._combo.setMinimumHeight(CONTROL_HEIGHT)
        self._combo.currentIndexChanged.connect(self._on_index)
        self._next = make_lucide_push_button("", "chevron-right")
        self._next.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._next.setStyleSheet(button_idle_qss())
        self._next.clicked.connect(lambda: self.step(1))
        layout.addWidget(self._previous)
        layout.addWidget(self._combo)
        layout.addWidget(self._next)
        self.set_years([])
```

</details>

### ⚙️ Method `selection`

```python
def selection(self) -> str
```

Return `last_365`, `all`, or a four-digit year string.

<details>
<summary>Code:</summary>

```python
def selection(self) -> str:
        data = self._combo.currentData()
        if data is None:
            return LAST_365_KEY
        return str(data)
```

</details>

### ⚙️ Method `set_years`

```python
def set_years(self, years: list[int]) -> None
```

Replace the year items. Order in the combo is newest first.

<details>
<summary>Code:</summary>

```python
def set_years(self, years: list[int]) -> None:
        current = self.selection()
        unique = sorted({int(year) for year in years}, reverse=True)
        self._combo.blockSignals(True)  # noqa: FBT003
        self._combo.clear()
        self._combo.addItem("Last 365 days", LAST_365_KEY)
        for year in unique:
            self._combo.addItem(str(year), str(year))
        self._combo.addItem("All years", ALL_YEARS_KEY)
        restored = self._combo.findData(current)
        self._combo.setCurrentIndex(max(restored, 0))
        self._combo.blockSignals(False)  # noqa: FBT003
        self._sync_arrows()
```

</details>

### ⚙️ Method `step`

```python
def step(self, delta: int) -> None
```

Move to the neighboring item. `delta` is `-1` or `1`.

<details>
<summary>Code:</summary>

```python
def step(self, delta: int) -> None:
        index = self._combo.currentIndex() + delta
        if 0 <= index < self._combo.count():
            self._combo.setCurrentIndex(index)
```

</details>

### ⚙️ Method `year`

```python
def year(self) -> int | None
```

Return the selected calendar year, or `None` for Last 365 days and All years.

<details>
<summary>Code:</summary>

```python
def year(self) -> int | None:
        key = self.selection()
        if key in {LAST_365_KEY, ALL_YEARS_KEY}:
            return None
        try:
            return int(key)
        except ValueError:
            return None
```

</details>

## 🔧 Function `apply_chart_list_chrome`

```python
def apply_chart_list_chrome(view: QAbstractItemView) -> None
```

Select rows with a light accent fill and a 3 px accent bar.

<details>
<summary>Code:</summary>

```python
def apply_chart_list_chrome(view: QAbstractItemView) -> None:

    def _refresh() -> None:
        palette = palette_for(view)
        fill = css(mix(palette.window_bg, with_alpha(palette.accent, 28)))
        hover = css(mix(palette.window_bg, with_alpha(palette.accent, 16)))
        accent = css(palette.accent)
        text = css(mix(palette.window_bg, palette.text_primary))
        muted = css(mix(palette.window_bg, palette.text_secondary))
        view.setStyleSheet(
            f"""
            QAbstractItemView {{
                background: transparent;
                outline: none;
                color: {text};
            }}
            QAbstractItemView::item {{
                padding: 4px 8px;
                border-radius: 6px;
                border-left: 3px solid transparent;
            }}
            QAbstractItemView::item:selected {{
                background: {fill};
                color: {text};
                border-left: 3px solid {accent};
            }}
            QAbstractItemView::item:hover:!selected {{
                background: {hover};
            }}
            QAbstractItemView::item:disabled {{
                color: {muted};
                background: transparent;
            }}
            """
        )

    bind_theme(view, _refresh)
```

</details>

## 🔧 Function `kpi_row_limits`

```python
def kpi_row_limits() -> tuple[int, int]
```

Return the supported KPI card count, `(3, 6)` is the design range.

<details>
<summary>Code:</summary>

```python
def kpi_row_limits() -> tuple[int, int]:
    return (_KPI_MIN, _KPI_MAX)
```

</details>

## 🔧 Function `mark_chart_list_separator`

```python
def mark_chart_list_separator(item: QStandardItem) -> None
```

Make a dash row a non-selectable divider.

<details>
<summary>Code:</summary>

```python
def mark_chart_list_separator(item: QStandardItem) -> None:
    item.setEnabled(False)
    item.setSelectable(False)
    item.setFlags(Qt.ItemFlag.NoItemFlags)
```

</details>
