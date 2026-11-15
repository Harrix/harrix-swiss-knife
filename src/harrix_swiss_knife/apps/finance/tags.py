"""Transaction tag text shared by the finance database and the tag editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.keyboard_layout_search import text_matches_autocomplete

if TYPE_CHECKING:
    from collections.abc import Sequence

# Suggest known tags once the fragment being typed is longer than this.
TAG_SUGGEST_MIN_CHARS = 2


def format_tag_text(names: list[str]) -> str:
    """Join tag names for the transaction tag cell.

    Args:

    - `names` (`list[str]`): Tag names, possibly with duplicates or extra spaces.

    Returns:

    - `str`: Unique names sorted without case, separated by `", "`. Empty when
      there are no names.

    """
    return ", ".join(sorted(parse_tag_text(", ".join(names)), key=str.casefold))


def matching_known_tags(
    known_tags: Sequence[str],
    query: str,
    *,
    exclude: Sequence[str] = (),
) -> list[str]:
    """Return known tags that match `query`, including EN/RU layout mistakes.

    Matching is case-insensitive and tolerates typing on the wrong keyboard
    layout (same as description autocomplete). Order follows `known_tags`.

    Args:

    - `known_tags` (`Sequence[str]`): Candidate tag names, newest-first from the DB.
    - `query` (`str`): Fragment typed after the last comma.
    - `exclude` (`Sequence[str]`): Tags already chosen in the field; skipped.

    Returns:

    - `list[str]`: Matching names. Empty when `query` is blank.

    """
    needle = " ".join(query.split())
    if not needle:
        return []
    excluded = {name.casefold() for name in exclude if name.strip()}
    matches: list[str] = []
    seen: set[str] = set()
    for name in known_tags:
        key = name.casefold()
        if key in excluded or key in seen:
            continue
        if not text_matches_autocomplete(name, needle):
            continue
        seen.add(key)
        matches.append(name)
    return matches


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


def tag_fragment_parts(text: str) -> tuple[str, str]:
    """Split a tags field into completed prefix and the fragment currently typed.

    Args:

    - `text` (`str`): Raw contents of the Tags line edit.

    Returns:

    - `tuple[str, str]`: `(prefix, fragment)` where `prefix` includes the trailing
      comma when present, and `fragment` is the text after that comma (or the whole
      field when there is no comma).

    """
    if "," not in text:
        return "", text
    head, sep, tail = text.rpartition(",")
    return f"{head}{sep}", tail
