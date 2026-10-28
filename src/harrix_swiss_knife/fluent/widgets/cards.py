"""Fluent cards: plain, interactive, command, popular, image, URL, promotion, and reminder cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect, QRectF, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QFont, QFontMetrics, QIcon, QLinearGradient, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, rounded_path, with_alpha
from harrix_swiss_knife.fluent.style import themed_icon
from harrix_swiss_knife.fluent.theme import bind_theme, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    CARD_ICON_SIZE,
    COMMAND_CARD_HEIGHT,
    COMMAND_CARD_WIDTH,
    ICON_SIZE,
    ICON_SIZE_LARGE,
    RADIUS_CARD,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XL,
    SPACE_XS,
    TYPE_BODY,
    TYPE_CAPTION,
    TYPE_SUBTITLE,
)
from harrix_swiss_knife.fluent.widgets.buttons import FluentIconButton, FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle
from harrix_swiss_knife.fluent.widgets.text import CaptionLabel
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from PySide6.QtGui import (
        QPaintEvent,
    )

    from harrix_swiss_knife.fluent.tokens import FluentPalette
from harrix_swiss_knife.fluent.widgets.card_base import FluentCard, FluentInteractiveCard

_IMAGE_CARD_HEIGHT = 200
_PROMOTION_HEIGHT = 180


class FluentAcrylicUrlCard(FluentInteractiveCard):
    """Compact link card (icon, title, URL) that opens the URL when clicked."""

    def __init__(
        self,
        title: str,
        url: str,
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = "link",
        description: str = "",
    ) -> None:
        """Create a link card."""
        self._title = title
        self._url = url
        self._icon = icon
        self._description = description or url
        super().__init__(parent)
        self.setFixedSize(198, 220)
        self.clicked.connect(self._open)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint an acrylic-like gradient surface with the icon, title, and link glyph."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, with_alpha(palette.accent, 26))
        gradient.setColorAt(1, with_alpha(palette.accent, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), RADIUS_CARD, RADIUS_CARD)
        icon = _icon_for(self._icon, palette, 54)
        if icon is not None:
            icon.paint(painter, QRect(SPACE_XL, SPACE_XL, 54, 54))
        width = self.width() - 2 * SPACE_XL
        title_font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        top = SPACE_XL + 54 + SPACE_L
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        for line in elide_lines(self._title, title_metrics, width, 2):
            painter.drawText(QRect(SPACE_XL, top, width, title_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line)
            top += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        for line in elide_lines(self._description, caption_metrics, width, 3):
            painter.drawText(
                QRect(SPACE_XL, top + SPACE_XS, width, caption_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line
            )
            top += caption_metrics.height()
        link = themed_icon("external-link", palette, palette.text_secondary, ICON_SIZE)
        link.paint(
            painter, self.width() - SPACE_L - ICON_SIZE, self.height() - SPACE_L - ICON_SIZE, ICON_SIZE, ICON_SIZE
        )
        painter.end()

    def url(self) -> str:
        """Return the target URL."""
        return self._url

    def _open(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))


class FluentCommandCard(FluentInteractiveCard):
    """Fixed-size command tile: icon on the left, bold title and two-line description.

    The tray command window shows every action as one of these. All sizes come
    from `fluent.tokens`, so grids of cards line up without per-card fitting.

    """

    def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        overline: str = "",
        user_data: object = None,
    ) -> None:
        """Create a command card.

        Args:

        - `title` (`str`): Command title (one line, elided).
        - `description` (`str`): Hint text (two lines, elided).
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`QIcon | str | None`): Ready icon, or a Lucide ID painted in the text color.
        - `overline` (`str`): Small caption above the title (for example the section name).
        - `user_data` (`object`): Arbitrary payload (for example a `QAction`).

        """
        self._title = title
        self._description = description
        self._icon = icon
        self._overline = overline
        self.user_data = user_data
        super().__init__(parent)
        self.setFixedSize(COMMAND_CARD_WIDTH, COMMAND_CARD_HEIGHT)
        tip = "\n".join(part for part in (overline, title, description) if part)
        self.setToolTip(tip)

    def description(self) -> str:
        """Return the description text."""
        return self._description

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the surface, icon, title, and description."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        left = SPACE_L
        if icon is not None:
            top = (self.height() - CARD_ICON_SIZE) // 2
            icon.paint(painter, QRect(left, top, CARD_ICON_SIZE, CARD_ICON_SIZE))
            left += CARD_ICON_SIZE + SPACE_L
        width = self.width() - left - SPACE_L
        base = self.font()
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(base, TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        caption_metrics = QFontMetrics(caption_font)
        overline = (
            caption_metrics.elidedText(self._overline, Qt.TextElideMode.ElideRight, width) if self._overline else ""
        )
        title = title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width)
        max_lines = 1 if overline else 2
        desc_lines = elide_lines(self._description, caption_metrics, width, max_lines) if self._description else []
        height = title_metrics.height() + len(desc_lines) * caption_metrics.height()
        if overline:
            height += caption_metrics.height()
        y = (self.height() - height) / 2
        if overline:
            painter.setFont(caption_font)
            painter.setPen(palette.accent_text)
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                overline,
            )
            y += caption_metrics.height()
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(left, y, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title,
        )
        y += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        for line in desc_lines:
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                line,
            )
            y += caption_metrics.height()
        painter.end()

    def set_icon(self, icon: QIcon | str | None) -> None:
        """Replace the icon."""
        self._icon = icon
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the fixed command card size."""
        return QSize(COMMAND_CARD_WIDTH, COMMAND_CARD_HEIGHT)

    def title(self) -> str:
        """Return the title text."""
        return self._title


