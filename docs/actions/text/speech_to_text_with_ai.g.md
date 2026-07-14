---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `speech_to_text_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSpeechToTextWithAI`](#️-class-onspeechtotextwithai)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnSpeechToTextWithAI`

```python
class OnSpeechToTextWithAI(ActionBase)
```

Convert audio to text via BotHub, then fix the transcript with the same prompt as OnFixTextWithAI.

<details>
<summary>Code:</summary>

```python
class OnSpeechToTextWithAI(ActionBase):

    icon = "🎙️"
    title = "Speech to text with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("converting speech to text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect audio, transcribe it to text, fix the transcript, and show the result."""
        dialog = AudioSourceDialog()
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        audio_path = dialog.get_audio_path()
        if not audio_path:
            return

        try:
            audio_data = audio_bytes_and_mime(audio_path)
        except ValueError as exc:
            message_box.critical(None, "Audio Error", str(exc))
            return

        bothub_state = BothubRequestState()

        def on_transcription_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_fix_success(fixed_text: str) -> None:
            if not fixed_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            current = fixed_text
            while True:
                self.text_to_clipboard(current)
                dialog_result = self.show_text_multiline(
                    current,
                    title="Speech to text result",
                    rerun_button=True,
                    rerun_button_label="Record new",
                    rerun_button_emoji="🎙️",
                    rewrite_button=True,
                    remove_paragraphs_button=True,
                )
                if not isinstance(dialog_result, tuple):
                    return
                _, action_code = dialog_result

                updated_text = resolve_text_result_dialog_action(
                    action_code,
                    current,
                    on_rerun=self,
                    on_rewrite=lambda current=current: OnRewriteTextWithAI(output_bus=self._output_bus)(
                        initial_text=current
                    ),
                )
                if updated_text is None:
                    return
                current = updated_text

        def on_fix_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                message_box.critical(None, "BotHub Error", "Empty transcription from BotHub.")
                return

            try:
                fix_prompt = build_text_fix_prompt(transcribed_text, self.config)
            except ValueError as exc:
                msg = str(exc)
                if msg == PROMPT_MISSING_MSG:
                    message_box.warning(None, "Prompt", msg)
                else:
                    message_box.critical(None, "BotHub API Key", msg)
                return

            run_bothub_request(
                None,
                self.config,
                fix_prompt,
                on_fix_success,
                toast_message="Fixing text…",
                is_busy=lambda: bothub_state.worker is not None,
                state=bothub_state,
                on_error=on_fix_error,
            )

        run_bothub_request(
            None,
            self.config,
            build_transcription_prompt(),
            on_transcription_success,
            audio=audio_data,
            model=get_speech_model(self.config),
            toast_message="Recognizing speech…",
            is_busy=lambda: bothub_state.worker is not None,
            state=bothub_state,
            on_error=on_transcription_error,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Collect audio, transcribe it to text, fix the transcript, and show the result.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        dialog = AudioSourceDialog()
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        audio_path = dialog.get_audio_path()
        if not audio_path:
            return

        try:
            audio_data = audio_bytes_and_mime(audio_path)
        except ValueError as exc:
            message_box.critical(None, "Audio Error", str(exc))
            return

        bothub_state = BothubRequestState()

        def on_transcription_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_fix_success(fixed_text: str) -> None:
            if not fixed_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            current = fixed_text
            while True:
                self.text_to_clipboard(current)
                dialog_result = self.show_text_multiline(
                    current,
                    title="Speech to text result",
                    rerun_button=True,
                    rerun_button_label="Record new",
                    rerun_button_emoji="🎙️",
                    rewrite_button=True,
                    remove_paragraphs_button=True,
                )
                if not isinstance(dialog_result, tuple):
                    return
                _, action_code = dialog_result

                updated_text = resolve_text_result_dialog_action(
                    action_code,
                    current,
                    on_rerun=self,
                    on_rewrite=lambda current=current: OnRewriteTextWithAI(output_bus=self._output_bus)(
                        initial_text=current
                    ),
                )
                if updated_text is None:
                    return
                current = updated_text

        def on_fix_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                message_box.critical(None, "BotHub Error", "Empty transcription from BotHub.")
                return

            try:
                fix_prompt = build_text_fix_prompt(transcribed_text, self.config)
            except ValueError as exc:
                msg = str(exc)
                if msg == PROMPT_MISSING_MSG:
                    message_box.warning(None, "Prompt", msg)
                else:
                    message_box.critical(None, "BotHub API Key", msg)
                return

            run_bothub_request(
                None,
                self.config,
                fix_prompt,
                on_fix_success,
                toast_message="Fixing text…",
                is_busy=lambda: bothub_state.worker is not None,
                state=bothub_state,
                on_error=on_fix_error,
            )

        run_bothub_request(
            None,
            self.config,
            build_transcription_prompt(),
            on_transcription_success,
            audio=audio_data,
            model=get_speech_model(self.config),
            toast_message="Recognizing speech…",
            is_busy=lambda: bothub_state.worker is not None,
            state=bothub_state,
            on_error=on_transcription_error,
        )
```

</details>
