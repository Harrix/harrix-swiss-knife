"""Fluent text, number, choice, and picker inputs."""

from __future__ import annotations

import html
import math
import re
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QPointF,
    QRectF,
    QSize,
    QStringListModel,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QDoubleValidator,
    QGuiApplication,
    QIcon,
    QKeyEvent,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QStandardItem,
    QStandardItemModel,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QCompleter,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.style import (
    combo_box_qss,
    item_view_qss,
    spin_box_qss,
    text_edit_qss,
    themed_icon,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_NORMAL,
    CONTROL_HEIGHT,
    CONTROL_HEIGHT_COMPACT,
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SPACE_S,
    SPACE_XS,
)
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentIconButton
from harrix_swiss_knife.fluent.widgets.text import BodyLabel, CaptionLabel

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from PySide6.QtGui import QMouseEvent, QPaintEvent
from harrix_swiss_knife.fluent.widgets.enums import MatchMode
from harrix_swiss_knife.fluent.widgets.input_base import FluentLineEdit

_STAR_COUNT = 5
_POPUP_MAX_ROWS = 8
_POPUP_MAX_ITEMS = 50


class FluentAutoComplete(FluentLineEdit):
    """Text box with a live-filtered popup and bold matched fragments."""

    suggestion_chosen = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        suggestions: Sequence[str] = (),
        mode: MatchMode = MatchMode.CONTAINS,
        placeholder: str = "",
    ) -> None:
        """Create an auto-complete box."""
        super().__init__(parent, placeholder=placeholder)
        self._suggestions = list(suggestions)
        self._mode = mode
        self._popup = QListWidget()
        self._popup.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self._popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._popup.setMouseTracking(True)
        self._popup.setItemDelegate(_HighlightDelegate(self._popup))
        self._popup.itemClicked.connect(self._choose_item)
        self.textEdited.connect(self._refilter)
        self.installEventFilter(self)
        self.destroyed.connect(self._popup.deleteLater)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Navigate the popup with arrows and Enter; hide on focus loss."""
        if watched is self and event.type() == QEvent.Type.FocusOut:
            self._popup.hide()
        if watched is self and event.type() == QEvent.Type.KeyPress and self._popup.isVisible():
            key = event.key()  # type: ignore[attr-defined]
            row = self._popup.currentRow()
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                step = 1 if key == Qt.Key.Key_Down else -1
                self._popup.setCurrentRow(max(0, min(self._popup.count() - 1, row + step)))
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self._popup.currentItem() is not None:
                self._choose_item(self._popup.currentItem())
                return True
            if key == Qt.Key.Key_Escape:
                self._popup.hide()
                return True
        return super().eventFilter(watched, event)

    def matches(self, text: str) -> list[str]:
        """Return suggestions that match `text` under the current mode."""
        if not text:
            return []
        folded = text.casefold()
        result: list[str] = []
        for candidate in self._suggestions:
            value = candidate.casefold()
            if self._mode == MatchMode.PREFIX:
                ok = value.startswith(folded)
            elif self._mode == MatchMode.SUFFIX:
                ok = value.endswith(folded)
            elif self._mode == MatchMode.REGEX:
                try:
                    ok = re.search(text, candidate, flags=re.IGNORECASE) is not None
                except re.error:
                    ok = False
            else:
                ok = folded in value
            if ok:
                result.append(candidate)
        return result

    def refresh_theme(self) -> None:
        """Re-apply chrome for the field and the popup."""
        super().refresh_theme()
        palette = palette_for(self)
        popup = getattr(self, "_popup", None)
        if popup is not None:
            popup.setStyleSheet(
                item_view_qss(palette, "QListWidget", transparent=False)
                + f"QListWidget {{ background: {css(palette.popup_bg)}; border: 1px solid {css(palette.popup_stroke)};"
                f" border-radius: {RADIUS_CONTROL}px; padding: {SPACE_XS}px; }}",
            )

    def set_match_mode(self, mode: MatchMode) -> None:
        """Change the matching mode."""
        self._mode = mode
        self._refilter(self.text())

    def set_suggestions(self, suggestions: Sequence[str]) -> None:
        """Replace the suggestion list."""
        self._suggestions = list(suggestions)

    def _choose_item(self, item: QListWidgetItem) -> None:
        text = item.data(Qt.ItemDataRole.UserRole)
        self.setText(text)
        self._popup.hide()
        self.suggestion_chosen.emit(text)

    def _highlight(self, candidate: str, text: str) -> str:
        if self._mode == MatchMode.REGEX:
            try:
                match = re.search(text, candidate, flags=re.IGNORECASE)
            except re.error:
                match = None
            if match is None:
                return html.escape(candidate)
            start, end = match.span()
        else:
            start = candidate.casefold().find(text.casefold())
            if self._mode == MatchMode.SUFFIX:
                start = len(candidate) - len(text)
            if start < 0:
                return html.escape(candidate)
            end = start + len(text)
        color = css(palette_for(self).accent_text)
        return (
            f"{html.escape(candidate[:start])}<b style='color:{color}'>{html.escape(candidate[start:end])}</b>"
            f"{html.escape(candidate[end:])}"
        )

    def _refilter(self, text: str) -> None:
        found = self.matches(text)
        self._popup.clear()
        if not found:
            self._popup.hide()
            return
        for candidate in found[:_POPUP_MAX_ITEMS]:
            item = QListWidgetItem(candidate)
            item.setData(Qt.ItemDataRole.UserRole, candidate)
            item.setData(_HTML_ROLE, self._highlight(candidate, text))
            self._popup.addItem(item)
        self._popup.setCurrentRow(0)
        rows = min(_POPUP_MAX_ROWS, len(found))
        row_height = self._popup.sizeHintForRow(0) if self._popup.count() else CONTROL_HEIGHT
        self._popup.setFixedSize(self.width(), rows * row_height + 2 * SPACE_S)
        self._popup.move(self.mapToGlobal(QPoint(0, self.height() + 2)))
        self._popup.show()


class FluentCaptcha(QWidget):
    """Code input split into one box per character with auto-advance and paste."""

    completed = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, length: int = 6, digits_only: bool = True) -> None:
        """Create a code input.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `length` (`int`): Number of characters. Defaults to `6`.
        - `digits_only` (`bool`): Accept only digits (else letters and digits).

        """
        super().__init__(parent)
        self._pattern = re.compile(r"\d" if digits_only else r"[0-9A-Za-z]")
        self._boxes: list[FluentLineEdit] = []
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE_S)
        for _ in range(length):
            box = FluentLineEdit(self, clearable=False)
            box.setMaxLength(1)
            box.setFixedWidth(CONTROL_HEIGHT + SPACE_S)
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.installEventFilter(self)
            box.textEdited.connect(lambda text, b=box: self._on_edited(b, text))
            row.addWidget(box)
            self._boxes.append(box)
        row.addStretch(1)

    def clear(self) -> None:
        """Empty every box and focus the first one."""
        for box in self._boxes:
            box.clear()
        if self._boxes:
            self._boxes[0].setFocus()

    def code(self) -> str:
        """Return the typed characters."""
        return "".join(box.text() for box in self._boxes)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Backspace/arrow navigation and paste distribution."""
        if event.type() != QEvent.Type.KeyPress or watched not in self._boxes:
            return super().eventFilter(watched, event)
        if not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        index = next(position for position, box in enumerate(self._boxes) if box is watched)
        key = event.key()
        if event.matches(QKeySequence.StandardKey.Paste):
            self.set_code(QGuiApplication.clipboard().text(), start=index)
            return True
        if key == Qt.Key.Key_Backspace and not self._boxes[index].text() and index > 0:
            self._boxes[index - 1].clear()
            self._boxes[index - 1].setFocus()
            return True
        if key == Qt.Key.Key_Left and index > 0:
            self._boxes[index - 1].setFocus()
            return True
        if key == Qt.Key.Key_Right and index + 1 < len(self._boxes):
            self._boxes[index + 1].setFocus()
            return True
        return super().eventFilter(watched, event)

    def set_code(self, text: str, *, start: int = 0) -> None:
        """Distribute allowed characters of `text` into boxes from `start`."""
        chars = [char for char in text if self._pattern.fullmatch(char)]
        for offset, char in enumerate(chars):
            index = start + offset
            if index >= len(self._boxes):
                break
            self._boxes[index].setText(char)
        last = min(len(self._boxes) - 1, start + len(chars))
        self._boxes[last].setFocus()
        self._check_complete()

    def _check_complete(self) -> None:
        code = self.code()
        if len(code) == len(self._boxes):
            self.completed.emit(code)

    def _on_edited(self, box: FluentLineEdit, text: str) -> None:
        if text and not self._pattern.fullmatch(text):
            box.clear()
            return
        if text:
            index = self._boxes.index(box)
            if index + 1 < len(self._boxes):
                self._boxes[index + 1].setFocus()
        self._check_complete()


