"""Plain-text formatters for tracker QStatusBar permanent labels and progress."""

from __future__ import annotations


def format_list_view_status(
    *,
    filtered: bool = False,
    loaded_count: int | None = None,
    has_more: bool = False,
) -> str:
    """Format filter / pagination context for a list status-bar label.

    Args:

    - `filtered` (`bool`): Whether an active filter narrows the list.
    - `loaded_count` (`int | None`): Rows currently loaded into the view.
    - `has_more` (`bool`): Whether more rows can be loaded by scrolling.

    Returns:

    - `str`: Status text, or empty when there is nothing useful to show.

    """
    parts: list[str] = []
    if filtered:
        parts.append("Filtered")
    if loaded_count is not None and loaded_count > 0:
        parts.append(f"{loaded_count} loaded")
    if has_more:
        parts.append("more below")
    return " · ".join(parts)


def format_selection_count_status(
    count: int,
    *,
    unit_singular: str = "row",
    unit_plural: str | None = None,
    detail: str = "",
) -> str:
    """Format a selection summary for a permanent status-bar label.

    Args:

    - `count` (`int`): Number of selected items.
    - `unit_singular` (`str`): Singular unit word (default `row`).
    - `unit_plural` (`str | None`): Plural unit; defaults to `unit_singular` + `s`.
    - `detail` (`str`): Optional trailing detail (e.g. sum text without leading separator).

    Returns:

    - `str`: Status text, or empty when `count <= 0`.

    """
    if count <= 0:
        return ""
    plural = unit_plural if unit_plural is not None else f"{unit_singular}s"
    unit = unit_singular if count == 1 else plural
    base = f"{count} {unit} selected"
    cleaned = detail.strip()
    if cleaned:
        return f"{base} · {cleaned}"
    return base


def format_translate_progress_status(
    base_message: str,
    remaining: int | None = None,
    *,
    item_label: str = "left",
) -> str:
    """Format a sticky background-translate status message.

    Args:

    - `base_message` (`str`): Base sticky text (ellipsis included).
    - `remaining` (`int | None`): Items still missing translation; omit when unknown.
    - `item_label` (`str`): Trailing label after the count (e.g. `descriptions left`).

    Returns:

    - `str`: Status text for `showMessage`.

    """
    cleaned = base_message.strip()
    if remaining is None or remaining <= 0:
        return cleaned
    return f"{cleaned} ({remaining} {item_label.strip()})"


def is_owned_status_message(current: str, base_message: str) -> bool:
    """Return whether `current` is the sticky message owned by `base_message`.

    Matches the exact base text or the base with a remaining-count suffix.

    """
    cleaned_current = current.strip()
    cleaned_base = base_message.strip()
    if not cleaned_base:
        return False
    if cleaned_current == cleaned_base:
        return True
    return cleaned_current.startswith(f"{cleaned_base} (")


def join_status_parts(*parts: str) -> str:
    """Join non-empty status fragments with a middle dot separator."""
    return " · ".join(part.strip() for part in parts if part and part.strip())
