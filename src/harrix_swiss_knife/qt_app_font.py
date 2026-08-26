"""Load bundled Fira Sans and JetBrains Mono, and set Fira Sans as the UI font."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife import resources_rc  # noqa: F401

APP_FONT_FAMILY = "Fira Sans"
MONO_FONT_FAMILY = "JetBrains Mono"
_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
_QRC_FONT_PREFIX = ":/assets/fonts"
_UI_FONT_FILES = (
    "FiraSans-Regular.ttf",
    "FiraSans-Medium.ttf",
    "FiraSans-Bold.ttf",
    "FiraSans-Italic.ttf",
    "FiraSans-MediumItalic.ttf",
)
_MONO_FONT_FILES = (
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
    "JetBrainsMono-Bold.ttf",
    "JetBrainsMono-Italic.ttf",
    "JetBrainsMono-MediumItalic.ttf",
)
_PROP = "_hskAppFontInstalled"


def apply_mono_font(widget: QWidget) -> None:
    """Set JetBrains Mono on `widget` after the bundled mono fonts are loaded."""
    load_jetbrains_mono_fonts()
    widget.setFont(mono_qfont(widget.font()))


def bundled_font_paths() -> list[Path]:
    """Return existing bundled TTF files shipped next to the package."""
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if (path := _FONT_DIR / name).is_file()]


def bundled_font_resource_paths() -> list[str]:
    """Return Qt resource paths for bundled fonts that exist in `resources_rc`."""
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if QFile.exists(path := f"{_QRC_FONT_PREFIX}/{name}")]


def install_app_fonts(app: QApplication) -> None:
    """Register bundled fonts and apply Fira Sans as the default UI font."""
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    load_jetbrains_mono_fonts()
    if not load_fira_sans_fonts():
        return
    app.setFont(_font_with_family(app.font(), APP_FONT_FAMILY))
    app.setProperty(_PROP, "1")


def load_fira_sans_fonts() -> bool:
    """Load bundled Fira Sans files. Return whether Regular loaded."""
    return _load_font_files(_UI_FONT_FILES, APP_FONT_FAMILY)


def load_jetbrains_mono_fonts() -> bool:
    """Load bundled JetBrains Mono files. Return whether Regular loaded."""
    return _load_font_files(_MONO_FONT_FILES, MONO_FONT_FAMILY)


def mono_qfont(source: QFont | None = None) -> QFont:
    """Return a copy of `source` using JetBrains Mono."""
    font = QFont(source) if source is not None else QFont()
    return _font_with_family(font, MONO_FONT_FAMILY)


def _add_font(path: str, family: str) -> bool:
    if path.startswith(":/"):
        if not QFile.exists(path):
            return False
    elif not Path(path).is_file():
        return False
    font_id = QFontDatabase.addApplicationFont(path)
    if font_id == -1:
        return False
    return family in QFontDatabase.applicationFontFamilies(font_id)


def _font_with_family(source: QFont, family: str) -> QFont:
    font = QFont(source)
    font.setFamily(family)
    return font


def _load_font_files(names: tuple[str, ...], family: str) -> bool:
    already = family in QFontDatabase.families()
    loaded_regular = already
    for name in names:
        qrc_path = f"{_QRC_FONT_PREFIX}/{name}"
        disk_path = _FONT_DIR / name
        loaded = _add_font(qrc_path, family) or _add_font(str(disk_path), family)
        if name == names[0] and loaded:
            loaded_regular = True
    return loaded_regular
