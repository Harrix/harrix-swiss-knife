---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ParsedFoodItem`](#%EF%B8%8F-class-parsedfooditem)
- [🏛️ Class `TextParser`](#%EF%B8%8F-class-textparser)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `parse_text`](#%EF%B8%8F-method-parse_text)
  - [⚙️ Method `_capitalize_name`](#%EF%B8%8F-method-_capitalize_name)
  - [⚙️ Method `_determine_parsing_strategy`](#%EF%B8%8F-method-_determine_parsing_strategy)
  - [⚙️ Method `_get_calories_from_database`](#%EF%B8%8F-method-_get_calories_from_database)
  - [⚙️ Method `_get_weight_and_calories_from_database`](#%EF%B8%8F-method-_get_weight_and_calories_from_database)
  - [⚙️ Method `_handle_unparseable_line`](#%EF%B8%8F-method-_handle_unparseable_line)
  - [⚙️ Method `_is_drink`](#%EF%B8%8F-method-_is_drink)
  - [⚙️ Method `_is_number`](#%EF%B8%8F-method-_is_number)
  - [⚙️ Method `_parse_line`](#%EF%B8%8F-method-_parse_line)
  - [⚙️ Method `_parse_name_only`](#%EF%B8%8F-method-_parse_name_only)
  - [⚙️ Method `_parse_name_with_one_number`](#%EF%B8%8F-method-_parse_name_with_one_number)
  - [⚙️ Method `_parse_name_with_portion`](#%EF%B8%8F-method-_parse_name_with_portion)
  - [⚙️ Method `_parse_name_with_two_numbers`](#%EF%B8%8F-method-_parse_name_with_two_numbers)
  - [⚙️ Method `_parse_name_with_two_numbers_and_portion`](#%EF%B8%8F-method-_parse_name_with_two_numbers_and_portion)

</details>

## 🏛️ Class `ParsedFoodItem`

```python
class ParsedFoodItem(NamedTuple)
```

Represents a parsed food item from text input.

Attributes:

- `name` (`str`): Food item name (capitalized).
- `weight` (`float | None`): Weight in grams.
- `calories_per_100g` (`float | None`): Calories per 100g.
- `portion_calories` (`float | None`): Calories for the portion.
- `food_date` (`str | None`): Date in YYYY-MM-DD format.
- `is_drink` (`bool`): Whether the item is a drink.

<details>
<summary>Code:</summary>

```python
class ParsedFoodItem(NamedTuple):

    name: str
    weight: float | None
    calories_per_100g: float | None
    portion_calories: float | None
    food_date: str | None
    is_drink: bool
