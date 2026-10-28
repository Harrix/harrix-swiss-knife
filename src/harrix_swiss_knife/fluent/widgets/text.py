"""Fluent type ramp labels (Caption, Body, Subtitle, Title, Display) and hyperlinks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class BodyLabel(FluentText):
    """Body text."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a body label."""
        super().__init__(text, parent, style=TextStyle.BODY)


class CaptionLabel(FluentText):
    """Caption text (12 px equivalent, secondary color)."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a caption label."""
        super().__init__(text, parent, style=TextStyle.CAPTION, role=TextRole.SECONDARY)


class DisplayLabel(FluentText):
    """Display text (68 px equivalent)."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a display label."""
        super().__init__(text, parent, style=TextStyle.DISPLAY)


class FluentHyperlinkLabel(FluentText):
    """Accent-colored text that opens `url` on click."""

    def __init__(self, text: str, url: str, parent: QWidget | None = None) -> None:
        """Create a hyperlink label.

        Args:

        - `text` (`str`): Visible text.
        - `url` (`str`): Target URL opened with the system handler.
        - `parent` (`QWidget | None`): Optional parent.

        """
        super().__init__(text, parent, role=TextRole.ACCENT)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(url)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001, N802
        """Open the URL on a left click."""
        if event.button() == Qt.MouseButton.LeftButton and self._url:
            QDesktopServices.openUrl(QUrl(self._url))
        super().mouseReleaseEvent(event)

    def url(self) -> str:
        """Return the target URL."""
        return self._url


class StrongBodyLabel(FluentText):
    """Semibold body text."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a semibold body label."""
        super().__init__(text, parent, style=TextStyle.BODY_STRONG)


class SubtitleLabel(FluentText):
    """Subtitle text (20 px equivalent, semibold)."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a subtitle label."""
        super().__init__(text, parent, style=TextStyle.SUBTITLE)


class TitleLabel(FluentText):
    """Title text (28 px equivalent, semibold)."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a title label."""
        super().__init__(text, parent, style=TextStyle.TITLE)


class TitleLargeLabel(FluentText):
    """Large title text (40 px equivalent)."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a large title label."""
        super().__init__(text, parent, style=TextStyle.TITLE_LARGE)
