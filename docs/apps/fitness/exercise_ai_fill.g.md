---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_ai_fill.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseFillResult`](#%EF%B8%8F-class-exercisefillresult)
- [🔧 Function `media_filename_hint`](#-function-media_filename_hint)
- [🔧 Function `parse_exercise_fill_response`](#-function-parse_exercise_fill_response)
- [🔧 Function `request_exercise_fill`](#-function-request_exercise_fill)

</details>

## 🏛️ Class `ExerciseFillResult`

```python
class ExerciseFillResult
```

Parsed AI fill fields for the add-exercise dialog.

<details>
<summary>Code:</summary>

```python
class ExerciseFillResult:

    name: str
    name_local: str
    unit: str
    calories_per_unit: float
```

</details>

## 🔧 Function `media_filename_hint`

```python
def media_filename_hint(media_path: str) -> str
```

Return the attached media filename, or an empty string when none is set.

<details>
<summary>Code:</summary>

```python
def media_filename_hint(media_path: str) -> str:
    path = media_path.strip()
    return Path(path).name if path else ""
```

</details>

## 🔧 Function `parse_exercise_fill_response`

```python
def parse_exercise_fill_response(text: str) -> ExerciseFillResult | None
```

Parse a TSV line: Name, NameLocal, Unit, CaloriesPerUnit.

<details>
<summary>Code:</summary>

```python
def parse_exercise_fill_response(text: str) -> ExerciseFillResult | None:
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
```

</details>

## 🔧 Function `request_exercise_fill`

```python
def request_exercise_fill(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, name_edit: QLineEdit, name_local_edit: QLineEdit, unit_edit: QLineEdit, calories_spin: QDoubleSpinBox, fill_button: QPushButton, media_path: str = '') -> None
```

Fill English/local names, unit, and calories via BotHub.

<details>
<summary>Code:</summary>

```python
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
) -> None:
    name = name_edit.text().strip()
    name_local = name_local_edit.text().strip()
    media_filename = media_filename_hint(media_path)
    if not name and not name_local and not media_filename:
        message_box.warning(parent, "Fill with AI", "Enter English name, local name, or attach a media file first")
        return

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
```

</details>
