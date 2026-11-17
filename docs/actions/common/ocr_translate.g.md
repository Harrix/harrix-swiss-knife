---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ocr_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OcrTranslateResult`](#%EF%B8%8F-class-ocrtranslateresult)
  - [⚙️ Method `display_text (property)`](#%EF%B8%8F-method-display_text-property)
- [🔧 Function `local_language_code_from_config`](#-function-local_language_code_from_config)
- [🔧 Function `parse_ocr_translate_response`](#-function-parse_ocr_translate_response)
- [🔧 Function `present_ai_markdown_answer`](#-function-present_ai_markdown_answer)
- [🔧 Function `present_recognized_text`](#-function-present_recognized_text)
- [🔧 Function `show_ocr_translate_result`](#-function-show_ocr_translate_result)
- [🔧 Function `start_text_translation`](#-function-start_text_translation)
- [🔧 Function `text_needs_translation`](#-function-text_needs_translation)

</details>

## 🏛️ Class `OcrTranslateResult`

```python
class OcrTranslateResult
```

Recognized text plus optional translation into the local language.

<details>
<summary>Code:</summary>

```python
class OcrTranslateResult:

    language: str
    is_local: bool
    original: str
    translation: str

    @property
    def display_text(self) -> str:
        """Text to copy by default: original OCR text."""
        return self.original
```

</details>

### ⚙️ Method `display_text (property)`

```python
def display_text(self) -> str
```

Text to copy by default: original OCR text.

<details>
<summary>Code:</summary>

```python
def display_text(self) -> str:
        return self.original
```

</details>

## 🔧 Function `local_language_code_from_config`

```python
def local_language_code_from_config(config: dict[str, Any]) -> str
```

Return `apps.local_language` for OCR/translate parsers.

<details>
<summary>Code:</summary>

```python
def local_language_code_from_config(config: dict[str, Any]) -> str:
    return get_apps_local_language(config)
```

</details>

## 🔧 Function `parse_ocr_translate_response`

```python
def parse_ocr_translate_response(text: str, *, local_language_code: str | None = None) -> OcrTranslateResult
```

Parse a BotHub OCR+translate JSON response into [`OcrTranslateResult`](#%EF%B8%8F-class-ocrtranslateresult).

<details>
<summary>Code:</summary>

```python
def parse_ocr_translate_response(text: str, *, local_language_code: str | None = None) -> OcrTranslateResult:
    payload = _extract_json_object(text)
    if payload is None:
        original = text.strip()
        return OcrTranslateResult(
            language="und",
            is_local=True,
            original=original,
            translation="",
        )

    original = str(payload.get("original") or "").strip()
    translation = str(payload.get("translation") or "").strip()
    language = str(payload.get("language") or "und").strip().lower() or "und"
    raw_local = payload.get("is_local")
    if isinstance(raw_local, bool):
        is_local = raw_local
    else:
        code = (local_language_code or "").strip().lower()
        is_local = not translation or (bool(code) and language == code) or translation == original

    if not original and not translation:
        return OcrTranslateResult(language=language, is_local=True, original="", translation="")

    if is_local or not translation or translation == original:
        return OcrTranslateResult(
            language=language,
            is_local=True,
            original=original or translation,
            translation="",
        )

    return OcrTranslateResult(
        language=language,
        is_local=False,
        original=original,
        translation=translation,
    )
