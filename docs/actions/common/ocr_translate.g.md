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
- [🔧 Function `show_ocr_translate_result`](#-function-show_ocr_translate_result)

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
        """Text to copy: translation when present, otherwise original."""
        if not self.is_local and self.translation.strip():
            return self.translation
        return self.original
```

</details>

### ⚙️ Method `display_text (property)`

```python
def display_text(self) -> str
```

Text to copy: translation when present, otherwise original.

<details>
<summary>Code:</summary>

```python
def display_text(self) -> str:
        if not self.is_local and self.translation.strip():
            return self.translation
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

## 🔧 Function `show_ocr_translate_result`

```python
def show_ocr_translate_result(action: ActionBase, result: OcrTranslateResult) -> None
```

Show original-only or original+translation dialog and copy the primary text.

<details>
<summary>Code:</summary>

```python
def show_ocr_translate_result(action: ActionBase, result: OcrTranslateResult) -> None:
    display = result.display_text.strip()
    if not display and not result.original.strip():
        action.add_line("No text recognized")
        action.show_toast("No text recognized")
        action.show_result(display_text="")
        return

    action.text_to_clipboard(display)
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
    )
    action.show_toast("✅ Recognized and translated")
```

</details>
