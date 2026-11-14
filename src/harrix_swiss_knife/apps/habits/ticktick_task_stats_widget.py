"""Habits tab: TickTick completion calendar and the tasks of the selected day."""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QResizeEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.chart_format import fmt_date, fmt_number
from harrix_swiss_knife.apps.common.chart_hover import create_chart_canvas, install_chart_hover
from harrix_swiss_knife.apps.common.chart_page_chrome import (
    ChartToolbar,
    MetricStrip,
    build_chart_type_radios,
    polish_chart_type_group,
)
from harrix_swiss_knife.apps.common.chart_theme import (
    accent_heatmap_colors,
    chart_tint,
    heatmap_zero_color,
    intensity_bin_label,
    map_value_to_intensity_bin,
    quantile_intensity_ranges,
)
from harrix_swiss_knife.apps.common.chart_timeline import TimelineBar, bar_at_x, build_timeline_figure, calendar_days
from harrix_swiss_knife.apps.common.ui_chrome import muted_caption_qss
from harrix_swiss_knife.apps.common.year_heatmap import YearHeatmap
from harrix_swiss_knife.apps.habits.ticktick_local_db import (
    TickTickCompletion,
    TickTickDbError,
    TickTickProject,
    load_ticktick_snapshot,
)
from harrix_swiss_knife.apps.habits.ticktick_task_stats import (
    CHART_MODE_BY_MONTH,
    CHART_MODE_BY_YEAR,
    CHART_MODE_COMPARE_LAST,
    CHART_MODE_COMPARE_SAME,
    CHART_MODE_HEATMAP,
    CHART_MODE_LABELS,
    LAST_365_DAYS_LABEL,
    ChartMode,
    TickTickPeriodStats,
    aggregate_completions,
    available_years,
    build_compare_months_chart,
    build_month_counts_chart,
    build_year_counts_chart,
    compare_last_months_series,
    compare_same_months_series,
    counts_by_month,
    counts_by_year,
    heatmap_cell_tooltip,
    resolve_period,
    task_timeline_bars,
)
from harrix_swiss_knife.fluent.theme import FluentTheme, bind_theme, css, mix

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.backend_bases import MouseEvent
    from matplotlib.figure import Figure

_ALL_PROJECTS = "__all__"
_DEFAULT_COMPARE_COUNT = 12
_SIDEBAR_MIN = 220
_SIDEBAR_WIDTH = 260
_DAY_MIN = 240
_DAY_WIDTH = 300
_DAY_MAX = 420
_NARROW_WIDTH = 1200


