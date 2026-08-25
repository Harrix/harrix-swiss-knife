"""Load bundled JetBrains Mono and set it as the application UI font."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import resources_rc  # noqa: F401

APP_FONT_FAMILY = "JetBrains Mono"
_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
_QRC_FONT_PREFIX = ":/assets/fonts"
_FONT_FILES = (
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
    "JetBrainsMono-Bold.ttf",
    "JetBrainsMono-Italic.ttf",
    "JetBrainsMono-MediumItalic.ttf",
)
_PROP = "_hskAppFontInstalled"


def bundled_font_paths() -> list[Path]:
    """Return existing JetBrains Mono files shipped next to the package."""
    return [path for name in _FONT_FILES if (path := _FONT_DIR / name).is_file()]


def bundled_font_resource_paths() -> list[str]:
    """Return Qt resource paths for JetBrains Mono that exist in `resources_rc`."""
    return [path for name in _FONT_FILES if QFile.exists(path := f"{_QRC_FONT_PREFIX}/{name}")]


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
    already = APP_FONT_FAMILY in QFontDatabase.families()
    loaded_regular = already
    for name in _FONT_FILES:
        qrc_path = f"{_QRC_FONT_PREFIX}/{name}"
        disk_path = _FONT_DIR / name
        loaded = _add_font(qrc_path) or _add_font(str(disk_path))
        if name == _FONT_FILES[0] and loaded:
            loaded_regular = True
    return loaded_regular


def _add_font(path: str) -> bool:
    if path.startswith(":/"):
        if not QFile.exists(path):
            return False
    elif not Path(path).is_file():
        return False
    font_id = QFontDatabase.addApplicationFont(path)
    if font_id == -1:
        return False
    return APP_FONT_FAMILY in QFontDatabase.applicationFontFamilies(font_id)


def _font_with_app_family(source: QFont) -> QFont:
    font = QFont(source)
    font.setFamily(APP_FONT_FAMILY)
    return font
