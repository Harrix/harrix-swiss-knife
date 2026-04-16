"""Amount delegate for formatting amounts in transactions table."""

import re
from typing import cast

from PySide6.QtCore import QAbstractItemModel, QLocale, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background


class AmountDelegate(QStyledItemDelegate):
    """Delegate for amount column with custom formatting and editing.

    This delegate provides custom formatting for amount values in the
    transactions table, including thousands separators, subscript decimals,
    and special formatting for income transactions.

    """

    def __init__(self, parent: QWidget | None = None, db_manager: object = None) -> None:
        """Initialize the amount delegate.

        Args:

        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
        - `db_manager` (`object | None`): The database manager instance. Defaults to `None`.

        """
        super().__init__(parent)
        self.db_manager = db_manager

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create editor for amount editing.

        Args:

        - `parent` (`QWidget`): The parent widget for the editor.
        - `_option` (`QStyleOptionViewItem`): The style options for the item.
        - `_index` (`QModelIndex`): The model index of the item being edited.

        Returns:

        - `QDoubleSpinBox`: A configured double spin box editor for amount input.

        """
        editor = QDoubleSpinBox(parent)
        editor.setRange(-999999999.99, 999999999.99)
        editor.setDecimals(2)
        editor.setGroupSeparatorShown(False)  # No separators in editor

        apply_white_editor_background(editor, "QDoubleSpinBox")

        return editor

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Format display text with spaces for thousands separator and subscript decimals.

        Args:

        - `value` (`object`): The value to format for display.
        - `_locale` (`QLocale | None`): The locale for formatting (unused in this implementation).

        Returns:

        - `str`: The formatted text with spaces as thousands separators and subscript decimal digits.

        """
        try:
            # Get the raw text value
            text = str(value)

            # Check if it's a negative number (starts with -)
            is_negative = text.startswith("-")

            # Remove minus sign for processing
            if is_negative:
                text = text[1:]

            # Try to parse as float
            try:
                num = float(text)
            except (ValueError, TypeError):
                return str(value)  # Return original if can't parse

            # Format with spaces as thousands separator
            # Split into integer and decimal parts
            if "." in str(num):
                integer_part, decimal_part = str(num).split(".")
            else:
                integer_part = str(int(num))
                decimal_part = "00"

            # Add spaces every 3 digits from right to left
            formatted_integer = ""
            for i, digit in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    formatted_integer = " " + formatted_integer
                formatted_integer = digit + formatted_integer

            # Convert decimal digits to subscript Unicode characters
            subscript_map = {
                "0": "₀",
                "1": "₁",
                "2": "₂",
                "3": "₃",
                "4": "₄",
                "5": "₅",
                "6": "₆",
                "7": "₇",
                "8": "₈",
                "9": "₉",
            }

            subscript_decimal = "".join(subscript_map.get(digit, digit) for digit in decimal_part)

            # Construct final formatted number with subscript decimals
            # Skip decimal part if it's actually zero
            formatted = formatted_integer if num == int(num) else f"{formatted_integer}.{subscript_decimal}"

            # Add minus sign back if needed
            if is_negative:
                formatted = "-" + formatted
        except Exception as e:
            print(f"Error while formatting amount: {e}")
            return str(value)
        return formatted

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint cell with special formatting for income transactions.

        Args:

        - `painter` (`QPainter`): The painter used for drawing.
        - `option` (`QStyleOptionViewItem`): The style options for the item.
        - `index` (`QModelIndex`): The model index of the item being painted.

        """
        try:
            total_per_day_column = 6  # Column index for "Total per day"
            if index.column() == total_per_day_column:
                raw_value = index.data(Qt.ItemDataRole.DisplayRole)
                # Show currency symbol only in cells that have a sum (non-empty value)
                if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                    super().paint(painter, option, index)
                    return
                # Total per day is in default (target) currency, not transaction currency
                currency_symbol = ""
                if self.db_manager is not None:
                    default_code = self.db_manager.get_default_currency()
                    if default_code:
                        currency_info = self.db_manager.get_currency_by_code(default_code)
                        if currency_info:
                            currency_symbol = currency_info[2]
                amount_text = self.displayText(raw_value, QLocale())
                display_text = f"{amount_text}{currency_symbol}"
                painter.save()
                painter.setFont(option.font)
                painter.drawText(
                    option.rect.adjusted(5, 0, -5, 0),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                    display_text,
                )
                painter.restore()
                return

            # Get the model and check if this is an income transaction
            model = index.model()
            if model is None:
                super().paint(painter, option, index)
                return

            # Get the category column (index 2) from the same row
            category_index = model.index(index.row(), 2)
            category_text = model.data(category_index, Qt.ItemDataRole.DisplayRole)

            # Check if this is an income transaction (has "(Income)" suffix)
            is_income = category_text and "(Income)" in str(category_text)

            if is_income:
                # Create a copy of the option to modify font
                income_option = option
                income_option.font = QFont(option.font)
                income_option.font.setBold(True)

                # Get the amount value and add emoji
                amount_text = self.displayText(index.data(), QLocale())

                # Add emoji prefix for display (but not for editing)
                if not amount_text.startswith("💰"):
                    display_text = f"💰 {amount_text}"

                    # Create a temporary index with modified data for display
                    painter.save()

                    # Set bold font
                    painter.setFont(income_option.font)

                    # Draw the text manually
                    painter.drawText(
                        option.rect.adjusted(5, 0, 0, 0),
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                        display_text,
                    )

                    painter.restore()
                    return

            # For expenses or other cases, use default painting
            super().paint(painter, option, index)

        except Exception:
            # Fallback to default painting on any error
            super().paint(painter, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set data in editor (without spaces).

        Args:

        - `editor` (`QWidget`): The editor widget to set data in.
        - `index` (`QModelIndex | QPersistentModelIndex`): The model index containing the data.

        """
        spin = cast("QDoubleSpinBox", editor)
        try:
            # Get the original value without formatting
            text = str(index.data(Qt.ItemDataRole.DisplayRole))

            # Remove spaces and convert to float
            clean_text = text.replace(" ", "")

            # Handle cases where the text might already be a formatted number
            # Remove any non-numeric characters except decimal point and minus
            clean_text = re.sub(r"[^\d.-]", "", clean_text)

            value = float(clean_text)
            spin.setValue(value)
        except (ValueError, TypeError):
            spin.setValue(0.0)

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set data from editor back to model.

        Args:

        - `editor` (`QWidget`): The editor widget containing the edited value.
        - `model` (`QAbstractItemModel`): The model to update with the new data.
        - `index` (`QModelIndex | QPersistentModelIndex`): The model index to update.

        """
        spin = cast("QDoubleSpinBox", editor)
        value = spin.value()

        # Only apply transaction type logic for Amount column (index 1), not for Total per day (index 6)
        amount_column_index = 1
        if index.column() == amount_column_index:
            # Get the category column (index 2) from the same row to determine transaction type
            category_index = model.index(index.row(), 2)
            category_text = model.data(category_index, Qt.ItemDataRole.DisplayRole)

            # Check if this is an income transaction (has "(Income)" suffix)
            is_income = category_text and "(Income)" in str(category_text)

            # For expenses (not income), ensure negative sign is present
            # For income, ensure no negative sign
            if not is_income:
                # Expense: ensure value is negative
                if value > 0:
                    value = -value
            # Income: ensure value is positive
            elif value < 0:
                value = abs(value)

        # Format the value as string with 2 decimal places for storage
        formatted_value = f"{value:.2f}"

        # Set both DisplayRole and EditRole to ensure consistency
        model.setData(index, formatted_value, Qt.ItemDataRole.DisplayRole)
        model.setData(index, formatted_value, Qt.ItemDataRole.EditRole)
