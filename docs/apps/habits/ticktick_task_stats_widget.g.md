---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_task_stats_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TickTickTaskStatsWidget`](#%EF%B8%8F-class-tickticktaskstatswidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `configure_day_table_columns`](#%EF%B8%8F-method-configure_day_table_columns)
  - [⚙️ Method `day_table (property)`](#%EF%B8%8F-method-day_table-property)
  - [⚙️ Method `ensure_loaded`](#%EF%B8%8F-method-ensure_loaded)
  - [⚙️ Method `reload`](#%EF%B8%8F-method-reload)

</details>

## 🏛️ Class `TickTickTaskStatsWidget`

```python
class TickTickTaskStatsWidget(QWidget)
```

GitHub-like completion calendar for local TickTick tasks (Habits tab).

<details>
<summary>Code:</summary>

```python
class TickTickTaskStatsWidget(QWidget):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        db_path: Path | None = None,
        autoload: bool = False,
    ) -> None:
        """Build the tab UI; load the TickTick DB when ``autoload`` or ``ensure_loaded``."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._db_path = db_path
        self._loaded = False
        self._projects: list[TickTickProject] = []
        self._completions: list[TickTickCompletion] = []
        self._stats: TickTickPeriodStats | None = None
        self._heatmap: TickTickHeatmapResult | None = None
        self._canvas: FigureCanvas | None = None
        self._selected_day: date | None = None

        self._summary_label = QLabel()
        self._summary_label.setWordWrap(True)
        self._summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._source_label = QLabel()
        self._source_label.setStyleSheet(muted_caption_qss())
        self._source_label.setWordWrap(True)
        self._source_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._chart_mode_combo = QComboBox()
        for mode, label in CHART_MODE_LABELS:
            self._chart_mode_combo.addItem(label, mode)

        self._period_combo = QComboBox()
        self._project_combo = QComboBox()
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 36)
        self._count_spin.setValue(_DEFAULT_COMPARE_COUNT)
        self._count_caption = QLabel("Months")
        self._count_caption.setStyleSheet(muted_caption_qss())
        self._same_month_combo = QComboBox()
        for month_index in range(1, 13):
            self._same_month_combo.addItem(calendar.month_name[month_index], month_index)
        self._same_month_caption = QLabel("Month")
        self._same_month_caption.setStyleSheet(muted_caption_qss())

        self._chart_host = QWidget()
        self._chart_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._chart_layout = QVBoxLayout(self._chart_host)
        self._chart_layout.setContentsMargins(0, 0, 0, 0)

        self._day_label = QLabel("Loading…")
        self._day_label.setStyleSheet(muted_caption_qss())

        self._day_table = QTableWidget(0, len(_HEADERS))
        self._day_table.setObjectName("ticktickDayTable")
        self._day_table.setHorizontalHeaderLabels(list(_HEADERS))
        self._day_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._day_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._day_table.setAlternatingRowColors(True)
        self._day_table.verticalHeader().setVisible(False)
        self._day_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._day_table.setMinimumHeight(160)
        self.configure_day_table_columns()

        self._day_panel = QWidget()
        day_layout = QVBoxLayout(self._day_panel)
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_layout.setSpacing(6)
        day_layout.addWidget(self._day_label)
        day_layout.addWidget(self._day_table, stretch=1)

        self._body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._body_splitter.setChildrenCollapsible(False)
        self._body_splitter.addWidget(self._chart_host)
        self._body_splitter.addWidget(self._day_panel)
        self._body_splitter.setStretchFactor(0, 3)
        self._body_splitter.setStretchFactor(1, 2)
        self._body_splitter.setSizes([720, 480])

        filters = QHBoxLayout()
        chart_caption = QLabel("Chart")
        chart_caption.setStyleSheet(muted_caption_qss())
        period_caption = QLabel("Period")
        period_caption.setStyleSheet(muted_caption_qss())
        self._period_caption = period_caption
        project_caption = QLabel("List")
        project_caption.setStyleSheet(muted_caption_qss())
        filters.addWidget(chart_caption)
        filters.addWidget(self._chart_mode_combo, stretch=1)
        filters.addWidget(period_caption)
        filters.addWidget(self._period_combo, stretch=1)
        filters.addWidget(project_caption)
        filters.addWidget(self._project_combo, stretch=2)

        self._compare_filters = QHBoxLayout()
        self._compare_filters.addWidget(self._count_caption)
        self._compare_filters.addWidget(self._count_spin)
        self._compare_filters.addWidget(self._same_month_caption)
        self._compare_filters.addWidget(self._same_month_combo, stretch=1)
        self._compare_filters.addStretch()

        refresh_button = make_lucide_push_button("Refresh", "refresh-cw")
        refresh_button.clicked.connect(self.reload)
        button_row = QHBoxLayout()
        button_row.addWidget(refresh_button)
        button_row.addStretch()

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.addWidget(self._summary_label)
        root.addWidget(self._source_label)
        root.addLayout(filters)
        root.addLayout(self._compare_filters)
        root.addWidget(self._body_splitter, stretch=1)
        root.addLayout(button_row)

        self._chart_mode_combo.currentIndexChanged.connect(self._on_chart_mode_changed)
        self._period_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._project_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._count_spin.valueChanged.connect(self._on_filters_changed)
        self._same_month_combo.currentIndexChanged.connect(self._on_filters_changed)

        self._sync_mode_controls()
        self._set_same_month_to_current()

        if autoload:
            self.reload()

    def configure_day_table_columns(self) -> None:
        """Time/List hug content; Task stretches to fill the table width."""
        header = self._day_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

    @property
    def day_table(self) -> QTableWidget:
        """Completed-tasks table for the selected heatmap day."""
        return self._day_table

    def ensure_loaded(self) -> None:
        """Load TickTick data once when the tab is first shown."""
        if not self._loaded:
            self.reload()

    def reload(self) -> None:
        """Copy the live TickTick DB again and refresh filters/heatmap."""
        self._loaded = True
        try:
            projects, completions, source = load_ticktick_snapshot(self._db_path)
        except TickTickDbError as exc:
            self._projects = []
            self._completions = []
            self._summary_label.setText(str(exc))
            self._source_label.setText("")
            self._clear_chart("TickTick database is not available.")
            self._fill_day_table([])
            self._period_combo.blockSignals(True)  # noqa: FBT003
            self._project_combo.blockSignals(True)  # noqa: FBT003
            self._period_combo.clear()
            self._project_combo.clear()
            self._period_combo.blockSignals(False)  # noqa: FBT003
            self._project_combo.blockSignals(False)  # noqa: FBT003
            return

        self._projects = projects
        self._completions = completions
        self._source_label.setText(f"DB: {source}")
        self._source_label.setToolTip(str(source))
        self._repopulate_filters()
        self._redraw()

    def _chart_mode(self) -> ChartMode:
        data = self._chart_mode_combo.currentData()
        for mode, _label in CHART_MODE_LABELS:
            if data == mode:
                return mode
        return CHART_MODE_HEATMAP

    def _clear_chart(self, message: str) -> None:
        self._release_canvas()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(muted_caption_qss())
        self._chart_layout.addWidget(label)
        self._heatmap = None

    def _figure_size(self) -> tuple[float, float]:
        width = max(self._chart_host.width(), 640)
        if self._chart_mode() == CHART_MODE_HEATMAP:
            height = max(_HEATMAP_MIN_HEIGHT, min(_HEATMAP_MAX_HEIGHT, 240))
        else:
            height = max(_CHART_MIN_HEIGHT, min(self._chart_host.height(), _CHART_MAX_HEIGHT))
            height = max(height, 360)
        return (width / 100, height / 100)

    def _fill_day_table(self, rows: list[TickTickCompletion]) -> None:
        self._day_table.setRowCount(len(rows))
        for index, item in enumerate(rows):
            time_item = QTableWidgetItem(item.completed_at.strftime("%H:%M:%S"))
            task_item = QTableWidgetItem(item.title)
            list_item = QTableWidgetItem(item.project_name)
            self._day_table.setItem(index, 0, time_item)
            self._day_table.setItem(index, 1, task_item)
            self._day_table.setItem(index, 2, list_item)
        self.configure_day_table_columns()

    def _on_chart_mode_changed(self) -> None:
        self._selected_day = None
        self._sync_mode_controls()
        self._redraw()

    def _on_filters_changed(self) -> None:
        self._selected_day = None
        self._redraw()

    def _on_heatmap_click(self, event: MouseEvent) -> None:
        if self._heatmap is None or event.inaxes is None or event.xdata is None or event.ydata is None:
            return
        day = day_from_heatmap_click(self._heatmap, float(event.xdata), float(event.ydata))
        if day is None:
            return
        self._selected_day = day
        self._show_day(day)
        project_id = self._selected_project_id()
        self._redraw_heatmap(project_id)

    def _redraw(self) -> None:
        mode = self._chart_mode()
        project_id = self._selected_project_id()
        if mode == CHART_MODE_HEATMAP:
            self._redraw_heatmap(project_id)
        elif mode == CHART_MODE_BY_YEAR:
            self._redraw_by_year(project_id)
        elif mode == CHART_MODE_BY_MONTH:
            self._redraw_by_month(project_id)
        elif mode == CHART_MODE_COMPARE_LAST:
            self._redraw_compare_last(project_id)
        else:
            self._redraw_compare_same(project_id)

    def _redraw_by_month(self, project_id: str | None) -> None:
        months = self._count_spin.value()
        month_counts = counts_by_month(self._completions, months, project_id=project_id)
        if not month_counts:
            self._clear_chart("No completed tasks in this period.")
            return
        self._summary_label.setText(f"Completed tasks by month (last {months})")
        self._show_figure(build_month_counts_chart(month_counts, figsize=self._figure_size()))

    def _redraw_by_year(self, project_id: str | None) -> None:
        year_counts = counts_by_year(self._completions, project_id=project_id)
        if not year_counts:
            self._clear_chart("No completed tasks in this period.")
            return
        self._summary_label.setText("Completed tasks by year")
        self._show_figure(build_year_counts_chart(year_counts, figsize=self._figure_size()))

    def _redraw_compare_last(self, project_id: str | None) -> None:
        months = self._count_spin.value()
        series = compare_last_months_series(self._completions, months, project_id=project_id)
        if not series or all(not item.points for item in series):
            self._clear_chart(f"No data for the last {months} months.")
            return
        title = f"Completed tasks (Last {months} months comparison)"
        self._show_figure(build_compare_months_chart(series, title=title, figsize=self._figure_size()))

    def _redraw_compare_same(self, project_id: str | None) -> None:
        years = self._count_spin.value()
        month = int(self._same_month_combo.currentData() or datetime.now().astimezone().month)
        series = compare_same_months_series(self._completions, month, years, project_id=project_id)
        month_name = calendar.month_name[month]
        if not series or all(not item.points for item in series):
            self._clear_chart(f"No data for {month_name.lower()} in the last {years} years.")
            return
        title = f"Completed tasks ({month_name} comparison — last {years} years)"
        self._show_figure(build_compare_months_chart(series, title=title, figsize=self._figure_size()))

    def _redraw_heatmap(self, project_id: str | None) -> None:
        self._day_panel.setVisible(True)
        start_date, end_date = resolve_period(year=self._selected_year())
        self._stats = aggregate_completions(
            self._completions,
            start_date,
            end_date,
            project_id=project_id,
        )
        self._summary_label.setText(format_period_summary(self._stats))
        if self._stats.total_completions == 0:
            self._selected_day = None
            self._clear_chart("No completed tasks in this period.")
            self._fill_day_table([])
            self._day_label.setText("No completed tasks in this period.")
            return

        day = self._selected_day
        if day is None or day < self._stats.start_date or day > self._stats.end_date:
            day = latest_active_day(self._stats)
            self._selected_day = day
        self._heatmap = build_contribution_heatmap(
            self._stats,
            figsize=self._figure_size(),
            dpi=100,
            selected_day=day,
        )
        self._show_heatmap(self._heatmap)
        if day is not None:
            self._show_day(day)
        else:
            self._day_label.setText("No completed tasks in this period.")
            self._fill_day_table([])

    def _release_canvas(self) -> None:
        while self._chart_layout.count():
            item = self._chart_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self._canvas = None

    def _repopulate_filters(self) -> None:
        self._period_combo.blockSignals(True)  # noqa: FBT003
        self._project_combo.blockSignals(True)  # noqa: FBT003
        current_period = self._period_combo.currentData()
        current_project = self._project_combo.currentData()
        self._period_combo.clear()
        self._period_combo.addItem(LAST_365_DAYS_LABEL, None)
        for year in available_years(self._completions):
            self._period_combo.addItem(str(year), year)
        self._project_combo.clear()
        self._project_combo.addItem("All lists", _ALL_PROJECTS)
        for project in self._projects:
            self._project_combo.addItem(project.name, project.id)
        period_index = self._period_combo.findData(current_period)
        self._period_combo.setCurrentIndex(max(period_index, 0))
        project_index = self._project_combo.findData(current_project)
        self._project_combo.setCurrentIndex(max(project_index, 0))
        self._period_combo.blockSignals(False)  # noqa: FBT003
        self._project_combo.blockSignals(False)  # noqa: FBT003

    def _selected_project_id(self) -> str | None:
        data = self._project_combo.currentData()
        if data is None or data == _ALL_PROJECTS:
            return None
        return str(data)

    def _selected_year(self) -> int | None:
        data = self._period_combo.currentData()
        return int(data) if isinstance(data, int) else None

    def _set_same_month_to_current(self) -> None:
        current_month = datetime.now().astimezone().month
        index = self._same_month_combo.findData(current_month)
        if index >= 0:
            self._same_month_combo.setCurrentIndex(index)

    def _show_day(self, day: date) -> None:
        rows = []
        if self._stats is not None:
            rows = list(self._stats.completions_by_day.get(day, []))
        count = len(rows)
        self._day_label.setText(f"{day.isoformat()} — {count} completed task{'s' if count != 1 else ''}")
        self._fill_day_table(rows)

    def _show_figure(self, figure: Figure) -> None:
        self._release_canvas()
        canvas = create_chart_canvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._chart_layout.addWidget(canvas, stretch=1)
        self._canvas = canvas
        canvas.draw()

    def _show_heatmap(self, result: TickTickHeatmapResult) -> None:
        self._release_canvas()
        canvas = FigureCanvas(result.figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        canvas.mpl_connect("button_press_event", self._on_heatmap_click)

        def resolve_tooltip(event: MouseEvent) -> str | None:
            if self._heatmap is None or event.inaxes is None or event.xdata is None or event.ydata is None:
                return None
            day = day_from_heatmap_click(self._heatmap, float(event.xdata), float(event.ydata))
            if day is None:
                return None
            count = 0 if self._stats is None else int(self._stats.counts_by_day.get(day, 0))
            return heatmap_cell_tooltip(day, count)

        install_chart_hover(canvas, resolve_tooltip=resolve_tooltip)
        self._chart_layout.addWidget(canvas, 0, Qt.AlignmentFlag.AlignTop)
        self._canvas = canvas
        canvas.draw()

    def _sync_mode_controls(self) -> None:
        mode = self._chart_mode()
        is_heatmap = mode == CHART_MODE_HEATMAP
        is_by_month = mode == CHART_MODE_BY_MONTH
        is_compare_last = mode == CHART_MODE_COMPARE_LAST
        is_compare_same = mode == CHART_MODE_COMPARE_SAME
        show_count = is_by_month or is_compare_last or is_compare_same
        show_same_month = is_compare_same

        self._period_caption.setVisible(is_heatmap)
        self._period_combo.setVisible(is_heatmap)
        self._count_caption.setVisible(show_count)
        self._count_spin.setVisible(show_count)
        self._same_month_caption.setVisible(show_same_month)
        self._same_month_combo.setVisible(show_same_month)

        if is_compare_same:
            self._count_caption.setText("Years")
            self._count_spin.setRange(1, 20)
        elif is_by_month or is_compare_last:
            self._count_caption.setText("Months")
            self._count_spin.setRange(1, 36)

        self._day_panel.setVisible(is_heatmap)
        if is_heatmap:
            self._chart_host.setMinimumHeight(_HEATMAP_MIN_HEIGHT)
            self._chart_host.setMaximumHeight(_HEATMAP_MAX_HEIGHT)
            self._chart_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self._body_splitter.setStretchFactor(0, 3)
            self._body_splitter.setStretchFactor(1, 2)
        else:
            self._chart_host.setMinimumHeight(_CHART_MIN_HEIGHT)
            self._chart_host.setMaximumHeight(16777215)
            self._chart_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self._body_splitter.setStretchFactor(0, 1)
            self._body_splitter.setStretchFactor(1, 0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, db_path: Path | None = None, autoload: bool = False) -> None
```

Build the tab UI; load the TickTick DB when ``autoload`` or ``ensure_loaded``.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        db_path: Path | None = None,
        autoload: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._db_path = db_path
        self._loaded = False
        self._projects: list[TickTickProject] = []
        self._completions: list[TickTickCompletion] = []
        self._stats: TickTickPeriodStats | None = None
        self._heatmap: TickTickHeatmapResult | None = None
        self._canvas: FigureCanvas | None = None
        self._selected_day: date | None = None

        self._summary_label = QLabel()
        self._summary_label.setWordWrap(True)
        self._summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._source_label = QLabel()
        self._source_label.setStyleSheet(muted_caption_qss())
        self._source_label.setWordWrap(True)
        self._source_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._chart_mode_combo = QComboBox()
        for mode, label in CHART_MODE_LABELS:
            self._chart_mode_combo.addItem(label, mode)

        self._period_combo = QComboBox()
        self._project_combo = QComboBox()
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 36)
        self._count_spin.setValue(_DEFAULT_COMPARE_COUNT)
        self._count_caption = QLabel("Months")
        self._count_caption.setStyleSheet(muted_caption_qss())
        self._same_month_combo = QComboBox()
        for month_index in range(1, 13):
            self._same_month_combo.addItem(calendar.month_name[month_index], month_index)
        self._same_month_caption = QLabel("Month")
        self._same_month_caption.setStyleSheet(muted_caption_qss())

        self._chart_host = QWidget()
        self._chart_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._chart_layout = QVBoxLayout(self._chart_host)
        self._chart_layout.setContentsMargins(0, 0, 0, 0)

        self._day_label = QLabel("Loading…")
        self._day_label.setStyleSheet(muted_caption_qss())

        self._day_table = QTableWidget(0, len(_HEADERS))
        self._day_table.setObjectName("ticktickDayTable")
        self._day_table.setHorizontalHeaderLabels(list(_HEADERS))
        self._day_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._day_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._day_table.setAlternatingRowColors(True)
        self._day_table.verticalHeader().setVisible(False)
        self._day_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._day_table.setMinimumHeight(160)
        self.configure_day_table_columns()

        self._day_panel = QWidget()
        day_layout = QVBoxLayout(self._day_panel)
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_layout.setSpacing(6)
        day_layout.addWidget(self._day_label)
        day_layout.addWidget(self._day_table, stretch=1)

        self._body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._body_splitter.setChildrenCollapsible(False)
        self._body_splitter.addWidget(self._chart_host)
        self._body_splitter.addWidget(self._day_panel)
        self._body_splitter.setStretchFactor(0, 3)
        self._body_splitter.setStretchFactor(1, 2)
        self._body_splitter.setSizes([720, 480])

        filters = QHBoxLayout()
        chart_caption = QLabel("Chart")
        chart_caption.setStyleSheet(muted_caption_qss())
        period_caption = QLabel("Period")
        period_caption.setStyleSheet(muted_caption_qss())
        self._period_caption = period_caption
        project_caption = QLabel("List")
        project_caption.setStyleSheet(muted_caption_qss())
        filters.addWidget(chart_caption)
        filters.addWidget(self._chart_mode_combo, stretch=1)
        filters.addWidget(period_caption)
        filters.addWidget(self._period_combo, stretch=1)
        filters.addWidget(project_caption)
        filters.addWidget(self._project_combo, stretch=2)

        self._compare_filters = QHBoxLayout()
        self._compare_filters.addWidget(self._count_caption)
        self._compare_filters.addWidget(self._count_spin)
        self._compare_filters.addWidget(self._same_month_caption)
        self._compare_filters.addWidget(self._same_month_combo, stretch=1)
        self._compare_filters.addStretch()

        refresh_button = make_lucide_push_button("Refresh", "refresh-cw")
        refresh_button.clicked.connect(self.reload)
        button_row = QHBoxLayout()
        button_row.addWidget(refresh_button)
        button_row.addStretch()

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.addWidget(self._summary_label)
        root.addWidget(self._source_label)
        root.addLayout(filters)
        root.addLayout(self._compare_filters)
        root.addWidget(self._body_splitter, stretch=1)
        root.addLayout(button_row)

        self._chart_mode_combo.currentIndexChanged.connect(self._on_chart_mode_changed)
        self._period_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._project_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._count_spin.valueChanged.connect(self._on_filters_changed)
        self._same_month_combo.currentIndexChanged.connect(self._on_filters_changed)

        self._sync_mode_controls()
        self._set_same_month_to_current()

        if autoload:
            self.reload()
```

</details>

### ⚙️ Method `configure_day_table_columns`

```python
def configure_day_table_columns(self) -> None
```

Time/List hug content; Task stretches to fill the table width.

<details>
<summary>Code:</summary>

```python
def configure_day_table_columns(self) -> None:
        header = self._day_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
```

</details>

### ⚙️ Method `day_table (property)`

```python
def day_table(self) -> QTableWidget
```

Completed-tasks table for the selected heatmap day.

<details>
<summary>Code:</summary>

```python
def day_table(self) -> QTableWidget:
        return self._day_table
```

</details>

### ⚙️ Method `ensure_loaded`

```python
def ensure_loaded(self) -> None
```

Load TickTick data once when the tab is first shown.

<details>
<summary>Code:</summary>

```python
def ensure_loaded(self) -> None:
        if not self._loaded:
            self.reload()
```

</details>

### ⚙️ Method `reload`

```python
def reload(self) -> None
```

Copy the live TickTick DB again and refresh filters/heatmap.

<details>
<summary>Code:</summary>

```python
def reload(self) -> None:
        self._loaded = True
        try:
            projects, completions, source = load_ticktick_snapshot(self._db_path)
        except TickTickDbError as exc:
            self._projects = []
            self._completions = []
            self._summary_label.setText(str(exc))
            self._source_label.setText("")
            self._clear_chart("TickTick database is not available.")
            self._fill_day_table([])
            self._period_combo.blockSignals(True)  # noqa: FBT003
            self._project_combo.blockSignals(True)  # noqa: FBT003
            self._period_combo.clear()
            self._project_combo.clear()
            self._period_combo.blockSignals(False)  # noqa: FBT003
            self._project_combo.blockSignals(False)  # noqa: FBT003
            return

        self._projects = projects
        self._completions = completions
        self._source_label.setText(f"DB: {source}")
        self._source_label.setToolTip(str(source))
        self._repopulate_filters()
        self._redraw()
```

</details>
