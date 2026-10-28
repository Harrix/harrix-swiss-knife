"""Fluent buttons: standard, accent, subtle, hyperlink, icon, tool, toggle, switch, copy.

Checkboxes and radio buttons use the shared Fluent indicators from
`qt_lucide_checkbox` (WinUI rounded square / circle), theme-aware.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QRectF, QSize, Qt, QTimer, QUrl, QVariantAnimation, Signal
from PySide6.QtGui import QDesktopServices, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import QAbstractButton, QCheckBox, QRadioButton, QSizePolicy, QToolButton, QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.style import (
    accent_button_qss,
    push_button_qss,
    subtle_button_qss,
    themed_icon,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_NORMAL,
    CONTROL_HEIGHT,
    SPACE_S,
    TOGGLE_SWITCH_HEIGHT,
    TOGGLE_SWITCH_WIDTH,
)
from harrix_swiss_knife.qt_lucide_checkbox import apply_lucide_checkbox_style, apply_lucide_radio_style

if TYPE_CHECKING:
    from PySide6.QtGui import QPaintEvent
    from PySide6.QtWidgets import QMenu
from harrix_swiss_knife.fluent.widgets.button_base import FluentIconMixin, FluentPushButton

_COPY_FEEDBACK_MS = 1500


class FluentCheckBox(QCheckBox):
    """Checkbox using the shared Fluent indicator and Fluent text color."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a checkbox."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_checkbox_style(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the label color."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QCheckBox {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QCheckBox:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()


class FluentCopyButton(FluentIconMixin, QToolButton):
    """Copies text to the clipboard and briefly shows a check mark."""

    copied = Signal(str)

    def __init__(self, text_to_copy: str = "", parent: QWidget | None = None, *, label: str = "") -> None:
        """Create a copy button.

        Args:

        - `text_to_copy` (`str`): Clipboard payload (see `set_text_to_copy`).
        - `parent` (`QWidget | None`): Optional parent.
        - `label` (`str`): Optional caption beside the icon.

        """
        super().__init__(parent)
        self._payload = text_to_copy
        self._icon_name = "copy"
        self.setText(label)
        self.setToolTip("Copy")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if label else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if not label:
            self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._reset = QTimer(self)
        self._reset.setSingleShot(True)
        self._reset.setInterval(_COPY_FEEDBACK_MS)
        self._reset.timeout.connect(self._restore_icon)
        self.clicked.connect(self._copy)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton"))
        self._sync_icon()

    def set_text_to_copy(self, text: str) -> None:
        """Set the clipboard payload."""
        self._payload = text

    def _copy(self) -> None:
        QGuiApplication.clipboard().setText(self._payload)
        self._icon_name = "check"
        self._sync_icon()
        self._reset.start()
        self.copied.emit(self._payload)

    def _restore_icon(self) -> None:
        self._icon_name = "copy"
        self._sync_icon()


class FluentDropDownButton(FluentPushButton):
    """Button that opens a menu from anywhere on its face."""

    def __init__(
        self, text: str = "", parent: QWidget | None = None, *, icon: str = "", menu: QMenu | None = None
    ) -> None:
        """Create a drop-down button.

        Args:

        - `text` (`str`): Caption.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Optional Lucide icon ID.
        - `menu` (`QMenu | None`): Menu shown on click.

        """
        super().__init__(text, parent, icon=icon)
        if menu is not None:
            self.setMenu(menu)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint the button, then a chevron on the right."""
        super().paintEvent(event)
        palette = palette_for(self)
        icon = themed_icon("chevron-down", palette, palette.text_secondary, 12)
        side = 12
        x = self.width() - side - SPACE_S - 2
        y = (self.height() - side) // 2
        painter = antialiased_painter(self)
        icon.paint(painter, x, y, side, side)
        painter.end()

    def refresh_theme(self) -> None:
        """Re-apply chrome and hide Qt's native menu indicator."""
        self.setStyleSheet(
            push_button_qss(palette_for(self))
            + "QPushButton { padding-right: 28px; } QPushButton::menu-indicator { image: none; width: 0px; }",
        )
        self._sync_icon()


class FluentHyperlinkButton(FluentPushButton):
    """Text button in the accent color that opens a URL."""

    def __init__(self, text: str, url: str = "", parent: QWidget | None = None) -> None:
        """Create a hyperlink button.

        Args:

        - `text` (`str`): Caption.
        - `url` (`str`): URL opened on click (empty: only `clicked` is emitted).
        - `parent` (`QWidget | None`): Optional parent.

        """
        super().__init__(text, parent)
        self._url = url
        self.clicked.connect(self._open_url)

    def refresh_theme(self) -> None:
        """Re-apply hyperlink chrome."""
        palette = palette_for(self)
        self.setStyleSheet(
            subtle_button_qss(palette, "QPushButton") + f"QPushButton {{ color: {css(palette.accent_text)}; }}",
        )

    def set_url(self, url: str) -> None:
        """Set the URL opened on click."""
        self._url = url

    def _open_url(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))


class FluentIconButton(FluentIconMixin, QToolButton):
    """Square subtle button that shows only a Lucide icon."""

    def __init__(self, icon: str, parent: QWidget | None = None, *, tooltip: str = "") -> None:
        """Create an icon button.

        Args:

        - `icon` (`str`): Lucide icon ID.
        - `parent` (`QWidget | None`): Optional parent.
        - `tooltip` (`str`): Tooltip and accessible name.

        """
        super().__init__(parent)
        self._icon_name = icon
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip or icon)
        self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome and icon color."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton { padding: 0px; }")
        self._sync_icon()

    def set_icon_name(self, name: str) -> None:
        """Switch the Lucide icon."""
        self._icon_name = name
        self._sync_icon()


