"""BotHub helper that turns a change description into a Git commit subject."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.prompts import build_prompt

PROMPT_KEY = "git_commit_subject"
PROMPT_MISSING_MSG = "Prompt git_commit_subject is not configured in config.json."
_MIN_WRAPPED_SUBJECT_LEN = 2


def build_git_commit_subject_prompt(description: str, config: dict[str, Any]) -> str:
    """Build the commit-subject prompt for `description`.

    Raises:

    - `ValueError`: If the prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        PROMPT_KEY,
        {"TEXT": description},
        prompt_display_name=PROMPT_KEY,
    )


def normalize_commit_subject(text: str) -> str:
    """Return the first subject line, without fences, quotes, or a trailing period."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    subject = next((line.strip() for line in cleaned.splitlines() if line.strip()), "")
    if len(subject) >= _MIN_WRAPPED_SUBJECT_LEN and subject[0] == subject[-1] and subject[0] in {'"', "'"}:
        subject = subject[1:-1].strip()
    if subject.endswith(".") and not subject.endswith(".."):
        subject = subject[:-1].rstrip()
    return subject
