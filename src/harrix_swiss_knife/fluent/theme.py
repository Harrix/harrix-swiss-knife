"""Process-wide Fluent light/dark theme with opt-in Windows.

The mode is stored in `config.json` (`ui_theme`: `"light"` or `"dark"`).
Only Windows that call `enable_fluent_theme` follow the dark mode; Fluent
widgets placed in any other window keep the light palette so unmigrated
forms never get dark islands inside light chrome.

"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtGui import QColor, QFont, QPalette

from harrix_swiss_knife.fluent.tokens import DARK_PALETTE, LIGHT_PALETTE, FluentPalette
from harrix_swiss_knife.win11_backdrop import set_window_dark_mode

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget

FLUENT_THEMED_PROPERTY = "hskFluentThemed"
_REFRESHER_NAME = "hskFluentThemeRefresher"


class FluentTheme(QObject):
    """Singleton holding the current Fluent theme mode."""

    changed = Signal(str)

    _instance: FluentTheme | None = None

    def __init__(self) -> None:
        """Start in light mode; call `load_from_config` to apply `ui_theme`."""
        super().__init__()
        self._mode = ThemeMode.LIGHT

    @classmethod
    def instance(cls) -> FluentTheme:
        """Return the shared theme object (created on first use)."""
        if cls._instance is None:
            cls._instance = FluentTheme()
        return cls._instance

    def is_dark(self) -> bool:
        """Return whether the dark palette is active."""
        return self._mode == ThemeMode.DARK

    def load_from_config(self, config: dict | None = None) -> ThemeMode:
        """Apply `ui_theme` from `config.json` (or the given dict) and return it."""
        # Lazy: widgets import this module from the installer, which has no `harrix_pylib`.
        from harrix_swiss_knife.config_model import get_ui_theme  # noqa: PLC0415

        mode = ThemeMode(get_ui_theme(config))
        self.set_mode(mode)
        return mode

    def mode(self) -> ThemeMode:
        """Return the current theme mode."""
        return self._mode

    def palette(self) -> FluentPalette:
        """Return the token set for the current mode."""
        return DARK_PALETTE if self.is_dark() else LIGHT_PALETTE

    def set_mode(self, mode: ThemeMode | str, *, persist: bool = False) -> None:
        """Switch the theme and notify every bound widget.

        Args:

        - `mode` (`ThemeMode | str`): `light` or `dark`.
        - `persist` (`bool`): Also write `ui_theme` to `config.json`. Defaults to `False`.

        """
        resolved = ThemeMode(mode)
        if persist:
            # Lazy for the same installer reason as `load_from_config`.
            from harrix_swiss_knife.config_model import set_ui_theme  # noqa: PLC0415

            set_ui_theme(theme=resolved.value)
        if resolved == self._mode:
            return
        self._mode = resolved
        self.changed.emit(resolved.value)

    def toggle(self, *, persist: bool = True) -> ThemeMode:
        """Flip between light and dark and return the new mode."""
        target = ThemeMode.LIGHT if self.is_dark() else ThemeMode.DARK
        self.set_mode(target, persist=persist)
        return target


class ThemeMode(StrEnum):
    """Supported Fluent theme modes."""

    LIGHT = "light"
    DARK = "dark"


class _ThemeRefresher(QObject):
    """Re-run a widget's theme callback on theme change and on re-parenting."""

    def __init__(self, widget: QWidget, refresh: Callable[[], None]) -> None:
        super().__init__(widget)
        self.setObjectName(_REFRESHER_NAME)
        self._widget = widget
        self._refresh = refresh
        self._dark: bool | None = None
        self._running = False
        widget.installEventFilter(self)
        FluentTheme.instance().changed.connect(self.on_theme_changed)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Refresh when the widget moves into a window with a different theme."""
        widget = getattr(self, "_widget", None)
        if (
            widget is not None
            and watched is widget
            and event.type()
            in {
                QEvent.Type.ParentChange,
                QEvent.Type.Show,
            }
        ):
            self.run(force=False)
        return False

    def on_theme_changed(self, _mode: str) -> None:
        """Refresh after `FluentTheme.changed`."""
        self.run(force=False)

    def run(self, *, force: bool) -> None:
        """Call the refresh callback when the resolved palette changed."""
        if getattr(self, "_running", False):
            return
        widget = getattr(self, "_widget", None)
        refresh = getattr(self, "_refresh", None)
        if widget is None or refresh is None:
            return
        try:
            dark = palette_for(widget).dark
        except RuntimeError:
            return
        if not force and dark == self._dark:
            return
        self._dark = dark
        self._running = True
        try:
            refresh()
        finally:
            self._running = False


def bind_theme(widget: QWidget, refresh: Callable[[], None]) -> None:
    """Call `refresh` now and whenever `widget`'s resolved palette changes.

    `refresh` should read colors through `palette_for(widget)`.
    Multiple bindings on one widget are allowed (each keeps its own refresher).

    """
    refresher = _ThemeRefresher(widget, refresh)
    refresher.run(force=True)


def css(color: QColor) -> str:
    """Return `color` as a QSS `rgba(...)` value (keeps alpha)."""
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"


def enable_fluent_theme(window: QWidget) -> None:
    """Opt `window` (and everything under it) into the current light/dark mode."""
    window.setProperty(FLUENT_THEMED_PROPERTY, True)  # noqa: FBT003
    bind_theme(window, lambda: _apply_window_palette(window))


def fluent_font(source: QFont, scale: float, *, weight: QFont.Weight | None = None) -> QFont:
    """Return `source` scaled along the Fluent type ramp.

    Args:

    - `source` (`QFont`): Base font (usually the application Roboto font).
    - `scale` (`float`): One of the `TYPE_*` ratios from `fluent.tokens`.
    - `weight` (`QFont.Weight | None`): Optional weight override.

    """
    font = QFont(source)
    if font.pointSizeF() > 0:
        font.setPointSizeF(max(1.0, font.pointSizeF() * scale))
    elif font.pixelSize() > 0:
        font.setPixelSize(max(1, round(font.pixelSize() * scale)))
    if weight is not None:
        font.setWeight(weight)
    return font


def is_fluent_themed(widget: QWidget | None) -> bool:
    """Return whether `widget` lives under a window that opted into the theme."""
    current = widget
    while current is not None:
        if bool(current.property(FLUENT_THEMED_PROPERTY)):
            return True
        current = current.parentWidget()
    return False


def mix(base: QColor, overlay: QColor) -> QColor:
    """Return the opaque color of `overlay` painted over opaque `base`."""
    alpha = overlay.alphaF()
    return QColor(
        round(base.red() * (1 - alpha) + overlay.red() * alpha),
        round(base.green() * (1 - alpha) + overlay.green() * alpha),
        round(base.blue() * (1 - alpha) + overlay.blue() * alpha),
    )


def palette_for(widget: QWidget | None) -> FluentPalette:
    """Return the palette `widget` should paint with (light outside opted-in Windows)."""
    theme = FluentTheme.instance()
    if theme.is_dark() and is_fluent_themed(widget):
        return DARK_PALETTE
    return LIGHT_PALETTE


def to_qpalette(palette: FluentPalette, base: QPalette | None = None) -> QPalette:
    """Build a `QPalette` with opaque Fluent colors for native-drawn children."""
    result = QPalette(base) if base is not None else QPalette()
    window = palette.window_bg
    surface = mix(window, palette.layer_bg)
    text = mix(window, palette.text_primary)
    secondary = mix(window, palette.text_secondary)
    disabled = mix(window, palette.text_disabled)
    roles = {
        QPalette.ColorRole.Window: window,
        QPalette.ColorRole.WindowText: text,
        QPalette.ColorRole.Base: palette.solid_quarternary_bg if not palette.dark else palette.solid_tertiary_bg,
        QPalette.ColorRole.AlternateBase: surface,
        QPalette.ColorRole.Text: text,
        QPalette.ColorRole.Button: surface,
        QPalette.ColorRole.ButtonText: text,
        QPalette.ColorRole.BrightText: palette.text_on_accent,
        QPalette.ColorRole.Highlight: palette.accent,
        QPalette.ColorRole.HighlightedText: palette.text_on_accent,
        QPalette.ColorRole.ToolTipBase: palette.popup_bg,
        QPalette.ColorRole.ToolTipText: text,
        QPalette.ColorRole.PlaceholderText: secondary,
        QPalette.ColorRole.Link: palette.accent_text,
        QPalette.ColorRole.Mid: mix(window, palette.divider),
    }
    for role, color in roles.items():
        result.setColor(role, color)
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
        result.setColor(QPalette.ColorGroup.Disabled, role, disabled)
    return result


def _apply_window_palette(window: QWidget) -> None:
    palette = palette_for(window)
    window.setPalette(to_qpalette(palette, window.palette()))
    # Do not auto-fill with the opaque Window role: Fluent app chrome paints a
    # transparent QMainWindow stylesheet so Windows 11 Mica can show through.
    window.setAutoFillBackground(False)
    if window.isWindow():
        set_window_dark_mode(window, dark=palette.dark)
    window.update()