class FluentComboBox(QComboBox):
    """Drop-down list with Fluent chrome and a rounded popup."""

    def __init__(self, parent: QWidget | None = None, *, items: Iterable[str] = (), compact: bool = False) -> None:
        """Create a combo box with optional string items (`compact` uses the compact control height)."""
        super().__init__(parent)
        self._height = CONTROL_HEIGHT_COMPACT if compact else CONTROL_HEIGHT
        if compact:
            self.setFixedHeight(self._height)
        else:
            self.setMinimumHeight(self._height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addItems(list(items))
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        self.setStyleSheet(combo_box_qss(palette_for(self), height=self._height))


class FluentDoubleSpinBox(QDoubleSpinBox):
    """Decimal number box with Fluent up/down buttons."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a decimal spin box."""
        super().__init__(parent)
        self.setMinimumHeight(CONTROL_HEIGHT)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        self.setStyleSheet(spin_box_qss(palette_for(self), "QDoubleSpinBox"))


class FluentEditableComboBox(FluentComboBox):
    """Combo box that also accepts typed text."""

    def __init__(self, parent: QWidget | None = None, *, items: Iterable[str] = ()) -> None:
        """Create an editable combo box."""
        super().__init__(parent, items=items)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)


class FluentKeyBinder(FluentPushButton):
    """Button that records one key (or chord) when clicked."""

    binding_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, binding: str = "") -> None:
        """Create a key binder with an optional initial binding (portable text)."""
        super().__init__("", parent, icon="keyboard")
        self._binding = binding
        self._recording = False
        self.clicked.connect(self._start_recording)
        self._show_binding()

    def binding(self) -> str:
        """Return the recorded binding in `QKeySequence` portable text."""
        return self._binding

    def focusOutEvent(self, event) -> None:  # noqa: ANN001, N802
        """Cancel recording when focus leaves."""
        self._recording = False
        self._show_binding()
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Capture the pressed key while recording; Escape cancels, Backspace clears."""
        if not self._recording:
            super().keyPressEvent(event)
            return
        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        self._recording = False
        if key == Qt.Key.Key_Escape:
            self._show_binding()
            return
        if key == Qt.Key.Key_Backspace:
            self.set_binding("")
            return
        combo = event.keyCombination()
        self.set_binding(QKeySequence(combo).toString(QKeySequence.SequenceFormat.PortableText))

    def set_binding(self, binding: str) -> None:
        """Set the binding and emit `binding_changed`."""
        self._binding = binding
        self._show_binding()
        self.binding_changed.emit(binding)

    def _show_binding(self) -> None:
        if self._recording:
            self.setText("Press a key…")
            return
        native = QKeySequence(self._binding).toString(QKeySequence.SequenceFormat.NativeText) if self._binding else ""
        self.setText(native or "Click to bind")

    def _start_recording(self) -> None:
        self._recording = True
        self.setFocus()
        self._show_binding()


class FluentMultiSelectComboBox(FluentComboBox):
    """Combo box whose popup items are checkable; the face shows the selection."""

    selection_changed = Signal(list)

    def __init__(
        self, parent: QWidget | None = None, *, items: Iterable[str] = (), placeholder: str = "Select"
    ) -> None:
        """Create a multi-select combo box."""
        super().__init__(parent)
        self._placeholder = placeholder
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        for text in items:
            self.add_option(text)
        self.view().pressed.connect(self._toggle_index)
        self._model.itemChanged.connect(lambda _item: self._on_changed())
        self._on_changed()

    def add_option(self, text: str, *, checked: bool = False) -> None:
        """Append a checkable option."""
        item = QStandardItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self._model.appendRow(item)

    def hidePopup(self) -> None:  # noqa: N802
        """Keep the popup open while toggling; close only when the pointer leaves it."""
        if self.view().underMouse():
            return
        super().hidePopup()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Show the joined selection (or the placeholder) on the face."""
        self.setCurrentIndex(-1)
        super().paintEvent(event)

    def selected_texts(self) -> list[str]:
        """Return checked option texts in order."""
        return [
            self._model.item(row).text()
            for row in range(self._model.rowCount())
            if self._model.item(row).checkState() == Qt.CheckState.Checked
        ]

    def set_selected(self, texts: Iterable[str]) -> None:
        """Check exactly the options named in `texts`."""
        wanted = set(texts)
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            item.setCheckState(Qt.CheckState.Checked if item.text() in wanted else Qt.CheckState.Unchecked)

    def _on_changed(self) -> None:
        selected = self.selected_texts()
        self.setPlaceholderText(", ".join(selected) if selected else self._placeholder)
        self.update()
        self.selection_changed.emit(selected)

    def _toggle_index(self, index) -> None:  # noqa: ANN001
        item = self._model.itemFromIndex(index)
        if item is None:
            return
        state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        item.setCheckState(state)


