---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_emoji_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_habit_emoji_response`](#-function-parse_habit_emoji_response)
- [🔧 Function `request_habit_emoji_suggestion`](#-function-request_habit_emoji_suggestion)

</details>

## 🔧 Function `parse_habit_emoji_response`

```python
def parse_habit_emoji_response(response_text: str) -> str
```

Extract a single emoji from an AI response.

<details>
<summary>Code:</summary>

````python
def parse_habit_emoji_response(response_text: str) -> str:
    for raw_line in response_text.strip().splitlines():
        line = raw_line.strip().strip("`").strip('"').strip("'")
        if not line or line.startswith("```"):
            continue
        match = _EMOJI_RE.search(line)
        if match:
            return match.group(0)
        token = line.split()[0]
        if token and not re.search(r"[A-Za-z]", token):
            return token
    return ""
````

</details>

## 🔧 Function `request_habit_emoji_suggestion`

```python
def request_habit_emoji_suggestion(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, habit_name: str, suggest_button: QPushButton, on_emoji: Callable[[str], None], on_finished: Callable[[], None]) -> None
```

Ask AI for an emoji that matches [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) and pass it to `on_emoji`.

<details>
<summary>Code:</summary>

```python
def request_habit_emoji_suggestion(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    habit_name: str,
    suggest_button: QPushButton,
    on_emoji: Callable[[str], None],
    on_finished: Callable[[], None],
) -> None:
    name = habit_name.strip()
    if not name:
        on_finished()
        return

    try:
        prompt_text = build_prompt(app_config, "habits_emoji_suggest", {"HABIT_NAME": name})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        on_finished()
        return

    suggest_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        on_finished()
        emoji = parse_habit_emoji_response(response_text)
        if not emoji:
            message_box.warning(parent, "Suggest emoji", "AI returned no emoji")
            return
        on_emoji(emoji)

    def on_error(error_message: str) -> None:
        on_finished()
        message_box.critical(parent, "AI Error", error_message)

    def on_cancelled() -> None:
        on_finished()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        toast_message="Suggesting emoji…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        on_finished()
```

</details>
