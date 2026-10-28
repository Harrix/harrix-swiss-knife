"""Fluent window shells: layer panel and a navigation window with the Win11 caption."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter
from harrix_swiss_knife.fluent.theme import bind_theme, enable_fluent_theme, palette_for
from harrix_swiss_knife.fluent.tokens import RADIUS_CARD
from harrix_swiss_knife.fluent.widgets.navigation import FluentNavigationBar
from harrix_swiss_knife.fluent.widgets.views import FluentScrollArea
from harrix_swiss_knife.win11_caption import install_win11_caption, try_handle_win11_caption_native_event

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QPaintEvent

_NAVIGATION_WIDTH = 240


class FluentLayerPanel(QWidget):
    """Content layer of a Fluent window: `layer_bg` with a rounded top-left corner.

    Mirrors the stacked-widget area of PyQt-Fluent-Widgets `FluentWindow`: the
    window background shows on the left and top, and the layer has a 1 px
    stroke on those two edges only.

    """

    def __init__(self, parent: QWidget | None = None, *, rounded: bool = True) -> None:
        """Create a layer panel."""
        super().__init__(parent)
        self._rounded = rounded
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the layer fill and its top / left stroke."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        radius = float(RADIUS_CARD if self._rounded else 0)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, radius + 1, radius + 1)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(palette.layer_bg)
        painter.drawPath(path)
        painter.setPen(palette.layer_stroke)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.end()


class FluentNavigationWindow(QWidget):
    """Top-level Fluent window: Win11 caption, navigation bar, and a layer with pages."""

    def __init__(self, title: str, parent: QWidget | None = None, *, trailing_widgets: Sequence[QWidget] = ()) -> None:
        """Create the window (pages are added with `add_page`)."""
        super().__init__(parent)
        self.setWindowTitle(title)
        enable_fluent_theme(self)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        body = QWidget(self)
        row = QHBoxLayout(body)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(body)
        self.navigation.setFixedWidth(_NAVIGATION_WIDTH)
        self.layer = FluentLayerPanel(body)
        layer_layout = QVBoxLayout(self.layer)
        layer_layout.setContentsMargins(1, 1, 0, 0)
        self.stack = QStackedWidget(self.layer)
        layer_layout.addWidget(self.stack)
        row.addWidget(self.navigation)
        row.addWidget(self.layer, 1)
        root.addWidget(body, 1)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self.show_page)
        self.caption_installed = install_win11_caption(self, trailing_widgets=list(trailing_widgets))

    def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "", scroll: bool = True) -> QWidget:
        """Register a page (wrapped in a transparent scroll area by default)."""
        page: QWidget = widget
        if scroll:
            area = FluentScrollArea(self.stack)
            area.setWidget(widget)
            page = area
        self._pages[key] = page
        self.stack.addWidget(page)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(page)
        return page

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Route caption hit-testing to the Win11 caption."""
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def page(self, key: str) -> QWidget | None:
        """Return the page registered under `key`."""
        return self._pages.get(key)

    def show_page(self, key: str) -> None:
        """Switch to the page registered under `key`."""
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)
            if self.navigation.current() != key:
                self.navigation.set_current(key)
