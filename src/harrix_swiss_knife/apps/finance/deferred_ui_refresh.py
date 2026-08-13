"""Debounced dirty-flag UI refresh after Finance transaction adds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer

if TYPE_CHECKING:
    from collections.abc import Callable


class DeferredUiRefreshScheduler(QObject):
    """Mark dirty work and flush it on a single-shot main-thread timer."""

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
        - `on_flush` (`Callable[..., None]`): Called as `on_flush(categories_may_change=…)`.
        - `interval_ms` (`int`): Debounce interval. Defaults to `400`.

        """
        super().__init__(parent)
        self._on_flush = on_flush
        self._dirty = False
        self._categories_may_change = False
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
        self._dirty = False
        self._categories_may_change = False
        self._timer.stop()
        self._on_flush(categories_may_change=categories_may_change)

    def mark(self, *, categories_may_change: bool = False) -> None:
        """Set dirty and (re)start the debounce timer."""
        self._dirty = True
        if categories_may_change:
            self._categories_may_change = True
        self._timer.start()

    def stop(self) -> None:
        """Cancel timer and clear dirty state without flushing."""
        self._timer.stop()
        self._dirty = False
        self._categories_may_change = False