class FluentNumberBox(QWidget):
    """Number box with minus/plus buttons, wheel, arrow keys, and a range clamp."""

    value_changed = Signal(float)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: float = 0.0,
        maximum: float = 100.0,
        step: float = 1.0,
        decimals: int = 0,
    ) -> None:
        """Create a number box.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `minimum` / `maximum` (`float`): Allowed range.
        - `step` (`float`): Increment for buttons, wheel, and arrow keys.
        - `decimals` (`int`): Digits after the decimal point.

        """
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._step = step
        self._decimals = decimals
        self._value = minimum
        self._edit = FluentLineEdit(self, clearable=False)
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setValidator(QDoubleValidator(minimum, maximum, decimals, self._edit))
        self._edit.editingFinished.connect(self._commit_text)
        self._edit.installEventFilter(self)
        self._minus = FluentIconButton("minus", self, tooltip="Decrease")
        self._plus = FluentIconButton("plus", self, tooltip="Increase")
        self._minus.clicked.connect(lambda: self.step_by(-1))
        self._plus.clicked.connect(lambda: self.step_by(1))
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE_XS)
        row.addWidget(self._minus)
        row.addWidget(self._edit, stretch=1)
        row.addWidget(self._plus)
        self._show_value()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Step with Up/Down keys and the mouse wheel inside the text field."""
        if watched is self._edit:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()  # type: ignore[attr-defined]
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    self.step_by(1 if key == Qt.Key.Key_Up else -1)
                    return True
            if event.type() == QEvent.Type.Wheel:
                delta = event.angleDelta().y()  # type: ignore[attr-defined]
                if delta:
                    self.step_by(1 if delta > 0 else -1)
                return True
        return super().eventFilter(watched, event)

    def set_value(self, value: float) -> None:
        """Set the value (clamped to the range)."""
        clamped = round(min(self._maximum, max(self._minimum, value)), self._decimals)
        if clamped == self._value:
            self._show_value()
            return
        self._value = clamped
        self._show_value()
        self.value_changed.emit(clamped)

    def step_by(self, steps: int) -> None:
        """Change the value by `steps` increments."""
        self.set_value(self._value + steps * self._step)

    def value(self) -> float:
        """Return the current value."""
        return self._value

    def _commit_text(self) -> None:
        text = self._edit.text().replace(",", ".").strip()
        try:
            self.set_value(float(text))
        except ValueError:
            self._show_value()

    def _show_value(self) -> None:
        self._edit.setText(f"{self._value:.{self._decimals}f}")
        self._minus.setEnabled(self._value > self._minimum)
        self._plus.setEnabled(self._value < self._maximum)


class FluentPasswordBox(FluentLineEdit):
    """Password text box with a reveal (eye) toggle."""

    def __init__(self, parent: QWidget | None = None, *, placeholder: str = "Password") -> None:
        """Create a password box."""
        self._reveal_action: QAction | None = None
        super().__init__(parent, placeholder=placeholder, clearable=False)
        self.setEchoMode(QLineEdit.EchoMode.Password)

    def is_revealed(self) -> bool:
        """Return whether the password is shown as plain text."""
        return self.echoMode() == QLineEdit.EchoMode.Normal

    def refresh_theme(self) -> None:
        """Re-apply chrome and the reveal glyph."""
        super().refresh_theme()
        if self._reveal_action is None:
            self._reveal_action = self.addAction(self._reveal_icon(), QLineEdit.ActionPosition.TrailingPosition)
            self._reveal_action.setToolTip("Show password")
            self._reveal_action.triggered.connect(self.toggle_reveal)
        else:
            self._reveal_action.setIcon(self._reveal_icon())

    def toggle_reveal(self) -> None:
        """Switch between hidden and visible text."""
        revealed = not self.is_revealed()
        self.setEchoMode(QLineEdit.EchoMode.Normal if revealed else QLineEdit.EchoMode.Password)
        if self._reveal_action is not None:
            self._reveal_action.setIcon(self._reveal_icon())
            self._reveal_action.setToolTip("Hide password" if revealed else "Show password")

    def _reveal_icon(self) -> QIcon:
        palette = palette_for(self)
        name = "eye-off" if self.echoMode() == QLineEdit.EchoMode.Normal else "eye"
        return themed_icon(name, palette, palette.text_secondary)


class FluentPlainTextEdit(QPlainTextEdit):
    """Multi-line plain text box."""

    def __init__(self, parent: QWidget | None = None, *, placeholder: str = "") -> None:
        """Create a multi-line text box."""
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        self.setStyleSheet(text_edit_qss(palette_for(self), "QPlainTextEdit"))


class FluentRatingControl(QWidget):
    """Star rating with hover preview and optional read-only mode."""

    rating_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, stars: int = _STAR_COUNT, read_only: bool = False) -> None:
        """Create a rating control."""
        super().__init__(parent)
        self._stars = stars
        self._value = 0
        self._hover = 0
        self._read_only = read_only
        self._size = 20
        self.setMouseTracking(True)
        if not read_only:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Clear the hover preview."""
        self._hover = 0
        self.update()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Preview the rating under the pointer."""
        if not self._read_only:
            self._hover = self._star_at(event.position().x())
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Commit the rating under the pointer (click the same star again to clear)."""
        if not self._read_only and event.button() == Qt.MouseButton.LeftButton:
            star = self._star_at(event.position().x())
            self.set_value(0 if star == self._value else star)
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint filled and empty stars."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        shown = self._hover or self._value
        top = (self.height() - self._size) / 2
        for index in range(self._stars):
            rect = QRectF(index * (self._size + SPACE_XS) + 1, top + 1, self._size - 2, self._size - 2)
            path = _star_path(rect)
            if index < shown:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(palette.accent if self.isEnabled() else palette.text_disabled)
            else:
                pen = QPen(palette.control_strong_stroke)
                pen.setWidthF(1.2)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        painter.end()

    def set_read_only(self, *, read_only: bool) -> None:
        """Enable or disable user input."""
        self._read_only = read_only
        self.setCursor(Qt.CursorShape.ArrowCursor if read_only else Qt.CursorShape.PointingHandCursor)

    def set_value(self, value: int) -> None:
        """Set the rating (`0` clears)."""
        value = max(0, min(self._stars, value))
        if value == self._value:
            return
        self._value = value
        self.update()
        self.rating_changed.emit(value)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the width of every star."""
        return QSize(self._stars * (self._size + SPACE_XS), CONTROL_HEIGHT)

    def value(self) -> int:
        """Return the rating."""
        return self._value

    def _star_at(self, x: float) -> int:
        return max(0, min(self._stars, int(x // (self._size + SPACE_XS)) + 1))


class FluentSearchLineEdit(FluentLineEdit):
    """Text box with a trailing search glyph; emits `search_requested` on Enter."""

    search_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, placeholder: str = "Search", compact: bool = False) -> None:
        """Create a search box."""
        self._search_action: QAction | None = None
        super().__init__(parent, placeholder=placeholder, compact=compact)
        self.returnPressed.connect(lambda: self.search_requested.emit(self.text()))

    def refresh_theme(self) -> None:
        """Re-apply chrome and the search glyph color."""
        super().refresh_theme()
        palette = palette_for(self)
        icon = themed_icon("search", palette, palette.text_secondary)
        if self._search_action is None:
            self._search_action = self.addAction(icon, QLineEdit.ActionPosition.TrailingPosition)
            self._search_action.triggered.connect(lambda: self.search_requested.emit(self.text()))
        else:
            self._search_action.setIcon(icon)


class FluentSelectorBar(QWidget):
    """Segmented selector with a sliding accent indicator."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        """Create a selector bar with text segments."""
        super().__init__(parent)
        self._items = list(items)
        self._current = 0 if self._items else -1
        self._indicator_x = 0.0
        self._hover = -1
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.valueChanged.connect(self._on_animation)
        bind_theme(self, self.update)

    def add_item(self, text: str) -> None:
        """Append a segment."""
        self._items.append(text)
        self._current = max(self._current, 0)
        self.updateGeometry()
        self.update()

    def current_index(self) -> int:
        """Return the selected segment index."""
        return self._current

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Clear the hover highlight."""
        self._hover = -1
        self.update()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered segment."""
        self._hover = self._index_at(event.position().x())
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select the clicked segment."""
        index = self._index_at(event.position().x())
        if index >= 0:
            self.set_current_index(index)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint segments, hover, and the sliding indicator."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        width = self._segment_width()
        for index, text in enumerate(self._items):
            rect = QRectF(index * width, 0, width, self.height())
            if index == self._hover:
                paint_surface(painter, rect.adjusted(2, 2, -2, -2), palette.subtle_hover, None, RADIUS_CONTROL)
            selected = index == self._current
            painter.setPen(palette.text_primary if selected else palette.text_secondary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        if self._current >= 0:
            indicator = QRectF(self._indicator_x + width / 2 - 8, self.height() - 3, 16, 3)
            paint_surface(painter, indicator, palette.accent, None, 1.5)
        painter.end()

    def set_current_index(self, index: int) -> None:
        """Select a segment and animate the indicator."""
        if index == self._current or not 0 <= index < len(self._items):
            return
        width = self._segment_width()
        self._animation.stop()
        self._animation.setStartValue(float(self._current * width))
        self._animation.setEndValue(float(index * width))
        self._current = index
        self._animation.start()
        self.current_changed.emit(index)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return segment width times count."""
        return QSize(max(1, len(self._items)) * self._segment_width(), CONTROL_HEIGHT + 4)

    def _index_at(self, x: float) -> int:
        width = self._segment_width()
        index = int(x // width) if width else -1
        return index if 0 <= index < len(self._items) else -1

    def _on_animation(self, value: float) -> None:
        self._indicator_x = float(value)
        self.update()

    def _segment_width(self) -> int:
        metrics = self.fontMetrics()
        widest = max((metrics.horizontalAdvance(text) for text in self._items), default=40)
        return widest + 2 * SPACE_S + 2 * SPACE_XS


class FluentSlider(QSlider):
    """Slider with a thin rounded track and a round accent thumb."""

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None) -> None:
        """Create a slider."""
        super().__init__(orientation, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply track and thumb colors."""
        palette = palette_for(self)
        thumb_border = palette.solid_quarternary_bg
        self.setStyleSheet(f"""
QSlider {{ background: transparent; min-height: 24px; min-width: 24px; }}
QSlider::groove:horizontal {{ height: 4px; border-radius: 2px; background: {css(palette.control_strong_fill)}; }}
QSlider::groove:vertical {{ width: 4px; border-radius: 2px; background: {css(palette.control_strong_fill)}; }}
QSlider::sub-page:horizontal {{ border-radius: 2px; background: {css(palette.accent)}; }}
QSlider::add-page:vertical {{ border-radius: 2px; background: {css(palette.accent)}; }}
QSlider::handle {{
    background: {css(palette.accent)};
    border: 5px solid {css(thumb_border)};
    width: 10px; height: 10px; border-radius: 10px;
}}
QSlider::handle:horizontal {{ margin: -8px 0px; }}
QSlider::handle:vertical {{ margin: 0px -8px; }}
QSlider::handle:hover {{ border-width: 4px; }}
QSlider::handle:pressed {{ border-width: 6px; }}
QSlider::handle:disabled {{ background: {css(palette.accent_disabled)}; }}
""")


class FluentSpinBox(QSpinBox):
    """Integer number box with Fluent up/down buttons."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an integer spin box."""
        super().__init__(parent)
        self.setMinimumHeight(CONTROL_HEIGHT)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        self.setStyleSheet(spin_box_qss(palette_for(self), "QSpinBox"))


class FluentSuggestBox(FluentSearchLineEdit):
    """Search box that suggests items from a list while typing."""

    suggestion_chosen = Signal(str)

    def __init__(
        self, parent: QWidget | None = None, *, suggestions: Sequence[str] = (), placeholder: str = "Search"
    ) -> None:
        """Create a suggest box."""
        super().__init__(parent, placeholder=placeholder)
        self._model = QStringListModel(list(suggestions), self)
        completer = QCompleter(self._model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(_POPUP_MAX_ROWS)
        completer.activated.connect(self.suggestion_chosen.emit)
        self.setCompleter(completer)
        self._style_popup()

    def refresh_theme(self) -> None:
        """Re-apply chrome and the popup style."""
        super().refresh_theme()
        if self.completer() is not None:
            self._style_popup()

    def set_suggestions(self, suggestions: Sequence[str]) -> None:
        """Replace the suggestion list."""
        self._model.setStringList(list(suggestions))

    def _style_popup(self) -> None:
        completer = self.completer()
        if completer is None:
            return
        popup = completer.popup()
        palette = palette_for(self)
        popup.setStyleSheet(
            item_view_qss(palette, "QListView", transparent=False)
            + f"QListView {{ background: {css(palette.popup_bg)}; border: 1px solid {css(palette.popup_stroke)};"
            f" border-radius: {RADIUS_OVERLAY}px; padding: {SPACE_XS}px; }}",
        )


class FluentTextEdit(QTextEdit):
    """Multi-line rich text box."""

    def __init__(self, parent: QWidget | None = None, *, placeholder: str = "") -> None:
        """Create a rich text box."""
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        self.setStyleSheet(text_edit_qss(palette_for(self), "QTextEdit"))


class FluentTransfer(QWidget):
    """Two lists with filters and buttons to move items between them."""

    changed = Signal(list)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        source: Sequence[str] = (),
        target: Sequence[str] = (),
        titles: tuple[str, str] = ("Available", "Selected"),
    ) -> None:
        """Create a transfer control."""
        super().__init__(parent)
        self._lists: list[QListWidget] = []
        self._filters: list[FluentLineEdit] = []
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE_S)
        for column, (title, values) in enumerate(zip(titles, (source, target), strict=True)):
            row.addLayout(self._make_column(title, values))
            if column == 0:
                buttons = QVBoxLayout()
                buttons.addStretch(1)
                to_right = FluentIconButton("chevron-right", self, tooltip="Move to selected")
                to_left = FluentIconButton("chevron-left", self, tooltip="Move to available")
                to_right.clicked.connect(lambda: self._move(0, 1))
                to_left.clicked.connect(lambda: self._move(1, 0))
                buttons.addWidget(to_right)
                buttons.addWidget(to_left)
                buttons.addStretch(1)
                row.addLayout(buttons)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply list chrome."""
        palette = palette_for(self)
        for widget in self._lists:
            widget.setStyleSheet(
                item_view_qss(palette, "QListWidget", transparent=False)
                + f"QListWidget {{ border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; }}",
            )

    def selected_items(self) -> list[str]:
        """Return items in the right-hand list."""
        target = self._lists[1]
        return [target.item(row).text() for row in range(target.count())]

    def _apply_filter(self, column: int, text: str) -> None:
        widget = self._lists[column]
        folded = text.casefold()
        for row in range(widget.count()):
            item = widget.item(row)
            item.setHidden(bool(folded) and folded not in item.text().casefold())

    def _make_column(self, title: str, values: Sequence[str]) -> QVBoxLayout:
        column = QVBoxLayout()
        column.setSpacing(SPACE_XS)
        column.addWidget(BodyLabel(title, self))
        index = len(self._lists)
        search = FluentLineEdit(self, placeholder="Filter")
        search.textChanged.connect(lambda text, i=index: self._apply_filter(i, text))
        widget = QListWidget(self)
        widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        widget.addItems(list(values))
        widget.itemDoubleClicked.connect(lambda _item, i=index: self._move(i, 1 - i))
        self._lists.append(widget)
        self._filters.append(search)
        column.addWidget(search)
        column.addWidget(widget, stretch=1)
        column.addWidget(CaptionLabel(f"{len(values)} items", self))
        return column

    def _move(self, source: int, target: int) -> None:
        origin = self._lists[source]
        destination = self._lists[target]
        for item in origin.selectedItems():
            destination.addItem(origin.takeItem(origin.row(item)))
        self.changed.emit(self.selected_items())


class FluentTreeSelect(FluentPushButton):
    """Drop-down that picks a leaf from a tree and shows its path."""

    leaf_selected = Signal(list)

    def __init__(self, parent: QWidget | None = None, *, placeholder: str = "Select item") -> None:
        """Create a tree select."""
        super().__init__(placeholder, parent, icon="list-tree")
        self._placeholder = placeholder
        self._path: list[str] = []
        self._popup = QFrame(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        layout = QVBoxLayout(self._popup)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._filter = FluentLineEdit(self._popup, placeholder="Filter")
        self._tree = QTreeWidget(self._popup)
        self._tree.setHeaderHidden(True)
        layout.addWidget(self._filter)
        layout.addWidget(self._tree)
        self._filter.textChanged.connect(self._apply_filter)
        self._tree.itemClicked.connect(self._on_item_clicked)
        self.clicked.connect(self._show_popup)
        self.destroyed.connect(self._popup.deleteLater)

    def add_branch(self, path: Sequence[str]) -> None:
        """Add a leaf by its full path (missing parent nodes are created)."""
        parent_item: QTreeWidgetItem | None = None
        for depth, name in enumerate(path):
            container = self._tree.invisibleRootItem() if parent_item is None else parent_item
            found = next(
                (container.child(i) for i in range(container.childCount()) if container.child(i).text(0) == name), None
            )
            if found is None:
                found = QTreeWidgetItem([name])
                container.addChild(found)
            found.setData(0, Qt.ItemDataRole.UserRole, list(path[: depth + 1]))
            parent_item = found

    def refresh_theme(self) -> None:
        """Re-apply chrome for the button and popup."""
        super().refresh_theme()
        popup = getattr(self, "_popup", None)
        if popup is None:
            return
        palette = palette_for(self)
        popup.setStyleSheet(
            f"QFrame {{ background: {css(palette.popup_bg)}; border: 1px solid {css(palette.popup_stroke)};"
            f" border-radius: {RADIUS_CONTROL}px; }}" + item_view_qss(palette, "QTreeWidget"),
        )

    def selected_path(self) -> list[str]:
        """Return the selected leaf path (empty when nothing is selected)."""
        return list(self._path)

    def _apply_filter(self, text: str) -> None:
        folded = text.casefold()

        def visit(item: QTreeWidgetItem) -> bool:
            children = [item.child(i) for i in range(item.childCount())]
            child_matches = [visit(child) for child in children if child is not None]
            child_match = any(child_matches)
            match = not folded or folded in item.text(0).casefold() or child_match
            item.setHidden(not match)
            if folded and child_match:
                item.setExpanded(True)
            return match

        root = self._tree.invisibleRootItem()
        for index in range(root.childCount()):
            child = root.child(index)
            if child is not None:
                visit(child)

    def _on_item_clicked(self, item: QTreeWidgetItem) -> None:
        if item.childCount():
            item.setExpanded(not item.isExpanded())
            return
        self._path = list(item.data(0, Qt.ItemDataRole.UserRole) or [])
        self.setText(" / ".join(self._path) or self._placeholder)
        self._popup.hide()
        self.leaf_selected.emit(self._path)

    def _show_popup(self) -> None:
        self._popup.setFixedWidth(max(self.width(), 240))
        self._popup.resize(self._popup.width(), 280)
        self._popup.move(self.mapToGlobal(QPoint(0, self.height() + 2)))
        self._popup.show()
        self._filter.setFocus()


class _HighlightDelegate(QStyledItemDelegate):
    """Paint item HTML (bold matched fragment) on top of the normal item chrome."""

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Draw the row background, then the rich text."""
        html = index.data(_HTML_ROLE)
        if not isinstance(html, str):
            super().paint(painter, option, index)
            return
        view_option = QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)
        view_option.text = ""
        widget = option.widget  # type: ignore[attr-defined]
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, view_option, painter, widget)
        document = QTextDocument()
        document.setDefaultFont(option.font)  # type: ignore[attr-defined]
        document.setHtml(html)
        rect = option.rect  # type: ignore[attr-defined]
        painter.save()
        top = rect.top() + (rect.height() - document.size().height()) / 2
        painter.translate(rect.left() + SPACE_S, top)
        document.drawContents(painter)
        painter.restore()


def _star_path(rect: QRectF) -> QPainterPath:
    center = rect.center()
    outer = rect.width() / 2
    inner = outer * 0.45
    path = QPainterPath()
    for point in range(10):
        radius = outer if point % 2 == 0 else inner
        angle = math.pi / 5 * point - math.pi / 2
        position = QPointF(center.x() + radius * math.cos(angle), center.y() + radius * math.sin(angle))
        if point == 0:
            path.moveTo(position)
        else:
            path.lineTo(position)
    path.closeSubpath()
    return path


_HTML_ROLE = Qt.ItemDataRole.UserRole + 1
