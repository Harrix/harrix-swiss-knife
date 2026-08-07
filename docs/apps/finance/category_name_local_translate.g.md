---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_name_local_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_category_name_local_response`](#-function-parse_category_name_local_response)
- [🔧 Function `request_category_name_local_translation`](#-function-request_category_name_local_translation)

</details>

## 🔧 Function `parse_category_name_local_response`

```python
def parse_category_name_local_response(response_text: str) -> str
```

Extract a single-line local category name from a BotHub response.

<details>
<summary>Code:</summary>

```python
def parse_category_name_local_response(response_text: str) -> str:
    for line in response_text.splitlines():
        text = line.strip().strip("`").strip('"').strip("'")
        if text:
            return text
    return response_text.strip()
```

</details>

## 🔧 Function `request_category_name_local_translation`

```python
def request_category_name_local_translation(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, name_edit: QLineEdit, name_local_edit: QLineEdit, translate_button: QPushButton) -> None
```

Translate category name into the local language via BotHub and fill `name_local_edit`.

<details>
<summary>Code:</summary>

```python
def request_category_name_local_translation(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    name_edit: QLineEdit,
    name_local_edit: QLineEdit,
    translate_button: QPushButton,
) -> None:
    name = name_edit.text().strip()
    if not name:
        message_box.warning(parent, "Translation", "Enter category name first")
        return

    try:
        prompt_text = build_prompt(app_config, "finance_category_translate_local", {"CATEGORY_NAME": name})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    translate_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        translate_button.setEnabled(True)
        translated = parse_category_name_local_response(response_text)
        if not translated:
            message_box.warning(parent, "Translation", "BotHub returned an empty translation")
            return
        name_local_edit.setText(translated)

    def on_error(error_message: str) -> None:
        translate_button.setEnabled(True)
        message_box.critical(parent, "BotHub Error", error_message)

    def on_cancelled() -> None:
        translate_button.setEnabled(True)

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        toast_message="Translating category…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        translate_button.setEnabled(True)
```

</details>
