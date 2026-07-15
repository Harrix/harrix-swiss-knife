"""Helpers for action titles that may include Markdown inline code markers."""


def strip_md_inline_code_markers(text: str) -> str:
    """Remove Markdown backtick markers for plain Qt UI display.

    Example: ``Open `config.json``` → ``Open config.json``.
    """
    return text.replace("`", "")
