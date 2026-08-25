"""Sort helpers for snippet items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.snippets.constants import SORT_ADDED, SORT_USED

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.snippets.database_manager import SnippetItem


def sort_items(items: Sequence[SnippetItem], mode: str, *, descending: bool) -> list[SnippetItem]:
    """Return items ordered by last use, date added, or alphabet.

    Last-use order puts unused items at the end alphabetically. `descending`
    reverses the default direction of the active mode.

    """
    if mode == SORT_USED:
        used = [item for item in items if item.last_used_at]
        unused = [item for item in items if not item.last_used_at]
        used_sorted = sorted(used, key=lambda item: item.last_used_at or "", reverse=not descending)
        unused_sorted = sorted(unused, key=lambda item: item.value.casefold())
        return used_sorted + unused_sorted
    if mode == SORT_ADDED:
        return sorted(items, key=lambda item: (item.created_at, item.item_id), reverse=not descending)
    return sorted(items, key=lambda item: item.value.casefold(), reverse=descending)