class TickTickTaskStatsWidget(QWidget):
    """TickTick charts: filters, heatmap plus timeline, and the selected day's tasks."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        db_path: Path | None = None,
        autoload: bool = False,
    ) -> None:
        """Build the three-column page. Load the database when ``autoload`` is set."""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._db_path = db_path
        self._loaded = False
        self._projects: list[TickTickProject] = []
        self._completions: list[TickTickCompletion] = []
        self._stats: TickTickPeriodStats | None = None
        self._selected_start: date | None = None
        self._selected_end: date | None = None
        self._timeline_bars: list[TimelineBar] = []
        self._timeline_weekly = False
        self._chart_toolbar: ChartToolbar | None = None
        self._narrow = False
        self._time_canvas: QWidget | None = None
        self._chart_canvas: QWidget | None = None

        self._project_combo = QComboBox()
        self._metrics = MetricStrip()
        self._heatmap_title = QLabel("Completed tasks")
        self._heatmap_title.setObjectName("ticktickHeatmapTitle")
        title_font = QFont(self.font())
        title_font.setBold(True)
        self._heatmap_title.setFont(title_font)
        self._heatmap = YearHeatmap()
        self._time_host = QWidget()
        self._time_layout = QVBoxLayout(self._time_host)
        self._time_layout.setContentsMargins(0, 0, 0, 0)
        self._chart_host = QWidget()
        self._chart_layout = QVBoxLayout(self._chart_host)
        self._chart_layout.setContentsMargins(0, 0, 0, 0)
        self._chart_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._day_title = QLabel("Selected day")
        self._day_title.setFont(title_font)
        self._day_title.setWordWrap(True)
        self._day_count = QLabel("")
        self._day_count.setStyleSheet(muted_caption_qss())
        self._day_count.setWordWrap(True)
        self._day_body = QWidget()
        self._day_list_layout = QVBoxLayout(self._day_body)
        self._day_list_layout.setContentsMargins(0, 0, 0, 0)
        self._day_list_layout.setSpacing(0)
        self._day_scroll = QScrollArea()
        self._day_scroll.setWidgetResizable(True)
        self._day_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._day_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._day_scroll.setWidget(self._day_body)

        self._day_panel = QWidget()
        self._day_panel.setObjectName("ticktickDayPanel")
        day_layout = QVBoxLayout(self._day_panel)
        day_layout.setContentsMargins(8, 0, 0, 0)
        day_layout.setSpacing(4)
        day_layout.addWidget(self._day_title)
        day_layout.addWidget(self._day_count)
        day_layout.addWidget(self._day_scroll, stretch=1)

        self._drawer = QDialog(self)
        self._drawer.setWindowTitle("Day details")
        self._drawer.setModal(False)
        self._drawer_layout = QVBoxLayout(self._drawer)
        self._drawer_layout.setContentsMargins(12, 12, 12, 12)

        center = QWidget()
        self._center_layout = QVBoxLayout(center)
        self._center_layout.setContentsMargins(0, 0, 0, 0)
        self._center_layout.setSpacing(8)
        self._center_layout.addWidget(self._heatmap_title, 0)
        self._center_layout.addWidget(self._heatmap, 0)
        self._center_layout.addWidget(self._time_host, 1)
        self._center_layout.addWidget(self._chart_host, 1)

        self._body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._body_splitter.setChildrenCollapsible(False)
        self._body_splitter.setObjectName("ticktickBodySplitter")
        self._body_splitter.addWidget(center)
        self._body_splitter.addWidget(self._day_panel)
        self._body_splitter.setStretchFactor(0, 1)
        self._body_splitter.setStretchFactor(1, 0)
        self._apply_day_width_limits()

        left_pane = QWidget()
        left_pane.setObjectName("ticktickFilters")
        left_pane.setMinimumWidth(_SIDEBAR_MIN)
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(12, 8, 12, 8)
        left_layout.setSpacing(8)

        chart_group = QGroupBox("Chart")
        chart_group.setObjectName("groupBox_ticktick_charts")
        chart_group_layout = QVBoxLayout(chart_group)
        _, self._chart_radios = build_chart_type_radios(chart_group, CHART_MODE_LABELS)
        for radio in self._chart_radios.values():
            chart_group_layout.addWidget(radio)
            radio.toggled.connect(self._on_chart_mode_changed)
        polish_chart_type_group(chart_group)
        left_layout.addWidget(chart_group)
        list_caption = QLabel("List")
        list_caption.setStyleSheet(muted_caption_qss())
        left_layout.addWidget(list_caption)
        left_layout.addWidget(self._project_combo)
        left_layout.addStretch(1)
        self._db_button = QPushButton("Database")
        self._db_button.setFlat(True)
        self._db_button.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(self._db_button)

        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(8, 0, 8, 8)
        workspace_layout.setSpacing(6)
        toolbar = ChartToolbar()
        toolbar_frame = toolbar.build(workspace)
        self._day_button = QPushButton("Day details")
        self._day_button.clicked.connect(self._open_day_drawer)
        toolbar.set_extra_slot(self._day_button)
        workspace_layout.addWidget(toolbar_frame, 0)
        workspace_layout.addWidget(self._metrics, 0)
        workspace_layout.addWidget(self._body_splitter, 1)
        toolbar.polish()
        toolbar.connect_changed(self._on_filters_changed)
        toolbar.connect_refresh(self.reload)
        toolbar.connect_presets(prev_year=self._on_prev_year, next_year=self._on_next_year)
        self._chart_toolbar = toolbar

        self._root_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._root_splitter.setChildrenCollapsible(False)
        self._root_splitter.addWidget(left_pane)
        self._root_splitter.addWidget(workspace)
        self._root_splitter.setStretchFactor(0, 0)
        self._root_splitter.setStretchFactor(1, 1)
        self._root_splitter.setSizes([_SIDEBAR_WIDTH, 1000])
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._root_splitter)

        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(120)
        self._resize_timer.timeout.connect(self._redraw_timeline)

        self._project_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._heatmap.day_clicked.connect(self._on_heatmap_day)
        bind_theme(self, self._on_theme_changed)
        self._sync_mode_controls()
        if autoload:
            self.reload()

    def ensure_loaded(self) -> None:
        """Load TickTick data once when the tab is first shown."""
        if not self._loaded:
            self.reload()

    def reload(self) -> None:
        """Read the TickTick database again and redraw the current chart."""
        self._loaded = True
        try:
            projects, completions, source = load_ticktick_snapshot(self._db_path)
        except TickTickDbError as exc:
            self._projects = []
            self._completions = []
            self._stats = None
            self._metrics.hide()
            self._db_button.setToolTip("")
            self._clear_chart(str(exc))
            self._show_span_message("TickTick database is not available.")
            self._project_combo.blockSignals(True)  # noqa: FBT003
            self._project_combo.clear()
            self._project_combo.blockSignals(False)  # noqa: FBT003
            return
        self._projects = projects
        self._completions = completions
        self._db_button.setToolTip(str(source))
        self._repopulate_filters()
        self._redraw()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Collapse the day column into a drawer when the window is narrow."""
        super().resizeEvent(event)
        narrow = self.width() < _NARROW_WIDTH
        if narrow != self._narrow:
            self._narrow = narrow
            self._place_day_panel()
            self._sync_day_button()
        self._resize_timer.start()

    def _apply_day_width_limits(self) -> None:
        self._day_panel.setMinimumWidth(_DAY_MIN)
        self._day_panel.setMaximumWidth(_DAY_MAX)

    def _chart_mode(self) -> ChartMode:
        for key, radio in self._chart_radios.items():
            if radio.isChecked() and key in {
                CHART_MODE_HEATMAP,
                CHART_MODE_BY_YEAR,
                CHART_MODE_BY_MONTH,
                CHART_MODE_COMPARE_LAST,
                CHART_MODE_COMPARE_SAME,
            }:
                return key
        return CHART_MODE_HEATMAP

    def _clear_chart(self, message: str) -> None:
        self._release_host(self._chart_layout)
        self._chart_canvas = None
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chart_layout.addWidget(label)

    def _clear_timeline(self) -> None:
        self._release_host(self._time_layout)
        self._time_canvas = None

    def _dock_day_panel(self) -> None:
        self._drawer.hide()
        self._apply_day_width_limits()
        if self._body_splitter.indexOf(self._day_panel) < 0:
            self._body_splitter.addWidget(self._day_panel)
        self._day_panel.show()
        total = max(self._body_splitter.width(), _DAY_WIDTH + 480)
        self._body_splitter.setSizes([max(total - _DAY_WIDTH, 200), _DAY_WIDTH])

    def _figure_size(self, host: QWidget) -> tuple[float, float]:
        width = max(host.width(), 480)
        height = max(host.height(), 220)
        return (width / 100, height / 100)

    def _fill_day_tasks(self, rows: list[TickTickCompletion]) -> None:
        while self._day_list_layout.count():
            item = self._day_list_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        if not rows:
            empty = QLabel("No completed tasks on this day")
            empty.setWordWrap(True)
            empty.setStyleSheet(muted_caption_qss())
            self._day_list_layout.addWidget(empty, alignment=Qt.AlignmentFlag.AlignTop)
            self._day_list_layout.addStretch(1)
            return
        for index, task in enumerate(rows):
            self._day_list_layout.addWidget(_task_block(task))
            if index + 1 < len(rows):
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                self._day_list_layout.addWidget(line)
        self._day_list_layout.addStretch(1)

    def _heatmap_colors(self, stats: TickTickPeriodStats) -> tuple[dict[date, str | None], list[tuple[str, str]]]:
        ranges = quantile_intensity_ranges(stats.counts_by_day.values(), max_bins=4)
        scale = accent_heatmap_colors(len(ranges))
        zero = heatmap_zero_color()
        colors: dict[date, str | None] = {}
        tips: dict[date, str] = {}
        for day in calendar_days(stats.start_date, stats.end_date):
            count = int(stats.counts_by_day.get(day, 0))
            tips[day] = heatmap_cell_tooltip(day, count)
            if count <= 0 or not scale:
                colors[day] = zero
                continue
            index = map_value_to_intensity_bin(count, ranges) - 1
            colors[day] = scale[max(0, min(index, len(scale) - 1))]
        legend = [(zero, "0")]
        legend.extend((color, intensity_bin_label(lo, hi)) for (lo, hi), color in zip(ranges, scale, strict=True))
        self._heatmap_tips = tips
        return colors, legend

    def _on_chart_mode_changed(self) -> None:
        sender = self.sender()
        if isinstance(sender, QRadioButton) and not sender.isChecked():
            return
        self._selected_start = None
        self._selected_end = None
        self._sync_mode_controls()
        self._redraw()

    def _on_filters_changed(self) -> None:
        self._selected_start = None
        self._selected_end = None
        self._redraw()

    def _on_heatmap_day(self, day: object) -> None:
        if isinstance(day, datetime) or not isinstance(day, date) or self._stats is None:
            return
        if day < self._stats.start_date or day > self._stats.end_date:
            return
        self._selected_start = day
        self._selected_end = day
        self._heatmap.set_selected({day})
        self._show_span(day, day)
        self._redraw_timeline()

    def _on_next_year(self) -> None:
        self._step_year(1)

    def _on_prev_year(self) -> None:
        self._step_year(-1)

    def _on_theme_changed(self) -> None:
        if self._loaded:
            self._redraw()

    def _on_timeline_click(self, event: MouseEvent) -> None:
        if event.xdata is None or not self._timeline_bars:
            return
        bar = bar_at_x(self._timeline_bars, float(event.xdata))
        if bar is None:
            return
        self._selected_start = bar.start
        self._selected_end = bar.end
        self._heatmap.set_selected(set(calendar_days(bar.start, bar.end)))
        self._show_span(bar.start, bar.end)
        self._redraw_timeline()

    def _open_day_drawer(self) -> None:
        self._undock_day_panel()
        self._day_panel.show()
        self._drawer.resize(340, max(self.height() - 40, 320))
        self._drawer.show()
        self._drawer.raise_()

    def _place_day_panel(self) -> None:
        if self._chart_mode() == CHART_MODE_HEATMAP and not self._narrow:
            self._dock_day_panel()
            return
        self._undock_day_panel()
        if self._chart_mode() != CHART_MODE_HEATMAP:
            self._drawer.hide()
            self._day_panel.hide()

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
        toolbar = self._chart_toolbar
        months = toolbar.count_value() if toolbar is not None else _DEFAULT_COMPARE_COUNT
        month_counts = counts_by_month(self._completions, months, project_id=project_id)
        if not month_counts:
            self._clear_chart("No completed tasks in this period.")
            return
        self._show_figure(build_month_counts_chart(month_counts, figsize=self._figure_size(self._chart_host)))

    def _redraw_by_year(self, project_id: str | None) -> None:
        year_counts = counts_by_year(self._completions, project_id=project_id)
        if not year_counts:
            self._clear_chart("No completed tasks in this period.")
            return
        self._show_figure(build_year_counts_chart(year_counts, figsize=self._figure_size(self._chart_host)))

    def _redraw_compare_last(self, project_id: str | None) -> None:
        toolbar = self._chart_toolbar
        months = toolbar.count_value() if toolbar is not None else _DEFAULT_COMPARE_COUNT
        series = compare_last_months_series(self._completions, months, project_id=project_id)
        if not series or all(not item.points for item in series):
            self._clear_chart(f"No data for the last {months} months.")
            return
        title = f"Completed tasks (Last {months} months comparison)"
        self._show_figure(build_compare_months_chart(series, title=title, figsize=self._figure_size(self._chart_host)))

    def _redraw_compare_same(self, project_id: str | None) -> None:
        toolbar = self._chart_toolbar
        years = toolbar.count_value() if toolbar is not None else _DEFAULT_COMPARE_COUNT
        month = toolbar.month_number() if toolbar is not None else datetime.now().astimezone().month
        series = compare_same_months_series(self._completions, month, years, project_id=project_id)
        month_name = calendar.month_name[month]
        if not series or all(not item.points for item in series):
            self._clear_chart(f"No data for {month_name.lower()} in the last {years} years.")
            return
        title = f"Completed tasks ({month_name} comparison, last {years} years)"
        self._show_figure(build_compare_months_chart(series, title=title, figsize=self._figure_size(self._chart_host)))

    def _redraw_heatmap(self, project_id: str | None) -> None:
        start_date, end_date = resolve_period(year=self._selected_year())
        self._stats = aggregate_completions(self._completions, start_date, end_date, project_id=project_id)
        self._set_metrics(self._stats)
        self._sync_year_nav_buttons()
        if self._selected_start is None or self._selected_start < start_date or self._selected_start > end_date:
            day = min(end_date, datetime.now().astimezone().date())
            self._selected_start = day
            self._selected_end = day
        colors, legend = self._heatmap_colors(self._stats)
        selected = set(calendar_days(self._selected_start, self._selected_end or self._selected_start))
        self._heatmap.set_calendar(
            start_date,
            end_date,
            colors,
            legend=legend,
            tooltips=getattr(self, "_heatmap_tips", {}),
            selected=selected,
        )
        self._show_span(self._selected_start, self._selected_end or self._selected_start)
        self._redraw_timeline()

    def _redraw_timeline(self) -> None:
        if self._chart_mode() != CHART_MODE_HEATMAP or self._stats is None:
            return
        stats = self._stats
        bars, weekly = task_timeline_bars(
            stats.counts_by_day,
            stats.start_date,
            stats.end_date,
            width_px=max(self._time_host.width(), 480),
        )
        self._timeline_bars = bars
        self._timeline_weekly = weekly
        title = "Completed tasks over time"
        if weekly:
            title = "Completed tasks over time, weekly totals"
        figure = build_timeline_figure(
            bars,
            title=title,
            ylabel="Tasks per week" if weekly else "Tasks",
            bar_label="Weekly totals" if weekly else "Completed tasks",
            line_label="7-day average, tasks/day",
            figsize=self._figure_size(self._time_host),
            selected_start=self._selected_start,
            selected_end=self._selected_end,
            line_on_twin=weekly,
            line_ylabel="7-day average, tasks/day" if weekly else "",
        )
        self._show_timeline(figure)

    def _release_host(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()

    def _repopulate_filters(self) -> None:
        self._project_combo.blockSignals(True)  # noqa: FBT003
        current_project = self._project_combo.currentData()
        self._project_combo.clear()
        self._project_combo.addItem("All lists", _ALL_PROJECTS)
        for project in self._projects:
            self._project_combo.addItem(project.name, project.id)
        project_index = self._project_combo.findData(current_project)
        self._project_combo.setCurrentIndex(max(project_index, 0))
        self._project_combo.blockSignals(False)  # noqa: FBT003

        years = available_years(self._completions)
        choices: list[tuple[str, object]] = [(LAST_365_DAYS_LABEL, None)]
        choices.extend((str(year), year) for year in reversed(years))
        toolbar = self._chart_toolbar
        if toolbar is not None:
            toolbar.set_period_choices(choices, current=self._selected_year_text())
        self._sync_year_nav_buttons()

    def _rows_between(self, start: date, end: date) -> list[TickTickCompletion]:
        if self._stats is None:
            return []
        rows: list[TickTickCompletion] = []
        for day in calendar_days(start, end):
            rows.extend(self._stats.completions_by_day.get(day, []))
        rows.sort(key=lambda item: item.completed_at)
        return rows

    def _selected_project_id(self) -> str | None:
        data = self._project_combo.currentData()
        if data is None or data == _ALL_PROJECTS:
            return None
        return str(data)

    def _selected_year(self) -> int | None:
        toolbar = self._chart_toolbar
        combo = toolbar.combo_period if toolbar is not None else None
        if combo is None:
            return None
        data = combo.currentData()
        return int(data) if isinstance(data, int) else None

    def _selected_year_text(self) -> str:
        toolbar = self._chart_toolbar
        combo = toolbar.combo_period if toolbar is not None else None
        if combo is None or not combo.currentText():
            return LAST_365_DAYS_LABEL
        return combo.currentText()

    def _set_metrics(self, stats: TickTickPeriodStats) -> None:
        busiest = "none"
        if stats.busiest_day is not None and stats.busiest_count > 0:
            busiest = (
                f"{fmt_number(stats.busiest_count, decimals=0)} · "
                f"{stats.busiest_day.day} {calendar.month_abbr[stats.busiest_day.month]}"
            )
        self._metrics.set_metrics(
            [
                ("Completed", fmt_number(stats.total_completions, decimals=0)),
                ("Active days", fmt_number(stats.active_days, decimals=0)),
                ("Current streak", str(stats.current_streak)),
                ("Longest streak", str(stats.longest_streak)),
                ("Busiest day", busiest),
            ],
        )
        self._metrics.show()

    def _show_figure(self, figure: Figure) -> None:
        self._release_host(self._chart_layout)
        canvas = create_chart_canvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._chart_layout.addWidget(canvas, stretch=1)
        self._chart_canvas = canvas
        canvas.draw()

    def _show_span(self, start: date, end: date) -> None:
        rows = self._rows_between(start, end)
        count = len(rows)
        if start == end:
            self._day_title.setText(fmt_date(start))
            noun = "task" if count == 1 else "tasks"
            self._day_count.setText(f"{count} completed {noun}")
        else:
            self._day_title.setText(f"{fmt_date(start)} - {fmt_date(end)}")
            self._day_count.setText(f"{count} completed tasks")
        self._fill_day_tasks(rows)

    def _show_span_message(self, text: str) -> None:
        self._day_title.setText("Selected day")
        self._day_count.setText(text)
        self._fill_day_tasks([])

    def _show_timeline(self, figure: Figure) -> None:
        self._clear_timeline()
        canvas = create_chart_canvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.mpl_connect("button_press_event", self._on_timeline_click)

        def resolve_tooltip(event: MouseEvent) -> str | None:
            if event.xdata is None:
                return None
            bar = bar_at_x(self._timeline_bars, float(event.xdata))
            return None if bar is None else bar.tooltip

        install_chart_hover(canvas, resolve_tooltip=resolve_tooltip)
        self._time_layout.addWidget(canvas, stretch=1)
        canvas.show()
        self._time_canvas = canvas
        canvas.draw()

    def _step_year(self, step: int) -> None:
        toolbar = self._chart_toolbar
        combo = toolbar.combo_period if toolbar is not None else None
        if combo is None:
            return
        # The combo is newest-first. Previous period is the next row.
        index = combo.currentIndex() - step
        if 0 <= index < combo.count():
            combo.setCurrentIndex(index)

    def _sync_day_button(self) -> None:
        toolbar = self._chart_toolbar
        if toolbar is None:
            return
        if self._chart_mode() == CHART_MODE_HEATMAP:
            toolbar.set_mode("heatmap", show_extra=self._narrow)

    def _sync_mode_controls(self) -> None:
        mode = self._chart_mode()
        toolbar = self._chart_toolbar
        if toolbar is None:
            return
        if mode == CHART_MODE_HEATMAP:
            toolbar.set_mode("heatmap", show_extra=self._narrow)
        elif mode == CHART_MODE_BY_YEAR:
            toolbar.set_mode("labels_only")
        elif mode == CHART_MODE_BY_MONTH:
            toolbar.set_mode("count")
        elif mode == CHART_MODE_COMPARE_LAST:
            toolbar.set_mode("compare_last")
        else:
            toolbar.set_mode("compare_same")
        heatmap = mode == CHART_MODE_HEATMAP
        self._metrics.setVisible(heatmap)
        self._heatmap_title.setVisible(heatmap)
        self._heatmap.setVisible(heatmap)
        self._time_host.setVisible(heatmap)
        self._chart_host.setVisible(not heatmap)
        self._place_day_panel()

    def _sync_year_nav_buttons(self) -> None:
        toolbar = self._chart_toolbar
        if toolbar is None or self._chart_mode() != CHART_MODE_HEATMAP:
            return
        prev_btn = toolbar.button_prev_year
        next_btn = toolbar.button_next_year
        combo = toolbar.combo_period
        if prev_btn is None or next_btn is None or combo is None:
            return
        index = combo.currentIndex()
        prev_btn.setEnabled(0 <= index < combo.count() - 1)
        next_btn.setEnabled(index > 0)

    def _undock_day_panel(self) -> None:
        self._day_panel.setMinimumWidth(_DAY_MIN)
        self._day_panel.setMaximumWidth(16_777_215)
        if self._body_splitter.indexOf(self._day_panel) >= 0:
            self._day_panel.setParent(self._drawer)
            self._drawer_layout.addWidget(self._day_panel)


def _chip_qss() -> str:
    palette = FluentTheme.instance().palette()
    background = css(chart_tint(palette.card_bg, palette.text_secondary, 0.14))
    foreground = css(mix(palette.window_bg, palette.text_secondary))
    return f"background: {background}; color: {foreground}; border-radius: 4px; padding: 1px 6px;"


def _task_block(task: TickTickCompletion) -> QWidget:
    block = QWidget()
    block.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    layout = QVBoxLayout(block)
    layout.setContentsMargins(0, 6, 0, 6)
    layout.setSpacing(2)
    time_label = QLabel(task.completed_at.strftime("%H:%M"))
    time_label.setStyleSheet(muted_caption_qss(bold=False))
    title = QLabel(task.title)
    title.setWordWrap(True)
    title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    chip = QLabel(task.project_name)
    chip.setStyleSheet(_chip_qss())
    chip.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    layout.addWidget(time_label)
    layout.addWidget(title)
    layout.addWidget(chip, alignment=Qt.AlignmentFlag.AlignLeft)
    return block