```

</details>

## 🏛️ Class `TextParser`

```python
class TextParser
```

Parser for converting text input to food log records.

This class implements the parsing logic for food information entered as text,
following specific rules for interpreting numbers, dates, and portion indicators.

Attributes:

- `portion_keywords` (`list[str]`): Keywords that indicate portion calories.
- `date_pattern` (`re.Pattern`): Regular expression for date matching.

<details>
<summary>Code:</summary>

```python
class TextParser:

    def __init__(self) -> None:
        """Initialize the text parser."""
        self.portion_keywords = ["порция", "portion", "пор", "п", "p"]
        self.date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

    def parse_text(
        self,
        text: str,
        parent_widget: QWidget | None = None,
        db_manager: Any | None = None,
        default_date: str | None = None,
    ) -> list[ParsedFoodItem]:
        """Parse text input and convert to food items.

        Args:

        - `text` (`str`): Text input to parse.
        - `parent_widget` (`QWidget | None`): Parent widget for dialogs. Defaults to `None`.
        - `db_manager` (`Any | None`): Database manager for looking up existing items. Defaults to `None`.
        - `default_date` (`str | None`): Default date to use if no date is found in text. Defaults to `None`.

        Returns:

        - `list[ParsedFoodItem]`: List of parsed food items.

        """
        lines = text.strip().split("\n")
        parsed_items = []
        # Use provided default_date or today's date
        today = default_date or date.today().strftime("%Y-%m-%d")

        for line_num, line in enumerate(lines, 1):
            line_new = line.strip()
            if not line_new:
                continue

            try:
                parsed_item = self._parse_line(line_new, today, parent_widget, db_manager)
                if parsed_item:
                    parsed_items.append(parsed_item)
            except Exception as e:
                # Instead of just showing an error, try to handle it gracefully
                error_msg = f"Error parsing line {line_num}: {line_new}\nError: {e}"
                if parent_widget:
                    # Try to parse the line as a simple name-only entry
                    try:
                        simple_item = self._parse_name_only([line_new], today, db_manager)
                        if simple_item:
                            parsed_items.append(simple_item)
                            continue
                    except (ValueError, TypeError, AttributeError) as e:
                        pass
                    except Exception as e:
                        print(f"⚠️ Unexpected error in simple parsing: {e}")

                    # If that fails, ask user to correct the line
                    corrected_line, ok = QInputDialog.getText(
                        parent_widget,
                        "Correct Line",
                        f"Unable to parse line: '{line_new}'\nPlease correct it or leave empty to skip:",
                        text=line_new,
                    )

                    if ok and corrected_line.strip():
                        try:
                            corrected_item = self._parse_line(corrected_line, today, parent_widget, db_manager)
                            if corrected_item:
                                parsed_items.append(corrected_item)
                        except Exception as e2:
                            print(f"❌ Failed to parse corrected line: {e2}")
                else:
                    print(f"❌ {error_msg}")

        return parsed_items

    def _capitalize_name(self, name: str) -> str:
        """Capitalize the first letter of the name.

        Args:

        - `name` (`str`): Name to capitalize.

        Returns:

        - `str`: Name with first letter capitalized.

        """
        if not name:
            return name
        return name[0].upper() + name[1:] if len(name) > 1 else name.upper()

    def _determine_parsing_strategy(
        self,
        parts: list[str],
        numbers: list[tuple[int, float]],
        non_numbers: list[tuple[int, str]],
        food_date: str,
        parent_widget: QWidget | None,
        db_manager: Any | None,
    ) -> ParsedFoodItem | None:
        """Determine the parsing strategy based on the line content.

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `numbers` (`list[tuple[int, float]]`): Numbers found in the line with their positions.
        - `non_numbers` (`list[tuple[int, str]]`): Non-number parts with their positions.
        - `food_date` (`str`): Date for the food item.
        - `parent_widget` (`QWidget | None`): Parent widget for dialogs.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem | None`: Parsed food item or None if parsing failed.

        """
        # Check for portion keywords
        portion_found = False
        portion_number = None

        for pos, word in non_numbers:
            if word.lower() in self.portion_keywords:
                portion_found = True
                # Find the number before this keyword
                for num_pos, num_val in numbers:
                    if num_pos < pos:
                        portion_number = num_val
                        break
                break

        # Strategy 1: Name + one number + portion keyword
        if len(numbers) == 1 and portion_found:
            return self._parse_name_with_portion(parts, numbers[0][1], food_date, db_manager)

        # Strategy 2: Name + two numbers + portion keyword
        count_parts = 2
        if len(numbers) == count_parts and portion_found:
            return self._parse_name_with_two_numbers_and_portion(parts, numbers, portion_number, food_date, db_manager)

        # Strategy 3: Name + two numbers (weight + calories per 100g)
        count_parts = 2
        if len(numbers) == count_parts:
            return self._parse_name_with_two_numbers(parts, numbers, food_date, db_manager)

        # Strategy 4: Name + one number (weight)
        if len(numbers) == 1:
            return self._parse_name_with_one_number(parts, numbers[0][1], food_date, db_manager)

        # Strategy 5: Name only
        if len(numbers) == 0:
            return self._parse_name_only(parts, food_date, db_manager)

        # If no strategy matches, ask user for correction
        return self._handle_unparseable_line(parts, food_date, parent_widget, db_manager)

    def _get_calories_from_database(self, name: str, db_manager: Any | None) -> float | None:
        """Get calories per 100g from database for the given food name.

        Args:

        - `name` (`str`): Food name to look up.
        - `db_manager` (`Any | None`): Database manager.

        Returns:

        - `float | None`: Calories per 100g or None if not found.

        """
        if not db_manager:
            return None

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item and food_item[4]:  # calories_per_100g is at index 4
                return float(food_item[4])

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item and food_log_item[3]:  # calories_per_100g is at index 3
                return float(food_log_item[3])

        except Exception as e:
            print(f"Error looking up calories for '{name}': {e}")

        return None

    def _get_weight_and_calories_from_database(
        self, name: str, db_manager: Any | None
    ) -> tuple[float | None, float | None]:
        """Get weight and calories from database for the given food name.

        Args:

        - `name` (`str`): Food name to look up.
        - `db_manager` (`Any | None`): Database manager.

        Returns:

        - `tuple[float | None, float | None]`: Tuple of (weight, calories_per_100g).

        """
        if not db_manager:
            return None, None

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item:
                weight = float(food_item[5]) if food_item[5] else None  # default_portion_weight is at index 5
                calories = float(food_item[4]) if food_item[4] else None  # calories_per_100g is at index 4
                return weight, calories

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item:
                weight = float(food_log_item[4]) if food_log_item[4] else None  # weight is at index 4
                calories = float(food_log_item[3]) if food_log_item[3] else None  # calories_per_100g is at index 3
                return weight, calories

        except Exception as e:
            print(f"Error looking up weight and calories for '{name}': {e}")

        return None, None

    def _handle_unparseable_line(
        self, parts: list[str], food_date: str, parent_widget: QWidget | None, db_manager: Any | None
    ) -> ParsedFoodItem | None:
        """Handle lines that don't match any parsing strategy.

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `food_date` (`str`): Date for the food item.
        - `parent_widget` (`QWidget | None`): Parent widget for dialogs.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem | None`: Parsed food item or None if user cancels.

        """
        original_line = " ".join(parts)

        if parent_widget:
            # Ask user to correct the line
            corrected_line, ok = QInputDialog.getText(
                parent_widget,
                "Correct Line",
                f"Unable to parse line: '{original_line}'\nPlease correct it or leave empty to skip:",
                text=original_line,
            )

            if ok and corrected_line.strip():
                # Try to parse the corrected line
                return self._parse_line(corrected_line, food_date, parent_widget, db_manager)

        return None

    def _is_drink(self, name: str, db_manager: Any | None) -> bool:
        """Check if the food item is a drink based on database lookup.

        Args:

        - `name` (`str`): Food name to check.
        - `db_manager` (`Any | None`): Database manager.

        Returns:

        - `bool`: True if it's a drink, False otherwise.

        """
        if not db_manager:
            return False

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item and food_item[3] is not None:  # is_drink is at index 3
                return bool(food_item[3])

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item and food_log_item[2] is not None:  # is_drink is at index 2
                return bool(food_log_item[2])

        except Exception as e:
            print(f"Error looking up drink status for '{name}': {e}")

        return False

    def _is_number(self, text: str) -> bool:
        """Check if text represents a number.

        Args:

        - `text` (`str`): Text to check.

        Returns:

        - `bool`: True if text is a number, False otherwise.

        """
        try:
            float(text)
        except ValueError:
            return False
        else:
            return True

    def _parse_line(
        self, line: str, default_date: str, parent_widget: QWidget | None, db_manager: Any | None
    ) -> ParsedFoodItem | None:
        """Parse a single line of text.

        Args:

        - `line` (`str`): Line to parse.
        - `default_date` (`str`): Default date to use if no date is found.
        - `parent_widget` (`QWidget | None`): Parent widget for dialogs.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem | None`: Parsed food item or None if parsing failed.

        """
        # Extract date if present
        date_match = self.date_pattern.search(line)
        food_date = date_match.group() if date_match else default_date

        # Remove date from line for further processing
        line_without_date = self.date_pattern.sub("", line).strip()

        # Split line into parts
        parts = line_without_date.split()
        if not parts:
            return None

        # Find numbers and their positions
        numbers = []
        non_numbers = []

        for i, part in enumerate(parts):
            # Check if part is a number (including decimals)
            if self._is_number(part):
                numbers.append((i, float(part)))
            else:
                non_numbers.append((i, part))

        # Determine parsing strategy based on numbers and keywords
        return self._determine_parsing_strategy(parts, numbers, non_numbers, food_date, parent_widget, db_manager)

    def _parse_name_only(self, parts: list[str], food_date: str, db_manager: Any | None) -> ParsedFoodItem:
        """Parse line with name only.

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `food_date` (`str`): Date for the food item.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem`: Parsed food item.

        """
        name = " ".join(parts)
        name = self._capitalize_name(name)

        # Look up weight and calories from database
        weight, calories_per_100g = self._get_weight_and_calories_from_database(name, db_manager)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )

    def _parse_name_with_one_number(
        self, parts: list[str], weight: float, food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        """Parse line with name and one number (weight).

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `weight` (`float`): Weight in grams.
        - `food_date` (`str`): Date for the food item.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem`: Parsed food item.

        """
        # Remove numbers to get the name
        name_parts = [part for part in parts if not self._is_number(part)]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Look up calories from database
        calories_per_100g = self._get_calories_from_database(name, db_manager)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )

    def _parse_name_with_portion(
        self, parts: list[str], portion_calories: float, food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        """Parse line with name and portion calories.

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `portion_calories` (`float`): Calories for the portion.
        - `food_date` (`str`): Date for the food item.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem`: Parsed food item.

        """
        # Remove numbers and portion keywords to get the name
        name_parts = [part for part in parts if not self._is_number(part) and part.lower() not in self.portion_keywords]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=None,
            calories_per_100g=0,  # Required by database schema
            portion_calories=portion_calories,
            food_date=food_date,
            is_drink=is_drink,
        )

    def _parse_name_with_two_numbers(
        self, parts: list[str], numbers: list[tuple[int, float]], food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        """Parse line with name and two numbers (weight + calories per 100g).

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `numbers` (`list[tuple[int, float]]`): Numbers found in the line.
        - `food_date` (`str`): Date for the food item.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem`: Parsed food item.

        """
        # Remove numbers to get the name
        name_parts = [part for part in parts if not self._is_number(part)]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # First number is weight, second is calories per 100g
        weight, calories_per_100g = numbers[0][1], numbers[1][1]

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )

    def _parse_name_with_two_numbers_and_portion(
        self,
        parts: list[str],
        numbers: list[tuple[int, float]],
        portion_calories: float | None,
        food_date: str,
        db_manager: Any | None,
    ) -> ParsedFoodItem:
        """Parse line with name, two numbers, and portion keyword.

        Args:

        - `parts` (`list[str]`): All parts of the line.
        - `numbers` (`list[tuple[int, float]]`): Numbers found in the line.
        - `portion_calories` (`float | None`): Calories for the portion.
        - `food_date` (`str`): Date for the food item.
        - `db_manager` (`Any | None`): Database manager for looking up existing items.

        Returns:

        - `ParsedFoodItem`: Parsed food item.

        """
        # Remove numbers and portion keywords to get the name
        name_parts = [part for part in parts if not self._is_number(part) and part.lower() not in self.portion_keywords]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Determine which number is weight and which is portion calories
        if portion_calories is not None:
            # One number is portion calories, the other is weight
            weight = next(num for pos, num in numbers if num != portion_calories)
        else:
            # Assume first number is weight, second is portion calories
            weight, portion_calories = numbers[0][1], numbers[1][1]

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=0,  # Required by database schema
            portion_calories=portion_calories,
            food_date=food_date,
            is_drink=is_drink,
        )
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
        self.portion_keywords = ["порция", "portion", "пор", "п", "p"]
        self.date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
