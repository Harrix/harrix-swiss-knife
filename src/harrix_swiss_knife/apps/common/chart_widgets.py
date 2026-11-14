"""Chart page shell: card, KPI row, year navigator, and sidebar.

Surfaces paint through Fluent cards and `bind_theme`. Chart pages in later
stages drop their plots into `ChartPage` instead of inventing another layout.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QHelpEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.apps.common.ui_chrome import button_idle_qss
from harrix_swiss_knife.fluent.paint import with_alpha
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_M, SPACE_S, SPACE_XS
from harrix_swiss_knife.fluent.widgets.card_base import FluentCard
from harrix_swiss_knife.fluent.widgets.enums import TextStyle
from harrix_swiss_knife.fluent.widgets.text import CaptionLabel
from harrix_swiss_knife.fluent.widgets.text_base import FluentText
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon, make_lucide_push_button

if TYPE_CHECKING:
    from PySide6.QtGui import QStandardItem

LAST_365_KEY = "last_365"
ALL_YEARS_KEY = "all"
_SIDEBAR_MIN = 220
_SIDEBAR_MAX = 420
_SIDEBAR_DEFAULT = 300
_BOTTOM_MIN_HEIGHT = 240
_SPLITTER_PANES = 2
_KPI_MIN = 3
_KPI_MAX = 6


class ChartCard(FluentCard):
    """Bordered chart card with the title in the header, not inside Matplotlib."""

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


class ChartPage(QWidget):
    """Sidebar plus toolbar, KPI row, main chart, and a bottom detail row.

    The bottom row is about two fifths of the page and at least 240 px.
    The page scrolls when the window is shorter than the content.

    """

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


class ChartSidebar(QWidget):
    """Filter column: section titles without colons, lists elide with a tooltip."""

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


class KpiCard(FluentCard):
    """One metric: muted caption, large value, optional trend line and icon."""

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


class KpiRow(QWidget):
    """Three to six equal-width KPI cards."""

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


@dataclass(frozen=True, slots=True)
class KpiSpec:
    """One KPI card: caption, value, optional detail line and Lucide icon."""

    caption: str
    value: str
    detail: str = ""
    trend: str = "flat"
    icon: str = ""


class YearNavigator(QWidget):
    """Compact previous / next control for Last 365 days, years, and All years.

    Items are Last 365 days, calendar years newest first, then All years.
    The arrows move to the neighboring item.

    """

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


class _ListElideTip(QObject):
    """Show the full item text when the row is elided."""

    def __init__(self, view: QAbstractItemView) -> None:
        super().__init__(view)
        self._view = view

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Show a tooltip with the full item text."""
        if watched is self._view.viewport() and isinstance(event, QHelpEvent):
            index = self._view.indexAt(event.pos())
            if index.isValid():
                text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
                if text:
                    QToolTip.showText(event.globalPos(), text, self._view)
                    return True
        return super().eventFilter(watched, event)


def apply_chart_list_chrome(view: QAbstractItemView) -> None:
    """Select rows with a light accent fill and a 3 px accent bar."""

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


def kpi_row_limits() -> tuple[int, int]:
    """Return the supported KPI card count, `(3, 6)` is the design range."""
    return (_KPI_MIN, _KPI_MAX)


def mark_chart_list_separator(item: QStandardItem) -> None:
    """Make a dash row a non-selectable divider."""
    item.setEnabled(False)
    item.setSelectable(False)
    item.setFlags(Qt.ItemFlag.NoItemFlags)