```

</details>

## 🔧 Function `present_ai_markdown_answer`

```python
def present_ai_markdown_answer(action: ActionBase, markdown: str, *, title: str | None = None, save_button: bool = False, save_default_path: str | None = None, rerun_button: bool = False, rerun_button_label: str = 'Run again', rerun_button_icon: str = 'refresh-cw', rewrite_button: bool = False, ask_ai_button: bool = False, translate_button: bool | None = None, remove_paragraphs_button: bool = False, handle_translate: bool = True) -> str | tuple[str | None, int] | None
```

Show an AI Markdown answer with Harrix `blank.html` when possible.

Prefers `QWebEngineView` + `path_html_template_dist/blank.html` (code highlight +
KaTeX). Falls back to Qt `setMarkdown` when WebEngine or the template is missing.

When `handle_translate` is `True` (default), starts translation if the user
presses Translate and does not return the dialog tuple to the caller.

<details>
<summary>Code:</summary>

```python
def present_ai_markdown_answer(
    action: ActionBase,
    markdown: str,
    *,
    title: str | None = None,
    save_button: bool = False,
    save_default_path: str | None = None,
    rerun_button: bool = False,
    rerun_button_label: str = "Run again",
    rerun_button_icon: str = "refresh-cw",
    rewrite_button: bool = False,
    ask_ai_button: bool = False,
    translate_button: bool | None = None,
    remove_paragraphs_button: bool = False,
    handle_translate: bool = True,
) -> str | tuple[str | None, int] | None:
    from harrix_swiss_knife.actions.common.ai_answer_webview import webengine_available  # noqa: PLC0415
    from harrix_swiss_knife.actions.common.ai_markdown_html import resolve_html_template_dist  # noqa: PLC0415

    offer_translate = (
        text_needs_translation(markdown, local_language_code_from_config(action.config))
        if translate_button is None
        else translate_button
    )
    dialog_title = title
    if dialog_title is None:
        dialog_title = "Ask AI answer"
        elapsed = action.elapsed_mm_ss()
        if elapsed is not None:
            dialog_title = f"Ask AI answer — {elapsed}"

    dist = resolve_html_template_dist(action.config if isinstance(action.config, dict) else None)

    def _show_plain_markdown() -> str | tuple[str | None, int] | None:
        return action.dialogs.show_text_multiline(
            markdown,
            dialog_title,
            open_folder_path=action.result_folder,
            save_button=save_button,
            save_default_path=save_default_path,
            rerun_button=rerun_button,
            rerun_button_label=rerun_button_label,
            rerun_button_icon=rerun_button_icon,
            rewrite_button=rewrite_button,
            ask_ai_button=ask_ai_button,
            translate_button=offer_translate,
            remove_paragraphs_button=remove_paragraphs_button,
            use_markdown=True,
        )

    dialog_result: str | tuple[str | None, int] | None
    if dist is not None and webengine_available():
        try:
            dialog_result = action.dialogs.show_ai_markdown(
                markdown,
                dialog_title,
                dist_dir=dist,
                open_folder_path=action.result_folder,
                save_button=save_button,
                save_default_path=save_default_path,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_icon=rerun_button_icon,
                rewrite_button=rewrite_button,
                ask_ai_button=ask_ai_button,
                translate_button=offer_translate,
                remove_paragraphs_button=remove_paragraphs_button,
            )
        except Exception:
            action.add_line("⚠️ Rich AI Markdown view failed; falling back to Qt Markdown")
            dialog_result = _show_plain_markdown()
    else:
        if dist is None:
            action.add_line("⚪ Rich AI Markdown needs `path_html_template_dist` with blank.html")
        elif not webengine_available():
            action.add_line("⚪ Rich AI Markdown needs PySide6-WebEngine; using Qt Markdown")
        dialog_result = _show_plain_markdown()

    if handle_translate and offer_translate and isinstance(dialog_result, tuple):
        text, action_code = dialog_result
        if action_code == TRANSLATE_DIALOG_CODE:
            start_text_translation(action, text or markdown)
            return None
    return dialog_result
```

</details>

## 🔧 Function `present_recognized_text`

```python
def present_recognized_text(action: ActionBase, markdown: str, *, save_button: bool = False, save_default_path: str | None = None, rich_markdown: bool = False) -> None
```

Show recognized text and offer Translate when it is not the local language.

<details>
<summary>Code:</summary>

```python
def present_recognized_text(
    action: ActionBase,
    markdown: str,
    *,
    save_button: bool = False,
    save_default_path: str | None = None,
    rich_markdown: bool = False,
) -> None:
    if rich_markdown:
        present_ai_markdown_answer(
            action,
            markdown,
            save_button=save_button,
            save_default_path=save_default_path,
        )
        return

    offer_translate = text_needs_translation(markdown, local_language_code_from_config(action.config))
    title = "Result"
    elapsed = action.elapsed_mm_ss()
    if elapsed is not None:
        title = f"Result — {elapsed}"
    dialog_result = action.dialogs.show_text_multiline(
        markdown,
        title,
        open_folder_path=action.result_folder,
        save_button=save_button,
        save_default_path=save_default_path,
        translate_button=offer_translate,
    )
    if not offer_translate or not isinstance(dialog_result, tuple):
        return
    text, action_code = dialog_result
    if action_code == TRANSLATE_DIALOG_CODE:
        start_text_translation(action, text or markdown)