```

</details>

### ⚙️ Method `parse_text`

```python
def parse_text(self, text: str, parent_widget: QWidget | None = None, db_manager: Any | None = None, default_date: str | None = None) -> list[ParsedFoodItem]
```

Parse text input and convert to food items.

Args:

- `text` (`str`): Text input to parse.
- `parent_widget` (`QWidget | None`): Parent widget for dialogs. Defaults to `None`.
- `db_manager` (`Any | None`): Database manager for looking up existing items. Defaults to `None`.
- `default_date` (`str | None`): Default date to use if no date is found in text. Defaults to `None`.

Returns:

- `list[ParsedFoodItem]`: List of parsed food items.

<details>
<summary>Code:</summary>

```python
def parse_text(
        self,
        text: str,
        parent_widget: QWidget | None = None,
        db_manager: Any | None = None,
        default_date: str | None = None,
    ) -> list[ParsedFoodItem]:
        lines = text.strip().split("\n")
        parsed_items = []
        # Use provided default_date or today's date
        today = default_date or date.today().strftime("%Y-%m-%d")

        for line_num, line in enumerate(lines, 1):
            line_new = line.strip()
            if not line_new:
                continue

            try:
                parsed_item = self._parse_line(line_new, today, parent_widget, db_manager)
                if parsed_item:
                    parsed_items.append(parsed_item)
            except Exception as e:
                # Instead of just showing an error, try to handle it gracefully
                error_msg = f"Error parsing line {line_num}: {line_new}\nError: {e}"
                if parent_widget:
                    # Try to parse the line as a simple name-only entry
                    try:
                        simple_item = self._parse_name_only([line_new], today, db_manager)
                        if simple_item:
                            parsed_items.append(simple_item)
                            continue
                    except (ValueError, TypeError, AttributeError) as e:
                        pass
                    except Exception as e:
                        print(f"⚠️ Unexpected error in simple parsing: {e}")

                    # If that fails, ask user to correct the line
                    corrected_line, ok = QInputDialog.getText(
                        parent_widget,
                        "Correct Line",
                        f"Unable to parse line: '{line_new}'\nPlease correct it or leave empty to skip:",
                        text=line_new,
                    )

                    if ok and corrected_line.strip():
                        try:
                            corrected_item = self._parse_line(corrected_line, today, parent_widget, db_manager)
                            if corrected_item:
                                parsed_items.append(corrected_item)
                        except Exception as e2:
                            print(f"❌ Failed to parse corrected line: {e2}")
                else:
                    print(f"❌ {error_msg}")

        return parsed_items
