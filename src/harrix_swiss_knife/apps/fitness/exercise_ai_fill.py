"""BotHub helper to fill exercise name, local name, unit, and calories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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
    from collections.abc import Callable

    from PySide6.QtWidgets import QDoubleSpinBox, QLineEdit, QPushButton, QWidget

_TSV_COLUMN_COUNT = 4


@dataclass(frozen=True)
class ExerciseFillResult:
    """Parsed AI fill fields for the add-exercise dialog."""

    name: str
    name_local: str
    unit: str
    calories_per_unit: float


def media_filename_hint(media_path: str) -> str:
    """Return the attached media filename, or an empty string when none is set."""
    path = media_path.strip()
    return Path(path).name if path else ""


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
    media_path: str = "",
    on_filled: Callable[[], None] | None = None,
    on_idle: Callable[[], None] | None = None,
) -> bool:
    """Fill English/local names, unit, and calories via BotHub.

    Returns:

    - `bool`: `True` when the request started.

    """

    def apply_result(result: ExerciseFillResult) -> None:
        name_edit.setText(result.name)
        name_local_edit.setText(result.name_local)
        unit_edit.setText(result.unit)
        calories_spin.setValue(result.calories_per_unit)
        if on_filled is not None:
            on_filled()

    return request_exercise_fill_from_values(
        parent,
        app_config=app_config,
        bothub_state=bothub_state,
        name=name_edit.text(),
        name_local=name_local_edit.text(),
        media_path=media_path,
        on_filled=apply_result,
        on_idle=on_idle,
        fill_button=fill_button,
    )


def request_exercise_fill_from_values(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    name: str,
    name_local: str,
    media_path: str = "",
    on_filled: Callable[[ExerciseFillResult], None],
    on_idle: Callable[[], None] | None = None,
    fill_button: QPushButton | None = None,
    owner_modal: bool = True,
) -> bool:
    """Fill exercise fields via BotHub from raw values.

    Returns:

    - `bool`: `True` when the request started.

    """
    name = name.strip()
    name_local = name_local.strip()
    media_filename = media_filename_hint(media_path)
    if not name and not name_local and not media_filename:
        message_box.warning(parent, "Fill with AI", "Enter English name, local name, or attach a media file first")
        return False

    try:
        prompt_text = build_prompt(
            app_config,
            "fitness_exercise_fill",
            {
                "NAME": name,
                "NAME_LOCAL": name_local,
                "MEDIA_FILENAME": media_filename,
                "LOCAL_LANGUAGE": get_apps_local_language_display_name(app_config),
            },
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return False

    if fill_button is not None:
        fill_button.setEnabled(False)

    def become_idle() -> None:
        if fill_button is not None:
            fill_button.setEnabled(True)
        if on_idle is not None:
            on_idle()

    def on_success(response_text: str) -> None:
        result = parse_exercise_fill_response(response_text)
        if result is None:
            become_idle()
            message_box.warning(parent, "Fill with AI", "BotHub returned an invalid exercise fill response")
            return
        if fill_button is not None:
            fill_button.setEnabled(True)
        on_filled(result)

    def on_error(error_message: str) -> None:
        become_idle()
        message_box.critical(parent, "BotHub Error", error_message)

    def on_cancelled() -> None:
        become_idle()

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
        owner_modal=owner_modal,
    )
    if not started:
        become_idle()
        return False
    return True


def should_auto_fill_exercise_on_ok(*, name: str, name_local: str, media_path: str) -> bool:
    """Return whether OK should fill missing English fields from local name and media.

    Args:

    - `name` (`str`): English exercise name.
    - `name_local` (`str`): Local-language name.
    - `media_path` (`str`): Attached media path.

    Returns:

    - `bool`: `True` when English name is empty and both local name and media are set.

    """
    return not name.strip() and bool(name_local.strip()) and bool(media_path.strip())


def _first_data_line(text: str) -> str:
    """Return first non-empty line, stripping Markdown code fences."""
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line
    return ""
