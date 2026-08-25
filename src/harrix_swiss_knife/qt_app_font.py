"""Load bundled JetBrains Mono and set it as the application UI font."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

APP_FONT_FAMILY = "JetBrains Mono"
_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
_FONT_FILES = (
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
    "JetBrainsMono-Bold.ttf",
    "JetBrainsMono-Italic.ttf",
    "JetBrainsMono-MediumItalic.ttf",
)
_PROP = "_hskAppFontInstalled"


def bundled_font_paths() -> list[Path]:
    """Return existing JetBrains Mono files shipped with the app."""
    return [path for name in _FONT_FILES if (path := _FONT_DIR / name).is_file()]


def install_app_fonts(app: QApplication) -> None:
    """Register bundled JetBrains Mono and apply it as the default UI font."""
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    if not load_jetbrains_mono_fonts():
        return
    app.setFont(_font_with_app_family(app.font()))
    app.setProperty(_PROP, "1")


def load_jetbrains_mono_fonts() -> bool:
    """Load bundled TTF files into `QFontDatabase`. Return whether Regular loaded."""
    families = QFontDatabase.applicationFontFamilies
    already = APP_FONT_FAMILY in QFontDatabase.families()
    loaded_regular = already
    for path in bundled_font_paths():
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id == -1:
            continue
        names = families(font_id)
        if path.name == _FONT_FILES[0] and APP_FONT_FAMILY in names:
            loaded_regular = True
    return loaded_regular


def _font_with_app_family(source: QFont) -> QFont:
    font = QFont(source)
    font.setFamily(APP_FONT_FAMILY)
    return font