```

</details>

### ⚙️ Method `_capitalize_name`

```python
def _capitalize_name(self, name: str) -> str
```

Capitalize the first letter of the name.

Args:

- `name` (`str`): Name to capitalize.

Returns:

- `str`: Name with first letter capitalized.

<details>
<summary>Code:</summary>

```python
def _capitalize_name(self, name: str) -> str:
        if not name:
            return name
        return name[0].upper() + name[1:] if len(name) > 1 else name.upper()
```

</details>

### ⚙️ Method `_determine_parsing_strategy`

```python
def _determine_parsing_strategy(self, parts: list[str], numbers: list[tuple[int, float]], non_numbers: list[tuple[int, str]], food_date: str, parent_widget: QWidget | None, db_manager: Any | None) -> ParsedFoodItem | None
```

Determine the parsing strategy based on the line content.

Args:

- `parts` (`list[str]`): All parts of the line.
- `numbers` (`list[tuple[int, float]]`): Numbers found in the line with their positions.
- `non_numbers` (`list[tuple[int, str]]`): Non-number parts with their positions.
- `food_date` (`str`): Date for the food item.
- `parent_widget` (`QWidget | None`): Parent widget for dialogs.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem | None`: Parsed food item or None if parsing failed.

<details>
<summary>Code:</summary>

