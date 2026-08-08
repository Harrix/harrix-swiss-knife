"""BotHub helper to fill exercise name, local name, unit, and calories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.apps_config import get_apps_local_language_display_name
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDoubleSpinBox, QLineEdit, QPushButton, QWidget

_TSV_COLUMN_COUNT = 4


@dataclass(frozen=True)
class ExerciseFillResult:
    """Parsed AI fill fields for the add-exercise dialog."""

    name: str
    name_local: str
    unit: str
    calories_per_unit: float


def parse_exercise_fill_response(text: str) -> ExerciseFillResult | None:
    """Parse a TSV line: Name, NameLocal, Unit, CaloriesPerUnit."""
    line = _first_data_line(text)
    if not line:
        return None

    parts = line.split("\t")
    if len(parts) != _TSV_COLUMN_COUNT:
        return None

    name = parts[0].strip()
    name_local = parts[1].strip()
    unit = parts[2].strip()
    if not name or not unit:
        return None

    try:
        calories_per_unit = float(parts[3].strip().replace(",", "."))
    except ValueError:
        return None

    if calories_per_unit < 0:
        return None

    return ExerciseFillResult(
        name=name,
        name_local=name_local,
        unit=unit,
        calories_per_unit=calories_per_unit,
    )


def request_exercise_fill(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    name_edit: QLineEdit,
    name_local_edit: QLineEdit,
    unit_edit: QLineEdit,
    calories_spin: QDoubleSpinBox,
    fill_button: QPushButton,
) -> None:
    """Fill English/local names, unit, and calories via BotHub."""
    name = name_edit.text().strip()
    name_local = name_local_edit.text().strip()
    if not name and not name_local:
        message_box.warning(parent, "Fill with AI", "Enter English name or local name first")
        return

    try:
        prompt_text = build_prompt(
            app_config,
            "fitness_exercise_fill",
            {
                "NAME": name,
                "NAME_LOCAL": name_local,
                "LOCAL_LANGUAGE": get_apps_local_language_display_name(app_config),
            },
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    fill_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        fill_button.setEnabled(True)
        result = parse_exercise_fill_response(response_text)
        if result is None:
            message_box.warning(parent, "Fill with AI", "BotHub returned an invalid exercise fill response")
            return
        name_edit.setText(result.name)
        name_local_edit.setText(result.name_local)
        unit_edit.setText(result.unit)
        calories_spin.setValue(result.calories_per_unit)

    def on_error(error_message: str) -> None:
        fill_button.setEnabled(True)
        message_box.critical(parent, "BotHub Error", error_message)

    def on_cancelled() -> None:
        fill_button.setEnabled(True)

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        toast_message="Filling exercise fields…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        fill_button.setEnabled(True)


def _first_data_line(text: str) -> str:
    """Return first non-empty line, stripping Markdown code fences."""
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line
    return ""
