"""Amount delegate for formatting amounts in finance tables."""

from __future__ import annotations

import logging
import re
from typing import Any, cast

from PySide6.QtCore import QAbstractItemModel, QLocale, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPalette
from PySide6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import BUTTON_SUCCESS_BG
from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background
from harrix_swiss_knife.apps.finance.number_utils import format_amount
from harrix_swiss_knife.apps.finance.transaction_day_totals import is_income_category_display
from harrix_swiss_knife.fluent.theme import palette_for
from harrix_swiss_knife.qt_compact_spin_box import CompactDoubleSpinBox

logger = logging.getLogger(__name__)

_INCOME_TEXT = QColor(BUTTON_SUCCESS_BG)


class AmountDelegate(QStyledItemDelegate):
    """Delegate for amount columns with subscript decimals, currency, and income chrome.

    Formatting includes thousands separators, subscript decimals, an optional
    currency symbol suffix, and bold green text for income amounts.

    """

    def __init__(
        self,
        parent: QWidget | None = None,
        db_manager: object = None,
        *,
        currency_column: int | None = None,
        use_default_currency: bool = False,
        category_column: int | None = None,
        amount_column: int | None = None,
        total_per_day: bool = False,
    ) -> None:
        """Initialize the amount delegate.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `db_manager` (`object | None`): Database manager for currency symbols.
        - `currency_column` (`int | None`): Column with a currency code for the symbol.
        - `use_default_currency` (`bool`): Use the project default currency symbol.
        - `category_column` (`int | None`): Category column used to detect income rows.
        - `amount_column` (`int | None`): Column index that applies expense/income sign
          rules when editing (transactions Amount).
        - `total_per_day` (`bool`): Honor per-cell alignment used by day spans.

        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.currency_column = currency_column
        self.use_default_currency = use_default_currency
        self.category_column = category_column
        self.amount_column = amount_column
        self.total_per_day = total_per_day

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create editor for amount editing."""
        editor = CompactDoubleSpinBox(parent)
        editor.setRange(-999999999.99, 999999999.99)
        editor.setDecimals(2)
        editor.setGroupSeparatorShown(False)
        apply_white_editor_background(editor, "QDoubleSpinBox")
        return editor

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Format display text with spaces and subscript decimals."""
        try:
            return format_amount(value)
        except Exception:
            logger.exception("Error while formatting amount")
            return str(value)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint amount with optional income styling and currency suffix."""
        try:
            raw_value = index.data(Qt.ItemDataRole.DisplayRole)
            if raw_value is None or (isinstance(raw_value, str) and not str(raw_value).strip()):
                super().paint(painter, option, index)
                return

            amount_text = self.displayText(raw_value, QLocale())
            symbol = self._currency_symbol(index)
            display_text = f"{amount_text}{symbol}" if symbol else amount_text

            is_income = self._is_income_row(index)
            if self.total_per_day:
                alignment = int(_total_per_day_alignment(index.data(Qt.ItemDataRole.TextAlignmentRole)))
            else:
                alignment = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

            painter.save()
            brush = index.data(Qt.ItemDataRole.BackgroundRole)
            if isinstance(brush, QBrush) and brush.style() != Qt.BrushStyle.NoBrush:
                painter.fillRect(option.rect, brush)

            font = QFont(option.font)
            font.setStyleHint(QFont.StyleHint.SansSerif)
            if is_income:
                font.setBold(True)
            painter.setFont(font)

            if is_income:
                painter.setPen(self._income_pen_color(option))
            else:
                painter.setPen(option.palette.color(QPalette.ColorRole.Text))

            top_pad = 3 if alignment & Qt.AlignmentFlag.AlignTop else 0
            painter.drawText(option.rect.adjusted(5, top_pad, -5, 0), alignment, display_text)
            painter.restore()
        except Exception:
            super().paint(painter, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set data in editor (without spaces / currency / subscripts)."""
        spin = cast("QDoubleSpinBox", editor)
        try:
            text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
            clean_text = re.sub(r"[^\d.-]", "", text.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")))
            spin.setValue(float(clean_text) if clean_text not in {"", "-", ".", "-."} else 0.0)
        except (ValueError, TypeError):
            spin.setValue(0.0)

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Set data from editor back to model."""
        spin = cast("QDoubleSpinBox", editor)
        value = spin.value()

        if self.amount_column is not None and index.column() == self.amount_column and self.category_column is not None:
            category_text = model.data(model.index(index.row(), self.category_column), Qt.ItemDataRole.DisplayRole)
            is_income = is_income_category_display(str(category_text or ""))
            if not is_income:
                if value > 0:
                    value = -value
            elif value < 0:
                value = abs(value)

        formatted_value = f"{value:.2f}"
        model.setData(index, formatted_value, Qt.ItemDataRole.DisplayRole)
        model.setData(index, formatted_value, Qt.ItemDataRole.EditRole)

    def _currency_symbol(self, index: QModelIndex | QPersistentModelIndex) -> str:
        db = cast("Any", self.db_manager)
        if db is None:
            return ""
        try:
            if self.use_default_currency:
                code = db.get_default_currency()
            elif self.currency_column is not None:
                model = index.model()
                if model is None:
                    return ""
                code = model.data(model.index(index.row(), self.currency_column), Qt.ItemDataRole.DisplayRole)
            else:
                return ""
            code_text = str(code or "").strip()
            if not code_text:
                return ""
            info = db.get_currency_by_code(code_text)
            if not info:
                return ""
            return str(info[2] or "")
        except Exception:
            logger.exception("Error resolving currency symbol for amount cell")
            return ""

    def _income_pen_color(self, option: QStyleOptionViewItem) -> QColor:
        host = option.widget if isinstance(option.widget, QWidget) else None
        try:
            return palette_for(host).success
        except Exception:
            return _INCOME_TEXT

    def _is_income_row(self, index: QModelIndex | QPersistentModelIndex) -> bool:
        if self.category_column is None:
            return False
        model = index.model()
        if model is None:
            return False
        category_text = model.data(model.index(index.row(), self.category_column), Qt.ItemDataRole.DisplayRole)
        return is_income_category_display(str(category_text or ""))


def _total_per_day_alignment(stored: object) -> Qt.AlignmentFlag:
    """Use the cell alignment, keeping totals left-aligned and centered by default."""
    default = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    if isinstance(stored, Qt.AlignmentFlag):
        flags = stored
    elif isinstance(stored, int) and not isinstance(stored, bool) and stored != 0:
        flags = Qt.AlignmentFlag(stored)
    else:
        return default
    if not (flags & Qt.AlignmentFlag.AlignHorizontal_Mask):
        flags |= Qt.AlignmentFlag.AlignLeft
    if not (flags & Qt.AlignmentFlag.AlignVertical_Mask):
        flags |= Qt.AlignmentFlag.AlignVCenter
    return flags
