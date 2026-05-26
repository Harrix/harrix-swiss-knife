---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fix_text_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFixTextWithAI`](#%EF%B8%8F-class-onfixtextwithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

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

    icon = "🪄"
    title = "Fix text with AI (keep code)"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("fixing text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show corrected output."""
        input_text = self.dialogs.get_text_textarea(
            "Fix text with AI",
            "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        prompts_cfg = self.config.get("prompts") or {}
        prompt_template = str(prompts_cfg.get("text_fix_ru", "")).strip()
        if not prompt_template:
            message_box.warning(
                None,
                "Prompt",
                "Prompt text_fix_ru is not configured in config.json.",
            )
            return

        prompt_text = prompt_template.replace("{{TEXT}}", input_text)

        api_key = str(self.config.get("bothub_api_key", "")).strip()
        if not api_key:
            message_box.critical(
                None,
                "BotHub API Key",
                "BotHub API key is not configured.\n\n"
                "Copy api-keys/bothub-api-key.example.txt to api-keys/bothub-api-key.txt "
                "and put your key there.",
            )
            return

        bothub_cfg = self.config.get("bothub") or {}
        base_url = str(bothub_cfg.get("base_url", "https://bothub.chat/api/v2/openai/v1")).strip()
        model = str(bothub_cfg.get("model", "gpt-5.4")).strip()
        proxy_url = bothub_network.resolve_bothub_proxy_url(self.config)

        def work() -> str:
            try:
                return chat_completion(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    text=prompt_text,
                    proxy_url=proxy_url,
                )
            except BotHubApiError as exc:
                raise RuntimeError(str(exc)) from exc

        def on_done(result: object) -> None:
            if not isinstance(result, str) or not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(result)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")

        self.start_thread(work, on_done, "Requesting BotHub…")
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
        input_text = self.dialogs.get_text_textarea(
            "Fix text with AI",
            "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        prompts_cfg = self.config.get("prompts") or {}
        prompt_template = str(prompts_cfg.get("text_fix_ru", "")).strip()
        if not prompt_template:
            message_box.warning(
                None,
                "Prompt",
                "Prompt text_fix_ru is not configured in config.json.",
            )
            return

        prompt_text = prompt_template.replace("{{TEXT}}", input_text)

        api_key = str(self.config.get("bothub_api_key", "")).strip()
        if not api_key:
            message_box.critical(
                None,
                "BotHub API Key",
                "BotHub API key is not configured.\n\n"
                "Copy api-keys/bothub-api-key.example.txt to api-keys/bothub-api-key.txt "
                "and put your key there.",
            )
            return

        bothub_cfg = self.config.get("bothub") or {}
        base_url = str(bothub_cfg.get("base_url", "https://bothub.chat/api/v2/openai/v1")).strip()
        model = str(bothub_cfg.get("model", "gpt-5.4")).strip()
        proxy_url = bothub_network.resolve_bothub_proxy_url(self.config)

        def work() -> str:
            try:
                return chat_completion(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    text=prompt_text,
                    proxy_url=proxy_url,
                )
            except BotHubApiError as exc:
                raise RuntimeError(str(exc)) from exc

        def on_done(result: object) -> None:
            if not isinstance(result, str) or not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(result)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")

        self.start_thread(work, on_done, "Requesting BotHub…")
```

</details>
