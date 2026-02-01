"""Exercise progress calculator.

This module provides a centralized class for calculating exercise progress,
goals, remaining amounts, daily targets, and record achievements.
"""

from __future__ import annotations

import calendar
import math
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager


class ExerciseProgressCalculator:
    """Calculate exercise progress, goals, and achievements.

    This class centralizes all exercise progress calculations including:

    - Monthly data retrieval
    - Current progress calculation
    - Remaining amounts to goals
    - Daily target calculations
    - Today's remaining amount
    - Monthly goal achievement checking
    - Record checking (all-time and yearly)

    Attributes:

    - `db_manager` (`DatabaseManager`): Database manager instance.

    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize the calculator with a database manager.

        Args:
            - `db_manager` (`DatabaseManager`): Database manager instance.

        """
        self.db_manager = db_manager

    def calculate_daily_needed(
        self, remaining_amount: float, remaining_days: int, total_days_including_current: int
    ) -> tuple[float, float]:
        """Calculate daily needed amounts.

        Args:

        - `remaining_amount` (`float`): Remaining amount to reach goal.
        - `remaining_days` (`int`): Remaining days in month (excluding today).
        - `total_days_including_current` (`int`): Total days including current day.

        Returns:

        - `tuple[float, float]`: Tuple of (daily_needed_including_current, daily_needed_max).
          - `daily_needed_including_current`: Daily amount needed including today.
          - `daily_needed_max`: Daily amount needed for remaining days only.

        """
        daily_needed_including_current = 0.0
        daily_needed_max = 0.0

        if total_days_including_current > 0:
            daily_needed_including_current = remaining_amount / total_days_including_current
            daily_needed_including_current = int(daily_needed_including_current) + (
                1 if daily_needed_including_current % 1 > 0 else 0
            )

        if remaining_days > 0:
            daily_needed_max = remaining_amount / remaining_days
            daily_needed_max = int(daily_needed_max) + (1 if daily_needed_max % 1 > 0 else 0)

        return (daily_needed_including_current, daily_needed_max)

    def calculate_exercise_recommendations(self, monthly_data: list, months_count: int) -> dict[str, float]:
        """Calculate exercise recommendations based on monthly data.

        Args:

        - `monthly_data` (`list`): Monthly data from get_monthly_data_for_exercise.
        - `months_count` (`int`): Number of months analyzed.

        Returns:

        - `dict[str, float]`: Dictionary containing all recommendation values:
          - `current_progress`: Current month progress
          - `last_month_value`: Last month total value
          - `max_value`: Maximum value across all months
          - `remaining_to_last_month`: Remaining amount to reach last month value
          - `remaining_to_max`: Remaining amount to reach max value
          - `daily_needed_last_month`: Daily amount needed to reach last month goal
          - `daily_needed_max`: Daily amount needed to reach max goal

        """
        # Find the maximum final value from all months and last month value
        max_value = 0.0
        last_month_value = 0.0

        for i, month_data in enumerate(monthly_data):
            if month_data:
                final_value = month_data[-1][1]
                max_value = max(max_value, final_value)
                # Last month is the second item (index 1) if it exists
                if i == 1:
                    last_month_value = final_value

        # Get current month progress
        today = datetime.now(UTC).astimezone()
        current_month_data = monthly_data[0] if monthly_data else []
        current_progress = current_month_data[-1][1] if current_month_data else 0.0

        # Calculate remaining amounts
        remaining_to_max = max(0, max_value - current_progress)
        remaining_to_last_month = max(0, last_month_value - current_progress) if last_month_value > 0 else 0

        # Calculate remaining days in current month
        current_month = today.month
        current_year = today.year
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day

        # Calculate daily needed amounts
        daily_needed_max = (
            int(remaining_to_max / remaining_days) + (1 if remaining_to_max % remaining_days > 0 else 0)
            if remaining_days > 0
            else 0
        )
        daily_needed_last_month = (
            int(remaining_to_last_month / remaining_days) + (1 if remaining_to_last_month % remaining_days > 0 else 0)
            if remaining_days > 0
            else 0
        )

        return {
            "current_progress": current_progress,
            "last_month_value": last_month_value,
            "max_value": max_value,
            "remaining_to_last_month": remaining_to_last_month,
            "remaining_to_max": remaining_to_max,
            "daily_needed_last_month": daily_needed_last_month,
            "daily_needed_max": daily_needed_max,
        }

    def check_for_new_records(
        self, exercise_id: int, type_id: int, current_value: float, type_name: str
    ) -> dict | None:
        """Check if the current value would be a new all-time or yearly record.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID.
        - `current_value` (`float`): Current value to check.
        - `type_name` (`str`): Type name.

        Returns:

        - `dict | None`: Record information if new record is found, None otherwise. Dictionary contains:
          - `is_all_time`: True if all-time record
          - `is_yearly`: True if yearly record
          - `current_value`: Current value
          - `previous_all_time`: Previous all-time record value
          - `previous_yearly`: Previous yearly record value
          - `type_name`: Type name

        """
        try:
            # Calculate date one year ago
            one_year_ago = datetime.now(UTC).astimezone() - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")

            # Use database manager method
            all_time_max, yearly_max = self.db_manager.get_exercise_max_values(exercise_id, type_id, one_year_ago_str)

            # Check for new records
            is_all_time_record = current_value > all_time_max
            is_yearly_record = current_value > yearly_max and not is_all_time_record

            if is_all_time_record or is_yearly_record:
                return {
                    "is_all_time": is_all_time_record,
                    "is_yearly": is_yearly_record,
                    "current_value": current_value,
                    "previous_all_time": all_time_max,
                    "previous_yearly": yearly_max,
                    "type_name": type_name,
                }
        except Exception as e:
            print(f"Error checking for new records: {e}")
            # Don't show error to user for first-time records, just return None

        return None

    def check_monthly_goal_achievement(
        self, exercise_id: int, exercise_name: str, added_value: float, date_str: str, months_count: int
    ) -> tuple[bool, float]:
        """Check if monthly goal was achieved when adding this record.

        Checks if "Remaining to Max" becomes 0 or less when adding this record.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `exercise_name` (`str`): Exercise name.
        - `added_value` (`float`): Value that was added.
        - `date_str` (`str`): Date string in YYYY-MM-DD format.
        - `months_count` (`int`): Number of months to compare.

        Returns:

        - `tuple[bool, float]`: Tuple of (True if monthly goal was achieved, current progress after adding).

        """
        goal_achieved = False
        current_progress = 0.0

        try:
            # Only check for today's records
            today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            if date_str == today:
                monthly_data = self.get_monthly_data_for_exercise(exercise_name, months_count)

                if monthly_data and any(month_data for month_data in monthly_data):
                    # Find the maximum final value from all months
                    max_value = 0.0
                    for month_data in monthly_data:
                        if month_data:
                            final_value = month_data[-1][1]
                            max_value = max(max_value, final_value)

                    if max_value > 0:
                        # Get current month progress (after adding the record)
                        current_month_data = monthly_data[0] if monthly_data else []
                        current_progress_after = current_month_data[-1][1] if current_month_data else 0.0

                        # Calculate progress before adding (subtract the added value)
                        current_progress_before = current_progress_after - added_value

                        # Calculate remaining_to_max before and after adding
                        remaining_to_max_before = max(0, max_value - current_progress_before)
                        remaining_to_max_after = max(0, max_value - current_progress_after)

                        # Goal was achieved if remaining_to_max_before > 0 and remaining_to_max_after <= 0
                        goal_achieved = remaining_to_max_before > 0 and remaining_to_max_after <= 0
                        current_progress = current_progress_after
        except Exception as e:
            print(f"Error checking for monthly goal achievement: {e}")

        return (goal_achieved, current_progress)

    def get_monthly_data_for_exercise(self, exercise_name: str, months_count: int) -> list:
        """Get monthly data for a specific exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.
        - `months_count` (`int`): Number of months to analyze.

        Returns:

        - `list`: List of monthly data, where each item is a list of (day, cumulative_value) tuples.

        """
        monthly_data = []
        today = datetime.now(UTC).astimezone()

        for i in range(months_count):
            # Calculate start and end of month
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = today
            else:
                last_day = calendar.monthrange(month_start.year, month_start.month)[1]
                month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Format for DB
            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            # Query data for this exercise (all types)
            rows = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise_name,
                exercise_type=None,  # Get all types
                date_from=date_from,
                date_to=date_to,
            )

            # Build cumulative data for this month
            cumulative_data = []
            if rows:
                cumulative_value = 0.0
                for date_str, value_str in rows:
                    try:
                        date_obj = datetime.fromisoformat(date_str).replace(tzinfo=UTC)
                        value = float(value_str)
                        cumulative_value += value
                        day_of_month = date_obj.day
                        cumulative_data.append((day_of_month, cumulative_value))
                    except (ValueError, TypeError):
                        continue

                # Extend horizontally to the end-of-visualization day
                if cumulative_data:
                    last_day_in_data = cumulative_data[-1][0]
                    last_value = cumulative_data[-1][1]
                    if i == 0:
                        # Current month: extend to today
                        today_day = today.day
                        if last_day_in_data < today_day:
                            cumulative_data.append((today_day, last_value))
                    else:
                        # Past months: extend to last day of month
                        last_day_of_month = calendar.monthrange(month_start.year, month_start.month)[1]
                        if last_day_in_data < last_day_of_month:
                            cumulative_data.append((last_day_of_month, last_value))

            monthly_data.append(cumulative_data)

        return monthly_data

    def get_remaining_days_info(self) -> tuple[int, int]:
        """Get remaining days information for current month.

        Returns:

        - `tuple[int, int]`: Tuple of (remaining_days, total_days_including_current).
            - `remaining_days`: Remaining days in month (excluding today).
            - `total_days_including_current`: Total days including current day.

        """
        today = datetime.now(UTC).astimezone()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1
        return (remaining_days, total_days_including_current)

    def get_today_goal_info(self, exercise_name: str, months_count: int) -> str:
        """Get today's goal information for an exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.
        - `months_count` (`int`): Number of months to compare.

        Returns:

        - `str`: Empty string if no data, checkmark with count if goal achieved,
          or remaining count if goal not achieved.

        """
        if self.db_manager is None:
            return ""

        # Get exercise ID
        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return ""

        # Get monthly data
        monthly_data = self.get_monthly_data_for_exercise(exercise_name, months_count)

        if not monthly_data or not any(month_data for month_data in monthly_data):
            return ""

        # Find the maximum final value from all months
        # monthly_data contains cumulative values, so we need the last value, not sum
        max_value = 0.0
        for month_data in monthly_data:
            if month_data:
                final_value = month_data[-1][1]  # Last cumulative value
                max_value = max(max_value, final_value)

        current_month_data = monthly_data[0] if monthly_data else []
        current_progress_with_today = current_month_data[-1][1] if current_month_data else 0.0

        target_value = max_value

        if target_value <= 0:
            return ""

        # Get today's progress
        today_progress = self.db_manager.get_exercise_total_today(exercise_id)

        # Calculate progress WITHOUT today's records to get stable daily target
        current_progress_without_today = current_progress_with_today - today_progress

        # Calculate remaining days in current month
        today = datetime.now(UTC).astimezone()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1

        # Calculate daily needed based on progress WITHOUT today
        # This makes the daily target stable and doesn't change when adding records
        remaining_to_goal = target_value - current_progress_without_today
        if total_days_including_current > 0 and remaining_to_goal > 0:
            daily_needed = remaining_to_goal / total_days_including_current
            daily_needed_rounded = math.ceil(daily_needed)

            # Calculate remaining for today: subtract what was already done today
            remaining_for_today = daily_needed_rounded - today_progress

            if remaining_for_today > 0:
                # Goal not achieved - show how much more is needed
                return f"(+{int(remaining_for_today)})"
            # Goal achieved - show checkmark and completed amount
            return f"✅ ({int(today_progress)})"
        if remaining_to_goal <= 0:
            # Max goal already achieved (without today's progress)
            return f"✅ ({int(today_progress)})"

        return ""

    def get_today_progress(self, exercise_id: int, exercise_name: str, exercise_type: str | None = None) -> float:
        """Get today's progress for an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `exercise_name` (`str`): Exercise name.
        - `exercise_type` (`str | None`): Exercise type or None for all types.

        Returns:

        - `float`: Today's progress value.

        """
        if exercise_type and exercise_type != "All types":
            # Get today's data for this specific exercise and type
            today = datetime.now(UTC).astimezone()
            today_data = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise_name,
                exercise_type=exercise_type,
                date_from=today.strftime("%Y-%m-%d"),
                date_to=today.strftime("%Y-%m-%d"),
            )
            return sum(float(value) for _, value in today_data)
        return self.db_manager.get_exercise_total_today(exercise_id)
