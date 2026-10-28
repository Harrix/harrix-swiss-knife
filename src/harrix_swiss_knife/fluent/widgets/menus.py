"""Fluent menus and bars: rounded menu, menu bar, tool bar, command bar, ribbon, status bar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.style import menu_qss, subtle_button_qss, themed_icon
from harrix_swiss_knife.fluent.theme import bind_theme, css, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    ICON_SIZE,
    ICON_SIZE_LARGE,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_M,
    SPACE_S,
    SPACE_XS,
    TYPE_CAPTION,
)
from harrix_swiss_knife.fluent.widgets.buttons import FluentToolButton
from harrix_swiss_knife.fluent.widgets.display import FluentDivider
from harrix_swiss_knife.fluent.widgets.navigation import FluentPivot
from harrix_swiss_knife.fluent.widgets.text import CaptionLabel

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QPaintEvent, QResizeEvent

_COMMAND_BUTTON_WIDTH_ESTIMATE = 96


class FluentCommandBar(QWidget):
    """Row of command buttons that moves overflowing commands into a `more` menu."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty command bar."""
        super().__init__(parent)
        self._actions: list[QAction] = []
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._row.setSpacing(SPACE_XS)
        self._buttons: list[FluentToolButton] = []
        self._more_menu = FluentMenu("", self)
        self._more = FluentToolButton("", self, icon="ellipsis", menu=self._more_menu)
        self._more.setToolTip("More")
        self._row.addStretch(1)
        self._row.addWidget(self._more)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)

    def add_command(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append a command."""
        action = _lucide_action(self, self, text, icon, slot)
        self._actions.append(action)
        button = FluentToolButton(text, self, icon=icon)
        button.clicked.connect(action.trigger)
        self._buttons.append(button)
        self._row.insertWidget(len(self._buttons) - 1, button)
        self._relayout()
        return action

    def add_separator(self) -> None:
        """Append a vertical hairline between commands."""
        divider = FluentDivider(self, orientation=Qt.Orientation.Vertical)
        divider.setFixedHeight(CONTROL_HEIGHT - SPACE_S)
        self._row.insertWidget(self._row.count() - 2, divider)

    def overflow_count(self) -> int:
        """Return how many commands are in the `more` menu."""
        return sum(1 for button in self._buttons if button.isHidden())

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the bar surface."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Re-flow commands into the overflow menu."""
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self) -> None:
        available = self.width() - CONTROL_HEIGHT - 3 * SPACE_XS
        used = 0
        self._more_menu.clear()
        for button, action in zip(self._buttons, self._actions, strict=True):
            width = max(button.sizeHint().width(), CONTROL_HEIGHT)
            fits = used + width <= available
            button.setVisible(fits)
            if fits:
                used += width + SPACE_XS
            else:
                self._more_menu.addAction(action)
        self._more.setVisible(bool(self._more_menu.actions()))


class FluentMenu(QMenu):
    """Context / drop-down menu with rounded translucent corners and Lucide icons."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        """Create a menu."""
        super().__init__(title, parent)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.aboutToShow.connect(self.refresh_theme)
        bind_theme(self, self.refresh_theme)

    def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append an action with a Lucide icon that follows the theme."""
        action = _lucide_action(self, self._palette_source(), text, icon, slot)
        self.addAction(action)
        return action

    def add_sub_menu(self, title: str, icon: str = "") -> FluentMenu:
        """Append a sub-menu and return it."""
        menu = FluentMenu(title, self)
        if icon:
            menu.setIcon(themed_icon(icon, palette_for(self._palette_source())))
        self.addMenu(menu)
        return menu

    def refresh_theme(self) -> None:
        """Re-apply chrome and recolor Lucide icons for the owner's palette."""
        source = self._palette_source()
        palette = palette_for(source)
        self.setStyleSheet(menu_qss(palette, "QMenu"))
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))

    def _palette_source(self) -> QWidget:
        parent = self.parentWidget()
        return parent if parent is not None else self


