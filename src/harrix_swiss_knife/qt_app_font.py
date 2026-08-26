"""Load bundled Fira Sans and JetBrains Mono, and set Fira Sans as the UI font."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QFile, QObject, Qt
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
_SCALE_PROP = "_hskUiFontScale"
_SCALED_PROP = "_hskFontScaled"
_MIN_POINT_SIZE = 6.0
_SCALE_EPSILON = 1e-6


class _UiFontScaleFilter(QObject):
    """Scale Designer-assigned fonts when a widget is polished."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Polish and isinstance(watched, QWidget):
            scale_explicit_widget_font(watched)
        return False


def apply_mono_font(widget: QWidget) -> None:
    """Set JetBrains Mono on `widget` after the bundled mono fonts are loaded."""
    load_jetbrains_mono_fonts()
    widget.setFont(mono_qfont(widget.font()))


def apply_ui_font_scale(root: QWidget) -> None:
    """Scale explicit fonts on `root` and its children."""
    scale_explicit_widget_font(root)
    for widget in root.findChildren(QWidget):
        scale_explicit_widget_font(widget)


def bundled_font_paths() -> list[Path]:
    """Return existing bundled TTF files shipped next to the package."""
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if (path := _FONT_DIR / name).is_file()]


def bundled_font_resource_paths() -> list[str]:
    """Return Qt resource paths for bundled fonts that exist in `resources_rc`."""
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if QFile.exists(path := f"{_QRC_FONT_PREFIX}/{name}")]


def current_ui_font_scale() -> float:
    """Return the UI font scale stored on the current `QApplication`."""
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return 1.0
    raw = app.property(_SCALE_PROP)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 1.0


def install_app_fonts(app: QApplication, scale: float | None = None) -> None:
    """Register bundled fonts and apply Fira Sans as the default UI font.

    `scale` multiplies the application font and any widget that set its own point
    size in Designer. When omitted, the value comes from `config.json`
    `ui_font_scale` (default `1.0`).

    """
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    load_jetbrains_mono_fonts()
    if not load_fira_sans_fonts():
        return
    resolved = _resolve_ui_font_scale(scale)
    app.setProperty(_SCALE_PROP, resolved)
    font = _font_with_family(app.font(), APP_FONT_FAMILY)
    point = font.pointSizeF()
    if resolved != 1.0 and point > 0:
        font.setPointSizeF(max(_MIN_POINT_SIZE, point * resolved))
    app.setFont(font)
    _install_ui_font_scale_filter(app)
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


def scale_explicit_widget_font(widget: QWidget) -> None:
    """Multiply a widget's own point size by the current UI font scale once."""
    scale = current_ui_font_scale()
    if abs(scale - 1.0) < _SCALE_EPSILON or widget.property(_SCALED_PROP) == "1":
        return
    if not widget.testAttribute(Qt.WidgetAttribute.WA_SetFont):
        return
    font = widget.font()
    point = font.pointSizeF()
    if point > 0:
        font.setPointSizeF(max(_MIN_POINT_SIZE, point * scale))
        widget.setFont(font)
    widget.setProperty(_SCALED_PROP, "1")


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


def _install_ui_font_scale_filter(app: QApplication) -> None:
    existing = app.property("_hskUiFontScaleFilter")
    if isinstance(existing, _UiFontScaleFilter):
        return
    event_filter = _UiFontScaleFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty("_hskUiFontScaleFilter", event_filter)


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


def _resolve_ui_font_scale(scale: float | None) -> float:
    # Imported lazily so the installer can load fonts without `harrix_pylib`.
    from harrix_swiss_knife.config_model import clamp_ui_font_scale, get_ui_font_scale  # noqa: PLC0415

    if scale is not None:
        return clamp_ui_font_scale(scale)
    return get_ui_font_scale()
