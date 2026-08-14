---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keywords_ai.py`

## 🔧 Function `request_keywords_fill`

```python
def request_keywords_fill(parent: QWidget, *, app_config: dict[str, Any], bothub_state: BothubRequestState, icon_path: Path, category: str, tags: list[str], fill_button: QPushButton, on_tags: Callable[[list[str]], None]) -> None
```

Send a raster preview plus category/tags to BotHub and return keywords.

<details>
<summary>Code:</summary>

```python
def request_keywords_fill(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    icon_path: Path,
    category: str,
    tags: list[str],
    fill_button: QPushButton,
    on_tags: Callable[[list[str]], None],
) -> None:
    image = render_icon_to_image(icon_path, _RASTER_SIDE)
    if image is None or image.isNull():
        message_box.warning(parent, "Process with AI", f"Could not rasterize icon:\n{icon_path}")
        return

    try:
        image_data = qimage_bytes_and_mime(image, max_image_side=_max_image_side(app_config))
        prompt_text = build_prompt(
            app_config,
            PROMPT_KEY,
            {
                "CATEGORY": category,
                "TAGS": "\n".join(tags),
            },
            prompt_display_name="vector_icons_keywords",
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    fill_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        fill_button.setEnabled(True)
        parsed = parse_keywords_text(response_text)
        if not parsed:
            message_box.warning(parent, "Process with AI", "BotHub returned no keywords.")
            return
        on_tags(parsed)

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
        image=image_data,
        toast_message="Processing keywords…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        fill_button.setEnabled(True)
```

</details>
