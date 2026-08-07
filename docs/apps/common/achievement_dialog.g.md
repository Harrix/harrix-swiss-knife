---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `achievement_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `MONTHLY_GOAL_STYLESHEET`](#-constant-monthly_goal_stylesheet)
- [📎 Constant `NEW_RECORD_STYLESHEET`](#-constant-new_record_stylesheet)
- [🔧 Function `show_monthly_goal_congratulations`](#-function-show_monthly_goal_congratulations)
- [🔧 Function `show_record_congratulations`](#-function-show_record_congratulations)

</details>

## 📎 Constant `MONTHLY_GOAL_STYLESHEET`

```python
MONTHLY_GOAL_STYLESHEET = '\n    QMessageBox {\n        background-color: #f0fff0;\n        font-size: 12px;\n    }\n    QMessageBox QLabel {\n        color: #228b22;\n        font-weight: bold;\n    }\n'
```

_No docstring provided._

## 📎 Constant `NEW_RECORD_STYLESHEET`

```python
NEW_RECORD_STYLESHEET = '\n    QMessageBox {\n        background-color: #f0f8ff;\n        font-size: 12px;\n    }\n    QMessageBox QLabel {\n        color: #2e8b57;\n        font-weight: bold;\n    }\n'
```

_No docstring provided._

## 🔧 Function `show_monthly_goal_congratulations`

```python
def show_monthly_goal_congratulations(parent: QWidget, exercise: str, type_name: str, current_value: float, unit: str | None = None) -> None
```

Show congratulations for achieving a monthly goal.

<details>
<summary>Code:</summary>

```python
def show_monthly_goal_congratulations(
    parent: QWidget,
    exercise: str,
    type_name: str,
    current_value: float,
    unit: str | None = None,
) -> None:
    unit_text = _unit_suffix(unit)
    exercise_display = _exercise_display(exercise, type_name or None)
    title = "✅ MONTHLY GOAL ACHIEVED! ✅"
    text = (
        f"🎉 Congratulations! You've achieved your MONTHLY GOAL! 🎉\n\n"
        f"Exercise: {exercise_display}\n"
        f"Current Month Progress: {int(current_value)}{unit_text}\n\n"
        f"🌟 Great job! Keep up the excellent work! 🌟"
    )
    message_box.information(parent, title, text, stylesheet=MONTHLY_GOAL_STYLESHEET)
```

</details>

## 🔧 Function `show_record_congratulations`

```python
def show_record_congratulations(parent: QWidget, exercise: str, record_info: dict, unit: str | None = None) -> None
```

Show congratulations for a new all-time or yearly record.

<details>
<summary>Code:</summary>

```python
def show_record_congratulations(
    parent: QWidget,
    exercise: str,
    record_info: dict,
    unit: str | None = None,
) -> None:
    unit_text = _unit_suffix(unit)
    exercise_display = _exercise_display(exercise, record_info.get("type_name") or None)
    current_value = record_info["current_value"]
    title = "🏆 NEW RECORD! 🏆"

    if record_info["is_all_time"]:
        previous_value = record_info["previous_all_time"]
        improvement = current_value - previous_value
        if previous_value == 0.0:
            text = (
                f"🎉 Congratulations! You've set your FIRST ALL-TIME RECORD! 🎉\n\n"
                f"Exercise: {exercise_display}\n"
                f"First Record: {current_value:g}{unit_text}\n\n"
                f"🚀 Great start! Keep up the momentum! 🚀"
            )
        else:
            text = (
                f"🎉 Congratulations! You've set a new ALL-TIME RECORD! 🎉\n\n"
                f"Exercise: {exercise_display}\n"
                f"New Record: {current_value:g}{unit_text}\n"
                f"Previous Best: {previous_value:g}{unit_text}\n"
                f"Improvement: +{improvement:g}{unit_text}\n\n"
                f"🔥 Amazing achievement! Keep up the great work! 🔥"
            )
    elif record_info["is_yearly"]:
        previous_value = record_info["previous_yearly"]
        improvement = current_value - previous_value
        if previous_value == 0.0:
            text = (
                f"🎊 Congratulations! You've set your FIRST YEARLY RECORD! 🎊\n\n"
                f"Exercise: {exercise_display}\n"
                f"First Year Record: {current_value:g}{unit_text}\n\n"
                f"⭐ Excellent start to the year! ⭐"
            )
        else:
            text = (
                f"🎊 Congratulations! You've set a new YEARLY RECORD! 🎊\n\n"
                f"Exercise: {exercise_display}\n"
                f"New Record: {current_value:g}{unit_text}\n"
                f"Previous Year Best: {previous_value:g}{unit_text}\n"
                f"Improvement: +{improvement:g}{unit_text}\n\n"
                f"⭐ Excellent progress this year! ⭐"
            )
    else:
        return

    message_box.information(parent, title, text, stylesheet=NEW_RECORD_STYLESHEET)
```

</details>
