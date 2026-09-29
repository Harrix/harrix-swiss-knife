"""Paint-like text settings bar for the screenshot preview."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon
from harrix_swiss_knife.screenshot.font_preview import FontPreviewDelegate, load_font_preview_text
from harrix_swiss_knife.screenshot.text_style import (
    ScreenshotTextSettings,
    available_text_font_families,
    font_size_choices,
)
from harrix_swiss_knife.screenshot.toolbar_style import TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_STYLE, TOOLBAR_ICON_SIZE

if TYPE_CHECKING:
    from PySide6.QtGui import QColor

    from harrix_swiss_knife.screenshot.text_style import TextAlign

_MIN_FONT_SIZE = 6.0
_MAX_FONT_SIZE = 200.0
_STYLE_BUTTONS: tuple[tuple[str, str, str], ...] = (
    ("bold", "B", "Bold"),
    ("italic", "I", "Italic"),
    ("underline", "U", "Underline"),
    ("strikeout", "S", "Strikethrough"),
)
_ALIGN_BUTTONS: tuple[tuple[str, str, str], ...] = (
    ("left", "align-left", "Align left"),
    ("center", "align-center", "Align center"),
    ("right", "align-right", "Align right"),
)


class ScreenshotTextToolbar(QWidget):
    """Compact font / style strip shown while the text tool is active."""

    settings_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build combos and toggles; call `set_settings` before showing."""
        super().__init__(parent)
        self._updating = False
        self._settings = ScreenshotTextSettings()
        self._preview_text = load_font_preview_text()
        self.setObjectName("hskScreenshotTextToolbar")
        self.setStyleSheet(
            "#hskScreenshotTextToolbar {  background: #f7f7f8;  border: 1px solid #d0d0d4;  border-radius: 10px;}"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(8)

        self._family = QComboBox(self)
        self._family.setEditable(True)
        self._family.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._family.setMinimumWidth(120)
        self._family.setMaximumWidth(180)
        self._family.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        family_completer = self._family.completer()
        if family_completer is not None:
            family_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            family_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            family_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        family_line = self._family.lineEdit()
        if family_line is not None:
            family_line.setPlaceholderText("Font")
            family_line.setClearButtonEnabled(True)
        self._family.currentTextChanged.connect(self._on_family_changed)
        self._family.setItemDelegate(FontPreviewDelegate(self._preview_text, self._family))
        view = self._family.view()
        if view is not None:
            view.setMinimumWidth(380)
            view.setUniformItemSizes(True)
        row.addWidget(self._family)

        self._cyrillic_only = QCheckBox("Cyrillic", self)
        self._cyrillic_only.setToolTip("Show only fonts that support Cyrillic")
        self._cyrillic_only.toggled.connect(self._on_cyrillic_toggled)
        row.addWidget(self._cyrillic_only)

        self._size = QComboBox(self)
        self._size.setEditable(True)
        self._size.setMinimumWidth(64)
        for size in font_size_choices():
            self._size.addItem(str(int(size) if size == int(size) else size))
        self._size.currentTextChanged.connect(self._on_size_changed)
        row.addWidget(self._size)

        row.addWidget(_vsep(self))

        self._style_buttons: dict[str, QToolButton] = {}
        for key, label, tip in _STYLE_BUTTONS:
            button = QToolButton(self)
            button.setText(label)
            button.setCheckable(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.toggled.connect(lambda checked, k=key: self._on_style_toggled(k, checked=checked))
            self._style_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._align_buttons: dict[str, QToolButton] = {}
        for key, icon_name, tip in _ALIGN_BUTTONS:
            button = QToolButton(self)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.setIcon(create_lucide_icon(icon_name, size=TOOLBAR_ICON_SIZE))
            button.toggled.connect(lambda checked, k=key: self._on_align_toggled(k, checked=checked))
            self._align_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._bg_fill = QCheckBox("Background fill", self)
        self._bg_fill.toggled.connect(self._on_bg_toggled)
        row.addWidget(self._bg_fill)
        row.addStretch(1)
        self._refill_family_combo(keep_family=self._settings.font_family)

    def set_color(self, color: QColor) -> None:
        """Update the text color stored in settings (from the main color picker)."""
        if not color.isValid():
            return
        self._settings.color = color.name()
        self._emit()

    def set_settings(self, settings: ScreenshotTextSettings) -> None:
        """Load `settings` into the controls without emitting."""
        self._updating = True
        self._settings = ScreenshotTextSettings(
            font_family=settings.font_family,
            font_size=settings.font_size,
            bold=settings.bold,
            italic=settings.italic,
            underline=settings.underline,
            strikeout=settings.strikeout,
            align=settings.align,
            background_fill=settings.background_fill,
            color=settings.color,
            cyrillic_fonts_only=settings.cyrillic_fonts_only,
        )
        self._cyrillic_only.setChecked(settings.cyrillic_fonts_only)
        self._refill_family_combo(keep_family=settings.font_family)
        size_value = settings.font_size
        size_text = str(int(size_value) if size_value == int(size_value) else size_value)
        size_index = self._size.findText(size_text)
        if size_index >= 0:
            self._size.setCurrentIndex(size_index)
        else:
            self._size.setEditText(size_text)
        self._style_buttons["bold"].setChecked(settings.bold)
        self._style_buttons["italic"].setChecked(settings.italic)
        self._style_buttons["underline"].setChecked(settings.underline)
        self._style_buttons["strikeout"].setChecked(settings.strikeout)
        for key, button in self._align_buttons.items():
            button.setChecked(key == settings.align)
        self._bg_fill.setChecked(settings.background_fill)
        self._updating = False

    def settings(self) -> ScreenshotTextSettings:
        """Return the current toolbar settings."""
        return self._settings

    def _emit(self) -> None:
        if self._updating:
            return
        self.settings_changed.emit(self._settings)

    def _on_align_toggled(self, key: str, *, checked: bool) -> None:
        if self._updating or not checked:
            return
        align: TextAlign = key if key in {"left", "center", "right"} else "left"
        self._settings.align = align
        self._emit()

    def _on_bg_toggled(self, checked: bool) -> None:  # noqa: FBT001
        if self._updating:
            return
        self._settings.background_fill = checked
        self._emit()

    def _on_cyrillic_toggled(self, checked: bool) -> None:  # noqa: FBT001
        if self._updating:
            return
        self._settings.cyrillic_fonts_only = checked
        self._refill_family_combo(keep_family=self._settings.font_family)
        self._emit()

    def _on_family_changed(self, family: str) -> None:
        if self._updating:
            return
        self._settings.font_family = family.strip()
        self._emit()

    def _on_size_changed(self, text: str) -> None:
        if self._updating:
            return
        try:
            size = float(text.replace(",", ".").strip())
        except ValueError:
            return
        if size < _MIN_FONT_SIZE or size > _MAX_FONT_SIZE:
            return
        self._settings.font_size = size
        self._emit()

    def _on_style_toggled(self, key: str, *, checked: bool) -> None:
        if self._updating:
            return
        if key == "bold":
            self._settings.bold = checked
        elif key == "italic":
            self._settings.italic = checked
        elif key == "underline":
            self._settings.underline = checked
        elif key == "strikeout":
            self._settings.strikeout = checked
        self._emit()

    def _refill_family_combo(self, *, keep_family: str) -> None:
        """Rebuild the font list; keep `keep_family` selected when possible."""
        was_updating = self._updating
        self._updating = True
        preview_text = load_font_preview_text()
        if preview_text != self._preview_text:
            self._preview_text = preview_text
            self._family.setItemDelegate(FontPreviewDelegate(preview_text, self._family))
        current = keep_family.strip()
        self._family.clear()
        for name in available_text_font_families(cyrillic_only=self._settings.cyrillic_fonts_only):
            self._family.addItem(name)
        index = self._family.findText(current)
        if index < 0 and current:
            self._family.addItem(current)
            index = self._family.findText(current)
        if index >= 0:
            self._family.setCurrentIndex(index)
        elif self._family.count() > 0:
            self._family.setCurrentIndex(0)
            current = self._family.currentText().strip()
            self._settings.font_family = current
        self._updating = was_updating


def _vsep(parent: QWidget) -> QLabel:
    sep = QLabel("|", parent)
    sep.setStyleSheet("color: #c4c4c8; padding: 0 2px;")
    sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return sep
