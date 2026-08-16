"""Shared text helpers for AI responses."""

from __future__ import annotations

from typing import Any

from harrix_pylib.funcs_md import strip_markdown_fences

__all__ = ["extract_openai_message_content", "strip_markdown_fences"]


def extract_openai_message_content(content: Any) -> str:
    """Extract plain text from OpenAI-style message content."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)