```python
def _determine_parsing_strategy(
        self,
        parts: list[str],
        numbers: list[tuple[int, float]],
        non_numbers: list[tuple[int, str]],
        food_date: str,
        parent_widget: QWidget | None,
        db_manager: Any | None,
    ) -> ParsedFoodItem | None:
        # Check for portion keywords
        portion_found = False
        portion_number = None

        for pos, word in non_numbers:
            if word.lower() in self.portion_keywords:
                portion_found = True
                # Find the number before this keyword
                for num_pos, num_val in numbers:
                    if num_pos < pos:
                        portion_number = num_val
                        break
                break

        # Strategy 1: Name + one number + portion keyword
        if len(numbers) == 1 and portion_found:
            return self._parse_name_with_portion(parts, numbers[0][1], food_date, db_manager)

        # Strategy 2: Name + two numbers + portion keyword
        count_parts = 2
        if len(numbers) == count_parts and portion_found:
            return self._parse_name_with_two_numbers_and_portion(parts, numbers, portion_number, food_date, db_manager)

        # Strategy 3: Name + two numbers (weight + calories per 100g)
        count_parts = 2
        if len(numbers) == count_parts:
            return self._parse_name_with_two_numbers(parts, numbers, food_date, db_manager)

        # Strategy 4: Name + one number (weight)
        if len(numbers) == 1:
            return self._parse_name_with_one_number(parts, numbers[0][1], food_date, db_manager)

        # Strategy 5: Name only
        if len(numbers) == 0:
            return self._parse_name_only(parts, food_date, db_manager)

        # If no strategy matches, ask user for correction
        return self._handle_unparseable_line(parts, food_date, parent_widget, db_manager)
```

