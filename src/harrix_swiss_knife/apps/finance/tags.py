"""Transaction tag text shared by the finance database and the tag editor."""

from __future__ import annotations


def format_tag_text(names: list[str]) -> str:
    """Join tag names for the transaction tag cell.

    Args:

    - `names` (`list[str]`): Tag names, possibly with duplicates or extra spaces.

    Returns:

    - `str`: Unique names sorted without case, separated by `", "`. Empty when
      there are no names.

    """
    return ", ".join(sorted(parse_tag_text(", ".join(names)), key=str.casefold))


def parse_tag_text(text: str) -> list[str]:
    """Split a tag field into unique names.

    Names are separated by commas. Surrounding whitespace is removed and runs of
    spaces inside a name are collapsed. Duplicate detection ignores case and keeps
    the first spelling.

    Args:

    - `text` (`str`): Raw tag field, possibly empty.

    Returns:

    - `list[str]`: Tag names in first-seen order.

    """
    seen: set[str] = set()
    names: list[str] = []
    for part in text.split(","):
        name = " ".join(part.split())
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        names.append(name)
    return names
