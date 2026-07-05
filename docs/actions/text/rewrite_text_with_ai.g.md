---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `rewrite_text_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRewriteTextWithAI`](#️-class-onrewritetextwithai)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `_run`](#️-method-_run)

</details>

## 🏛️ Class `OnRewriteTextWithAI`

```python
class OnRewriteTextWithAI(ActionBase)
```

Send text to BotHub and return deeply rewritten text (no changes in `...` / code blocks).

<details>
<summary>Code:</summary>

```python
class OnRewriteTextWithAI(ActionBase):

    icon = "✍️"
    title = "Rewrite text with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("rewriting text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show rewritten output."""
        self._run(initial_text=kwargs.get("initial_text"), cli_sync=bool(kwargs.get("cli_sync", False)))

    def _run(self, *, initial_text: str | None = None, cli_sync: bool = False) -> None:
        if initial_text is None:
            input_text = self.dialogs.get_text_textarea(
                "Rewrite text with AI",
                (
                    "Paste text for deep rewrite (grammar, style, sentence flow).\n"
                    "Code in backticks must remain unchanged."
                ),
            )
            if input_text is None:
                return
        else:
            input_text = initial_text

        try:
            prompt_text = build_text_rewrite_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = rewrite_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            dialog_result = self.show_text_multiline(
                result,
                title="Rewritten text (copied to clipboard)",
                rerun_button=True,
            )
            if isinstance(dialog_result, tuple):
                _, action_code = dialog_result
                if action_code == RERUN_DIALOG_CODE:
                    self._run(initial_text=result, cli_sync=True)
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            _, action_code = self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Rewritten text diff (Before/After)",
                rerun_button=True,
            )
            if action_code == RERUN_DIALOG_CODE:
                self._run(initial_text=response_text)

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

Collect text, call BotHub, and show rewritten output.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self._run(initial_text=kwargs.get("initial_text"), cli_sync=bool(kwargs.get("cli_sync", False)))
```

</details>

### ⚙️ Method `_run`

```python
def _run(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _run(self, *, initial_text: str | None = None, cli_sync: bool = False) -> None:
        if initial_text is None:
            input_text = self.dialogs.get_text_textarea(
                "Rewrite text with AI",
                (
                    "Paste text for deep rewrite (grammar, style, sentence flow).\n"
                    "Code in backticks must remain unchanged."
                ),
            )
            if input_text is None:
                return
        else:
            input_text = initial_text

        try:
            prompt_text = build_text_rewrite_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = rewrite_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            dialog_result = self.show_text_multiline(
                result,
                title="Rewritten text (copied to clipboard)",
                rerun_button=True,
            )
            if isinstance(dialog_result, tuple):
                _, action_code = dialog_result
                if action_code == RERUN_DIALOG_CODE:
                    self._run(initial_text=result, cli_sync=True)
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            _, action_code = self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Rewritten text diff (Before/After)",
                rerun_button=True,
            )
            if action_code == RERUN_DIALOG_CODE:
                self._run(initial_text=response_text)

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
