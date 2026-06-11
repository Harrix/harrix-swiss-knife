"""Tests for scroll pagination helpers."""

from harrix_swiss_knife.apps.common.scroll_pagination import (
    ScrollPagination,
    is_scroll_near_bottom,
    on_scroll_load_more,
)


def test_is_scroll_near_bottom() -> None:
    assert is_scroll_near_bottom(95, 100) is True
    assert is_scroll_near_bottom(94, 100) is False
    assert is_scroll_near_bottom(8, 10, threshold=2) is True


def test_on_scroll_load_more_calls_callback_near_bottom() -> None:
    calls: list[int] = []

    on_scroll_load_more(98, 100, lambda: calls.append(1))
    on_scroll_load_more(90, 100, lambda: calls.append(2))

    assert calls == [1]


def test_scroll_pagination_first_page_and_load_more() -> None:
    pagination = ScrollPagination()
    pages: list[list[int]] = [[1, 2], [3, 4], [5]]

    pagination.record_first_page(len(pages[0]), limit=2)
    assert pagination.loaded_count == 2
    assert pagination.has_more is True

    def fetch_rows(limit: int, offset: int) -> list[int]:
        start = offset // 2
        batch = pages[start]
        return batch[:limit]

    appended: list[list[int]] = []

    pagination.load_more(
        load_more_count=2,
        fetch_rows=fetch_rows,
        append_rows=appended.extend,
    )
    assert appended == [3, 4]
    assert pagination.loaded_count == 4
    assert pagination.has_more is True

    pagination.load_more(
        load_more_count=2,
        fetch_rows=fetch_rows,
        append_rows=appended.extend,
    )
    assert appended == [3, 4, 5]
    assert pagination.loaded_count == 5
    assert pagination.has_more is False


def test_scroll_pagination_reset() -> None:
    pagination = ScrollPagination()
    pagination.record_first_page(10, limit=10)
    pagination.loading = True

    pagination.reset()

    assert pagination.loaded_count == 0
    assert pagination.has_more is False
    assert pagination.loading is False
