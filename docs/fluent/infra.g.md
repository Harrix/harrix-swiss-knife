---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `infra.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentEventBus`](#%EF%B8%8F-class-fluenteventbus)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `instance (classmethod)`](#%EF%B8%8F-method-instance-classmethod)
  - [⚙️ Method `publish`](#%EF%B8%8F-method-publish)
  - [⚙️ Method `subscribe`](#%EF%B8%8F-method-subscribe)
  - [⚙️ Method `unsubscribe`](#%EF%B8%8F-method-unsubscribe)
- [🏛️ Class `FluentLog`](#%EF%B8%8F-class-fluentlog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `detach`](#%EF%B8%8F-method-detach)
- [🏛️ Class `FluentNavigationRouter`](#%EF%B8%8F-class-fluentnavigationrouter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `back`](#%EF%B8%8F-method-back)
  - [⚙️ Method `can_go_back`](#%EF%B8%8F-method-can_go_back)
  - [⚙️ Method `can_go_forward`](#%EF%B8%8F-method-can_go_forward)
  - [⚙️ Method `current`](#%EF%B8%8F-method-current)
  - [⚙️ Method `forward`](#%EF%B8%8F-method-forward)
  - [⚙️ Method `push`](#%EF%B8%8F-method-push)
- [🏛️ Class `FluentRouter`](#%EF%B8%8F-class-fluentrouter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `add_route`](#%EF%B8%8F-method-add_route)
  - [⚙️ Method `match`](#%EF%B8%8F-method-match)
  - [⚙️ Method `navigate`](#%EF%B8%8F-method-navigate)
- [🏛️ Class `Route`](#%EF%B8%8F-class-route)

</details>

## 🏛️ Class `FluentEventBus`

```python
class FluentEventBus(QObject)
```

Process-wide publish / subscribe by event name with arbitrary payloads.

<details>
<summary>Code:</summary>

```python
class FluentEventBus(QObject):

    published = Signal(str, object)

    _instance: FluentEventBus | None = None

    def __init__(self) -> None:
        """Create a bus (use `instance()` for the shared one)."""
        super().__init__()
        self._handlers: dict[str, list[Callable[[object], None]]] = {}

    @classmethod
    def instance(cls) -> FluentEventBus:
        """Return the shared bus."""
        if cls._instance is None:
            cls._instance = FluentEventBus()
        return cls._instance

    def publish(self, event: str, payload: object = None) -> int:
        """Call every subscriber of `event` and return how many were called."""
        handlers = list(self._handlers.get(event, ()))
        for handler in handlers:
            handler(payload)
        self.published.emit(event, payload)
        return len(handlers)

    def subscribe(self, event: str, handler: Callable[[object], None]) -> None:
        """Register `handler` for `event`."""
        self._handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable[[object], None]) -> None:
        """Remove `handler` from `event`."""
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create a bus (use `instance()` for the shared one).

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()
        self._handlers: dict[str, list[Callable[[object], None]]] = {}
```

</details>

### ⚙️ Method `instance (classmethod)`

```python
def instance(cls) -> FluentEventBus
```

Return the shared bus.

<details>
<summary>Code:</summary>

```python
def instance(cls) -> FluentEventBus:
        if cls._instance is None:
            cls._instance = FluentEventBus()
        return cls._instance
```

</details>

### ⚙️ Method `publish`

```python
def publish(self, event: str, payload: object = None) -> int
```

Call every subscriber of `event` and return how many were called.

<details>
<summary>Code:</summary>

```python
def publish(self, event: str, payload: object = None) -> int:
        handlers = list(self._handlers.get(event, ()))
        for handler in handlers:
            handler(payload)
        self.published.emit(event, payload)
        return len(handlers)
```

</details>

### ⚙️ Method `subscribe`

```python
def subscribe(self, event: str, handler: Callable[[object], None]) -> None
```

Register `handler` for `event`.

<details>
<summary>Code:</summary>

```python
def subscribe(self, event: str, handler: Callable[[object], None]) -> None:
        self._handlers.setdefault(event, []).append(handler)
```

</details>

### ⚙️ Method `unsubscribe`

```python
def unsubscribe(self, event: str, handler: Callable[[object], None]) -> None
```

Remove `handler` from `event`.

<details>
<summary>Code:</summary>

```python
def unsubscribe(self, event: str, handler: Callable[[object], None]) -> None:
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
```

</details>

## 🏛️ Class `FluentLog`

```python
class FluentLog(QObject)
```

Bridge from the `logging` module to a Qt signal (for [`FluentLogView`](widgets/editors.g.md#%EF%B8%8F-class-fluentlogview)).

<details>
<summary>Code:</summary>

```python
class FluentLog(QObject):

    record_emitted = Signal(int, str)

    def __init__(self, parent: QObject | None = None, *, level: int = logging.INFO, logger_name: str = "") -> None:
        """Attach a handler to `logger_name` (root by default)."""
        super().__init__(parent)
        self._handler = _SignalHandler(self)
        self._handler.setLevel(level)
        self._handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", "%H:%M:%S"))
        self._logger = logging.getLogger(logger_name)
        self._logger.addHandler(self._handler)

    def detach(self) -> None:
        """Remove the handler from the logger."""
        self._logger.removeHandler(self._handler)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, *, level: int = logging.INFO, logger_name: str = '') -> None
```

Attach a handler to `logger_name` (root by default).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, *, level: int = logging.INFO, logger_name: str = "") -> None:
        super().__init__(parent)
        self._handler = _SignalHandler(self)
        self._handler.setLevel(level)
        self._handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", "%H:%M:%S"))
        self._logger = logging.getLogger(logger_name)
        self._logger.addHandler(self._handler)
```

</details>

### ⚙️ Method `detach`

```python
def detach(self) -> None
```

Remove the handler from the logger.

<details>
<summary>Code:</summary>

```python
def detach(self) -> None:
        self._logger.removeHandler(self._handler)
```

</details>

## 🏛️ Class `FluentNavigationRouter`

```python
class FluentNavigationRouter(QObject)
```

Back / forward history of navigation keys (for a navigation bar + stack).

<details>
<summary>Code:</summary>

```python
class FluentNavigationRouter(QObject):

    navigated = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Create an empty history."""
        super().__init__(parent)
        self._back: list[str] = []
        self._forward: list[str] = []
        self._current = ""

    def back(self) -> str:
        """Go back and return the new current key (unchanged when empty)."""
        if not self._back:
            return self._current
        self._forward.append(self._current)
        self._current = self._back.pop()
        self.navigated.emit(self._current)
        return self._current

    def can_go_back(self) -> bool:
        """Return whether there is a previous key."""
        return bool(self._back)

    def can_go_forward(self) -> bool:
        """Return whether there is a next key."""
        return bool(self._forward)

    def current(self) -> str:
        """Return the current key."""
        return self._current

    def forward(self) -> str:
        """Go forward and return the new current key."""
        if not self._forward:
            return self._current
        self._back.append(self._current)
        self._current = self._forward.pop()
        self.navigated.emit(self._current)
        return self._current

    def push(self, key: str) -> None:
        """Navigate to `key` (clears the forward history)."""
        if key == self._current:
            return
        if self._current:
            self._back.append(self._current)
        self._forward.clear()
        self._current = key
        self.navigated.emit(key)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Create an empty history.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._back: list[str] = []
        self._forward: list[str] = []
        self._current = ""
```

</details>

### ⚙️ Method `back`

```python
def back(self) -> str
```

Go back and return the new current key (unchanged when empty).

<details>
<summary>Code:</summary>

```python
def back(self) -> str:
        if not self._back:
            return self._current
        self._forward.append(self._current)
        self._current = self._back.pop()
        self.navigated.emit(self._current)
        return self._current
```

</details>

### ⚙️ Method `can_go_back`

```python
def can_go_back(self) -> bool
```

Return whether there is a previous key.

<details>
<summary>Code:</summary>

```python
def can_go_back(self) -> bool:
        return bool(self._back)
```

</details>

### ⚙️ Method `can_go_forward`

```python
def can_go_forward(self) -> bool
```

Return whether there is a next key.

<details>
<summary>Code:</summary>

```python
def can_go_forward(self) -> bool:
        return bool(self._forward)
```

</details>

### ⚙️ Method `current`

```python
def current(self) -> str
```

Return the current key.

<details>
<summary>Code:</summary>

```python
def current(self) -> str:
        return self._current
```

</details>

### ⚙️ Method `forward`

```python
def forward(self) -> str
```

Go forward and return the new current key.

<details>
<summary>Code:</summary>

```python
def forward(self) -> str:
        if not self._forward:
            return self._current
        self._back.append(self._current)
        self._current = self._forward.pop()
        self.navigated.emit(self._current)
        return self._current
```

</details>

### ⚙️ Method `push`

```python
def push(self, key: str) -> None
```

Navigate to `key` (clears the forward history).

<details>
<summary>Code:</summary>

```python
def push(self, key: str) -> None:
        if key == self._current:
            return
        if self._current:
            self._back.append(self._current)
        self._forward.clear()
        self._current = key
        self.navigated.emit(key)
```

</details>

## 🏛️ Class `FluentRouter`

```python
class FluentRouter(QObject)
```

Map paths like `/notes/:id` to page factories and remember the history.

<details>
<summary>Code:</summary>

```python
class FluentRouter(QObject):

    routed = Signal(str, object)

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a router without routes."""
        super().__init__(parent)
        self._routes: list[Route] = []
        self.history = FluentNavigationRouter(self)

    def add_route(self, pattern: str, factory: Callable[[dict[str, str]], QWidget]) -> None:
        """Register a route."""
        self._routes.append(Route(pattern, factory))

    def match(self, path: str) -> tuple[Route, dict[str, str]] | None:
        """Return the first route matching `path` and its parameters."""
        parts = [part for part in path.split("/") if part]
        for route in self._routes:
            pattern = [part for part in route.pattern.split("/") if part]
            if len(pattern) != len(parts):
                continue
            params: dict[str, str] = {}
            for expected, actual in zip(pattern, parts, strict=True):
                if expected.startswith(":"):
                    params[expected[1:]] = actual
                elif expected != actual:
                    break
            else:
                return route, params
        return None

    def navigate(self, path: str) -> QWidget | None:
        """Build the page for `path`, record it in history, and emit `routed`."""
        found = self.match(path)
        if found is None:
            return None
        route, params = found
        page = route.factory(params)
        self.history.push(path)
        self.routed.emit(path, page)
        return page
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Create a router without routes.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._routes: list[Route] = []
        self.history = FluentNavigationRouter(self)
```

</details>

### ⚙️ Method `add_route`

```python
def add_route(self, pattern: str, factory: Callable[[dict[str, str]], QWidget]) -> None
```

Register a route.

<details>
<summary>Code:</summary>

```python
def add_route(self, pattern: str, factory: Callable[[dict[str, str]], QWidget]) -> None:
        self._routes.append(Route(pattern, factory))
```

</details>

### ⚙️ Method `match`

```python
def match(self, path: str) -> tuple[Route, dict[str, str]] | None
```

Return the first route matching `path` and its parameters.

<details>
<summary>Code:</summary>

```python
def match(self, path: str) -> tuple[Route, dict[str, str]] | None:
        parts = [part for part in path.split("/") if part]
        for route in self._routes:
            pattern = [part for part in route.pattern.split("/") if part]
            if len(pattern) != len(parts):
                continue
            params: dict[str, str] = {}
            for expected, actual in zip(pattern, parts, strict=True):
                if expected.startswith(":"):
                    params[expected[1:]] = actual
                elif expected != actual:
                    break
            else:
                return route, params
        return None
```

</details>

### ⚙️ Method `navigate`

```python
def navigate(self, path: str) -> QWidget | None
```

Build the page for `path`, record it in history, and emit `routed`.

<details>
<summary>Code:</summary>

```python
def navigate(self, path: str) -> QWidget | None:
        found = self.match(path)
        if found is None:
            return None
        route, params = found
        page = route.factory(params)
        self.history.push(path)
        self.routed.emit(path, page)
        return page
```

</details>

## 🏛️ Class `Route`

```python
class Route
```

Path pattern (segments starting with `:` are parameters) and a page factory.

<details>
<summary>Code:</summary>

```python
class Route:

    pattern: str
    factory: Callable[[dict[str, str]], QWidget]
```

</details>