</details>

### ⚙️ Method `_get_calories_from_database`

```python
def _get_calories_from_database(self, name: str, db_manager: Any | None) -> float | None
```

Get calories per 100g from database for the given food name.

Args:

- `name` (`str`): Food name to look up.
- `db_manager` (`Any | None`): Database manager.

Returns:

- `float | None`: Calories per 100g or None if not found.

<details>
<summary>Code:</summary>

```python
def _get_calories_from_database(self, name: str, db_manager: Any | None) -> float | None:
        if not db_manager:
            return None

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item and food_item[4]:  # calories_per_100g is at index 4
                return float(food_item[4])

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item and food_log_item[3]:  # calories_per_100g is at index 3
                return float(food_log_item[3])

        except Exception as e:
            print(f"Error looking up calories for '{name}': {e}")

        return None
```

</details>

### ⚙️ Method `_get_weight_and_calories_from_database`

```python
def _get_weight_and_calories_from_database(self, name: str, db_manager: Any | None) -> tuple[float | None, float | None]
```

Get weight and calories from database for the given food name.

Args:

- `name` (`str`): Food name to look up.
- `db_manager` (`Any | None`): Database manager.

Returns:

- `tuple[float | None, float | None]`: Tuple of (weight, calories_per_100g).

<details>
<summary>Code:</summary>

```python
def _get_weight_and_calories_from_database(
        self, name: str, db_manager: Any | None
    ) -> tuple[float | None, float | None]:
        if not db_manager:
            return None, None

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item:
                weight = float(food_item[5]) if food_item[5] else None  # default_portion_weight is at index 5
                calories = float(food_item[4]) if food_item[4] else None  # calories_per_100g is at index 4
                return weight, calories

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item:
                weight = float(food_log_item[4]) if food_log_item[4] else None  # weight is at index 4
                calories = float(food_log_item[3]) if food_log_item[3] else None  # calories_per_100g is at index 3
                return weight, calories

        except Exception as e:
            print(f"Error looking up weight and calories for '{name}': {e}")

        return None, None
```

</details>

### ⚙️ Method `_handle_unparseable_line`

```python
def _handle_unparseable_line(self, parts: list[str], food_date: str, parent_widget: QWidget | None, db_manager: Any | None) -> ParsedFoodItem | None
```

Handle lines that don't match any parsing strategy.

Args:

- `parts` (`list[str]`): All parts of the line.
- `food_date` (`str`): Date for the food item.
- `parent_widget` (`QWidget | None`): Parent widget for dialogs.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem | None`: Parsed food item or None if user cancels.

<details>
<summary>Code:</summary>

```python
def _handle_unparseable_line(
        self, parts: list[str], food_date: str, parent_widget: QWidget | None, db_manager: Any | None
    ) -> ParsedFoodItem | None:
        original_line = " ".join(parts)

        if parent_widget:
            # Ask user to correct the line
            corrected_line, ok = QInputDialog.getText(
                parent_widget,
                "Correct Line",
                f"Unable to parse line: '{original_line}'\nPlease correct it or leave empty to skip:",
                text=original_line,
            )

            if ok and corrected_line.strip():
                # Try to parse the corrected line
                return self._parse_line(corrected_line, food_date, parent_widget, db_manager)

        return None
