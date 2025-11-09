"""Report amount delegate for formatting amounts in reports without editing."""

from PySide6.QtCore import QLocale, QModelIndex, Qt
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


class ReportAmountDelegate(QStyledItemDelegate):
    """Delegate for amount columns in reports with read-only formatting.

    This delegate provides custom formatting for amount values in reports,
    including thousands separators and subscript decimals, without editing capability.

    """

    def __init__(self, parent: QWidget | None = None, is_bold: bool = False) -> None:
        """Initialize the report amount delegate.

        Args:

        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
        - `is_bold` (`bool`): Whether to display text in bold. Defaults to `False`.

        """
        super().__init__(parent)
        self.is_bold = is_bold

    def displayText(self, value: object, _locale: QLocale) -> str:  # noqa: N802
        """Format display text with spaces for thousands separator and subscript decimals.

        Args:

        - `value` (`object`): The value to format for display.
        - `_locale` (`QLocale`): The locale for formatting (unused in this implementation).

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

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paint cell with bold font if configured.

        Args:

        - `painter` (`QPainter`): The painter used for drawing.
        - `option` (`QStyleOptionViewItem`): The style options for the item.
        - `index` (`QModelIndex`): The model index of the item being painted.

        """
        try:
            if self.is_bold:
                # Create a copy of the option to modify font
                bold_option = QStyleOptionViewItem(option)
                bold_option.font = QFont(option.font)
                bold_option.font.setBold(True)

                # Get the formatted amount text
                amount_text = self.displayText(index.data(), None)

                # Draw the text manually with bold font
                painter.save()
                painter.setFont(bold_option.font)
                painter.drawText(
                    option.rect.adjusted(5, 0, 0, 0),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    amount_text,
                )
                painter.restore()
                return

            # For non-bold columns, use default painting
            super().paint(painter, option, index)

        except Exception:
            # Fallback to default painting on any error
            super().paint(painter, option, index)
