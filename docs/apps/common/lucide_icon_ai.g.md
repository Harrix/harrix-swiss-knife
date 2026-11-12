---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lucide_icon_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_lucide_icon_response`](#-function-parse_lucide_icon_response)
- [🔧 Function `request_lucide_icon_suggestions`](#-function-request_lucide_icon_suggestions)

</details>

## 🔧 Function `parse_lucide_icon_response`

```python
def parse_lucide_icon_response(response_text: str, *, known_names: Sequence[str] | None = None) -> list[str]
```

Extract unique Lucide ids from an AI response, validated against the catalog.

<details>
<summary>Code:</summary>

````python
def parse_lucide_icon_response(
    response_text: str,
    *,
    known_names: Sequence[str] | None = None,
) -> list[str]:
    catalog = tuple(known_names) if known_names is not None else list_lucide_icon_names()
    by_cf = {name.casefold(): name for name in catalog}
    found: list[str] = []
    seen: set[str] = set()
    cleaned = response_text.replace("```", "\n")
    for raw_line in cleaned.splitlines():
        line = raw_line.strip().lstrip("-*•").strip().strip("`").strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        for match in _ICON_ID_RE.finditer(line.casefold()):
            resolved = _resolve_lucide_icon_name(match.group(0), by_cf)
            if resolved is None or resolved in seen:
                continue
            seen.add(resolved)
            found.append(resolved)
            if len(found) >= _MAX_SUGGESTIONS:
                return found
    return found
````

</details>

## 🔧 Function `request_lucide_icon_suggestions`

```python
def request_lucide_icon_suggestions(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, query: str, on_icons: Callable[[list[str]], None], on_finished: Callable[[], None]) -> None
```

Ask AI for Lucide ids that match `query` and pass them to `on_icons`.

<details>
<summary>Code:</summary>

```python
def request_lucide_icon_suggestions(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    query: str,
    on_icons: Callable[[list[str]], None],
    on_finished: Callable[[], None],
) -> None:
    text = query.strip()
    if not text:
        on_finished()
        return

    try:
        prompt_text = build_prompt(app_config, "lucide_icon_suggest", {"QUERY": text})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        on_finished()
        return

    def on_success(response_text: str) -> None:
        on_finished()
        icons = parse_lucide_icon_response(response_text)
        if not icons:
            message_box.warning(parent, "Suggest Lucide", "AI returned no valid Lucide icons")
            return
        on_icons(icons)

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
        toast_message="Suggesting Lucide icons…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        on_finished()
```

</details>
