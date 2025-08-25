"""Text parser for finance entries.

This module provides functionality to parse text input and convert it
to transaction records according to specific rules.
"""

from __future__ import annotations

import re
from typing import Any, NamedTuple


class ParsedPurchaseItem(NamedTuple):
    """Represents a parsed purchase item from text input.

    Attributes:

    - `name` (`str`): Purchase item name.
    - `category` (`str`): Category name.
    - `amount` (`float`): Amount in currency units.
    - `currency_symbol` (`str`): Currency symbol (₽, $, etc.).

    """

    name: str
    category: str
    amount: float
    currency_symbol: str


class TextParser:
    """Parser for converting text input to purchase records.

    This class implements the parsing logic for purchase information entered as text,
    following specific rules for interpreting tab-separated values.

    """

    def __init__(self) -> None:
        """Initialize the text parser."""
        pass

    def parse_text(self, text: str) -> list[ParsedPurchaseItem]:
        """Parse text input and convert to purchase items.

        Args:

        - `text` (`str`): Text input to parse.

        Returns:

        - `list[ParsedPurchaseItem]`: List of parsed purchase items.

        """
        lines = text.strip().split("\n")
        parsed_items = []

        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip()
            if not line_clean:
                continue

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

        - `amount_str` (`str`): Amount string (e.g., "99 ₽", "$15.50").

        Returns:

        - `tuple[float | None, str]`: Tuple of (amount, currency_symbol) or (None, "") if parsing failed.

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

        - `ParsedPurchaseItem | None`: Parsed item or None if parsing failed.

        """
        # Split by tab character
        parts = line.split("\t")

        if len(parts) != 3:
            print(f"Line {line_num}: Expected 3 columns separated by tabs, got {len(parts)}")
            return None

        name = parts[0].strip()
        category = parts[1].strip()
        amount_str = parts[2].strip()

        if not name or not category or not amount_str:
            print(f"Line {line_num}: Empty values not allowed")
            return None

        # Parse amount and currency
        amount, currency_symbol = self._parse_amount(amount_str)
        if amount is None:
            print(f"Line {line_num}: Invalid amount format: {amount_str}")
            return None

        return ParsedPurchaseItem(name=name, category=category, amount=amount, currency_symbol=currency_symbol)
