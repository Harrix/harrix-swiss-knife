"""Commit heatmap charts for the dirty-repos commit window."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.actions.common.git_dirty_ops import (
    COMMIT_SCOPE_LABELS,
    CommitScope,
    configured_git_roots,
    count_commits_by_day,
)
from harrix_swiss_knife.apps.common.chart_format import fmt_number
from harrix_swiss_knife.apps.common.chart_hover import create_chart_canvas, install_chart_hover
from harrix_swiss_knife.apps.common.chart_page_chrome import MetricStrip, build_chart_type_radios
from harrix_swiss_knife.apps.common.chart_timeline import bar_at_x, build_timeline_figure
from harrix_swiss_knife.apps.common.year_heatmap import YearHeatmap
from harrix_swiss_knife.apps.habits.habit_process_charts import (
    habit_calendar_model,
    habit_legend_colors,
    habit_period_stats,
    habit_timeline_bars,
    habit_token_color,
)
from harrix_swiss_knife.fluent.tokens import SPACE_M, SPACE_S, SPACE_XL
from harrix_swiss_knife.fluent.widgets import FluentPushButton, FluentText, TextRole
from harrix_swiss_knife.toast_notification import ToastNotification

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

_CHART_PERIOD_DAYS = 365
_SIDEBAR_WIDTH = 220


class GitCommitChartsPage(QWidget):
    """Heatmap + timeline of commits under `paths_git_roots`, filtered by scope."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the charts page with a scope sidebar and heatmap body."""
        super().__init__(parent)
        self.setObjectName("gitCommitChartsPage")
        self._scope: CommitScope = "all"
        self._recorded: dict[date, int] = {}
        self._start: date | None = None
        self._end: date | None = None
        self._busy = False
        self._worker: _CommitsChartWorker | None = None
        self._timeline_bars: list[Any] = []
        self._timeline_canvas: FigureCanvas | None = None

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
        self._period_label = FluentText("Last 365 days", body, role=TextRole.SECONDARY)
        toolbar.addWidget(self._period_label, 1)
        self._refresh_button = FluentPushButton("Refresh", body, icon="refresh-cw")
        self._refresh_button.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_button)
        body_layout.addLayout(toolbar)

        self._metrics = MetricStrip(body)
        body_layout.addWidget(self._metrics)

        self._title = QLabel("Commits", body)
        self._title.setObjectName("gitCommitChartsTitle")
        body_layout.addWidget(self._title)

        self._heatmap = YearHeatmap(body)
        body_layout.addWidget(self._heatmap)

        self._time_host = QWidget(body)
        self._time_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._time_layout = QVBoxLayout(self._time_host)
        self._time_layout.setContentsMargins(0, 0, 0, 0)
        self._time_layout.setSpacing(0)
        body_layout.addWidget(self._time_host, 1)

        self._status = FluentText("", body, role=TextRole.SECONDARY)
        body_layout.addWidget(self._status)
        root.addWidget(body, 1)

    def refresh(self) -> None:
        """Reload commit counts for the current scope on a worker thread."""
        if self._busy:
            return
        today = datetime.now(UTC).astimezone().date()
        end = today
        start = end - timedelta(days=_CHART_PERIOD_DAYS - 1)
        self._start = start
        self._end = end
        self._period_label.setText(f"Last {_CHART_PERIOD_DAYS} days")
        self._status.setText("Loading commits…")
        self._set_busy(busy=True)
        roots = configured_git_roots()
        scope = self._scope
        worker = _CommitsChartWorker(roots, start, end, scope, self)
        worker.finished_ok.connect(self._on_loaded)
        worker.failed.connect(self._on_failed)
        self._worker = worker
        worker.start()

    def showEvent(self, event: Any) -> None:  # noqa: N802
        """Load charts the first time the tab becomes visible."""
        super().showEvent(event)
        if self._start is None and not self._busy:
            self.refresh()

    def _clear_timeline(self) -> None:
        while self._time_layout.count():
            item = self._time_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._timeline_canvas = None
        self._timeline_bars = []

    def _on_failed(self, message: str) -> None:
        self._set_busy(busy=False)
        self._status.setText(message)
        ToastNotification(message, duration=2500, parent=self)

    def _on_loaded(self, recorded: object) -> None:
        self._set_busy(busy=False)
        if not isinstance(recorded, dict):
            self._status.setText("Could not load commits")
            return
        self._recorded = {day: int(value) for day, value in recorded.items() if isinstance(day, date)}
        self._present()

    def _on_scope_toggled(self, scope: str, *, checked: bool) -> None:
        if not checked:
            return
        self._scope = cast("CommitScope", scope)
        self.refresh()

    def _present(self) -> None:
        start = self._start
        end = self._end
        if start is None or end is None:
            return
        today = datetime.now(UTC).astimezone().date()
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
        self._heatmap.set_calendar(
            start,
            end,
            colors,
            legend=habit_legend_colors(legend, bin_count=bin_count),
            marks=marks,
            tooltips=tips,
        )
        stats = habit_period_stats(self._recorded, start, end, is_bool=False, today=today)
        self._metrics.set_metrics(
            [
                ("Total", fmt_number(stats.total, decimals=0)),
                ("Active days", fmt_number(stats.completed, decimals=0)),
                ("Current streak", fmt_number(stats.current_streak, decimals=0)),
                ("Longest streak", fmt_number(stats.longest_streak, decimals=0)),
            ],
        )
        label = next((text for key, text in COMMIT_SCOPE_LABELS if key == self._scope), "Commits")
        self._title.setText(label)
        bars, _percent = habit_timeline_bars(self._recorded, start, end, is_bool=False, today=today)
        self._timeline_bars = bars
        self._show_timeline(bars)
        total = stats.total
        noun = "commit" if total == 1 else "commits"
        self._status.setText(f"{fmt_number(total, decimals=0)} {noun} in the selected period")

    def _set_busy(self, *, busy: bool) -> None:
        self._busy = busy
        self._refresh_button.setEnabled(not busy)
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


class _CommitsChartWorker(QThread):
    """Load per-day commit counts off the UI thread."""

    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        roots: list[Path],
        start: date,
        end: date,
        scope: CommitScope,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._roots = roots
        self._start = start
        self._end = end
        self._scope = scope

    def run(self) -> None:
        try:
            self.finished_ok.emit(
                count_commits_by_day(self._roots, self._start, self._end, scope=self._scope),
            )
        except Exception as exc:
            self.failed.emit(str(exc))


def _commit_cell_tip(day: date, value: int) -> str:
    when = day.isoformat()
    if value <= 0:
        return f"{when}\nNo commits"
    noun = "commit" if value == 1 else "commits"
    return f"{when}\n{fmt_number(value, decimals=0)} {noun}"
