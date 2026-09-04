"""Wrapping flow layout for Qt widgets (left-to-right, top-to-bottom)."""

from __future__ import annotations

from typing import cast

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QStyle, QWidget


class FlowLayout(QLayout):
    """Lay out child widgets in rows that wrap when the width is too small."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        margin: int = -1,
        h_spacing: int = -1,
        v_spacing: int = -1,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        """Create an empty flow layout.

        Args:

        - `parent` (`QWidget | None`): Optional parent widget.
        - `margin` (`int`): Uniform contents margin; `-1` keeps the style default.
        - `h_spacing` (`int`): Horizontal gap; `-1` uses style spacing.
        - `v_spacing` (`int`): Vertical gap; `-1` uses style spacing.
        - `alignment` (`Qt.AlignmentFlag`): Horizontal alignment of each row
          (`AlignLeft`, `AlignRight`, or `AlignHCenter`).

        """
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._alignment = alignment
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem) -> None:  # noqa: N802
        """Append `item` to the flow."""
        self._items.append(item)

    def count(self) -> int:
        """Return the number of items."""
        return len(self._items)

    def expandingDirections(self) -> Qt.Orientation:  # noqa: N802
        """Flow layouts do not expand in either direction by themselves."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        """Height depends on the available width."""
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        """Return the height needed to lay out items in `width` pixels."""
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def itemAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        """Return the item at `index`, or `None`."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def minimumSize(self) -> QSize:  # noqa: N802
        """Return the size that fits the largest single child plus margins."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self._margins()
        size += QSize(left + right, top + bottom)
        return size

    def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        """Position children inside `rect`."""
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Prefer the minimum size that can fit every child."""
        return self.minimumSize()

    def takeAt(self, index: int) -> QLayoutItem | None:  # noqa: N802
        """Remove and return the item at `index`."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def _build_rows(self, available_width: int, space_x: int) -> list[list[tuple[QLayoutItem, QSize]]]:
        rows: list[list[tuple[QLayoutItem, QSize]]] = []
        current: list[tuple[QLayoutItem, QSize]] = []
        x = 0
        for item in self._items:
            size = item.sizeHint()
            space_x_eff = self._item_spacing(item, horizontal=True, fallback=space_x)
            needed = size.width() if not current else size.width() + space_x_eff
            if current and x + needed > available_width:
                rows.append(current)
                current = []
                x = 0
                needed = size.width()
            current.append((item, size))
            x += needed
        if current:
            rows.append(current)
        return rows

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        left, top, right, bottom = self._margins()
        effective = rect.adjusted(left, top, -right, -bottom)
        space_x = self._horizontal_spacing()
        space_y = self._vertical_spacing()
        rows = self._build_rows(effective.width(), space_x)

        y = effective.y()
        for row_index, row in enumerate(rows):
            row_width = sum(size.width() for _item, size in row)
            if len(row) > 1:
                row_width += space_x * (len(row) - 1)
            x = self._row_start_x(effective, row_width)
            line_height = 0
            for item, size in row:
                if not test_only:
                    item.setGeometry(QRect(QPoint(x, y), size))
                x += size.width() + space_x
                line_height = max(line_height, size.height())
            y += line_height
            if row_index + 1 < len(rows):
                y += space_y

        if not rows:
            return top + bottom
        return y - rect.y() + bottom

    def _horizontal_spacing(self) -> int:
        if self._h_spacing >= 0:
            return self._h_spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def _item_spacing(self, item: QLayoutItem, *, horizontal: bool, fallback: int) -> int:
        if horizontal and self._h_spacing >= 0:
            return self._h_spacing
        if not horizontal and self._v_spacing >= 0:
            return self._v_spacing
        widget = item.widget()
        if widget is None:
            return fallback
        orientation = Qt.Orientation.Horizontal if horizontal else Qt.Orientation.Vertical
        return widget.style().layoutSpacing(
            QSizePolicy.ControlType.PushButton,
            QSizePolicy.ControlType.PushButton,
            orientation,
        )

    def _margins(self) -> tuple[int, int, int, int]:
        return cast("tuple[int, int, int, int]", self.getContentsMargins())

    def _row_start_x(self, effective: QRect, row_width: int) -> int:
        if self._alignment & Qt.AlignmentFlag.AlignRight:
            return effective.x() + max(0, effective.width() - row_width)
        if self._alignment & Qt.AlignmentFlag.AlignHCenter:
            return effective.x() + max(0, (effective.width() - row_width) // 2)
        return effective.x()

    def _smart_spacing(self, metric: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent.style().pixelMetric(metric, None, parent)
        return self.spacing()

    def _vertical_spacing(self) -> int:
        if self._v_spacing >= 0:
            return self._v_spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)
