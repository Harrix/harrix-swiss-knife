"""Tag delegate: chip display in the table and a Fluent check-list editor."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import (
    QAbstractItemModel,
    QEventLoop,
    QModelIndex,
    QPersistentModelIndex,
    QPoint,
    QRect,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFontMetrics,
    QGuiApplication,
    QHideEvent,
    QKeyEvent,
    QKeySequence,
    QPainter,
    QPaintEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QAbstractItemDelegate,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.finance.tags import format_tag_text, parse_tag_text
from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.theme import enable_fluent_theme, is_fluent_themed, palette_for
from harrix_swiss_knife.fluent.tokens import RADIUS_OVERLAY, SPACE_S, SPACE_XS, FluentPalette
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentCheckBox, FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.display import severity_colors
from harrix_swiss_knife.fluent.widgets.enums import Severity
from harrix_swiss_knife.fluent.widgets.input_base import FluentLineEdit
from harrix_swiss_knife.fluent.widgets.views import FluentScrollArea

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QObject

_EDITOR_HEIGHT = 300
_EDITOR_MIN_WIDTH = 280
_POPUP_HEIGHT = 320
_POPUP_GAP = 2
_CHIP_HEIGHT = 20
_CHIP_PAD_X = 8
_CHIP_GAP = 4
_CHIP_MARGIN_Y = 2


class TagCheckListEditor(QFrame):
    """Fluent popup: checkboxes for known tags, a new-tag field, OK and Close."""

    accepted = Signal()
    rejected = Signal()

    def __init__(
        self,
        known_tags: list[str],
        selected: list[str],
        parent: QWidget | None = None,
    ) -> None:
        """Build the Fluent check list and the field used to type one more tag."""
        super().__init__(parent)
        self.setObjectName("financeTagEditor")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
        layout.setSpacing(SPACE_S)

        self._scroll = FluentScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._host = QWidget(self._scroll)
        self._host.setObjectName("financeTagEditorHost")
        self._checks_layout = QVBoxLayout(self._host)
        self._checks_layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._checks_layout.setSpacing(2)
        self._checks_layout.addStretch(1)
        self._scroll.setWidget(self._host)
        layout.addWidget(self._scroll, stretch=1)

        self._checks: list[FluentCheckBox] = []
        names = list(known_tags)
        selected_keys = {name.casefold() for name in selected}
        known_keys = {name.casefold() for name in names}
        for name in selected:
            if name.casefold() not in known_keys:
                names.append(name)
                known_keys.add(name.casefold())
        for name in names:
            box = FluentCheckBox(name, self._host)
            box.setChecked(name.casefold() in selected_keys)
            self._checks_layout.insertWidget(self._checks_layout.count() - 1, box)
            self._checks.append(box)

        self._new_tag = FluentLineEdit(self, placeholder="Add tag", clearable=True, compact=True)
        layout.addWidget(self._new_tag)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACE_S)
        self._ok_button = FluentPrimaryButton("OK", self)
        self._ok_button.setDefault(True)
        self._ok_button.setAutoDefault(True)
        self._close_button = FluentPushButton("Close", self)
        self._close_button.setAutoDefault(False)
        buttons.addWidget(self._ok_button, stretch=1)
        buttons.addWidget(self._close_button, stretch=1)
        layout.addLayout(buttons)

        self._ok_button.clicked.connect(self.accepted.emit)
        self._close_button.clicked.connect(self.rejected.emit)
        self._new_tag.returnPressed.connect(self.accepted.emit)
        # Shortcuts work while focus is on checkboxes / the add field.
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.rejected.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self.accepted.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self.accepted.emit)
        self.setFocusProxy(self._new_tag if not self._checks else self._checks[0])

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """OK on Enter; Close on Escape when the frame itself has focus."""
        if event.key() == Qt.Key.Key_Escape:
            self.rejected.emit()
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accepted.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint the Fluent popup surface behind the checklist."""
        del event
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()

    def set_selected_tags(self, selected: list[str]) -> None:
        """Sync checkbox states to `selected` without changing the offered names."""
        selected_keys = {name.casefold() for name in selected}
        for box in self._checks:
            box.setChecked(box.text().casefold() in selected_keys)

    def tags_text(self) -> str:
        """Return the checked names plus any tag still typed in the add field."""
        names = [box.text() for box in self._checks if box.isChecked()]
        names.extend(parse_tag_text(self._new_tag.text()))
        return format_tag_text(names)


