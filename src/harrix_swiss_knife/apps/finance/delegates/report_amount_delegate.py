"""Report amount delegate for formatting amounts in reports without editing."""

from __future__ import annotations

import logging
import re

from PySide6.QtCore import QLocale, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.finance.number_utils import format_amount

logger = logging.getLogger(__name__)


class ReportAmountDelegate(QStyledItemDelegate):
    """Delegate for amount columns in reports with read-only formatting.

    This delegate provides custom formatting for amount values in reports,
    including thousands separators and subscript decimals, without editing capability.

    """

    def __init__(self, parent: QWidget | None = None, *, is_bold: bool = False) -> None:
        """Initialize the report amount delegate.

        Args:

        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
        - `is_bold` (`bool`): Whether to display text in bold. Defaults to `False`.

        """
        super().__init__(parent)
        self.is_bold = is_bold

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Format display text with spaces for thousands separator and subscript decimals."""
        try:
            text = str(value)
            # Preserve a non-numeric suffix (e.g. currency already in the cell).
            match = re.match(r"^(-?\s*[\d\s₀₁₂₃₄₅₆₇₈₉.]+)(.*)$", text)
            if match is None:
                return format_amount(text)
            number_part, suffix = match.group(1), match.group(2)
            return f"{format_amount(number_part)}{suffix}"
        except Exception:
            logger.exception("Error while formatting amount")
            return str(value)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint cell with bold font if configured.

        Args:

        - `painter` (`QPainter`): The painter used for drawing.
        - `option` (`QStyleOptionViewItem`): The style options for the item.
        - `index` (`QModelIndex`): The model index of the item being painted.

        """
        try:
            if self.is_bold:
                bold_option = QStyleOptionViewItem(option)
                bold_option.font = QFont(option.font)
                bold_option.font.setBold(True)
                super().paint(painter, bold_option, index)
                return

            super().paint(painter, option, index)

        except Exception:
            super().paint(painter, option, index)
