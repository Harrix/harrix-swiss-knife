"""Delegates for food app table views."""

from harrix_swiss_knife.apps.common.delegates import DateDelegate
from harrix_swiss_knife.apps.food.delegates.day_total_delegate import (
    FoodLogDayTotalDelegate,
    apply_food_log_macros_row_heights,
)
from harrix_swiss_knife.apps.food.delegates.is_drink_delegate import (
    IsDrinkDelegate,
    is_drink_to_model,
    parse_is_drink_cell,
)

__all__ = [
    "DateDelegate",
    "FoodLogDayTotalDelegate",
    "IsDrinkDelegate",
    "apply_food_log_macros_row_heights",
    "is_drink_to_model",
    "parse_is_drink_cell",
]