```

</details>

### ⚙️ Method `_is_drink`

```python
def _is_drink(self, name: str, db_manager: Any | None) -> bool
```

Check if the food item is a drink based on database lookup.

Args:

- `name` (`str`): Food name to check.
- `db_manager` (`Any | None`): Database manager.

Returns:

- `bool`: True if it's a drink, False otherwise.

<details>
<summary>Code:</summary>

```python
def _is_drink(self, name: str, db_manager: Any | None) -> bool:
        if not db_manager:
            return False

        try:
            # Try to get from food_items table first
            food_item = db_manager.get_food_item_by_name(name)
            if food_item and food_item[3] is not None:  # is_drink is at index 3
                return bool(food_item[3])

            # Try to get from food_log table
            food_log_item = db_manager.get_food_log_item_by_name(name)
            if food_log_item and food_log_item[2] is not None:  # is_drink is at index 2
                return bool(food_log_item[2])

        except Exception as e:
            print(f"Error looking up drink status for '{name}': {e}")

        return False
```

</details>

### ⚙️ Method `_is_number`

```python
def _is_number(self, text: str) -> bool
```

Check if text represents a number.

Args:

- `text` (`str`): Text to check.

Returns:

- `bool`: True if text is a number, False otherwise.

<details>
<summary>Code:</summary>

```python
def _is_number(self, text: str) -> bool:
        try:
            float(text)
        except ValueError:
            return False
        else:
            return True
```

</details>

### ⚙️ Method `_parse_line`

```python
def _parse_line(self, line: str, default_date: str, parent_widget: QWidget | None, db_manager: Any | None) -> ParsedFoodItem | None
```

Parse a single line of text.

Args:

- `line` (`str`): Line to parse.
- `default_date` (`str`): Default date to use if no date is found.
- `parent_widget` (`QWidget | None`): Parent widget for dialogs.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem | None`: Parsed food item or None if parsing failed.

<details>
<summary>Code:</summary>

```python
def _parse_line(
        self, line: str, default_date: str, parent_widget: QWidget | None, db_manager: Any | None
    ) -> ParsedFoodItem | None:
        # Extract date if present
        date_match = self.date_pattern.search(line)
        food_date = date_match.group() if date_match else default_date

        # Remove date from line for further processing
        line_without_date = self.date_pattern.sub("", line).strip()

        # Split line into parts
        parts = line_without_date.split()
        if not parts:
            return None

        # Find numbers and their positions
        numbers = []
        non_numbers = []

        for i, part in enumerate(parts):
            # Check if part is a number (including decimals)
            if self._is_number(part):
                numbers.append((i, float(part)))
            else:
                non_numbers.append((i, part))

        # Determine parsing strategy based on numbers and keywords
        return self._determine_parsing_strategy(parts, numbers, non_numbers, food_date, parent_widget, db_manager)
```

</details>

### ⚙️ Method `_parse_name_only`

```python
def _parse_name_only(self, parts: list[str], food_date: str, db_manager: Any | None) -> ParsedFoodItem
```

Parse line with name only.

Args:

- `parts` (`list[str]`): All parts of the line.
- `food_date` (`str`): Date for the food item.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem`: Parsed food item.

<details>
<summary>Code:</summary>

```python
def _parse_name_only(self, parts: list[str], food_date: str, db_manager: Any | None) -> ParsedFoodItem:
        name = " ".join(parts)
        name = self._capitalize_name(name)

        # Look up weight and calories from database
        weight, calories_per_100g = self._get_weight_and_calories_from_database(name, db_manager)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )
```

</details>

### ⚙️ Method `_parse_name_with_one_number`

```python
def _parse_name_with_one_number(self, parts: list[str], weight: float, food_date: str, db_manager: Any | None) -> ParsedFoodItem
```

Parse line with name and one number (weight).

Args:

- `parts` (`list[str]`): All parts of the line.
- `weight` (`float`): Weight in grams.
- `food_date` (`str`): Date for the food item.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem`: Parsed food item.

<details>
<summary>Code:</summary>

