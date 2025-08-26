"""Amount delegate for formatting amounts in transactions table."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate


class AmountDelegate(QStyledItemDelegate):
    """Delegate for amount column with custom formatting and editing."""

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager

    def createEditor(self, parent, option, index):
        """Create editor for amount editing."""
        editor = QDoubleSpinBox(parent)
        editor.setRange(-999999999.99, 999999999.99)
        editor.setDecimals(2)
        editor.setGroupSeparatorShown(False)  # No separators in editor
        return editor

    def displayText(self, value, locale):
        """Format display text with spaces for thousands separator and subscript decimals."""
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
                '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
            }

            subscript_decimal = ''.join(subscript_map.get(digit, digit) for digit in decimal_part)

            # Construct final formatted number with subscript decimals
            formatted = f"{formatted_integer}.{subscript_decimal}"

            # Add minus sign back if needed
            if is_negative:
                formatted = "-" + formatted

            return formatted

        except Exception:
            return str(value)

    def paint(self, painter, option, index):
        """Custom paint method to handle income formatting."""
        try:
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
                amount_text = self.displayText(index.data(), None)

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

    def setEditorData(self, editor, index):
        """Set data in editor (without spaces)."""
        try:
            # Get the original value without formatting
            text = str(index.data(Qt.ItemDataRole.DisplayRole))

            # Remove spaces and convert to float
            clean_text = text.replace(" ", "")
            value = float(clean_text)

            editor.setValue(value)
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        """Set data from editor back to model."""
        value = editor.value()

        # Format the value as string without spaces for storage
        formatted_value = f"{value:.2f}"

        model.setData(index, formatted_value, Qt.ItemDataRole.DisplayRole)
