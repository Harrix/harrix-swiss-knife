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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, is_bold: bool = False) -> None
```

Initialize the report amount delegate.

Args:

- [`parent`](../transaction_day_headers.g.md#%EF%B8%8F-method-parent) (`QWidget | None`): The parent widget. Defaults to `None`.
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
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str
```

Format display text with spaces for thousands separator and subscript decimals.

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
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
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint cell with bold font if configured.

Args:

- `painter` (`QPainter`): The painter used for drawing.
- `option` (`QStyleOptionViewItem`): The style options for the item.
- [`index`](../transaction_day_headers.g.md#%EF%B8%8F-method-index) (`QModelIndex`): The model index of the item being painted.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
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
