---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `speech_to_text_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSpeechToTextWithAI`](#%EF%B8%8F-class-onspeechtotextwithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnSpeechToTextWithAI`

```python
class OnSpeechToTextWithAI(ActionBase)
```

Convert audio to text via BotHub, then fix the transcript with the text fixing prompt.

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
        store = SpeechToTextPendingStore()
        pending = store.load()
        audio_path: str | None = None

        if pending is not None:
            choice = _ask_pending_choice(
                None,
                title="Unsent recording",
                text=(
                    "An unsent speech recording was found.\n\n"
                    f"{pending.path.name} · {format_file_size(pending.size_bytes)}\n\n"
                    "Retry sending it, discard it, or record a new one."
                ),
                include_record_new=True,
            )
            if choice == _PendingChoice.CLOSE:
                return
            if choice == _PendingChoice.DISCARD:
                store.clear()
            elif choice == _PendingChoice.RETRY:
                audio_path = str(pending.path)
            elif choice == _PendingChoice.RECORD_NEW:
                store.clear()

        if audio_path is None:
            audio_path = self._collect_audio_path()
            if not audio_path:
                return
            try:
                store.save(audio_path)
            except (OSError, ValueError) as exc:
                message_box.critical(None, "Speech to text", f"Could not preserve recording:\n{exc}")
                return
            pending = store.load()
            if pending is not None:
                audio_path = str(pending.path)

        self._process_audio_path(store, audio_path)

    def _collect_audio_path(self) -> str | None:
        dialog = AudioSourceDialog()
        if dialog.exec() != dialog.DialogCode.Accepted:
            dialog.release_multimedia()
            return None

        audio_path = dialog.get_audio_path()
        dialog.release_multimedia()
        return audio_path or None

    def _handle_process_failure(
        self,
        store: SpeechToTextPendingStore,
        message: str,
        *,
        show_retry_dialog: bool = True,
    ) -> None:
        """Keep the pending recording after a failed or cancelled send.

        Args:

        - `store` (`SpeechToTextPendingStore`): Pending audio store.
        - `message` (`str`): Error or cancel explanation.
        - `show_retry_dialog` (`bool`): When `False`, keep the file silently after the
          global AI retry dialog was already closed. Defaults to `True`.

        """
        pending = store.load()
        if pending is None:
            message_box.critical(None, "Speech to text", message)
            return

        if not show_retry_dialog:
            # Global Retry / Close already handled this turn; keep file for next launch.
            return

        choice = _ask_pending_choice(
            None,
            title="Speech to text",
            text=(f"{message}\n\nUnsent recording kept:\n{pending.path.name} · {format_file_size(pending.size_bytes)}"),
            include_record_new=False,
        )
        if choice == _PendingChoice.RETRY:
            self._process_audio_path(store, str(pending.path))
        elif choice == _PendingChoice.DISCARD:
            store.clear()
        # CLOSE: leave pending for the next launch.

    def _process_audio_path(self, store: SpeechToTextPendingStore, audio_path: str) -> None:
        try:
            audio_data = audio_bytes_and_mime(audio_path)
        except ValueError as exc:
            self._handle_process_failure(store, str(exc))
            return

        bothub_state = BothubRequestState()

        def on_fix_success(fixed_text: str) -> None:
            if not fixed_text.strip():
                self._handle_process_failure(store, "Empty response from BotHub.")
                return

            store.clear()
            current = fixed_text
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
            result_text, action_code = dialog_result
            if result_text is not None:
                current = result_text
            resolve_text_result_dialog_action(
                action_code,
                current,
                on_rerun=self,
                on_rewrite=lambda current=current: OnRewriteTextWithAI(output_bus=self._output_bus)(
                    initial_text=current
                ),
            )

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                self._handle_process_failure(store, "Empty transcription from BotHub.")
                return

            try:
                fix_prompt = build_text_fix_prompt(transcribed_text, self.config)
            except ValueError as exc:
                self._handle_process_failure(store, str(exc))
                return

            run_bothub_request(
                None,
                self.config,
                fix_prompt,
                on_fix_success,
                toast_message="Fixing text…",
                is_busy=lambda: bothub_state.worker is not None,
                state=bothub_state,
                on_error=lambda message: self._handle_process_failure(
                    store,
                    message,
                    show_retry_dialog=False,
                ),
                on_cancelled=lambda: self._handle_process_failure(
                    store,
                    "Request cancelled. The unsent recording was kept.",
                    show_retry_dialog=False,
                ),
            )

        started = run_bothub_request(
            None,
            self.config,
            build_transcription_prompt(),
            on_transcription_success,
            audio=audio_data,
            model=get_speech_model(self.config),
            toast_message="Recognizing speech…",
            is_busy=lambda: bothub_state.worker is not None,
            state=bothub_state,
            on_error=lambda message: self._handle_process_failure(
                store,
                message,
                show_retry_dialog=False,
            ),
            on_cancelled=lambda: self._handle_process_failure(
                store,
                "Request cancelled. The unsent recording was kept.",
                show_retry_dialog=False,
            ),
        )
        if not started:
            # API key / busy: keep pending for the next launch.
            pending = store.load()
            if pending is not None:
                self._handle_process_failure(
                    store,
                    "Could not start recognition. The unsent recording was kept.",
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
        store = SpeechToTextPendingStore()
        pending = store.load()
        audio_path: str | None = None

        if pending is not None:
            choice = _ask_pending_choice(
                None,
                title="Unsent recording",
                text=(
                    "An unsent speech recording was found.\n\n"
                    f"{pending.path.name} · {format_file_size(pending.size_bytes)}\n\n"
                    "Retry sending it, discard it, or record a new one."
                ),
                include_record_new=True,
            )
            if choice == _PendingChoice.CLOSE:
                return
            if choice == _PendingChoice.DISCARD:
                store.clear()
            elif choice == _PendingChoice.RETRY:
                audio_path = str(pending.path)
            elif choice == _PendingChoice.RECORD_NEW:
                store.clear()

        if audio_path is None:
            audio_path = self._collect_audio_path()
            if not audio_path:
                return
            try:
                store.save(audio_path)
            except (OSError, ValueError) as exc:
                message_box.critical(None, "Speech to text", f"Could not preserve recording:\n{exc}")
                return
            pending = store.load()
            if pending is not None:
                audio_path = str(pending.path)

        self._process_audio_path(store, audio_path)
```

</details>