class FluentImageCard(FluentInteractiveCard):
    """Card with an image on top and a title / caption below."""

    def __init__(
        self, title: str, caption: str = "", parent: QWidget | None = None, *, pixmap: QPixmap | None = None
    ) -> None:
        """Create an image card."""
        self._title = title
        self._caption = caption
        self._pixmap = pixmap
        super().__init__(parent)
        self.setFixedSize(240, _IMAGE_CARD_HEIGHT)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the clipped image and text."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        image_rect = QRectF(1, 1, self.width() - 2, self.height() * 0.6)
        painter.save()
        painter.setClipPath(rounded_path(image_rect.adjusted(0, 0, 0, RADIUS_CARD), RADIUS_CARD))
        painter.setClipRect(image_rect, Qt.ClipOperation.IntersectClip)
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                image_rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(image_rect.topLeft(), scaled)
        else:
            painter.fillRect(image_rect, palette.subtle_hover)
            icon = themed_icon("image", palette, palette.text_tertiary, ICON_SIZE_LARGE)
            center = image_rect.center()
            icon.paint(
                painter,
                int(center.x() - ICON_SIZE_LARGE / 2),
                int(center.y() - ICON_SIZE_LARGE / 2),
                ICON_SIZE_LARGE,
                ICON_SIZE_LARGE,
            )
        painter.restore()
        text_top = int(image_rect.bottom()) + SPACE_S
        width = self.width() - 2 * SPACE_M
        title_font = fluent_font(self.font(), TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(SPACE_M, text_top, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width),
        )
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        painter.drawText(
            QRect(SPACE_M, text_top + title_metrics.height(), width, caption_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            caption_metrics.elidedText(self._caption, Qt.TextElideMode.ElideRight, width),
        )
        painter.end()

    def set_pixmap(self, pixmap: QPixmap | None) -> None:
        """Replace the image."""
        self._pixmap = pixmap
        self.update()


class FluentPopularCard(FluentInteractiveCard):
    """Square-ish tile: large icon, title, caption, and a hover reveal of the details."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        details: str = "",
    ) -> None:
        """Create a popular-item card."""
        self._title = title
        self._subtitle = subtitle
        self._icon = icon
        self._details = details
        super().__init__(parent)
        self.setFixedSize(200, 160)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint icon and text; show details while hovered."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = self.rect().adjusted(SPACE_L, SPACE_L, -SPACE_L, -SPACE_L)
        base = self.font()
        caption = fluent_font(base, TYPE_CAPTION)
        if self._hovered and self._details:
            painter.setFont(caption)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                rect,
                int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
                self._details,
            )
            painter.end()
            return
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        if icon is not None:
            icon.paint(painter, QRect(rect.left(), rect.top(), CARD_ICON_SIZE, CARD_ICON_SIZE))
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        metrics = QFontMetrics(title_font)
        top = rect.top() + CARD_ICON_SIZE + SPACE_M
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(rect.left(), top, rect.width(), metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, rect.width()),
        )
        painter.setFont(caption)
        painter.setPen(palette.text_secondary)
        lines = elide_lines(self._subtitle, QFontMetrics(caption), rect.width(), 2)
        line_height = QFontMetrics(caption).height()
        for index, line in enumerate(lines):
            painter.drawText(
                QRect(rect.left(), top + metrics.height() + SPACE_XS + index * line_height, rect.width(), line_height),
                int(Qt.AlignmentFlag.AlignLeft),
                line,
            )
        painter.end()


class FluentPromotionCard(FluentInteractiveCard):
    """Wide banner card: gradient or image background, title, text, and an action button."""

    action_clicked = Signal()

    def __init__(
        self,
        title: str,
        text: str = "",
        parent: QWidget | None = None,
        *,
        action_text: str = "",
        pixmap: QPixmap | None = None,
    ) -> None:
        """Create a promotion banner."""
        self._pixmap = pixmap
        super().__init__(parent)
        self.setMinimumHeight(_PROMOTION_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        layout.addWidget(FluentText(title, self, style=TextStyle.TITLE))
        if text:
            layout.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        layout.addStretch(1)
        if action_text:
            button = FluentPrimaryButton(action_text, self)
            button.clicked.connect(self.action_clicked)
            row = QHBoxLayout()
            row.addWidget(button)
            row.addStretch(1)
            layout.addLayout(row)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the gradient (or image) background."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setOpacity(0.35)
            painter.drawPixmap(rect.topLeft(), scaled)
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, with_alpha(palette.accent, 46))
            gradient.setColorAt(1, with_alpha(palette.accent, 4))
            painter.fillRect(rect, gradient)
        painter.end()


class FluentReminderCard(FluentCard):
    """Reminder row: severity icon, title, time caption, and a dismiss button."""

    dismissed = Signal()

    def __init__(
        self, title: str, when: str = "", parent: QWidget | None = None, *, icon: str = "bell", text: str = ""
    ) -> None:
        """Create a reminder card."""
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_M, SPACE_S, SPACE_M)
        row.setSpacing(SPACE_M)
        self._icon_name = icon
        self._icon_widget = _IconView(icon, self)
        row.addWidget(self._icon_widget, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(2)
        column.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        if text:
            column.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        if when:
            column.addWidget(CaptionLabel(when, self))
        row.addLayout(column, 1)
        close = FluentIconButton("x", self, tooltip="Dismiss")
        close.clicked.connect(self._dismiss)
        row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)

    def _dismiss(self) -> None:
        self.dismissed.emit()
        self.hide()


class _IconView(QWidget):
    def __init__(self, icon: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._icon = icon
        self.setFixedSize(ICON_SIZE_LARGE, ICON_SIZE_LARGE)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        themed_icon(self._icon, palette, palette.accent_text, ICON_SIZE_LARGE).paint(painter, self.rect())
        painter.end()


def elide_lines(text: str, metrics: QFontMetrics, width: int, max_lines: int) -> list[str]:
    """Word-wrap `text` to `width` and elide the last of at most `max_lines` lines.

    Args:

    - `text` (`str`): Source text.
    - `metrics` (`QFontMetrics`): Metrics of the font the text is painted with.
    - `width` (`int`): Available width in pixels.
    - `max_lines` (`int`): Maximum number of lines.

    Returns:

    - `list[str]`: Lines ready to paint.

    """
    words = text.split()
    lines: list[str] = []
    current = ""
    index = 0
    while index < len(words):
        candidate = f"{current} {words[index]}".strip()
        if metrics.horizontalAdvance(candidate) <= width or not current:
            current = candidate
            index += 1
            continue
        lines.append(current)
        current = ""
        if len(lines) == max_lines - 1:
            break
    rest = " ".join([current, *words[index:]]).strip() if len(lines) == max_lines - 1 else current
    if rest:
        lines.append(metrics.elidedText(rest, Qt.TextElideMode.ElideRight, width))
    return lines[:max_lines]


def _icon_for(icon: QIcon | str | None, palette: FluentPalette, size: int) -> QIcon | None:
    if isinstance(icon, QIcon):
        return None if icon.isNull() else icon
    if icon:
        return themed_icon(icon, palette, palette.text_primary, size)
    return None
