"""Ask AI for a Git commit subject that follows the project style."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import run_bothub_request
from harrix_swiss_knife.integrations.bothub.errors import show_bothub_prompt_build_error
from harrix_swiss_knife.integrations.bothub.git_commit_subject import (
    build_git_commit_subject_prompt,
    normalize_commit_subject,
)


class OnNameGitCommitWithAI(ActionBase):
    """Turn a free-form change description into a styled commit subject."""

    icon = "🏷️"
    title = "Name Git commit with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("naming a Git commit with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for a description, then copy the AI subject to the clipboard."""
        description = self.dialogs.get_text_textarea(
            "Name Git commit",
            "Describe what this commit does. Any language is fine.",
        )
        if description is None:
            return

        try:
            prompt_text = build_git_commit_subject_prompt(description, self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_success(response_text: str) -> None:
            subject = normalize_commit_subject(response_text)
            if not subject:
                message_box.critical(None, "AI Error", "Empty commit title from AI.")
                return
            self.text_to_clipboard(subject)
            self.show_text_multiline(subject, title="Commit title (copied to clipboard)")

        def on_error(message: str) -> None:
            message_box.critical(None, "AI Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