class TagDelegate(QStyledItemDelegate):
    """Paint tags as Fluent chips and edit them with a check list."""

    def __init__(
        self,
        parent: QObject | None = None,
        tags: list[str] | None = None,
        *,
        tags_provider: Callable[[], list[str]] | None = None,
    ) -> None:
        """Initialize the tag delegate.

        Args:

        - `parent` (`QObject | None`): Parent object, usually the transactions view.
        - `tags` (`list[str] | None`): Fallback names when `tags_provider` is omitted.
        - `tags_provider` (`Callable[[], list[str]] | None`): Called each time the
          editor opens so newly saved tags appear without rebuilding the delegate.

        """
        super().__init__(parent)
        self._tags = list(tags or [])
        self._tags_provider = tags_provider

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Open a Fluent check list of known tags with the current cell values checked."""
        raw = index.data()
        selected = parse_tag_text(str(raw) if raw is not None else "")
        editor = TagCheckListEditor(self._known_tags(), selected, parent)
        editor.accepted.connect(lambda: self._commit_editor(editor))
        editor.rejected.connect(lambda: self._close_editor(editor, revert=True))
        return editor

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw soft accent chips instead of plain comma-separated text."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)
        else:
            super().paint(painter, opt, index)

        raw = index.data()
        names = parse_tag_text(str(raw) if raw is not None else "")
        if not names:
            return
        _paint_tag_chips(painter, opt.rect, names, palette_for(widget))

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Check the tags currently stored in the cell."""
        checklist = cast("TagCheckListEditor", editor)
        raw = index.data()
        checklist.set_selected_tags(parse_tag_text(str(raw) if raw is not None else ""))

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write the checked tags back as one comma-separated cell value."""
        checklist = cast("TagCheckListEditor", editor)
        model.setData(index, checklist.tags_text(), Qt.ItemDataRole.DisplayRole)

    @property
    def tags(self) -> list[str]:
        """Tag names shown when no provider is set."""
        return list(self._tags)

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        self._tags = list(value or [])

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Place a Fluent-sized popup over the cell without clipping off-screen."""
        rect = QRect(option.rect)
        height = _EDITOR_HEIGHT
        width = max(rect.width(), _EDITOR_MIN_WIDTH)
        parent = editor.parentWidget()
        if parent is not None:
            bounds = parent.rect()
            width = min(width, bounds.width())
            height = min(height, bounds.height())
            if rect.top() + height > bounds.bottom() + 1:
                rect.moveTop(max(bounds.top(), bounds.bottom() + 1 - height))
            if rect.left() + width > bounds.right() + 1:
                rect.moveLeft(max(bounds.left(), bounds.right() + 1 - width))
        rect.setWidth(width)
        rect.setHeight(height)
        editor.setGeometry(rect)

    def _close_editor(self, editor: QWidget, *, revert: bool) -> None:
        hint = (
            QAbstractItemDelegate.EndEditHint.RevertModelCache
            if revert
            else QAbstractItemDelegate.EndEditHint.SubmitModelCache
        )
        self.closeEditor.emit(editor, hint)

    def _commit_editor(self, editor: QWidget) -> None:
        self.commitData.emit(editor)
        self._close_editor(editor, revert=False)

    def _known_tags(self) -> list[str]:
        """Return the tag names the editor should offer."""
        if self._tags_provider is not None:
            return list(self._tags_provider())
        return list(self._tags)