class FluentPillButton(FluentPushButton):
    """Checkable rounded pill (filter chip)."""

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a checkable pill button."""
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)

    def refresh_theme(self) -> None:
        """Re-apply pill chrome."""
        radius = CONTROL_HEIGHT // 2
        self.setStyleSheet(push_button_qss(palette_for(self)) + f"QPushButton {{ border-radius: {radius}px; }}")
        self._sync_icon()


class FluentPrimaryButton(FluentPushButton):
    """Accent-filled button for the main action of a view."""

    _icon_on_accent = True

    def refresh_theme(self) -> None:
        """Re-apply accent chrome."""
        self.setStyleSheet(accent_button_qss(palette_for(self)))
        self._sync_icon()


class FluentRadioButton(QRadioButton):
    """Radio button using the shared Fluent indicator and Fluent text color."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a radio button."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_radio_style(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the label color."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QRadioButton {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QRadioButton:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()


class FluentToggleButton(FluentPushButton):
    """Button that toggles between rest and accent (checked) states."""

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a toggle button."""
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)
        self.toggled.connect(lambda _checked: self._sync_toggle_icon())

    def refresh_theme(self) -> None:
        """Re-apply chrome; the icon follows the checked fill."""
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_toggle_icon()

    def _sync_toggle_icon(self) -> None:
        self._icon_on_accent = self.isChecked()
        self._sync_icon()


class FluentToggleSwitch(QAbstractButton):
    """Animated on/off switch with an optional label on the right."""

    def __init__(self, parent: QWidget | None = None, *, on_text: str = "On", off_text: str = "Off") -> None:
        """Create a toggle switch.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `on_text` (`str`): Label while checked (empty hides it).
        - `off_text` (`str`): Label while unchecked.

        """
        super().__init__(parent)
        self._on_text = on_text
        self._off_text = off_text
        self._knob = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(lambda value: self.set_knob(float(value)))
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate)
        bind_theme(self, self.update)

    def get_knob(self) -> float:
        """Return the knob position (`0.0` off, `1.0` on)."""
        return self._knob

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the track, knob, and label."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        track = QRectF(
            0.5, (self.height() - TOGGLE_SWITCH_HEIGHT) / 2 + 0.5, TOGGLE_SWITCH_WIDTH - 1, TOGGLE_SWITCH_HEIGHT - 1
        )
        on = self._knob > 0.5  # noqa: PLR2004
        hovered = self.underMouse()
        if not self.isEnabled():
            fill = palette.accent_disabled if on else None
            stroke = palette.text_disabled
            knob_color = palette.text_on_accent if on else palette.text_disabled
        elif on:
            fill = palette.accent_hover if hovered else palette.accent
            stroke = None
            knob_color = palette.text_on_accent
        else:
            fill = palette.control_alt_fill if hovered else None
            stroke = palette.control_strong_stroke
            knob_color = palette.text_secondary
        paint_surface(painter, track, fill, stroke, track.height() / 2)
        knob_size = 12 if not hovered else 14
        travel = TOGGLE_SWITCH_WIDTH - 8 - knob_size
        knob_x = track.left() + 3.5 + travel * self._knob
        knob = QRectF(knob_x, track.center().y() - knob_size / 2, knob_size, knob_size)
        paint_surface(painter, knob, knob_color, None, knob_size / 2)
        text = self._on_text if self.isChecked() else self._off_text
        if text:
            painter.setPen(palette.text_primary if self.isEnabled() else palette.text_disabled)
            text_rect = QRectF(
                TOGGLE_SWITCH_WIDTH + SPACE_S, 0, self.width() - TOGGLE_SWITCH_WIDTH - SPACE_S, self.height()
            )
            painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
        painter.end()

    def set_knob(self, value: float) -> None:
        """Move the knob (animation property)."""
        self._knob = value
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the track width plus the widest label."""
        metrics = QFontMetrics(self.font())
        labels = [text for text in (self._on_text, self._off_text) if text]
        text_width = max((metrics.horizontalAdvance(text) for text in labels), default=0)
        extra = SPACE_S + text_width if labels else 0
        return QSize(TOGGLE_SWITCH_WIDTH + extra, CONTROL_HEIGHT)

    def _animate(self, checked: bool) -> None:  # noqa: FBT001
        self._animation.stop()
        self._animation.setStartValue(self._knob)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()


class FluentToolButton(FluentIconMixin, QToolButton):
    """Subtle tool button with icon, optional text, and an optional instant menu."""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        menu: QMenu | None = None,
    ) -> None:
        """Create a tool button.

        Args:

        - `text` (`str`): Caption beside the icon.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Lucide icon ID.
        - `menu` (`QMenu | None`): Menu shown instantly on click.

        """
        super().__init__(parent)
        self._icon_name = icon
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if text else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if menu is not None:
            self.setMenu(menu)
            self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome."""
        self.setStyleSheet(
            subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton::menu-indicator { image: none; }",
        )
        self._sync_icon()


class FluentTransparentButton(FluentPushButton):
    """Subtle button without a fill until hovered."""

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QPushButton"))
        self._sync_icon()
