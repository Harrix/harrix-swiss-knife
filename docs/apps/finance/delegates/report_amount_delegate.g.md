---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_amount_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReportAmountDelegate`](#%EF%B8%8F-class-reportamountdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)

</details>

## 🏛️ Class `ReportAmountDelegate`

```python
class ReportAmountDelegate(QStyledItemDelegate)
```

Delegate for amount columns in reports with read-only formatting.

This delegate provides custom formatting for amount values in reports,
including thousands separators and subscript decimals, without editing capability.

<details>
<summary>Code:</summary>

```python
class ReportAmountDelegate(QStyledItemDelegate):

    def __init__(self, parent: QWidget | None = None, *, is_bold: bool = False) -> None:
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
                bold_option = QStyleOptionViewItem(option)
                bold_option.font = QFont(option.font)
                bold_option.font.setBold(True)
                super().paint(painter, bold_option, index)
                return

            super().paint(painter, option, index)

        except Exception:
            super().paint(painter, option, index)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the report amount delegate.

Args:

- `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
- `is_bold` (`bool`): Whether to display text in bold. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, is_bold: bool = False) -> None:
        super().__init__(parent)
        self.is_bold = is_bold
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, value: object, _locale: QLocale) -> str
```

Format display text with spaces for thousands separator and subscript decimals.

Args:

- `value` (`object`): The value to format for display.
- `_locale` (`QLocale`): The locale for formatting (unused in this implementation).

Returns:

- `str`: The formatted text with spaces as thousands separators and subscript decimal digits.

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale) -> str:  # noqa: N802
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
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None
```

Paint cell with bold font if configured.

Args:

- `painter` (`QPainter`): The painter used for drawing.
- `option` (`QStyleOptionViewItem`): The style options for the item.
- `index` (`QModelIndex`): The model index of the item being painted.

<details>
<summary>Code:</summary>

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
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
```

</details>
