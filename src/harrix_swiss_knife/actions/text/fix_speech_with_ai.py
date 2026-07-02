"""Fix speech with AI (BotHub): transcribe audio then correct text."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.dialogs.audio_source_dialog import AudioSourceDialog
from harrix_swiss_knife.integrations.bothub import (
    PROMPT_MISSING_MSG,
    BothubRequestState,
    audio_bytes_and_format,
    build_text_fix_prompt,
    build_transcription_prompt,
    get_speech_model,
    run_bothub_request,
)


class OnFixSpeechWithAI(ActionBase):
    """Transcribe audio via BotHub, then fix text with the same prompt as OnFixTextWithAI."""

    icon = "🎙️"
    title = "Fix speech with AI…"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("fixing speech with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect audio, transcribe, fix text, and show corrected output."""
        dialog = AudioSourceDialog()
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        audio_path = dialog.get_audio_path()
        if not audio_path:
            return

        try:
            audio_data = audio_bytes_and_format(audio_path)
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
            self.text_to_clipboard(fixed_text)
            self.dialogs.show_text_diff_side_by_side(
                transcribed_holder["text"],
                fixed_text,
                title="Fixed text diff (Before/After)",
            )

        def on_fix_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        transcribed_holder: dict[str, str] = {"text": ""}

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                message_box.critical(None, "BotHub Error", "Empty transcription from BotHub.")
                return

            transcribed_holder["text"] = transcribed_text

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
