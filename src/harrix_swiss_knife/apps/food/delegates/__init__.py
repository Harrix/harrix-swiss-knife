"""Delegates for food app table views."""

from harrix_swiss_knife.apps.food.delegates.is_drink_delegate import (
    IsDrinkDelegate,
    is_drink_to_model,
    parse_is_drink_cell,
)

__all__ = [
    "IsDrinkDelegate",
    "is_drink_to_model",
    "parse_is_drink_cell",
]
