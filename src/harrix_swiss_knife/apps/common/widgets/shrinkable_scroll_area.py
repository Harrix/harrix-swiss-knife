"""Scroll area that does not force its parent to honor child minimum sizes."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QTabWidget, QVBoxLayout, QWidget

_MIN_VIEWPORT = 160


class ShrinkableScrollArea(QScrollArea):
    """`QScrollArea` whose minimum size ignores the inner widget.

    Child widgets keep their own minimum widths. When the viewport is smaller,
    scrollbars appear instead of blocking the window from shrinking.

    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a frameless expanding scroll area."""
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Allow the parent to shrink below the inner widget minimum."""
        return QSize(_MIN_VIEWPORT, _MIN_VIEWPORT)


def wrap_tab_pages_in_shrinkable_scroll(tab_widget: QTabWidget) -> None:
    """Wrap every tab page so a narrow window shows scrollbars instead of a min-width clamp."""
    for index in range(tab_widget.count()):
        page = tab_widget.widget(index)
        if page is not None:
            wrap_widget_contents_in_shrinkable_scroll(page)


def wrap_widget_contents_in_shrinkable_scroll(host: QWidget) -> ShrinkableScrollArea:
    """Move `host`'s current layout into a shrinkable scroll area.

    Args:

    - `host` (`QWidget`): Tab page or other container that currently owns the content layout.

    Returns:

    - `ShrinkableScrollArea`: The scroll area now filling `host`.

    """
    existing = host.layout()
    inner = QWidget()
    if existing is not None:
        inner.setLayout(existing)
    scroll = ShrinkableScrollArea(host)
    scroll.setWidget(inner)
    outer = QVBoxLayout(host)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)
    outer.addWidget(scroll)
    return scroll
