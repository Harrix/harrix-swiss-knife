"""Sort helpers for snippet items."""

# ruff: noqa: RUF001

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.snippets.constants import SORT_ADDED, SORT_USED, ZONE_SYMBOL

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.snippets.database_manager import SnippetItem

_DASH_LENGTH_RANK: dict[str, int] = {
    "-": 0,
    "‐": 1,
    "‑": 1,
    "−": 2,
    "‒": 3,
    "–": 4,
    "—": 5,
    "―": 6,
    "⸺": 7,
    "⸻": 8,
    "－": 5,
}


def dash_length_rank(value: str) -> int | None:
    """Return an increasing length rank for a hyphen or dash, or `None`."""
    return _DASH_LENGTH_RANK.get(value.strip())


def pin_dash_symbols_first(items: Sequence[SnippetItem]) -> list[SnippetItem]:
    """Keep hyphens and dashes first, together, from shortest to longest."""
    dashes: list[tuple[int, SnippetItem]] = []
    rest: list[SnippetItem] = []
    for item in items:
        rank = dash_length_rank(item.value)
        if rank is None:
            rest.append(item)
        else:
            dashes.append((rank, item))
    dashes.sort(key=lambda pair: pair[0])
    return [item for _rank, item in dashes] + rest


def sort_items(items: Sequence[SnippetItem], mode: str, *, descending: bool) -> list[SnippetItem]:
    """Return items ordered by last use, date added, or alphabet.

    Last-use order puts unused items at the end alphabetically. `descending`
    reverses the default direction of the active mode. Symbol hyphens and
    dashes stay first, grouped by increasing length.

    """
    if mode == SORT_USED:
        used = [item for item in items if item.last_used_at]
        unused = [item for item in items if not item.last_used_at]
        used_sorted = sorted(used, key=lambda item: item.last_used_at or "", reverse=not descending)
        unused_sorted = sorted(unused, key=lambda item: item.value.casefold())
        ordered = used_sorted + unused_sorted
    elif mode == SORT_ADDED:
        ordered = sorted(items, key=lambda item: (item.created_at, item.item_id), reverse=not descending)
    else:
        ordered = sorted(items, key=lambda item: item.value.casefold(), reverse=descending)
    if any(item.zone == ZONE_SYMBOL for item in ordered):
        return pin_dash_symbols_first(ordered)
    return ordered