class _TagPickerPopup(QFrame):
    """Frameless Qt.Popup hosting `TagCheckListEditor` under an anchor field."""

    finished = Signal(object)

    def __init__(
        self,
        known_tags: list[str],
        selected: list[str],
        *,
        fluent: bool,
    ) -> None:
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("financeTagPickerPopup")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        if fluent:
            enable_fluent_theme(self)
        self._emitted = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.editor = TagCheckListEditor(known_tags, selected, self)
        layout.addWidget(self.editor)
        self.editor.accepted.connect(self._accept)
        self.editor.rejected.connect(self._reject)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Click-outside closes a Qt.Popup — treat that as Cancel."""
        super().hideEvent(event)
        self._emit_finished(None)

    def _accept(self) -> None:
        self._emit_finished(self.editor.tags_text())
        self.hide()

    def _emit_finished(self, value: str | None) -> None:
        if self._emitted:
            return
        self._emitted = True
        self.finished.emit(value)

    def _reject(self) -> None:
        self._emit_finished(None)
        self.hide()


def pick_transaction_tags(
    anchor: QWidget,
    known_tags: list[str],
    selected: list[str],
) -> str | None:
    """Show the tag check-list as a popup under `anchor` and return chosen text, or `None`."""
    popup = _TagPickerPopup(
        known_tags,
        selected,
        fluent=is_fluent_themed(anchor),
    )
    width = max(anchor.width(), _EDITOR_MIN_WIDTH)
    popup.resize(width, _POPUP_HEIGHT)
    _place_popup_under_anchor(popup, anchor)

    result: dict[str, object] = {"value": None}
    loop = QEventLoop(popup)

    def on_finished(value: object) -> None:
        result["value"] = value
        loop.quit()

    popup.finished.connect(on_finished)
    popup.show()
    popup.editor.setFocus(Qt.FocusReason.PopupFocusReason)
    loop.exec()
    popup.deleteLater()
    value = result["value"]
    return value if isinstance(value, str) else None


def _draw_chip(
    painter: QPainter,
    rect: QRectF,
    text: str,
    foreground: QColor,
    background: QColor,
    stroke: QColor,
) -> None:
    paint_surface(painter, rect, background, stroke, rect.height() / 2)
    painter.setPen(foreground)
    text_rect = rect.adjusted(_CHIP_PAD_X, 0, -_CHIP_PAD_X, 0)
    painter.drawText(
        text_rect,
        int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
        text,
    )


def _paint_tag_chips(painter: QPainter, cell: QRect, names: list[str], palette: FluentPalette) -> None:
    """Paint as many accent chips as fit, then a `+N` overflow chip when needed."""
    foreground, background = severity_colors(palette, Severity.ACCENT)
    metrics = QFontMetrics(painter.font())
    x = cell.left() + 2
    y = cell.top() + max(_CHIP_MARGIN_Y, (cell.height() - _CHIP_HEIGHT) // 2)
    right_limit = cell.right() - 2
    remaining = list(names)
    painted = 0
    stroke = QColor(foreground.red(), foreground.green(), foreground.blue(), 60)

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setClipRect(cell)

    while remaining:
        name = remaining[0]
        left = len(remaining) - 1
        chip_w = metrics.horizontalAdvance(name) + _CHIP_PAD_X * 2
        need_overflow = left > 0
        overflow_w = metrics.horizontalAdvance(f"+{left}") + _CHIP_PAD_X * 2 if need_overflow else 0
        room_after = right_limit - (x + chip_w + (_CHIP_GAP if need_overflow else 0))
        if painted > 0 and (x + chip_w > right_limit or (need_overflow and room_after < overflow_w)):
            overflow = f"+{len(remaining)}"
            _draw_chip(
                painter,
                QRectF(x, y, metrics.horizontalAdvance(overflow) + _CHIP_PAD_X * 2, _CHIP_HEIGHT),
                overflow,
                foreground,
                background,
                stroke,
            )
            break
        if x + chip_w > right_limit and painted == 0:
            available = max(24, right_limit - x)
            elided = metrics.elidedText(name, Qt.TextElideMode.ElideRight, available - _CHIP_PAD_X * 2)
            chip_w = metrics.horizontalAdvance(elided) + _CHIP_PAD_X * 2
            _draw_chip(painter, QRectF(x, y, chip_w, _CHIP_HEIGHT), elided, foreground, background, stroke)
            break
        _draw_chip(painter, QRectF(x, y, chip_w, _CHIP_HEIGHT), name, foreground, background, stroke)
        x += chip_w + _CHIP_GAP
        remaining.pop(0)
        painted += 1

    painter.restore()


def _place_popup_under_anchor(popup: QWidget, anchor: QWidget) -> None:
    """Move `popup` under `anchor`, flipping above when the screen has no room below."""
    gap = _POPUP_GAP
    below = anchor.mapToGlobal(QPoint(0, anchor.height() + gap))
    screen = QGuiApplication.screenAt(anchor.mapToGlobal(anchor.rect().center()))
    area = screen.availableGeometry() if screen is not None else QRect(below, popup.size())
    x = max(area.left() + 4, min(below.x(), area.right() - popup.width() - 4))
    y = below.y()
    if y + popup.height() > area.bottom() - 4:
        above = anchor.mapToGlobal(QPoint(0, -popup.height() - gap))
        y = above.y() if above.y() >= area.top() + 4 else max(area.top() + 4, area.bottom() - popup.height() - 4)
    popup.move(x, y)
