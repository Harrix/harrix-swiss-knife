"""Dialog: TickTick completion contribution calendar from the local DB."""

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.actions.common.ticktick_local_db import (
    TickTickCompletion,
    TickTickDbError,
    TickTickProject,
    load_ticktick_snapshot,
)
from harrix_swiss_knife.actions.common.ticktick_task_stats import (
    LAST_365_DAYS_LABEL,
    TickTickHeatmapResult,
    TickTickPeriodStats,
    aggregate_completions,
    available_years,
    build_contribution_heatmap,
    day_from_heatmap_click,
    format_period_summary,
    resolve_period,
)
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.apps.common.ui_chrome import muted_caption_qss
from harrix_swiss_knife.installer.icon_assets import apply_window_icon
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons, make_lucide_push_button

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from matplotlib.backend_bases import MouseEvent

_ALL_PROJECTS = "__all__"
_HEADERS = ("Time", "Task", "List")


class TickTickTaskStatsDialog(QDialog):
    """Show a GitHub-like completion calendar for local TickTick tasks."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        db_path: Path | None = None,
    ) -> None:
        """Build the dialog and load the first snapshot from ``db_path`` or the default."""
        super().__init__(parent)
        self.setWindowTitle("TickTick task stats")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        apply_window_icon(self)

        self._db_path = db_path
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

        self._period_combo = QComboBox()
        self._project_combo = QComboBox()
        self._heatmap_host = QWidget()
        self._heatmap_layout = QVBoxLayout(self._heatmap_host)
        self._heatmap_layout.setContentsMargins(0, 0, 0, 0)

        self._day_label = QLabel("Click a day on the calendar to list completed tasks.")
        self._day_label.setStyleSheet(muted_caption_qss())

        self._day_table = QTableWidget(0, len(_HEADERS))
        self._day_table.setHorizontalHeaderLabels(list(_HEADERS))
        self._day_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._day_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._day_table.setAlternatingRowColors(True)
        self._day_table.verticalHeader().setVisible(False)
        header = self._day_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._day_table.setMinimumHeight(160)

        filters = QHBoxLayout()
        period_caption = QLabel("Period")
        period_caption.setStyleSheet(muted_caption_qss())
        project_caption = QLabel("List")
        project_caption.setStyleSheet(muted_caption_qss())
        filters.addWidget(period_caption)
        filters.addWidget(self._period_combo, stretch=1)
        filters.addWidget(project_caption)
        filters.addWidget(self._project_combo, stretch=2)

        refresh_button = make_lucide_push_button("Refresh", "refresh-cw")
        refresh_button.clicked.connect(self._reload_from_disk)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        apply_lucide_dialog_buttons(buttons)
        buttons.rejected.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.addWidget(refresh_button)
        button_row.addStretch()
        button_row.addWidget(buttons)

        root = QVBoxLayout(self)
        root.addWidget(self._summary_label)
        root.addWidget(self._source_label)
        root.addLayout(filters)
        root.addWidget(self._heatmap_host, stretch=2)
        root.addWidget(self._day_label)
        root.addWidget(self._day_table, stretch=1)
        root.addLayout(button_row)

        self._period_combo.currentIndexChanged.connect(self._on_filters_changed)
        self._project_combo.currentIndexChanged.connect(self._on_filters_changed)

        self._reload_from_disk()

    def _clear_heatmap(self, message: str) -> None:
        self._release_canvas()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(muted_caption_qss())
        self._heatmap_layout.addWidget(label)
        self._heatmap = None

    def _fill_day_table(self, rows: list[TickTickCompletion]) -> None:
        self._day_table.setRowCount(len(rows))
        for index, item in enumerate(rows):
            time_item = QTableWidgetItem(item.completed_at.strftime("%H:%M:%S"))
            task_item = QTableWidgetItem(item.title)
            list_item = QTableWidgetItem(item.project_name)
            self._day_table.setItem(index, 0, time_item)
            self._day_table.setItem(index, 1, task_item)
            self._day_table.setItem(index, 2, list_item)

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

    def _redraw(self) -> None:
        start_date, end_date = resolve_period(year=self._selected_year())
        self._stats = aggregate_completions(
            self._completions,
            start_date,
            end_date,
            project_id=self._selected_project_id(),
        )
        self._summary_label.setText(format_period_summary(self._stats))
        if self._stats.total_completions == 0:
            self._clear_heatmap("No completed tasks in this period.")
            self._fill_day_table([])
            self._day_label.setText("No completed tasks in this period.")
            return

        width = max(self._heatmap_host.width(), 900)
        height = max(220, min(320, self.height() // 3 if self.height() else 260))
        self._heatmap = build_contribution_heatmap(
            self._stats,
            figsize=(width / 100, height / 100),
            dpi=100,
        )
        self._show_heatmap(self._heatmap)
        if self._selected_day is not None:
            self._show_day(self._selected_day)
        else:
            self._day_label.setText("Click a day on the calendar to list completed tasks.")
            self._fill_day_table([])

    def _release_canvas(self) -> None:
        while self._heatmap_layout.count():
            item = self._heatmap_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._canvas = None

    def _reload_from_disk(self) -> None:
        """Copy the live TickTick DB again and refresh filters/heatmap."""
        try:
            projects, completions, source = load_ticktick_snapshot(self._db_path)
        except TickTickDbError as exc:
            self._projects = []
            self._completions = []
            self._summary_label.setText(str(exc))
            self._source_label.setText("")
            self._clear_heatmap("TickTick database is not available.")
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
        self._source_label.setText(f"Source: {source}")
        self._repopulate_filters()
        self._redraw()

    def _repopulate_filters(self) -> None:
        """Fill period/project combos while preserving the previous selection when possible."""
        prev_period = self._period_combo.currentData()
        prev_project = self._project_combo.currentData()

        self._period_combo.blockSignals(True)  # noqa: FBT003
        self._project_combo.blockSignals(True)  # noqa: FBT003
        self._period_combo.clear()
        self._project_combo.clear()

        self._period_combo.addItem(LAST_365_DAYS_LABEL, None)
        for year in available_years(self._completions):
            self._period_combo.addItem(str(year), year)

        self._project_combo.addItem("All lists", _ALL_PROJECTS)
        for project in self._projects:
            self._project_combo.addItem(project.name, project.id)

        period_index = self._period_combo.findData(prev_period)
        self._period_combo.setCurrentIndex(max(period_index, 0))
        project_index = self._project_combo.findData(prev_project)
        self._project_combo.setCurrentIndex(max(project_index, 0))

        self._period_combo.blockSignals(False)  # noqa: FBT003
        self._project_combo.blockSignals(False)  # noqa: FBT003

    def _selected_project_id(self) -> str | None:
        data = self._project_combo.currentData()
        if data in (None, _ALL_PROJECTS):
            return None
        return str(data)

    def _selected_year(self) -> int | None:
        data = self._period_combo.currentData()
        return int(data) if data is not None else None

    def _show_day(self, day: date) -> None:
        rows = []
        if self._stats is not None:
            rows = list(self._stats.completions_by_day.get(day, []))
        count = len(rows)
        self._day_label.setText(f"{day.isoformat()} — {count} completed task{'s' if count != 1 else ''}")
        self._fill_day_table(rows)

    def _show_heatmap(self, result: TickTickHeatmapResult) -> None:
        self._release_canvas()
        canvas = FigureCanvas(result.figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.mpl_connect("button_press_event", self._on_heatmap_click)
        self._heatmap_layout.addWidget(canvas)
        self._canvas = canvas
        canvas.draw()


def show_ticktick_task_stats_dialog(
    parent: QWidget | None = None,
    *,
    db_path: Path | None = None,
) -> None:
    """Open the TickTick task-stats dialog sized like tracker apps."""
    dialog = TickTickTaskStatsDialog(parent, db_path=db_path)
    apply_app_window_size_and_position(dialog)
    dialog.exec()
