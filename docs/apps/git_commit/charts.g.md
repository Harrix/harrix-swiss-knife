---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `charts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GitCommitChartsPage`](#%EF%B8%8F-class-gitcommitchartspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

</details>

## 🏛️ Class `GitCommitChartsPage`

```python
class GitCommitChartsPage(QWidget)
```

Heatmap + timeline of commits under `paths_git_roots`, filtered by scope.

<details>
<summary>Code:</summary>

```python
class GitCommitChartsPage(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the charts page with a scope sidebar and heatmap body."""
        super().__init__(parent)
        self.setObjectName("gitCommitChartsPage")
        self._scope: CommitScope = "all"
        self._recorded: dict[date, int] = {}
        self._cache_ready = False
        self._busy = False
        self._worker: _CommitsChartWorker | None = None
        self._loading_toast: ToastCountdownNotification | None = None
        self._timeline_bars: list[Any] = []
        self._timeline_canvas: FigureCanvas | None = None
        self._updating_period = False

        root = QHBoxLayout(self)
        root.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        root.setSpacing(SPACE_M)

        sidebar = QWidget(self)
        sidebar.setFixedWidth(_SIDEBAR_WIDTH)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(SPACE_S)
        side_layout.addWidget(FluentText("Repositories", sidebar, role=TextRole.SECONDARY))
        self._scope_group, self._scope_radios = build_chart_type_radios(
            sidebar,
            list(COMMIT_SCOPE_LABELS),
            checked_key="all",
        )
        for key, radio in self._scope_radios.items():
            side_layout.addWidget(radio)
            radio.toggled.connect(lambda checked, scope=key: self._on_scope_toggled(scope, checked=checked))
        side_layout.addStretch(1)
        root.addWidget(sidebar)

        body = QWidget(self)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACE_S)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        toolbar.addWidget(FluentText("Period", body, role=TextRole.SECONDARY))
        self._period_nav = YearNavigator(body)
        self._period_nav.changed.connect(self._on_period_changed)
        toolbar.addWidget(self._period_nav, 0)
        toolbar.addStretch(1)
        self._refresh_button = FluentPushButton("Refresh", body, icon="refresh-cw")
        self._refresh_button.clicked.connect(lambda: self.refresh(force=True))
        toolbar.addWidget(self._refresh_button)
        body_layout.addLayout(toolbar)

        self._metrics = MetricStrip(body)
        body_layout.addWidget(self._metrics)

        self._title = QLabel("Commits", body)
        self._title.setObjectName("gitCommitChartsTitle")
        title_font = self._title.font()
        title_font.setBold(True)
        self._title.setFont(title_font)
        body_layout.addWidget(self._title)

        self._heatmap = YearHeatmap(body)
        body_layout.addWidget(self._heatmap)
        self._year_stack = YearHeatmapStack(body)
        self._year_stack.hide()
        body_layout.addWidget(self._year_stack, 1)

        self._time_host = QWidget(body)
        self._time_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._time_layout = QVBoxLayout(self._time_host)
        self._time_layout.setContentsMargins(0, 0, 0, 0)
        self._time_layout.setSpacing(0)
        body_layout.addWidget(self._time_host, 1)

        self._status = FluentText("", body, role=TextRole.SECONDARY)
        body_layout.addWidget(self._status)
        root.addWidget(body, 1)

    def refresh(self, *, force: bool = False) -> None:
        """Load commit counts. Cached after the first scan unless `force`."""
        if self._busy:
            return
        if self._cache_ready and not force:
            self._present_from_cache()
            return
        self._status.setText(_LOADING_TOAST_MESSAGE)
        self._set_busy(busy=True)
        self._start_loading_toast()
        roots = configured_git_roots()
        scope = self._scope
        worker = _CommitsChartWorker(roots, scope, force=force, parent=self)
        self._worker = worker

        def on_ok(payload: object) -> None:
            self._on_loaded(payload)

        def on_fail(message: str) -> None:
            self._on_failed(message)

        def cleanup() -> None:
            if self._worker is worker:
                self._worker = None
            worker.deleteLater()

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_fail)
        worker.finished.connect(cleanup)
        worker.start()

    def showEvent(self, event: Any) -> None:  # noqa: N802
        """Load charts the first time the tab becomes visible."""
        super().showEvent(event)
        if not self._cache_ready and not self._busy:
            self.refresh()

    def _clear_timeline(self) -> None:
        while self._time_layout.count():
            item = self._time_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._timeline_canvas = None
        self._timeline_bars = []

    def _close_loading_toast(self) -> None:
        """Stop the elapsed-time toast after the worker finishes."""
        toast = self._loading_toast
        self._loading_toast = None
        if toast is None:
            return
        toast.update_time()
        toast.close()

    def _on_failed(self, message: str) -> None:
        self._close_loading_toast()
        self._set_busy(busy=False)
        self._status.setText(message)
        ToastNotification(message, duration=2500, parent=self)

    def _on_loaded(self, payload: object) -> None:
        self._close_loading_toast()
        self._set_busy(busy=False)
        try:
            recorded, years = cast("tuple[object, object]", payload)
        except (TypeError, ValueError):
            self._status.setText("Could not load commits")
            return
        if not isinstance(recorded, dict) or not isinstance(years, list):
            self._status.setText("Could not load commits")
            return
        self._recorded = {day: int(value) for day, value in recorded.items() if isinstance(day, date)}
        self._cache_ready = True
        self._updating_period = True
        self._period_nav.set_years([int(year) for year in years if isinstance(year, int)])
        self._updating_period = False
        self._present()

    def _on_period_changed(self) -> None:
        if self._updating_period or not self._cache_ready:
            return
        self._present()

    def _on_scope_toggled(self, scope: str, *, checked: bool) -> None:
        if not checked:
            return
        self._scope = cast("CommitScope", scope)
        if self._cache_ready:
            self._present_from_cache()
        else:
            self.refresh()

    def _period_bounds(self, today: date) -> tuple[date, date] | None:
        """Return `(start, end)` for Last 365 / year, or `None` for All years."""
        key = self._period_nav.selection()
        if key == ALL_YEARS_KEY:
            return None
        if key == LAST_365_KEY:
            return today - timedelta(days=_CHART_PERIOD_DAYS - 1), today
        year = self._period_nav.year()
        if year is None:
            return today - timedelta(days=_CHART_PERIOD_DAYS - 1), today
        return date(year, 1, 1), date(year, 12, 31)

    def _present(self) -> None:
        today = datetime.now(UTC).astimezone().date()
        bounds = self._period_bounds(today)
        label = next((text for key, text in COMMIT_SCOPE_LABELS if key == self._scope), "Commits")
        self._title.setText(label)
        if bounds is None:
            self._present_all_years(today)
            return
        start, end = bounds
        recorded = {day: value for day, value in self._recorded.items() if start <= day <= end}
        first_day = min(recorded) if recorded else None
        tokens, marks, legend, bin_count = habit_calendar_model(
            recorded,
            start,
            end,
            is_bool=False,
            activity_start=first_day,
            today=today,
        )
        colors = {day: habit_token_color(state, bin_count=bin_count) for day, state in tokens.items()}
        tips = {day: _commit_cell_tip(day, recorded.get(day, 0)) for day in tokens}
        self._heatmap.set_calendar(
            start,
            end,
            colors,
            legend=habit_legend_colors(legend, bin_count=bin_count),
            marks=marks,
            tooltips=tips,
        )
        self._heatmap.show()
        self._year_stack.hide()
        self._time_host.show()
        stats = habit_period_stats(recorded, start, end, is_bool=False, today=today)
        self._metrics.set_metrics(
            [
                ("Total", fmt_number(stats.total, decimals=0)),
                ("Active days", fmt_number(stats.completed, decimals=0)),
                ("Current streak", fmt_number(stats.current_streak, decimals=0)),
                ("Longest streak", fmt_number(stats.longest_streak, decimals=0)),
            ],
        )
        bars, _percent = habit_timeline_bars(recorded, start, end, is_bool=False, today=today)
        self._timeline_bars = bars
        self._show_timeline(bars)
        total = stats.total
        noun = "commit" if total == 1 else "commits"
        self._status.setText(f"{fmt_number(total, decimals=0)} {noun} in the selected period")

    def _present_all_years(self, today: date) -> None:
        years = sorted({day.year for day in self._recorded if day.year <= today.year}, reverse=True)
        bands = heatmap_year_bands(years, today=today)
        if not bands:
            self._heatmap.hide()
            self._year_stack.hide()
            self._time_host.hide()
            self._clear_timeline()
            self._metrics.set_metrics([])
            self._status.setText("No commits in the selected repositories")
            return
        start = bands[-1][1]
        end = bands[0][2]
        first_day = min(self._recorded) if self._recorded else None
        tokens, marks, legend, bin_count = habit_calendar_model(
            self._recorded,
            start,
            end,
            is_bool=False,
            activity_start=first_day,
            today=today,
        )
        colors = {day: habit_token_color(state, bin_count=bin_count) for day, state in tokens.items()}
        tips = {day: _commit_cell_tip(day, self._recorded.get(day, 0)) for day in tokens}
        self._year_stack.set_years(
            bands,
            colors,
            legend=habit_legend_colors(legend, bin_count=bin_count),
            marks=marks,
            tooltips=tips,
        )
        self._heatmap.hide()
        self._year_stack.show()
        self._time_host.hide()
        self._clear_timeline()
        stats = habit_period_stats(self._recorded, start, end, is_bool=False, today=today)
        self._metrics.set_metrics(
            [
                ("Total", fmt_number(stats.total, decimals=0)),
                ("Active days", fmt_number(stats.completed, decimals=0)),
                ("Current streak", fmt_number(stats.current_streak, decimals=0)),
                ("Longest streak", fmt_number(stats.longest_streak, decimals=0)),
            ],
        )
        total = stats.total
        noun = "commit" if total == 1 else "commits"
        self._status.setText(f"{fmt_number(total, decimals=0)} {noun} across all years")

    def _present_from_cache(self) -> None:
        """Re-filter the warm cache for the current scope without scanning Git."""
        roots = configured_git_roots()
        today = datetime.now(UTC).astimezone().date()
        self._recorded = count_commits_by_day(roots, _EARLIEST, today, scope=self._scope)
        years = list_commit_years(roots, scope=self._scope)
        self._updating_period = True
        self._period_nav.set_years(years)
        self._updating_period = False
        self._present()

    def _set_busy(self, *, busy: bool) -> None:
        self._busy = busy
        self._refresh_button.setEnabled(not busy)
        self._period_nav.setEnabled(not busy)
        for radio in self._scope_radios.values():
            radio.setEnabled(not busy)

    def _show_timeline(self, bars: list[Any]) -> None:
        self._clear_timeline()
        width = max(self._time_host.width(), 480)
        height = max(self._time_host.height(), 220)
        figure = build_timeline_figure(
            bars,
            title="Commits over time",
            ylabel="Value",
            bar_label="Weekly total",
            line_label="7-day average",
            figsize=(width / 100, height / 100),
            line_on_twin=True,
            line_ylabel="7-day average",
        )
        canvas = create_chart_canvas(figure)

        def resolve_tooltip(event: Any) -> str | None:
            if event.xdata is None:
                return None
            bar = bar_at_x(self._timeline_bars, float(event.xdata))
            return None if bar is None else bar.tooltip

        install_chart_hover(canvas, resolve_tooltip=resolve_tooltip)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._time_layout.addWidget(canvas, stretch=1)
        self._timeline_canvas = canvas
        canvas.show()
        canvas.draw()

    def _start_loading_toast(self) -> None:
        """Show a countdown toast so the long first scan is visible by elapsed time."""
        self._close_loading_toast()
        toast = ToastCountdownNotification(_LOADING_TOAST_MESSAGE, parent=self.window())
        toast.start_countdown()
        self._loading_toast = toast
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the charts page with a scope sidebar and heatmap body.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("gitCommitChartsPage")
        self._scope: CommitScope = "all"
        self._recorded: dict[date, int] = {}
        self._cache_ready = False
        self._busy = False
        self._worker: _CommitsChartWorker | None = None
        self._loading_toast: ToastCountdownNotification | None = None
        self._timeline_bars: list[Any] = []
        self._timeline_canvas: FigureCanvas | None = None
        self._updating_period = False

        root = QHBoxLayout(self)
        root.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        root.setSpacing(SPACE_M)

        sidebar = QWidget(self)
        sidebar.setFixedWidth(_SIDEBAR_WIDTH)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(SPACE_S)
        side_layout.addWidget(FluentText("Repositories", sidebar, role=TextRole.SECONDARY))
        self._scope_group, self._scope_radios = build_chart_type_radios(
            sidebar,
            list(COMMIT_SCOPE_LABELS),
            checked_key="all",
        )
        for key, radio in self._scope_radios.items():
            side_layout.addWidget(radio)
            radio.toggled.connect(lambda checked, scope=key: self._on_scope_toggled(scope, checked=checked))
        side_layout.addStretch(1)
        root.addWidget(sidebar)

        body = QWidget(self)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACE_S)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        toolbar.addWidget(FluentText("Period", body, role=TextRole.SECONDARY))
        self._period_nav = YearNavigator(body)
        self._period_nav.changed.connect(self._on_period_changed)
        toolbar.addWidget(self._period_nav, 0)
        toolbar.addStretch(1)
        self._refresh_button = FluentPushButton("Refresh", body, icon="refresh-cw")
        self._refresh_button.clicked.connect(lambda: self.refresh(force=True))
        toolbar.addWidget(self._refresh_button)
        body_layout.addLayout(toolbar)

        self._metrics = MetricStrip(body)
        body_layout.addWidget(self._metrics)

        self._title = QLabel("Commits", body)
        self._title.setObjectName("gitCommitChartsTitle")
        title_font = self._title.font()
        title_font.setBold(True)
        self._title.setFont(title_font)
        body_layout.addWidget(self._title)

        self._heatmap = YearHeatmap(body)
        body_layout.addWidget(self._heatmap)
        self._year_stack = YearHeatmapStack(body)
        self._year_stack.hide()
        body_layout.addWidget(self._year_stack, 1)

        self._time_host = QWidget(body)
        self._time_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._time_layout = QVBoxLayout(self._time_host)
        self._time_layout.setContentsMargins(0, 0, 0, 0)
        self._time_layout.setSpacing(0)
        body_layout.addWidget(self._time_host, 1)

        self._status = FluentText("", body, role=TextRole.SECONDARY)
        body_layout.addWidget(self._status)
        root.addWidget(body, 1)
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self, *, force: bool = False) -> None
```

Load commit counts. Cached after the first scan unless `force`.

<details>
<summary>Code:</summary>

```python
def refresh(self, *, force: bool = False) -> None:
        if self._busy:
            return
        if self._cache_ready and not force:
            self._present_from_cache()
            return
        self._status.setText(_LOADING_TOAST_MESSAGE)
        self._set_busy(busy=True)
        self._start_loading_toast()
        roots = configured_git_roots()
        scope = self._scope
        worker = _CommitsChartWorker(roots, scope, force=force, parent=self)
        self._worker = worker

        def on_ok(payload: object) -> None:
            self._on_loaded(payload)

        def on_fail(message: str) -> None:
            self._on_failed(message)

        def cleanup() -> None:
            if self._worker is worker:
                self._worker = None
            worker.deleteLater()

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_fail)
        worker.finished.connect(cleanup)
        worker.start()
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: Any) -> None
```

Load charts the first time the tab becomes visible.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: Any) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._cache_ready and not self._busy:
            self.refresh()
```

</details>