class FluentMenuBar(QMenuBar):
    """Flat menu bar with subtle hover; menus use `FluentMenu` chrome."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a menu bar."""
        super().__init__(parent)
        bind_theme(self, self.refresh_theme)

    def add_fluent_menu(self, title: str) -> FluentMenu:
        """Append a `FluentMenu` and return it."""
        menu = FluentMenu(title, self)
        self.addMenu(menu)
        return menu

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        self.setStyleSheet(f"""
QMenuBar {{ background: transparent; color: {css(palette.text_primary)}; border: none; padding: 2px; }}
QMenuBar::item {{ background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 6px 10px; }}
QMenuBar::item:selected {{ background: {css(palette.subtle_hover)}; }}
QMenuBar::item:pressed {{ background: {css(palette.subtle_pressed)}; }}
{menu_qss(palette, "QMenu")}
""")


class FluentRibbonBar(QWidget):
    """Ribbon: tab strip above a card of groups per tab."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty ribbon."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        self.tab_bar = FluentRibbonTabBar(self)
        self.stack = QStackedWidget(self)
        self.stack.setFixedHeight(96)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack)
        self.tab_bar.current_changed.connect(self._on_tab)
        bind_theme(self, self.update)

    def add_group(self, tab: int, title: str) -> FluentRibbonGroup:
        """Append a group to tab `tab` and return it."""
        page = self.stack.widget(tab)
        layout = page.layout() if page is not None else None
        if not isinstance(layout, QHBoxLayout):
            message = f"Ribbon tab {tab} does not exist"
            raise IndexError(message)
        group = FluentRibbonGroup(title, page)
        layout.insertWidget(layout.count() - 1, group)
        return group

    def add_tab(self, title: str) -> int:
        """Append a tab and return its index."""
        page = QWidget(self.stack)
        row = QHBoxLayout(page)
        row.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        row.setSpacing(SPACE_M)
        row.addStretch(1)
        self.stack.addWidget(page)
        self.tab_bar.add_item(title)
        return self.stack.count() - 1

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card behind the groups."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.stack.geometry(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()

    def _on_tab(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.current_changed.emit(index)


class FluentRibbonGroup(QWidget):
    """Titled cluster of large ribbon buttons (icon above text)."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a ribbon group."""
        super().__init__(parent)
        self._title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(2)
        self._buttons = QHBoxLayout()
        self._buttons.setSpacing(2)
        layout.addLayout(self._buttons, 1)
        caption = CaptionLabel(title, self)
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(caption)

    def add_button(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QToolButton:
        """Append a large button."""
        button = FluentToolButton(text, self, icon=icon)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIconSize(QSize(ICON_SIZE_LARGE, ICON_SIZE_LARGE))
        button.setMinimumSize(56, 64)
        font = fluent_font(button.font(), TYPE_CAPTION)
        button.setFont(font)
        if slot is not None:
            button.clicked.connect(slot)
        self._buttons.addWidget(button)
        return button

    def title(self) -> str:
        """Return the group title."""
        return self._title


class FluentRibbonTabBar(FluentPivot):
    """Ribbon tab strip (a pivot with ribbon spacing)."""


class FluentStatusBar(QStatusBar):
    """Status bar on the layer surface with a hairline top border."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a status bar."""
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QStatusBar {{ background: transparent; color: {css(palette.text_secondary)};"
            f" border-top: 1px solid {css(palette.divider)}; }}"
            " QStatusBar::item { border: none; }",
        )
        font = QFont(self.font())
        self.setFont(fluent_font(font, TYPE_CAPTION))


class FluentToolBar(QToolBar):
    """Tool bar with subtle buttons and hairline separators."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        """Create a tool bar."""
        super().__init__(title, parent)
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        bind_theme(self, self.refresh_theme)

    def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append an action with a Lucide icon."""
        action = _lucide_action(self, self, text, icon, slot)
        self.addAction(action)
        return action

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon colors."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QToolBar {{ background: transparent; border: none; spacing: {SPACE_XS}px; padding: {SPACE_XS}px; }}"
            f" QToolBar::separator {{ background: {css(palette.divider)}; width: 1px; margin: 6px 4px; }}"
            f"{subtle_button_qss(palette, 'QToolBar QToolButton')}",
        )
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))


def _lucide_action(
    parent: QWidget, palette_widget: QWidget, text: str, icon: str, slot: Callable[[], None] | None
) -> QAction:
    action = QAction(text, parent)
    if icon:
        action.setIcon(themed_icon(icon, palette_for(palette_widget)))
        action.setProperty("hskLucideIcon", icon)
    if slot is not None:
        action.triggered.connect(slot)
    return action
