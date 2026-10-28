"""Hand-written Fluent (WinUI 3) widgets for PySide6 with light and dark themes.

The theme mode lives in `config.json` (`ui_theme`). Windows opt in with
`enable_fluent_theme(window)`; widgets read colors through `palette_for(widget)`.
Widgets are in `harrix_swiss_knife.fluent.widgets`.

"""

from harrix_swiss_knife.fluent.theme import (
    FluentTheme,
    ThemeMode,
    bind_theme,
    css,
    enable_fluent_theme,
    fluent_font,
    is_fluent_themed,
    mix,
    palette_for,
)
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE, LIGHT_PALETTE, FluentPalette

__all__ = [
    "DARK_PALETTE",
    "LIGHT_PALETTE",
    "FluentPalette",
    "FluentTheme",
    "ThemeMode",
    "bind_theme",
    "css",
    "enable_fluent_theme",
    "fluent_font",
    "is_fluent_themed",
    "mix",
    "palette_for",
]