```python
def _parse_name_with_one_number(
        self, parts: list[str], weight: float, food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        # Remove numbers to get the name
        name_parts = [part for part in parts if not self._is_number(part)]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Look up calories from database
        calories_per_100g = self._get_calories_from_database(name, db_manager)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )
```

</details>

### ⚙️ Method `_parse_name_with_portion`

```python
def _parse_name_with_portion(self, parts: list[str], portion_calories: float, food_date: str, db_manager: Any | None) -> ParsedFoodItem
```

Parse line with name and portion calories.

Args:

- `parts` (`list[str]`): All parts of the line.
- `portion_calories` (`float`): Calories for the portion.
- `food_date` (`str`): Date for the food item.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem`: Parsed food item.

<details>
<summary>Code:</summary>

```python
def _parse_name_with_portion(
        self, parts: list[str], portion_calories: float, food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        # Remove numbers and portion keywords to get the name
        name_parts = [part for part in parts if not self._is_number(part) and part.lower() not in self.portion_keywords]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=None,
            calories_per_100g=0,  # Required by database schema
            portion_calories=portion_calories,
            food_date=food_date,
            is_drink=is_drink,
        )
```

</details>

### ⚙️ Method `_parse_name_with_two_numbers`

```python
def _parse_name_with_two_numbers(self, parts: list[str], numbers: list[tuple[int, float]], food_date: str, db_manager: Any | None) -> ParsedFoodItem
```

Parse line with name and two numbers (weight + calories per 100g).

Args:

- `parts` (`list[str]`): All parts of the line.
- `numbers` (`list[tuple[int, float]]`): Numbers found in the line.
- `food_date` (`str`): Date for the food item.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem`: Parsed food item.

<details>
<summary>Code:</summary>

```python
def _parse_name_with_two_numbers(
        self, parts: list[str], numbers: list[tuple[int, float]], food_date: str, db_manager: Any | None
    ) -> ParsedFoodItem:
        # Remove numbers to get the name
        name_parts = [part for part in parts if not self._is_number(part)]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # First number is weight, second is calories per 100g
        weight, calories_per_100g = numbers[0][1], numbers[1][1]

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=calories_per_100g,
            portion_calories=None,
            food_date=food_date,
            is_drink=is_drink,
        )
```

</details>

### ⚙️ Method `_parse_name_with_two_numbers_and_portion`

```python
def _parse_name_with_two_numbers_and_portion(self, parts: list[str], numbers: list[tuple[int, float]], portion_calories: float | None, food_date: str, db_manager: Any | None) -> ParsedFoodItem
```

Parse line with name, two numbers, and portion keyword.

Args:

- `parts` (`list[str]`): All parts of the line.
- `numbers` (`list[tuple[int, float]]`): Numbers found in the line.
- `portion_calories` (`float | None`): Calories for the portion.
- `food_date` (`str`): Date for the food item.
- `db_manager` (`Any | None`): Database manager for looking up existing items.

Returns:

- `ParsedFoodItem`: Parsed food item.

<details>
<summary>Code:</summary>

```python
def _parse_name_with_two_numbers_and_portion(
        self,
        parts: list[str],
        numbers: list[tuple[int, float]],
        portion_calories: float | None,
        food_date: str,
        db_manager: Any | None,
    ) -> ParsedFoodItem:
        # Remove numbers and portion keywords to get the name
        name_parts = [part for part in parts if not self._is_number(part) and part.lower() not in self.portion_keywords]

        name = " ".join(name_parts)
        name = self._capitalize_name(name)

        # Determine which number is weight and which is portion calories
        if portion_calories is not None:
            # One number is portion calories, the other is weight
            weight = next(num for pos, num in numbers if num != portion_calories)
        else:
            # Assume first number is weight, second is portion calories
            weight, portion_calories = numbers[0][1], numbers[1][1]

        # Determine if it's a drink based on database lookup
        is_drink = self._is_drink(name, db_manager)

        return ParsedFoodItem(
            name=name,
            weight=weight,
            calories_per_100g=0,  # Required by database schema
            portion_calories=portion_calories,
            food_date=food_date,
            is_drink=is_drink,
        )
```

</details>
