---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `name_local_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_name_local_batch_response`](#-function-parse_name_local_batch_response)
- [🔧 Function `parse_name_local_response`](#-function-parse_name_local_response)
- [🔧 Function `request_name_local_translation`](#-function-request_name_local_translation)
- [🔧 Function `request_names_local_batch_translation`](#-function-request_names_local_batch_translation)

</details>

## 🔧 Function `parse_name_local_batch_response`

```python
def parse_name_local_batch_response(text: str) -> dict[str, str]
```

Parse TSV lines `Name<TAB>LocalName` into a name-to-translation map.

<details>
<summary>Code:</summary>

```python
def parse_name_local_batch_response(text: str) -> dict[str, str]:
    translations: dict[str, str] = {}
    for line in _iter_data_lines(text):
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        name = parts[0].strip()
        name_local = parts[1].strip()
        if not name or not name_local:
            continue
        translations[name] = name_local
    return translations
```

</details>

## 🔧 Function `parse_name_local_response`

```python
def parse_name_local_response(response_text: str) -> str
```

Extract a single-line local name from a BotHub response.

<details>
<summary>Code:</summary>

```python
def parse_name_local_response(response_text: str) -> str:
    for line in response_text.splitlines():
        text = line.strip().strip("`").strip('"').strip("'")
        if text:
            return text
    return response_text.strip()
```

</details>

## 🔧 Function `request_name_local_translation`

```python
def request_name_local_translation(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, name_edit: QLineEdit, name_local_edit: QLineEdit, translate_button: QPushButton) -> None
```

Translate between English name and local name via BotHub.

Prefer English → local when `name_edit` is filled. If English is empty and
local is filled, translate local → English into `name_edit`.

<details>
<summary>Code:</summary>

```python
def request_name_local_translation(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    name_edit: QLineEdit,
    name_local_edit: QLineEdit,
    translate_button: QPushButton,
) -> None:
    name = name_edit.text().strip()
    name_local = name_local_edit.text().strip()
    local_language = get_apps_local_language_display_name(app_config)

    if name:
        prompt_key = "fitness_name_translate_local"
        prompt_vars = {"NAME": name, "LOCAL_LANGUAGE": local_language}
        target_edit = name_local_edit
        toast_message = "Translating name…"
    elif name_local:
        prompt_key = "fitness_name_translate_from_local"
        prompt_vars = {"NAME_LOCAL": name_local, "LOCAL_LANGUAGE": local_language}
        target_edit = name_edit
        toast_message = "Translating local name…"
    else:
        message_box.warning(parent, "Translation", "Enter English name or local name first")
        return

    try:
        prompt_text = build_prompt(app_config, prompt_key, prompt_vars)
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    translate_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        translate_button.setEnabled(True)
        translated = parse_name_local_response(response_text)
        if not translated:
            message_box.warning(parent, "Translation", "BotHub returned an empty translation")
            return
        target_edit.setText(translated)

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
        toast_message=toast_message,
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        translate_button.setEnabled(True)
```

</details>

## 🔧 Function `request_names_local_batch_translation`

```python
def request_names_local_batch_translation(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, names: list[str], on_success: Callable[[dict[str, str]], None], on_finished: Callable[[], None] | None = None) -> None
```

Translate many names into the local language and pass a map to `on_success`.

<details>
<summary>Code:</summary>

```python
def request_names_local_batch_translation(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    names: list[str],
    on_success: Callable[[dict[str, str]], None],
    on_finished: Callable[[], None] | None = None,
) -> None:
    if not names:
        message_box.information(parent, "Translation", "All names already have a local translation.")
        if on_finished is not None:
            on_finished()
        return

    names_text = "\n".join(names)
    try:
        prompt_text = build_prompt(
            app_config,
            "fitness_names_translate_local",
            {
                "NAMES": names_text,
                "LOCAL_LANGUAGE": get_apps_local_language_display_name(app_config),
            },
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        if on_finished is not None:
            on_finished()
        return

    def success_wrapper(response_text: str) -> None:
        translations = parse_name_local_batch_response(response_text)
        on_success(translations)
        if on_finished is not None:
            on_finished()

    def on_error(error_message: str) -> None:
        message_box.critical(parent, "BotHub Error", error_message)
        if on_finished is not None:
            on_finished()

    def on_cancelled() -> None:
        if on_finished is not None:
            on_finished()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        success_wrapper,
        toast_message="Translating names…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started and on_finished is not None:
        on_finished()
```

</details>
