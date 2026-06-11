"""Shared scroll-triggered table pagination helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

DEFAULT_SCROLL_THRESHOLD = 5


@dataclass
class ScrollPagination(Generic[T]):
    """Pagination state and helpers for limit/offset scroll loading."""

    loaded_count: int = 0
    has_more: bool = False
    loading: bool = False

    def load_more(
        self,
        *,
        load_more_count: int,
        fetch_rows: Callable[[int, int], list[T]],
        append_rows: Callable[[list[T]], None],
    ) -> None:
        """Fetch and append the next page when more rows are available."""
        if not self.has_more or self.loading:
            return

        self.loading = True
        try:
            rows = fetch_rows(load_more_count, self.loaded_count)
            if not rows:
                self.has_more = False
                return

            append_rows(rows)
            self.loaded_count += len(rows)
            self.has_more = len(rows) == load_more_count
        finally:
            self.loading = False

    def record_first_page(
        self,
        row_count: int,
        limit: int | None,
        *,
        pagination_enabled: bool = True,
    ) -> None:
        """Update state after the first page is loaded into the table."""
        self.loaded_count = row_count
        self.has_more = pagination_enabled and limit is not None and row_count == limit

    def reset(self) -> None:
        """Reset counters before loading a fresh first page."""
        self.loaded_count = 0
        self.has_more = False
        self.loading = False


def is_scroll_near_bottom(scroll_value: int, maximum: int, *, threshold: int = DEFAULT_SCROLL_THRESHOLD) -> bool:
    """Return whether the scroll position is within `threshold` pixels of the bottom."""
    return scroll_value >= maximum - threshold


def on_scroll_load_more(
    scroll_value: int,
    maximum: int,
    load_more: Callable[[], None],
    *,
    threshold: int = DEFAULT_SCROLL_THRESHOLD,
) -> None:
    """Call `load_more` when the user scrolls near the bottom of a view."""
    if is_scroll_near_bottom(scroll_value, maximum, threshold=threshold):
        load_more()
