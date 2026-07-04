---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fix_text_with_ai_from_clipboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFixTextWithAIFromClipboard`](#️-class-onfixtextwithaifromclipboard)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnFixTextWithAIFromClipboard`

```python
class OnFixTextWithAIFromClipboard(ActionBase)
```

Fix clipboard text with BotHub and put corrected text back to clipboard.

<details>
<summary>Code:</summary>

```python
class OnFixTextWithAIFromClipboard(ActionBase):

    icon = "🤖"
    title = "Fix text with AI from clipboard"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("fixing clipboard text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Read clipboard text, call BotHub, and copy fixed text to clipboard."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        try:
            prompt_text = build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            self.show_toast(f"❌ {exc!s}", duration=6000)
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                self.show_toast("❌ BotHub error: empty response.", duration=6000)
                return

            clipboard.setText(response_text, QClipboard.Mode.Clipboard)
            self.show_toast("✅ Fixed text copied to clipboard.", duration=4000)

        def on_error(message: str) -> None:
            self.show_toast(f"❌ BotHub error: {message}", duration=6000)

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

Read clipboard text, call BotHub, and copy fixed text to clipboard.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        try:
            prompt_text = build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            self.show_toast(f"❌ {exc!s}", duration=6000)
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                self.show_toast("❌ BotHub error: empty response.", duration=6000)
                return

            clipboard.setText(response_text, QClipboard.Mode.Clipboard)
            self.show_toast("✅ Fixed text copied to clipboard.", duration=4000)

        def on_error(message: str) -> None:
            self.show_toast(f"❌ BotHub error: {message}", duration=6000)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
```

</details>
