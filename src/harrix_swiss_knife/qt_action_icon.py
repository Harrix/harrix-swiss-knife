"""Qt helper for tray/menu action icons (custom SVG, then emoji).

GUI surfaces prefer `icon_svg` (a file under `assets/actions/`). The action
`icon` emoji stays on the class for Markdown/docs.

"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QCursor, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon

logger = logging.getLogger(__name__)

_CACHE: dict[tuple[str, int, float], QIcon] = {}


def action_svg_path(name: str) -> Path | None:
    """Return `assets/actions/<name>.svg` when `name` is a safe existing file."""
    raw = name.strip()
    if not raw or ".." in raw or "/" in raw or "\\" in raw:
        return None
    filename = raw if raw.casefold().endswith(".svg") else f"{raw}.svg"
    if Path(filename).name != filename:
        return None
    path = _actions_dir() / filename
    if path.is_file():
        return path
    return None


def create_action_icon(action_cls: type, size: int = 32) -> QIcon:
    """Build the GUI `QIcon` for an action class (`icon_svg`, else `icon`)."""
    return create_menu_icon(resolve_ui_icon_spec(action_cls), size)


def create_menu_icon(spec: str, size: int = 32, *, device_pixel_ratio: float | None = None) -> QIcon:
    """Load a GUI icon from an action SVG, a Qt resource SVG, or an emoji."""
    if not spec:
        return QIcon()
    svg_path = action_svg_path(spec)
    if svg_path is not None:
        return create_svg_file_icon(svg_path, size, device_pixel_ratio=device_pixel_ratio)
    if ".svg" in spec:
        return QIcon(f":/assets/{spec}")
    return create_emoji_icon(spec, size, device_pixel_ratio=device_pixel_ratio)


def create_svg_file_icon(
    path: Path,
    size: int = 32,
    *,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    """Rasterize a colored SVG file into a square `QIcon`."""
    ratio = device_pixel_ratio if device_pixel_ratio is not None else _icon_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    cache_key = (str(path.resolve()), size, ratio)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached

    renderer = QSvgRenderer(str(path))
    if not renderer.isValid():
        logger.warning("Action SVG `%s` is invalid", path)
        return QIcon()

    physical = max(1, round(size * ratio))
    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    renderer.render(painter, QRectF(0.0, 0.0, float(physical), float(physical)))
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    _CACHE[cache_key] = icon
    return icon


def resolve_ui_icon_spec(action_cls: type) -> str:
    """Return the GUI icon spec: existing `icon_svg` file, else emoji `icon`."""
    svg = str(getattr(action_cls, "icon_svg", "") or "").strip()
    emoji = str(getattr(action_cls, "icon", "") or "").strip()
    if svg and action_svg_path(svg) is not None:
        return svg if svg.casefold().endswith(".svg") else f"{svg}.svg"
    return emoji


def _actions_dir() -> Path:
    return Path(__file__).resolve().parent / "assets" / "actions"


def _icon_device_pixel_ratio() -> float:
    app = QGuiApplication.instance()
    if isinstance(app, QGuiApplication):
        screen = QGuiApplication.screenAt(QCursor.pos()) or app.primaryScreen()
        if screen is not None:
            ratio = screen.devicePixelRatio()
            if ratio > 0:
                return float(ratio)
    return 1.0
