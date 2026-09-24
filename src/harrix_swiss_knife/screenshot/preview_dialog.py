"""Non-modal screenshot preview window with tabs and annotation tools."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import TYPE_CHECKING, Literal

import harrix_pylib as h
from PySide6.QtCore import QSize, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QColor, QIcon, QImage, QKeyEvent, QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from harrix_swiss_knife.actions.common.raster_optimize import process_png_to_avif
from harrix_swiss_knife.actions.common.text_result_dialog import (
    CANCEL_BUTTON_LABEL,
    COPY_BUTTON_LABEL,
    OK_BUTTON_LABEL,
)
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.qt_flow_layout import FlowLayout
from harrix_swiss_knife.qt_lucide_icon import (
    AI_BUTTON_ICON,
    AI_BUTTON_ICON_COLOR,
    CANCEL_BUTTON_ICON,
    COPY_BUTTON_ICON,
    DEFAULT_LUCIDE_MENU_ICON_SIZE,
    OK_BUTTON_ICON,
    SAVE_BUTTON_ICON,
    create_lucide_icon,
    create_tabler_icon,
    make_lucide_push_button,
)
from harrix_swiss_knife.screenshot.annotation_colors import load_annotation_colors
from harrix_swiss_knife.screenshot.annotations import AnnotationDocument, AnnotationTool
from harrix_swiss_knife.screenshot.dated_image_path import images_folder, next_dated_image_path
from harrix_swiss_knife.screenshot.preview_canvas import ScreenshotPreviewCanvas
from harrix_swiss_knife.screenshot.text_style import (
    ScreenshotTextSettings,
    annotation_style_to_settings,
    load_screenshot_text_settings,
    save_screenshot_text_settings,
    settings_to_annotation_style,
)
from harrix_swiss_knife.screenshot.text_toolbar import ScreenshotTextToolbar
from harrix_swiss_knife.screenshot.toolbar_style import (
    TOOLBAR_BUTTON_GAP,
    TOOLBAR_BUTTON_SIZE,
    TOOLBAR_BUTTON_STYLE,
    TOOLBAR_ICON_SIZE,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QResizeEvent
    from PySide6.QtWidgets import QPushButton

_SAVE_BUTTON_ICON = SAVE_BUTTON_ICON
_SAVE_BUTTON_LABEL = "Save as…"
_SAVE_DESKTOP_BUTTON_ICON = "monitor"
_SAVE_DESKTOP_BUTTON_LABEL = "Save to desktop"
_SAVE_ALL_DESKTOP_BUTTON_ICON = "images"
_SAVE_ALL_DESKTOP_BUTTON_LABEL = "Save all to desktop"
_ScreenshotFormat = Literal["png", "jpeg", "avif_hq", "avif_optimized"]
_SAVE_FORMATS: tuple[tuple[_ScreenshotFormat, str, str], ...] = (
    ("png", "PNG", "PNG Image (*.png)"),
    ("jpeg", "JPEG", "JPEG Image (*.jpg *.jpeg)"),
    ("avif_hq", "AVIF high quality", "AVIF Image (*.avif)"),
    ("avif_optimized", "AVIF optimized", "AVIF Image (*.avif)"),
)
_FORMAT_ICONS: dict[_ScreenshotFormat, str] = {
    "png": "file-type-png",
    "jpeg": "file-type-jpg",
    "avif_hq": "file-type-avif",
    "avif_optimized": "file-type-avif",
}
_JPEG_QUALITY = 95
_JPEG_SUFFIXES = frozenset({".jpg", ".jpeg"})
_RECOGNIZE_BUTTON_LABEL = "Recognize…"
_RECOGNIZE_BUTTON_ICON = "scan-text"
_REDUCE_BUTTON_LABEL = "Reduce size…"
_REDUCE_BUTTON_ICON = "shrink"
_REDUCE_MAX_SIDE = 1024
_MARKDOWN_AI_ICON = AI_BUTTON_ICON
_MARKDOWN_OCR_ICON = "scan-text"
_TABLE_AI_ICON = "table"
_TRANSLATE_ICON = "languages"
_STATUS_HINT = (
    "Tools: arrow / shapes / pen / text / eyedropper / crop · Click a shape to select · "
    "Delete removes · Shift constrains · Undo · Ctrl+wheel zoom · Middle-drag pan · Ctrl+S save to images"
)
_VK_S = 0x53
_KEY_CYRILLIC_YERU = 0x042B  # Cyrillic yeru (same physical key as Latin S)  # ignore: HP001
_MIN_WINDOW_WIDTH = 480
_MIN_WINDOW_HEIGHT = 360
_DEFAULT_TITLE = "Screenshot"
_DEFAULT_ANNOTATION_COLOR = QColor("#de2b26")

_TOOL_BUTTONS: tuple[tuple[AnnotationTool, str, str], ...] = (
    (AnnotationTool.NONE, "mouse-pointer-2", "Select / view"),
    (AnnotationTool.ARROW, "arrow-right", "Arrow (Shift: 0° / 45°)"),
    (AnnotationTool.RECTANGLE, "square", "Rectangle (Shift: square)"),
    (AnnotationTool.ELLIPSE, "circle", "Ellipse (Shift: circle)"),
    (AnnotationTool.LINE, "minus", "Line (Shift: 0° / 45°)"),
    (AnnotationTool.PEN, "pencil", "Pen"),
    (AnnotationTool.TEXT, "type", "Text"),
    (AnnotationTool.EYEDROPPER, "pipette", "Eyedropper — click a pixel to copy its color"),
    (AnnotationTool.CROP, "crop", "Crop"),
)

_preview_holder: dict[str, ScreenshotPreviewWindow | None] = {"window": None}


class ScreenshotPreviewWindow(QMainWindow):
    """Normal (non-modal) window that hosts one or more screenshot tabs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build an empty preview window; call `add_image` before showing."""
        super().__init__(parent)
        self.setWindowTitle(_DEFAULT_TITLE)
        self.setMinimumSize(_MIN_WINDOW_WIDTH, _MIN_WINDOW_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self._text_settings = load_screenshot_text_settings()
        color = QColor(self._text_settings.color)
        self._annotation_color = color if color.isValid() else QColor(_DEFAULT_ANNOTATION_COLOR)
        self._tool_buttons: dict[AnnotationTool, QToolButton] = {}

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        tools_host = QWidget(central)
        tools_layout = FlowLayout(
            tools_host,
            margin=0,
            h_spacing=TOOLBAR_BUTTON_GAP,
            v_spacing=TOOLBAR_BUTTON_GAP,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )
        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        icon_size = QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE)
        eyedropper_button: QToolButton | None = None
        for tool, icon_name, tip in _TOOL_BUTTONS:
            button = QToolButton(tools_host)
            button.setIcon(create_lucide_icon(icon_name, TOOLBAR_ICON_SIZE))
            button.setIconSize(icon_size)
            button.setToolTip(tip)
            button.setCheckable(True)
            button.setAutoRaise(False)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            if tool == AnnotationTool.NONE:
                button.setChecked(True)
            self._tool_group.addButton(button)
            self._tool_buttons[tool] = button
            button.clicked.connect(lambda _checked=False, t=tool: self._set_tool(t))
            if tool == AnnotationTool.EYEDROPPER:
                eyedropper_button = button
                continue
            tools_layout.addWidget(button)

        undo_button = QToolButton(tools_host)
        undo_button.setIcon(create_lucide_icon("undo-2", TOOLBAR_ICON_SIZE))
        undo_button.setIconSize(icon_size)
        undo_button.setToolTip("Undo")
        undo_button.setAutoRaise(False)
        undo_button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        undo_button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
        undo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        undo_button.clicked.connect(self._undo)
        tools_layout.addWidget(undo_button)

        self._color_button = QToolButton(tools_host)
        self._color_button.setToolTip("Stroke color")
        self._color_button.setAutoRaise(False)
        self._color_button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        self._color_button.setIconSize(icon_size)
        self._color_button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
        self._color_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._color_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._color_menu = QMenu(self._color_button)
        self._color_button.setMenu(self._color_menu)
        self._rebuild_color_menu()
        self._update_color_button()
        tools_layout.addWidget(self._color_button)
        if eyedropper_button is not None:
            tools_layout.addWidget(eyedropper_button)

        self._tools_host = tools_host
        self._tools_layout = tools_layout
        root.addWidget(tools_host)

        text_bar_host = QWidget(central)
        text_bar_row = QHBoxLayout(text_bar_host)
        text_bar_row.setContentsMargins(0, 0, 0, 0)
        text_bar_row.addStretch(1)
        self._text_toolbar = ScreenshotTextToolbar(text_bar_host)
        self._text_toolbar.set_settings(self._text_settings)
        self._text_toolbar.settings_changed.connect(self._on_text_settings_changed)
        text_bar_row.addWidget(self._text_toolbar, 0, Qt.AlignmentFlag.AlignHCenter)
        text_bar_row.addStretch(1)
        self._text_bar_host = text_bar_host
        text_bar_host.hide()
        root.addWidget(text_bar_host)

        self._tabs = QTabWidget(central)
        self._tabs.setTabsClosable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self._close_tab_at)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self._tabs, stretch=1)

        footer = QVBoxLayout()
        footer.setSpacing(8)

        buttons_host = QWidget(central)
        self._buttons = FlowLayout(
            buttons_host,
            h_spacing=6,
            v_spacing=6,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        self._action_buttons: list[QPushButton] = []
        self._add_footer_button(
            make_lucide_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_ICON),
            self._copy_to_clipboard,
        )
        self._add_save_menu_button(
            _SAVE_DESKTOP_BUTTON_LABEL,
            _SAVE_DESKTOP_BUTTON_ICON,
            "Save as YYYY-MM-DD_NN in Desktop/Screenshots. Choose PNG, JPEG, or AVIF.",
            self._save_to_desktop,
        )
        self._save_all_desktop_button = self._add_save_menu_button(
            _SAVE_ALL_DESKTOP_BUTTON_LABEL,
            _SAVE_ALL_DESKTOP_BUTTON_ICON,
            "Save every tab as YYYY-MM-DD_NN in Desktop/Screenshots. Choose PNG, JPEG, or AVIF.",
            self._save_all_to_desktop,
        )
        self._save_all_desktop_button.hide()
        self._add_save_menu_button(
            _SAVE_BUTTON_LABEL,
            _SAVE_BUTTON_ICON,
            "Choose a format, then pick where to save the screenshot.",
            self._save_as,
        )
        self._add_recognize_menu_button()
        self._add_reduce_size_menu_button()
        self._add_footer_button(
            make_lucide_push_button(OK_BUTTON_LABEL, OK_BUTTON_ICON),
            self._close_current_tab,
        )
        self._buttons_host = buttons_host
        footer.addWidget(buttons_host)

        self._crop_bar = QWidget(central)
        crop_row = QHBoxLayout(self._crop_bar)
        crop_row.setContentsMargins(0, 0, 0, 0)
        crop_row.addStretch(1)
        self._crop_ok_button = make_lucide_push_button(OK_BUTTON_LABEL, OK_BUTTON_ICON)
        self._crop_ok_button.setToolTip("Apply crop (Enter)")
        self._crop_ok_button.setEnabled(False)
        self._crop_ok_button.clicked.connect(self._confirm_crop)
        crop_row.addWidget(self._crop_ok_button)
        self._crop_cancel_button = make_lucide_push_button(CANCEL_BUTTON_LABEL, CANCEL_BUTTON_ICON)
        self._crop_cancel_button.setToolTip("Cancel crop (Esc)")
        self._crop_cancel_button.clicked.connect(self._cancel_crop)
        crop_row.addWidget(self._crop_cancel_button)
        crop_row.addStretch(1)
        self._crop_bar.hide()
        footer.addWidget(self._crop_bar)

        self._status = QLabel(central)
        self._status.setWordWrap(True)
        self._status.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._status.setText(_STATUS_HINT)
        footer.addWidget(self._status)
        root.addLayout(footer)

        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        save_shortcut.activated.connect(self._save_to_images)
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        undo_shortcut.activated.connect(self._undo)
        apply_app_window_size_and_position(self)
        QTimer.singleShot(0, self._refit_tools_host)

    def add_image(self, image: QImage) -> None:
        """Append a new tab for `image` and select it."""
        tab = _ScreenshotTab(image, self._tabs)
        tab.canvas.document_changed.connect(self._on_document_changed)
        tab.canvas.crop_mode_changed.connect(self._on_crop_mode_changed)
        tab.canvas.crop_pending_changed.connect(self._on_crop_pending_changed)
        tab.canvas.color_hovered.connect(self._on_color_hovered)
        tab.canvas.color_picked.connect(self._on_color_picked)
        tab.canvas.text_editing_changed.connect(self._on_text_editing_changed)
        tab.canvas.set_style(style=settings_to_annotation_style(self._text_settings))
        tab.canvas.set_style(color=self._annotation_color)
        index = self._tabs.addTab(tab, self._tab_label(None, self._tabs.count() + 1))
        self._tabs.setCurrentIndex(index)
        self._apply_tool_to_current()
        self._update_window_title()
        self._update_multi_tab_chrome()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Clear the process-wide preview reference when the window closes."""
        if _preview_holder["window"] is self:
            _preview_holder["window"] = None
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Save on Ctrl+S; Delete selected; Enter/Esc for crop."""  # ignore: HP001
        tab = self._current_tab()
        if tab is not None and tab.canvas.crop_mode:
            if event.key() in {int(Qt.Key.Key_Return), int(Qt.Key.Key_Enter)} and tab.canvas.crop_pending:
                self._confirm_crop()
                event.accept()
                return
            if event.key() == int(Qt.Key.Key_Escape):
                self._cancel_crop()
                event.accept()
                return
        if tab is not None and tab.canvas.tool == AnnotationTool.EYEDROPPER and event.key() == int(Qt.Key.Key_Escape):
            self._set_tool(AnnotationTool.NONE)
            event.accept()
            return
        if (
            tab is not None
            and event.key() in {int(Qt.Key.Key_Delete), int(Qt.Key.Key_Backspace)}
            and tab.canvas.delete_selected()
        ):
            self._status.setText("Annotation deleted · Ctrl+Z undo")
            event.accept()
            return
        if tab is not None and event.key() == int(Qt.Key.Key_Escape) and tab.canvas.clear_selection():
            event.accept()
            return
        if _is_ctrl_s(event):
            self._save_to_images()
            event.accept()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reflow the top tool row when the window width changes."""
        super().resizeEvent(event)
        self._refit_tools_host()

    def _add_footer_button(self, button: QPushButton, slot: Callable[[], None]) -> None:
        button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        button.clicked.connect(slot)
        self._buttons.addWidget(button)
        self._action_buttons.append(button)

    def _add_recognize_menu_button(self) -> None:
        """Add a footer button whose click opens text and table recognition."""
        button = make_lucide_push_button(_RECOGNIZE_BUTTON_LABEL, _RECOGNIZE_BUTTON_ICON)
        button.setToolTip("Recognize text or a table. Choose AI, local OCR, or OCR with translation.")
        menu = QMenu(button)
        items: tuple[tuple[str, str, str | None, Callable[[], None]], ...] = (
            ("Recognize text (AI)", _MARKDOWN_AI_ICON, AI_BUTTON_ICON_COLOR, self._run_markdown_with_ai),
            ("Recognize table (AI)", _TABLE_AI_ICON, AI_BUTTON_ICON_COLOR, self._run_table_with_ai),
            ("Recognize text (OCR)", _MARKDOWN_OCR_ICON, None, self._run_markdown_with_ocr),
            ("OCR + translate", _TRANSLATE_ICON, None, self._run_ocr_translate),
        )
        for title, icon_name, color, slot in items:
            action = menu.addAction(title)
            action.setIcon(create_lucide_icon(icon_name, DEFAULT_LUCIDE_MENU_ICON_SIZE, color=color))
            action.triggered.connect(lambda _checked=False, chosen=slot: chosen())
        button.setMenu(menu)
        button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._buttons.addWidget(button)
        self._action_buttons.append(button)

    def _add_reduce_size_menu_button(self) -> None:
        """Add a footer button whose click opens screenshot size reduction."""
        button = make_lucide_push_button(_REDUCE_BUTTON_LABEL, _REDUCE_BUTTON_ICON)
        button.setToolTip("Reduce the screenshot pixel size. Choose half, 1024 px, or a custom size.")
        menu = QMenu(button)
        items: tuple[tuple[str, str, Callable[[], None]], ...] = (
            ("Half size", "shrink", self._resize_half),
            ("Max 1024 px", "scaling", self._resize_max_side),
            ("Custom size…", "proportions", self._resize_custom),
        )
        for title, icon_name, slot in items:
            action = menu.addAction(title)
            action.setIcon(create_lucide_icon(icon_name, DEFAULT_LUCIDE_MENU_ICON_SIZE))
            action.triggered.connect(lambda _checked=False, chosen=slot: chosen())
        button.setMenu(menu)
        button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._buttons.addWidget(button)
        self._action_buttons.append(button)

    def _add_save_menu_button(
        self,
        label: str,
        icon_name: str,
        tooltip: str,
        slot: Callable[[_ScreenshotFormat], None],
    ) -> QPushButton:
        """Add a footer button whose click opens the screenshot format menu."""
        button = make_lucide_push_button(label, icon_name)
        button.setToolTip(tooltip)
        menu = QMenu(button)
        for fmt, title, _file_filter in _SAVE_FORMATS:
            action = menu.addAction(title)
            action.setIcon(create_tabler_icon(_FORMAT_ICONS[fmt]))
            action.triggered.connect(lambda _checked=False, chosen=fmt: slot(chosen))
        button.setMenu(menu)
        button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._buttons.addWidget(button)
        self._action_buttons.append(button)
        return button

    def _apply_pixel_resize(self, width: int, height: int) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        tab.canvas.commit_text_edit()
        if not tab.document.apply_resize(width, height):
            self._status.setText("Size unchanged")
            return
        tab.canvas.set_document(tab.document)
        tab.canvas.reset_to_original_size()
        image = tab.document.base_image
        self._status.setText(f"Reduced to {image.width()} x {image.height()}")

    def _apply_tool_to_current(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        checked = self._tool_group.checkedButton()
        tool = AnnotationTool.NONE
        for candidate, button in self._tool_buttons.items():
            if button is checked:
                tool = candidate
                break
        tab.canvas.set_style(style=settings_to_annotation_style(self._text_settings))
        tab.canvas.set_style(color=self._annotation_color)
        tab.canvas.set_tool(tool)

    def _cancel_crop(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        tab.canvas.cancel_crop()
        select = self._tool_buttons.get(AnnotationTool.NONE)
        if select is not None:
            select.setChecked(True)
        self._status.setText("Crop cancelled")

    def _close_current_tab(self) -> None:
        index = self._tabs.currentIndex()
        if index >= 0:
            self._close_tab_at(index)

    def _close_tab_at(self, index: int) -> None:
        widget = self._tabs.widget(index)
        self._tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()
        if self._tabs.count() == 0:
            self.close()
            return
        self._update_multi_tab_chrome()
        self._relabel_untitled_tabs()
        self._update_window_title()

    def _confirm_crop(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        ok = tab.canvas.confirm_crop()
        select = self._tool_buttons.get(AnnotationTool.NONE)
        if select is not None:
            select.setChecked(True)
        self._status.setText("Crop applied" if ok else "Crop cancelled")

    def _copy_to_clipboard(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(tab.image)
            self._status.setText("Copied to clipboard")

    def _current_tab(self) -> _ScreenshotTab | None:
        widget = self._tabs.currentWidget()
        return widget if isinstance(widget, _ScreenshotTab) else None

    def _desktop_folder(self) -> Path | None:
        desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        if not desktop:
            self._status.setText("Desktop folder not found")
            return None
        return Path(desktop) / "Screenshots"

    def _on_color_hovered(self, color: object) -> None:
        tab = self._current_tab()
        if tab is None or tab.canvas.tool != AnnotationTool.EYEDROPPER:
            return
        if not isinstance(color, QColor) or not color.isValid():
            self._status.setText("Eyedropper: move over the screenshot · click to copy and use as stroke")
            return
        self._status.setText(f"{_format_pixel_color(color)} · click to copy and use as stroke")

    def _on_color_picked(self, color: QColor) -> None:
        if not color.isValid():
            return
        self._set_annotation_color(color)
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(color.name())
        self._status.setText(f"Picked {_format_pixel_color(color)} · copied · set as stroke")

    def _on_crop_mode_changed(self, active: bool) -> None:  # noqa: FBT001
        self._set_crop_chrome_visible(active=active)
        if active:
            tab = self._current_tab()
            pending = tab is not None and tab.canvas.crop_pending
            self._crop_ok_button.setEnabled(pending)
            if pending:
                self._status.setText("Crop: move/resize the frame · Enter to apply · Esc to cancel")
            else:
                self._status.setText("Crop: drag a region · snap to edges · Enter OK · Esc Cancel")
        else:
            self._status.setText(_STATUS_HINT)
            self._refit_tools_host()

    def _on_crop_pending_changed(self, pending: bool) -> None:  # noqa: FBT001
        self._crop_ok_button.setEnabled(pending)
        if pending:
            self._status.setText("Crop: move/resize the frame · Enter to apply · Esc to cancel")

    def _on_document_changed(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        count = len(tab.document.annotations)
        self._status.setText(f"Annotations: {count} · Click to select · Delete removes · Ctrl+Z undo")

    def _on_tab_changed(self, _index: int) -> None:
        tab = self._current_tab()
        if tab is not None and tab.canvas.crop_mode:
            crop_button = self._tool_buttons.get(AnnotationTool.CROP)
            if crop_button is not None:
                crop_button.setChecked(True)
            self._set_crop_chrome_visible(active=True)
            self._crop_ok_button.setEnabled(tab.canvas.crop_pending)
        else:
            self._set_crop_chrome_visible(active=False)
            self._apply_tool_to_current()
            self._refit_tools_host()
        self._update_window_title()

    def _on_text_editing_changed(self, active: bool) -> None:  # noqa: FBT001
        tab = self._current_tab()
        if tab is None or not active:
            return
        settings = annotation_style_to_settings(tab.canvas.annotation_style)
        self._text_settings = settings
        self._text_toolbar.set_settings(settings)
        color = QColor(settings.color)
        if color.isValid():
            self._annotation_color = color
            self._update_color_button()

    def _on_text_settings_changed(self, settings: object) -> None:
        if not isinstance(settings, ScreenshotTextSettings):
            return
        self._text_settings = settings
        color = QColor(settings.color)
        if color.isValid():
            self._annotation_color = color
            self._update_color_button()
        save_screenshot_text_settings(settings)
        tab = self._current_tab()
        if tab is not None:
            tab.canvas.set_style(style=settings_to_annotation_style(settings))

    def _rebuild_color_menu(self) -> None:
        self._color_menu.clear()
        for hex_value, hint in load_annotation_colors():
            color = QColor(hex_value)
            if not color.isValid():
                continue
            label = f"{hex_value} — {hint}" if hint else hex_value
            action = self._color_menu.addAction(_color_swatch_icon(color, TOOLBAR_ICON_SIZE), label)
            action.triggered.connect(lambda _checked=False, c=color: self._set_annotation_color(c))

    def _refit_tools_host(self) -> None:
        """Size the top tool strip so FlowLayout can wrap on narrow Windows."""
        width = max(TOOLBAR_BUTTON_SIZE, self._tools_host.width())
        height = max(TOOLBAR_BUTTON_SIZE, self._tools_layout.heightForWidth(width))
        self._tools_host.setMinimumHeight(height)
        self._tools_host.updateGeometry()

    def _relabel_untitled_tabs(self) -> None:
        for index in range(self._tabs.count()):
            tab = self._tabs.widget(index)
            if not isinstance(tab, _ScreenshotTab) or tab.saved_name:
                continue
            self._tabs.setTabText(index, self._tab_label(None, index + 1))

    def _resize_custom(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        image = tab.document.base_image
        dialog = _ReduceSizeDialog(image.width(), image.height(), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        width, height = dialog.size_pixels()
        self._apply_pixel_resize(width, height)

    def _resize_half(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        image = tab.document.base_image
        target = _half_pixel_size(image.width(), image.height())
        if target is None:
            self._status.setText("Size unchanged")
            return
        self._apply_pixel_resize(*target)

    def _resize_max_side(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        image = tab.document.base_image
        target = _max_side_pixel_size(image.width(), image.height(), _REDUCE_MAX_SIDE)
        if target is None:
            self._status.setText("Already within 1024 px")
            return
        self._apply_pixel_resize(*target)

    def _run_markdown_with_ai(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self._close_current_tab()

        def run() -> None:
            from harrix_swiss_knife.actions.images.recognize_text_with_ai import (  # noqa: PLC0415
                OnRecognizeTextWithAI,
            )

            OnRecognizeTextWithAI()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _run_markdown_with_ocr(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self._close_current_tab()

        def run() -> None:
            from harrix_swiss_knife.actions.images.recognize_text_with_ocr import (  # noqa: PLC0415
                OnRecognizeTextWithOcr,
            )

            OnRecognizeTextWithOcr()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _run_ocr_translate(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        image = tab.image.copy()
        self._close_current_tab()

        def run() -> None:
            from harrix_swiss_knife.actions.images.screenshot_region_translate import (  # noqa: PLC0415
                OnScreenshotRegionTranslate,
            )

            OnScreenshotRegionTranslate()(image=image)

        QTimer.singleShot(0, run)

    def _run_table_with_ai(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self._close_current_tab()

        def run() -> None:
            from harrix_swiss_knife.actions.images.recognize_table_with_ai import (  # noqa: PLC0415
                OnRecognizeTableWithAI,
            )

            OnRecognizeTableWithAI()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _save_all_to_desktop(self, fmt: _ScreenshotFormat = "png") -> None:
        desktop = self._desktop_folder()
        if desktop is None:
            return
        saved_paths: list[Path] = []
        for index in range(self._tabs.count()):
            widget = self._tabs.widget(index)
            if not isinstance(widget, _ScreenshotTab):
                continue
            path = self._save_tab_dated(widget, desktop, tab_index=index, fmt=fmt)
            if path is None:
                return
            saved_paths.append(path)
        if not saved_paths:
            self._status.setText("No screenshots to save")
            return
        self._status.setText(f"Saved {len(saved_paths)} images to {desktop}")
        self._update_window_title()

    def _save_as(self, fmt: _ScreenshotFormat = "png") -> None:
        tab = self._current_tab()
        if tab is None:
            return
        suffix = _format_suffix(fmt)
        if tab.saved_as_path is not None:
            suggested = str(tab.saved_as_path.with_suffix(suffix))
        elif tab.saved_name:
            suggested = str(Path(tab.saved_name).with_suffix(suffix))
        else:
            suggested = f"screenshot{suffix}"
        file_filter = next(item[2] for item in _SAVE_FORMATS if item[0] == fmt)
        path_str, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save screenshot",
            suggested,
            file_filter,
        )
        if not path_str:
            return
        path = Path(path_str)
        if path.suffix.lower() not in _accepted_suffixes(fmt):
            path = path.with_suffix(suffix)
        try:
            _write_screenshot_file(tab.image, path, fmt)
        except (OSError, RuntimeError, ValueError) as exc:
            self._status.setText(str(exc))
            return
        tab.saved_as_path = path.resolve()
        tab.saved_name = path.name
        index = self._tabs.currentIndex()
        self._tabs.setTabText(index, path.name)
        self._status.setText(f"Saved: {path}")
        self._update_window_title()

    def _save_dated(self, folder: Path, fmt: _ScreenshotFormat = "png") -> None:
        tab = self._current_tab()
        if tab is None:
            return
        path = self._save_tab_dated(tab, folder, tab_index=self._tabs.currentIndex(), fmt=fmt)
        if path is None:
            return
        self._status.setText(f"Saved: {path}")
        self._update_window_title()

    def _save_tab_dated(
        self,
        tab: _ScreenshotTab,
        folder: Path,
        *,
        tab_index: int,
        fmt: _ScreenshotFormat = "png",
    ) -> Path | None:
        folder = folder.resolve()
        suffix = _format_suffix(fmt)
        folder_key = f"{folder}|{suffix}"
        existing = tab.saved_paths.get(folder_key)
        if existing is not None and existing.parent.resolve() == folder and existing.suffix.lower() == suffix:
            path = existing
        else:
            path = next_dated_image_path(folder, extension=suffix)
        try:
            _write_screenshot_file(tab.image, path, fmt)
        except (OSError, RuntimeError, ValueError) as exc:
            self._status.setText(str(exc))
            return None
        resolved = path.resolve()
        tab.saved_paths[folder_key] = resolved
        tab.saved_name = resolved.name
        if 0 <= tab_index < self._tabs.count():
            self._tabs.setTabText(tab_index, resolved.name)
        return resolved

    def _save_temp_png(self) -> str | None:
        tab = self._current_tab()
        if tab is None:
            return None
        with NamedTemporaryFile(suffix=".png", delete=False) as handle:
            temp_path = Path(handle.name)
        if tab.image.save(str(temp_path)):
            return str(temp_path)
        return None

    def _save_to_desktop(self, fmt: _ScreenshotFormat = "png") -> None:
        desktop = self._desktop_folder()
        if desktop is None:
            return
        self._save_dated(desktop, fmt)

    def _save_to_images(self) -> None:
        self._save_dated(images_folder(h.dev.get_project_root()))

    def _set_annotation_color(self, color: QColor) -> None:
        if not color.isValid():
            return
        self._annotation_color = QColor(color)
        self._text_settings.color = color.name()
        self._text_toolbar.set_settings(self._text_settings)
        save_screenshot_text_settings(self._text_settings)
        self._update_color_button()
        tab = self._current_tab()
        if tab is not None:
            tab.canvas.set_style(color=self._annotation_color)

    def _set_crop_chrome_visible(self, *, active: bool) -> None:
        """Show only OK/Cancel while cropping; hide the normal tool and action bars."""
        self._tools_host.setVisible(not active)
        self._buttons_host.setVisible(not active)
        self._crop_bar.setVisible(active)
        if active:
            self._text_bar_host.hide()
        multi = self._tabs.count() > 1
        self._tabs.tabBar().setVisible(not active and multi)
        self._save_all_desktop_button.setVisible(not active and multi)

    def _set_tool(self, tool: AnnotationTool) -> None:
        button = self._tool_buttons.get(tool)
        if button is not None:
            button.setChecked(True)
        self._apply_tool_to_current()
        self._text_bar_host.setVisible(tool == AnnotationTool.TEXT)
        tip = next((item[2] for item in _TOOL_BUTTONS if item[0] == tool), tool.value)
        if tool == AnnotationTool.TEXT:
            self._status.setText(
                "Text: click to type on the image · resize the box after commit · "
                "Ctrl+Enter finish · Esc cancel · double-click to re-edit"
            )
        elif tool != AnnotationTool.CROP:
            self._status.setText(f"Tool: {tip}")

    def _tab_label(self, saved_name: str | None, number: int) -> str:
        return saved_name or f"Screenshot {number}"

    def _undo(self) -> None:
        tab = self._current_tab()
        if tab is None or not tab.document.undo():
            self._status.setText("Nothing to undo")
            return
        tab.canvas.set_document(tab.document)
        self._status.setText("Undone")

    def _update_color_button(self) -> None:
        self._color_button.setIcon(_color_swatch_icon(self._annotation_color, TOOLBAR_ICON_SIZE))
        self._color_button.setToolTip(f"Stroke color ({self._annotation_color.name()})")

    def _update_multi_tab_chrome(self) -> None:
        multi = self._tabs.count() > 1
        self._tabs.tabBar().setVisible(multi)
        self._save_all_desktop_button.setVisible(multi)

    def _update_window_title(self) -> None:
        tab = self._current_tab()
        if tab is not None and tab.saved_name:
            self.setWindowTitle(f"{_DEFAULT_TITLE} — {tab.saved_name}")
            return
        self.setWindowTitle(_DEFAULT_TITLE)


class _ReduceSizeDialog(QDialog):
    """Ask for a smaller width and height, keeping the aspect ratio unless unlocked."""

    def __init__(self, width: int, height: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Reduce size")
        self._source_w = max(1, width)
        self._source_h = max(1, height)
        self._ratio = self._source_h / self._source_w
        self._syncing = False

        self._width = QSpinBox(self)
        self._width.setRange(1, self._source_w)
        self._width.setValue(self._source_w)
        self._width.setSuffix(" px")
        self._height = QSpinBox(self)
        self._height.setRange(1, self._source_h)
        self._height.setValue(self._source_h)
        self._height.setSuffix(" px")
        self._lock = QCheckBox("Keep aspect ratio", self)
        self._lock.setChecked(True)

        form = QFormLayout()
        form.addRow("Width", self._width)
        form.addRow("Height", self._height)
        form.addRow(self._lock)

        self._ok = make_lucide_push_button(OK_BUTTON_LABEL, OK_BUTTON_ICON)
        self._ok.setEnabled(False)
        cancel = make_lucide_push_button(CANCEL_BUTTON_LABEL, CANCEL_BUTTON_ICON)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self._ok)
        buttons.addWidget(cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

        self._width.valueChanged.connect(self._on_width_changed)
        self._height.valueChanged.connect(self._on_height_changed)
        self._ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

    def size_pixels(self) -> tuple[int, int]:
        """Chosen width and height in pixels."""
        return self._width.value(), self._height.value()

    def _on_height_changed(self, height: int) -> None:
        if self._lock.isChecked() and self._ratio > 0:
            self._set_paired(self._width, max(1, round(height / self._ratio)))
        self._update_ok()

    def _on_width_changed(self, width: int) -> None:
        if self._lock.isChecked():
            self._set_paired(self._height, max(1, round(width * self._ratio)))
        self._update_ok()

    def _set_paired(self, box: QSpinBox, value: int) -> None:
        if self._syncing:
            return
        self._syncing = True
        box.setValue(min(box.maximum(), max(box.minimum(), value)))
        self._syncing = False

    def _update_ok(self) -> None:
        width, height = self.size_pixels()
        self._ok.setEnabled(width < self._source_w or height < self._source_h)


class _ScreenshotTab(QWidget):
    """One preview tab: canvas plus annotation document."""

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.document = AnnotationDocument(image)
        self.saved_name: str | None = None
        self.saved_as_path: Path | None = None
        self.saved_paths: dict[str, Path] = {}
        self.canvas = ScreenshotPreviewCanvas(image, self)
        self.canvas.set_document(self.document)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    @property
    def image(self) -> QImage:
        """Current image with annotations baked in (for save / copy / OCR)."""
        return self.document.render(include_draft=False)


def show_screenshot_preview(image: QImage) -> ScreenshotPreviewWindow:
    """Show `image` in the shared preview window, adding a tab if it is already open."""
    window = _preview_holder["window"]
    if window is None or not isValid(window):
        window = ScreenshotPreviewWindow()
        _preview_holder["window"] = window
    window.add_image(image)
    window.show()
    window.raise_()
    window.activateWindow()
    return window


def _accepted_suffixes(fmt: _ScreenshotFormat) -> frozenset[str]:
    if fmt == "jpeg":
        return _JPEG_SUFFIXES
    return frozenset({_format_suffix(fmt)})


def _color_swatch_icon(color: QColor, size: int) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setPen(QColor(102, 102, 102))
    painter.setBrush(color)
    margin = 1
    painter.drawRoundedRect(margin, margin, size - margin * 2 - 1, size - margin * 2 - 1, 3, 3)
    painter.end()
    return QIcon(pixmap)


def _format_pixel_color(color: QColor) -> str:
    return f"{color.name()} · rgb({color.red()}, {color.green()}, {color.blue()})"


def _format_suffix(fmt: _ScreenshotFormat) -> str:
    if fmt == "jpeg":
        return ".jpg"
    if fmt in {"avif_hq", "avif_optimized"}:
        return ".avif"
    return ".png"


def _half_pixel_size(width: int, height: int) -> tuple[int, int] | None:
    """Return half the pixel size, or `None` when it cannot get smaller."""
    if width < 1 or height < 1:
        return None
    target = (max(1, width // 2), max(1, height // 2))
    if target == (width, height):
        return None
    return target


def _is_ctrl_s(event: QKeyEvent) -> bool:
    if event.modifiers() & Qt.KeyboardModifier.AltModifier:
        return False
    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
        return False
    if event.nativeVirtualKey() == _VK_S:
        return True
    return event.key() in {int(Qt.Key.Key_S), _KEY_CYRILLIC_YERU}


def _jpeg_image(image: QImage) -> QImage:
    if not image.hasAlphaChannel():
        return image
    flat = QImage(image.size(), QImage.Format.Format_RGB32)
    flat.fill(Qt.GlobalColor.white)
    painter = QPainter(flat)
    painter.drawImage(0, 0, image)
    painter.end()
    return flat


def _max_side_pixel_size(width: int, height: int, max_side: int) -> tuple[int, int] | None:
    """Return a size whose longest side is `max_side`, keeping the aspect ratio."""
    longest = max(width, height)
    if width < 1 or height < 1 or max_side < 1 or longest <= max_side:
        return None
    if width >= height:
        target_w = max_side
        target_h = max(1, round(height * max_side / width))
    else:
        target_h = max_side
        target_w = max(1, round(width * max_side / height))
    if (target_w, target_h) == (width, height):
        return None
    return target_w, target_h


def _write_screenshot_file(image: QImage, path: Path, fmt: _ScreenshotFormat) -> None:
    """Write `image` to `path` as PNG, JPEG, or AVIF.

    AVIF high quality uses the same encoder as Optimize images (high quality).
    AVIF optimized uses the same encoder as Optimize images.

    Args:

    - `image` (`QImage`): Screenshot with annotations baked in.
    - `path` (`Path`): Destination file. Parent folders are created.
    - `fmt` (`str`): `png`, `jpeg`, `avif_hq`, or `avif_optimized`.

    Raises:

    - `RuntimeError`: When the file cannot be written.
    - `OSError`: When AVIF encoding cannot start.

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "png":
        if not image.save(str(path), "PNG"):  # ty: ignore[no-matching-overload]
            msg = f"Could not save {path.name}"
            raise RuntimeError(msg)
        return
    if fmt == "jpeg":
        if not _jpeg_image(image).save(str(path), "JPEG", _JPEG_QUALITY):  # ty: ignore[no-matching-overload]
            msg = f"Could not save {path.name}"
            raise RuntimeError(msg)
        return
    with TemporaryDirectory(prefix="screenshot_avif_") as temp_dir:
        temp_png = Path(temp_dir) / f"{path.stem}.png"
        if not image.save(str(temp_png), "PNG"):  # ty: ignore[no-matching-overload]
            msg = "Could not prepare the screenshot for AVIF"
            raise RuntimeError(msg)
        process_png_to_avif(
            temp_png,
            path.parent,
            h.dev.get_project_root(),
            quality=fmt == "avif_hq",
        )
    if not path.is_file():
        msg = f"Could not save {path.name}"
        raise RuntimeError(msg)


# Backward-compatible name used by older tests and imports.
ScreenshotPreviewDialog = ScreenshotPreviewWindow
