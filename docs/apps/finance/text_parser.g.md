---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ParsedPurchaseItem`](#️-class-parsedpurchaseitem)
- [🏛️ Class `TextParser`](#️-class-textparser)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `parse_row`](#️-method-parse_row)
  - [⚙️ Method `parse_text`](#️-method-parse_text)

</details>

## 🏛️ Class `ParsedPurchaseItem`

```python
class ParsedPurchaseItem(NamedTuple)
```

Represents a parsed purchase item from text input.

Attributes:

- `name` (`str`): Purchase item name.
- `category` (`str`): Category name.
- `amount` (`float`): Amount in currency units.
- `currency_symbol` (`str`): Currency symbol (₽, $, etc.).

<details>
<summary>Code:</summary>

```python
class ParsedPurchaseItem(NamedTuple):

    name: str
    category: str
    amount: float
    currency_symbol: str
```

</details>

## 🏛️ Class `TextParser`

```python
class TextParser
```

Parser for converting text input to purchase records.

This class implements the parsing logic for purchase information entered as text,
following specific rules for interpreting tab-separated values.

<details>
<summary>Code:</summary>

```python
class TextParser:

    def __init__(self) -> None:
        """Initialize the text parser."""

    def parse_row(self, name: str, category: str, amount_str: str) -> ParsedPurchaseItem | None:
        """Parse a single table row (same rules as a TSV line).

        Args:

        - `name` (`str`): Purchase item name.
        - `category` (`str`): Category name.
        - `amount_str` (`str`): Amount string (e.g., `99 ₽`).

        Returns:

        - `ParsedPurchaseItem | None`: Parsed item or `None` if parsing failed.

        """
        name = name.strip()
        category = category.strip()
        amount_str = amount_str.strip()

        if not name or not category or not amount_str:
            return None

        amount, currency_symbol = self._parse_amount(amount_str)
        if amount is None:
            return None

        return ParsedPurchaseItem(name=name, category=category, amount=amount, currency_symbol=currency_symbol)

    def parse_text(self, text: str) -> list[ParsedPurchaseItem]:
        """Parse text input and convert to purchase items.

        Args:

        - `text` (`str`): Text input to parse.

        Returns:

        - `list[ParsedPurchaseItem]`: List of parsed purchase items.

        """
        parsed_items = []

        for line_num, line_clean in enumerate_stripped_non_empty_lines(text):
            try:
                parsed_item = self._parse_line(line_clean, line_num)
                if parsed_item:
                    parsed_items.append(parsed_item)
            except Exception as e:
                print(f"Error parsing line {line_num}: {line_clean}\nError: {e}")
                continue

        return parsed_items

    def _parse_amount(self, amount_str: str) -> tuple[float | None, str]:
        """Parse amount string to extract numeric value and currency symbol.

        Args:

        - `amount_str` (`str`): Amount string (e.g., `99 ₽`, `$15.50`).

        Returns:

        - `tuple[float | None, str]`: Tuple of (amount, currency_symbol) or (`None`, `""`) if parsing failed.

        """
        # Remove all non-numeric characters except decimal point
        amount_match = re.search(r"[\d.,]+", amount_str)
        if not amount_match:
            return None, ""

        amount_text = amount_match.group()
        # Replace comma with dot for decimal
        amount_text = amount_text.replace(",", ".")

        try:
            amount = float(amount_text)
        except ValueError:
            return None, ""

        # Extract currency symbol (everything after the number)
        currency_symbol = amount_str[amount_match.end() :].strip()

        return amount, currency_symbol

    def _parse_line(self, line: str, line_num: int) -> ParsedPurchaseItem | None:
        """Parse a single line of text.

        Args:

        - `line` (`str`): Line to parse.
        - `line_num` (`int`): Line number for error reporting.

        Returns:

        - `ParsedPurchaseItem | None`: Parsed item or `None` if parsing failed.

        """
        # Split by tab character
        parts = line.split("\t")

        expected_columns = 3
        if len(parts) != expected_columns:
            print(f"Line {line_num}: Expected 3 columns separated by tabs, got {len(parts)}")
            return None

        parsed = self.parse_row(parts[0], parts[1], parts[2])
        if parsed is None:
            print(f"Line {line_num}: Invalid row: {line}")
        return parsed
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the text parser.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
```

</details>

### ⚙️ Method `parse_row`

```python
def parse_row(self, name: str, category: str, amount_str: str) -> ParsedPurchaseItem | None
```

Parse a single table row (same rules as a TSV line).

Args:

- `name` (`str`): Purchase item name.
- `category` (`str`): Category name.
- `amount_str` (`str`): Amount string (e.g., `99 ₽`).

Returns:

- `ParsedPurchaseItem | None`: Parsed item or `None` if parsing failed.

<details>
<summary>Code:</summary>

```python
def parse_row(self, name: str, category: str, amount_str: str) -> ParsedPurchaseItem | None:
        name = name.strip()
        category = category.strip()
        amount_str = amount_str.strip()

        if not name or not category or not amount_str:
            return None

        amount, currency_symbol = self._parse_amount(amount_str)
        if amount is None:
            return None

        return ParsedPurchaseItem(name=name, category=category, amount=amount, currency_symbol=currency_symbol)
```

</details>

### ⚙️ Method `parse_text`

```python
def parse_text(self, text: str) -> list[ParsedPurchaseItem]
```

Parse text input and convert to purchase items.

Args:

- `text` (`str`): Text input to parse.

Returns:

- `list[ParsedPurchaseItem]`: List of parsed purchase items.

<details>
<summary>Code:</summary>

```python
def parse_text(self, text: str) -> list[ParsedPurchaseItem]:
        parsed_items = []

        for line_num, line_clean in enumerate_stripped_non_empty_lines(text):
            try:
                parsed_item = self._parse_line(line_clean, line_num)
                if parsed_item:
                    parsed_items.append(parsed_item)
            except Exception as e:
                print(f"Error parsing line {line_num}: {line_clean}\nError: {e}")
                continue

        return parsed_items
```

</details>
