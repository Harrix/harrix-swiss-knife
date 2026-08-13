---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `number_utils.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clean_number_text`](#-function-clean_number_text)
- [🔧 Function `evaluate_arithmetic_expression`](#-function-evaluate_arithmetic_expression)
- [🔧 Function `format_amount`](#-function-format_amount)
- [🔧 Function `try_evaluate_arithmetic_expression`](#-function-try_evaluate_arithmetic_expression)

</details>

## 🔧 Function `clean_number_text`

```python
def clean_number_text(text: str) -> str
```

Remove spaces and replace subscript digits with ASCII digits.

Args:

- `text` (`str`): Raw string that may contain spaces and Unicode subscript digits.

Returns:

- `str`: String with spaces removed and ₀-₉ replaced by 0-9.

<details>
<summary>Code:</summary>

```python
def clean_number_text(text: str) -> str:
    return (
        str(text)
        .replace(" ", "")
        .replace("₀", "0")
        .replace("₁", "1")
        .replace("₂", "2")
        .replace("₃", "3")
        .replace("₄", "4")
        .replace("₅", "5")
        .replace("₆", "6")
        .replace("₇", "7")
        .replace("₈", "8")
        .replace("₉", "9")
    )
```

</details>

## 🔧 Function `evaluate_arithmetic_expression`

```python
def evaluate_arithmetic_expression(expression: str) -> float
```

Safely evaluate a simple arithmetic expression (`+`, `-`, `*`, `/`, parentheses).

Args:

- `expression` (`str`): String containing a mathematical expression.

Returns:

- `float`: Calculated result.

Raises:

- `ValueError`: If the expression is empty, invalid, or unsafe.

<details>
<summary>Code:</summary>

```python
def evaluate_arithmetic_expression(expression: str) -> float:
    expression = expression.replace(" ", "").replace(",", ".")
    if not expression:
        msg = "Expression is empty"
        raise ValueError(msg)

    if not re.match(r"^[0-9+\-*/().]+$", expression):
        msg = "Expression contains invalid characters"
        raise ValueError(msg)

    if expression.count("(") != expression.count(")"):
        msg = "Unbalanced parentheses"
        raise ValueError(msg)

    def _raise_value_error(msg: str) -> NoReturn:
        raise ValueError(msg)

    try:
        tree = ast.parse(expression, mode="eval")
        if not _is_safe_arithmetic_node(tree):
            _raise_value_error("Expression contains unsafe operations")
        code = compile(tree, "<string>", "eval")
        result = eval(code, {"__builtins__": {}}, {})  # noqa: S307
        if not isinstance(result, (int, float)):
            _raise_value_error("Expression does not evaluate to a number")
        return float(result)
    except SyntaxError as e:
        _raise_value_error(f"Invalid expression syntax: {e!s}")
    except ZeroDivisionError:
        _raise_value_error("Division by zero")
    except ValueError:
        raise
    except Exception as e:
        _raise_value_error(f"Invalid expression: {e!s}")
```

</details>

## 🔧 Function `format_amount`

```python
def format_amount(value: float | str) -> str
```

Format amount with spaces for thousands separator and subscript decimals.

Args:

- `value` (`float | str`): The value to format.

Returns:

- `str`: The formatted text with spaces as thousands separators and subscript decimal digits.

<details>
<summary>Code:</summary>

```python
def format_amount(value: float | str) -> str:
    try:
        text = str(value)
        is_negative = text.startswith("-")
        if is_negative:
            text = text[1:]

        try:
            num = float(text)
        except (ValueError, TypeError):
            return str(value)

        if "." in str(num):
            integer_part, decimal_part = str(num).split(".")
        else:
            integer_part = str(int(num))
            decimal_part = "00"

        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer = " " + formatted_integer
            formatted_integer = digit + formatted_integer

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

        formatted = formatted_integer if num == int(num) else f"{formatted_integer}.{subscript_decimal}"
        if is_negative:
            formatted = "-" + formatted
    except Exception:
        return str(value)
    else:
        return formatted
```

</details>

## 🔧 Function `try_evaluate_arithmetic_expression`

```python
def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]
```

Evaluate an expression and return `(value, None)` or `(None, error_message)`.

<details>
<summary>Code:</summary>

```python
def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]:
    try:
        return evaluate_arithmetic_expression(expression), None
    except ValueError as e:
        return None, str(e)
```

</details>
