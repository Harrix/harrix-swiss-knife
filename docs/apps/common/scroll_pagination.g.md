---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `scroll_pagination.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScrollPagination`](#%EF%B8%8F-class-scrollpagination)
  - [⚙️ Method `load_more`](#%EF%B8%8F-method-load_more)
  - [⚙️ Method `record_first_page`](#%EF%B8%8F-method-record_first_page)
  - [⚙️ Method `reset`](#%EF%B8%8F-method-reset)
- [🔧 Function `is_scroll_near_bottom`](#-function-is_scroll_near_bottom)
- [🔧 Function `on_scroll_load_more`](#-function-on_scroll_load_more)

</details>

## 🏛️ Class `ScrollPagination`

```python
class ScrollPagination
```

Pagination state and helpers for limit/offset scroll loading.

<details>
<summary>Code:</summary>

```python
class ScrollPagination:

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
```

</details>

### ⚙️ Method `load_more`

```python
def load_more(self) -> None
```

Fetch and append the next page when more rows are available.

<details>
<summary>Code:</summary>

```python
def load_more(
        self,
        *,
        load_more_count: int,
        fetch_rows: Callable[[int, int], list[T]],
        append_rows: Callable[[list[T]], None],
    ) -> None:
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
```

</details>

### ⚙️ Method `record_first_page`

```python
def record_first_page(self, row_count: int, limit: int | None) -> None
```

Update state after the first page is loaded into the table.

<details>
<summary>Code:</summary>

```python
def record_first_page(
        self,
        row_count: int,
        limit: int | None,
        *,
        pagination_enabled: bool = True,
    ) -> None:
        self.loaded_count = row_count
        self.has_more = pagination_enabled and limit is not None and row_count == limit
```

</details>

### ⚙️ Method `reset`

```python
def reset(self) -> None
```

Reset counters before loading a fresh first page.

<details>
<summary>Code:</summary>

```python
def reset(self) -> None:
        self.loaded_count = 0
        self.has_more = False
        self.loading = False
```

</details>

## 🔧 Function `is_scroll_near_bottom`

```python
def is_scroll_near_bottom(scroll_value: int, maximum: int) -> bool
```

Return whether the scroll position is within `threshold` pixels of the bottom.

<details>
<summary>Code:</summary>

```python
def is_scroll_near_bottom(scroll_value: int, maximum: int, *, threshold: int = DEFAULT_SCROLL_THRESHOLD) -> bool:
    return scroll_value >= maximum - threshold
```

</details>

## 🔧 Function `on_scroll_load_more`

```python
def on_scroll_load_more(scroll_value: int, maximum: int, load_more: Callable[[], None]) -> None
```

Call `load_more` when the user scrolls near the bottom of a view.

<details>
<summary>Code:</summary>

```python
def on_scroll_load_more(
    scroll_value: int,
    maximum: int,
    load_more: Callable[[], None],
    *,
    threshold: int = DEFAULT_SCROLL_THRESHOLD,
) -> None:
    if is_scroll_near_bottom(scroll_value, maximum, threshold=threshold):
        load_more()
```

</details>
