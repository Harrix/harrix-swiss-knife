"""Accept both comma and period as the decimal separator in `QDoubleSpinBox`."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QLineEdit

_ALT_SEPARATORS = {",": ".", ".": ","}


class FlexibleDecimalSpinFilter(QObject):
    """Map `,`/`.` keys and pasted text to the spin box locale decimal point."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Rewrite decimal keys and normalize pasted numbers in double spin boxes."""
        spin = double_spinbox_from_widget(watched)
        if spin is None:
            return False

        self._ensure_line_edit_hook(spin)
        decimal = spinbox_decimal_point(spin)
        other = _ALT_SEPARATORS.get(decimal)
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False

        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            line = spin.lineEdit()
            if clipboard is not None and line is not None:
                line.insert(normalize_decimal_text(clipboard.text(), decimal))
                return True

        if other is not None and event.text() == other:
            key = Qt.Key.Key_Period if decimal == "." else Qt.Key.Key_Comma
            replacement = QKeyEvent(QEvent.Type.KeyPress, key, event.modifiers(), decimal)
            QApplication.sendEvent(watched, replacement)
            return True

        return False

    def _ensure_line_edit_hook(self, spin: QDoubleSpinBox) -> None:
        line = spin.lineEdit()
        if line is None or line.property("_hskFlexibleDecimal") == "1":
            return
        line.setProperty("_hskFlexibleDecimal", "1")
        line.textChanged.connect(lambda text, editor=line, box=spin: _normalize_spin_line(editor, box, text))


def double_spinbox_from_widget(widget: QObject | None) -> QDoubleSpinBox | None:
    """Return the `QDoubleSpinBox` that owns `widget`, if any."""
    current: QObject | None = widget
    while current is not None:
        if isinstance(current, QDoubleSpinBox):
            return current
        current = current.parent()
    return None


def install_flexible_decimal_separators(app: QApplication) -> None:
    """Install an application-wide filter so every `QDoubleSpinBox` accepts `,` and `.`."""
    if not isinstance(app, QApplication):
        return
    existing = app.property("_hskFlexibleDecimalFilter")
    if isinstance(existing, FlexibleDecimalSpinFilter):
        return
    event_filter = FlexibleDecimalSpinFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty("_hskFlexibleDecimalFilter", event_filter)


def normalize_decimal_text(text: str, decimal_point: str) -> str:
    """Replace the other separator with `decimal_point` when it is the only one used."""
    other = _ALT_SEPARATORS.get(decimal_point)
    if other is None or other not in text or decimal_point in text:
        return text
    return text.replace(other, decimal_point)


def spinbox_decimal_point(spin: QDoubleSpinBox) -> str:
    """Return the locale decimal-point character for `spin`."""
    point = spin.locale().decimalPoint()
    return point if isinstance(point, str) and point else "."


def _normalize_spin_line(line: QLineEdit, spin: QDoubleSpinBox, text: str) -> None:
    normalized = normalize_decimal_text(text, spinbox_decimal_point(spin))
    if normalized == text:
        return
    cursor = line.cursorPosition()
    line.setText(normalized)
    line.setCursorPosition(min(cursor, len(normalized)))
