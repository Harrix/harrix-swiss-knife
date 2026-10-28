"""Non-visual helpers from the Fluent catalog: event bus, navigation history, router, log bridge."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget


class FluentEventBus(QObject):
    """Process-wide publish / subscribe by event name with arbitrary payloads."""

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


class FluentLog(QObject):
    """Bridge from the `logging` module to a Qt signal (for `FluentLogView`)."""

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


class FluentNavigationRouter(QObject):
    """Back / forward history of navigation keys (for a navigation bar + stack)."""

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


class FluentRouter(QObject):
    """Map paths like `/notes/:id` to page factories and remember the history."""

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


@dataclass
class Route:
    """Path pattern (segments starting with `:` are parameters) and a page factory."""

    pattern: str
    factory: Callable[[dict[str, str]], QWidget]


class _SignalHandler(logging.Handler):
    def __init__(self, owner: FluentLog) -> None:
        super().__init__()
        self._owner = owner

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._owner.record_emitted.emit(record.levelno, self.format(record))
        except RuntimeError:
            return