```

</details>

## 🔧 Function `show_ocr_translate_result`

```python
def show_ocr_translate_result(action: ActionBase, result: OcrTranslateResult) -> None
```

Show original-only or original+translation dialog and copy the original text.

<details>
<summary>Code:</summary>

```python
def show_ocr_translate_result(action: ActionBase, result: OcrTranslateResult) -> None:
    original = result.original.strip()
    if not original and not result.translation.strip():
        action.add_line("No text recognized")
        action.show_toast("No text recognized")
        action.show_result(display_text="")
        return

    action.text_to_clipboard(original or result.translation.strip())
    action.add_line("📋 Text copied to clipboard")

    if result.is_local or not result.translation.strip():
        action.dialogs.show_text_multiline(
            result.original,
            title="Recognized text",
            remove_paragraphs_button=True,
        )
        action.show_toast("✅ Recognized text")
        return

    action.dialogs.show_text_diff_side_by_side(
        result.original,
        result.translation,
        title="Recognized text + translation",
        remove_paragraphs_button=True,
        before_label="Original",
        after_label="Translation",
        highlight_changes=False,
        copy_before=True,
        copy_after_button=True,
    )
    action.show_toast("✅ Recognized and translated")
```

</details>

## 🔧 Function `start_text_translation`

```python
def start_text_translation(action: ActionBase, original: str) -> None
```

Translate `original` into the local language and show original + translation.

<details>
<summary>Code:</summary>

```python
def start_text_translation(action: ActionBase, original: str) -> None:
    source = original.strip()
    if not source:
        return
    try:
        prompt_text = build_text_translate_prompt(source, action.config)
    except ValueError as exc:
        show_bothub_prompt_build_error(None, exc)
        return

    state = getattr(action, "_bothub_state", None)
    if not isinstance(state, BothubRequestState):
        state = BothubRequestState()
        action._bothub_state = state  # noqa: SLF001

    def on_error(message: str) -> None:
        message_box.critical(None, "BotHub Error", message)

    def on_success(response_text: str) -> None:
        translation = response_text.strip()
        if not translation:
            message_box.warning(None, "Translate", "AI returned an empty translation")
            return
        action.text_to_clipboard(source)
        action.dialogs.show_text_diff_side_by_side(
            source,
            translation,
            title="Recognized text + translation",
            remove_paragraphs_button=True,
            before_label="Original",
            after_label="Translation",
            highlight_changes=False,
            copy_before=True,
            copy_after_button=True,
        )
        action.show_toast("✅ Translated")

    run_bothub_request(
        None,
        action.config,
        prompt_text,
        on_success,
        toast_message="Translating…",
        is_busy=lambda: state.worker is not None,
        state=state,
        on_error=on_error,
    )
```

</details>

## 🔧 Function `text_needs_translation`

```python
def text_needs_translation(text: str, local_language_code: str) -> bool
```

Return whether `text` looks unlike the configured local language.

<details>
<summary>Code:</summary>

```python
def text_needs_translation(text: str, local_language_code: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped == _EMPTY_OCR_MARKDOWN:
        return False
    cyrillic, latin, cjk = _script_letter_counts(stripped)
    total = cyrillic + latin + cjk
    if total < _MIN_SCRIPT_LETTERS:
        return False
    code = (local_language_code or "").strip().lower()
    local_share = latin / total
    if code in _CYRILLIC_CODES:
        local_share = cyrillic / total
    elif code in _CJK_CODES:
        local_share = cjk / total
    return local_share < _LOCAL_SCRIPT_MIN_SHARE
```

</details>
