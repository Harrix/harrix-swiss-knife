---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `deferred_ui_refresh.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DeferredUiRefreshScheduler`](#%EF%B8%8F-class-deferreduirefreshscheduler)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `categories_may_change (property)`](#%EF%B8%8F-method-categories_may_change-property)
  - [⚙️ Method `dirty (property)`](#%EF%B8%8F-method-dirty-property)
  - [⚙️ Method `flush`](#%EF%B8%8F-method-flush)
  - [⚙️ Method `mark`](#%EF%B8%8F-method-mark)
  - [⚙️ Method `reload_transactions (property)`](#%EF%B8%8F-method-reload_transactions-property)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)

</details>

## 🏛️ Class `DeferredUiRefreshScheduler`

```python
class DeferredUiRefreshScheduler(QObject)
```

Mark dirty work and flush it on a single-shot main-thread timer.

<details>
<summary>Code:</summary>

```python
class DeferredUiRefreshScheduler(QObject):

    def __init__(
        self,
        parent: QObject | None,
        on_flush: Callable[..., None],
        *,
        interval_ms: int = 400,
    ) -> None:
        """Initialize scheduler.

        Args:

        - `parent` (`QObject | None`): Qt parent (usually the Finance window).
        - `on_flush` (`Callable[..., None]`): Called as
          `on_flush(categories_may_change=…, reload_transactions=…)`.
        - `interval_ms` (`int`): Debounce interval. Defaults to `400`.

        """
        super().__init__(parent)
        self._on_flush = on_flush
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.flush)

    @property
    def categories_may_change(self) -> bool:
        """Whether a deferred flush should also refresh category UI."""
        return self._categories_may_change

    @property
    def dirty(self) -> bool:
        """Whether a deferred flush is pending."""
        return self._dirty

    def flush(self) -> None:
        """Run pending refresh once, then clear dirty state."""
        if not self._dirty:
            return
        categories_may_change = self._categories_may_change
        reload_transactions = self._reload_transactions
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
        self._timer.stop()
        self._on_flush(
            categories_may_change=categories_may_change,
            reload_transactions=reload_transactions,
        )

    def mark(self, *, categories_may_change: bool = False, reload_transactions: bool = False) -> None:
        """Set dirty and (re)start the debounce timer."""
        self._dirty = True
        if categories_may_change:
            self._categories_may_change = True
        if reload_transactions:
            self._reload_transactions = True
        self._timer.start()

    @property
    def reload_transactions(self) -> bool:
        """Whether a deferred flush should reload the transactions table."""
        return self._reload_transactions

    def stop(self) -> None:
        """Cancel timer and clear dirty state without flushing."""
        self._timer.stop()
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None, on_flush: Callable[..., None], *, interval_ms: int = 400) -> None
```

Initialize scheduler.

Args:

- `parent` (`QObject | None`): Qt parent (usually the Finance window).
- `on_flush` (`Callable[..., None]`): Called as
  `on_flush(categories_may_change=…, reload_transactions=…)`.
- `interval_ms` (`int`): Debounce interval. Defaults to `400`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QObject | None,
        on_flush: Callable[..., None],
        *,
        interval_ms: int = 400,
    ) -> None:
        super().__init__(parent)
        self._on_flush = on_flush
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.flush)
```

</details>

### ⚙️ Method `categories_may_change (property)`

```python
def categories_may_change(self) -> bool
```

Whether a deferred flush should also refresh category UI.

<details>
<summary>Code:</summary>

```python
def categories_may_change(self) -> bool:
        return self._categories_may_change
```

</details>

### ⚙️ Method `dirty (property)`

```python
def dirty(self) -> bool
```

Whether a deferred flush is pending.

<details>
<summary>Code:</summary>

```python
def dirty(self) -> bool:
        return self._dirty
```

</details>

### ⚙️ Method `flush`

```python
def flush(self) -> None
```

Run pending refresh once, then clear dirty state.

<details>
<summary>Code:</summary>

```python
def flush(self) -> None:
        if not self._dirty:
            return
        categories_may_change = self._categories_may_change
        reload_transactions = self._reload_transactions
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
        self._timer.stop()
        self._on_flush(
            categories_may_change=categories_may_change,
            reload_transactions=reload_transactions,
        )
```

</details>

### ⚙️ Method `mark`

```python
def mark(self, *, categories_may_change: bool = False, reload_transactions: bool = False) -> None
```

Set dirty and (re)start the debounce timer.

<details>
<summary>Code:</summary>

```python
def mark(self, *, categories_may_change: bool = False, reload_transactions: bool = False) -> None:
        self._dirty = True
        if categories_may_change:
            self._categories_may_change = True
        if reload_transactions:
            self._reload_transactions = True
        self._timer.start()
```

</details>

### ⚙️ Method `reload_transactions (property)`

```python
def reload_transactions(self) -> bool
```

Whether a deferred flush should reload the transactions table.

<details>
<summary>Code:</summary>

```python
def reload_transactions(self) -> bool:
        return self._reload_transactions
```

</details>

### ⚙️ Method `stop`

```python
def stop(self) -> None
```

Cancel timer and clear dirty state without flushing.

<details>
<summary>Code:</summary>

```python
def stop(self) -> None:
        self._timer.stop()
        self._dirty = False
        self._categories_may_change = False
        self._reload_transactions = False
```

</details>
