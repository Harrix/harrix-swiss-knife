"""Number parsing and safe arithmetic expression evaluation for finance app."""

from __future__ import annotations

import ast
import re
from typing import NoReturn


def clean_number_text(text: str) -> str:
    """Remove spaces and replace subscript digits with ASCII digits.

    Args:

    - `text` (`str`): Raw string that may contain spaces and Unicode subscript digits.

    Returns:

    - `str`: String with spaces removed and ₀-₉ replaced by 0-9.

    """
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


def evaluate_arithmetic_expression(expression: str) -> float:
    """Safely evaluate a simple arithmetic expression (`+`, `-`, `*`, `/`, parentheses).

    Args:

    - `expression` (`str`): String containing a mathematical expression.

    Returns:

    - `float`: Calculated result.

    Raises:

    - `ValueError`: If the expression is empty, invalid, or unsafe.

    """
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


def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]:
    """Evaluate an expression and return `(value, None)` or `(None, error_message)`."""
    try:
        return evaluate_arithmetic_expression(expression), None
    except ValueError as e:
        return None, str(e)


def _is_safe_arithmetic_node(node: ast.AST) -> bool:
    """Return `True` if the AST node is limited to safe arithmetic."""
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float))
    if isinstance(node, ast.BinOp):
        return (
            isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div))
            and _is_safe_arithmetic_node(node.left)
            and _is_safe_arithmetic_node(node.right)
        )
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.op, (ast.UAdd, ast.USub)) and _is_safe_arithmetic_node(node.operand)
    if isinstance(node, ast.Expression):
        return _is_safe_arithmetic_node(node.body)
    return False
