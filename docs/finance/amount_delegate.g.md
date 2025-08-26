---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `amount_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AmountDelegate`](#%EF%B8%8F-class-amountdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `AmountDelegate`

```python
class AmountDelegate(QStyledItemDelegate)
```

Delegate for amount column with custom formatting and editing.

<details>
<summary>Code:</summary>

```python
class AmountDelegate(QStyledItemDelegate):

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
        """Format display text with spaces for thousands separator."""
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

            # Construct final formatted number
            formatted = f"{formatted_integer}.{decimal_part}"

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent = None, db_manager = None)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent, option, index)
```

Create editor for amount editing.

<details>
<summary>Code:</summary>

```python
def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setRange(-999999999.99, 999999999.99)
        editor.setDecimals(2)
        editor.setGroupSeparatorShown(False)  # No separators in editor
        return editor
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, value, locale)
```

Format display text with spaces for thousands separator.

<details>
<summary>Code:</summary>

```python
def displayText(self, value, locale):
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

            # Construct final formatted number
            formatted = f"{formatted_integer}.{decimal_part}"

            # Add minus sign back if needed
            if is_negative:
                formatted = "-" + formatted

            return formatted

        except Exception:
            return str(value)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter, option, index)
```

Custom paint method to handle income formatting.

<details>
<summary>Code:</summary>

```python
def paint(self, painter, option, index):
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
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor, index)
```

Set data in editor (without spaces).

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor, index):
        try:
            # Get the original value without formatting
            text = str(index.data(Qt.ItemDataRole.DisplayRole))

            # Remove spaces and convert to float
            clean_text = text.replace(" ", "")
            value = float(clean_text)

            editor.setValue(value)
        except (ValueError, TypeError):
            editor.setValue(0.0)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor, model, index)
```

Set data from editor back to model.

<details>
<summary>Code:</summary>

```python
def setModelData(self, editor, model, index):
        value = editor.value()

        # Format the value as string without spaces for storage
        formatted_value = f"{value:.2f}"

        model.setData(index, formatted_value, Qt.ItemDataRole.DisplayRole)
```

</details>
