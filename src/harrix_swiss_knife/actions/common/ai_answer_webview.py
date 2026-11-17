"""QWebEngineView helper for rich AI Markdown answers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QSizePolicy, QWidget

if TYPE_CHECKING:
    from pathlib import Path

_webengine_available: bool | None = None


def create_ai_answer_webview(parent: QWidget | None = None) -> QWidget:
    """Create a `QWebEngineView` configured for local Harrix template assets."""
    from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: PLC0415

    view = QWebEngineView(parent)
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    view.setMinimumHeight(280)
    return view


def load_ai_answer_html(view: QWidget, html: str, *, dist_dir: Path) -> None:
    """Load assembled HTML with `dist_dir` as the document base URL."""
    from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: PLC0415

    if not isinstance(view, QWebEngineView):
        msg = f"Expected QWebEngineView, got {type(view)!r}"
        raise TypeError(msg)
    base = QUrl.fromLocalFile(str(dist_dir.resolve().as_posix()) + "/")
    view.setHtml(html, base)


def webengine_available() -> bool:
    """Return whether `QWebEngineView` can be imported in this environment."""
    global _webengine_available  # noqa: PLW0603
    if _webengine_available is not None:
        return _webengine_available
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401, PLC0415
    except Exception:
        _webengine_available = False
    else:
        _webengine_available = True
    return _webengine_available
