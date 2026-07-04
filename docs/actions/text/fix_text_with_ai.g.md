---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fix_text_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFixTextWithAI`](#️-class-onfixtextwithai)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnFixTextWithAI`

```python
class OnFixTextWithAI(ActionBase)
```

Send text to BotHub and return corrected text (no changes in `...` / code blocks).

<details>
<summary>Code:</summary>

```python
class OnFixTextWithAI(ActionBase):

    icon = "🤖"
    title = "Fix text with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("fixing text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show corrected output."""
        cli_sync = bool(kwargs.get("cli_sync", False))

        input_text = self.dialogs.get_text_textarea(
            "Fix text with AI",
            "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        try:
            prompt_text = build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = fix_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Fixed text diff (Before/After)",
            )

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Collect text, call BotHub, and show corrected output.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        cli_sync = bool(kwargs.get("cli_sync", False))

        input_text = self.dialogs.get_text_textarea(
            "Fix text with AI",
            "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        try:
            prompt_text = build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = fix_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Fixed text diff (Before/After)",
            )

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
```

</details>
