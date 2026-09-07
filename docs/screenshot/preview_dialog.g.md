---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScreenshotPreviewWindow`](#%EF%B8%8F-class-screenshotpreviewwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_image`](#%EF%B8%8F-method-add_image)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
- [🔧 Function `show_screenshot_preview`](#-function-show_screenshot_preview)

</details>

## 🏛️ Class `ScreenshotPreviewWindow`

```python
class ScreenshotPreviewWindow(QMainWindow)
```

Normal (non-modal) window that hosts one or more screenshot tabs.

<details>
<summary>Code:</summary>

```python
class ScreenshotPreviewWindow(QMainWindow):

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
        desktop_button = make_lucide_push_button(_SAVE_DESKTOP_BUTTON_LABEL, _SAVE_DESKTOP_BUTTON_ICON)
        desktop_button.setToolTip("Save as YYYY-MM-DD_NN.png on the Desktop")
        self._add_footer_button(desktop_button, self._save_to_desktop)
        self._add_footer_button(
            make_lucide_push_button(_SAVE_BUTTON_LABEL, _SAVE_BUTTON_ICON),
            self._save_as,
        )
        ai_button = make_lucide_push_button(
            "Recognize text (AI)",
            _MARKDOWN_AI_ICON,
            color=AI_BUTTON_ICON_COLOR,
        )
        ai_button.setToolTip("Recognize text (AI)…")
        self._add_footer_button(ai_button, self._run_markdown_with_ai)
        ocr_button = make_lucide_push_button("Recognize text (OCR)", _MARKDOWN_OCR_ICON)
        ocr_button.setToolTip("Recognize text (OCR, local)…")
        self._add_footer_button(ocr_button, self._run_markdown_with_ocr)
        translate_button = make_lucide_push_button("OCR + translate", _TRANSLATE_ICON)
        translate_button.setToolTip("Recognize text and translate to the local language…")
        self._add_footer_button(translate_button, self._run_ocr_translate)
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
        self._tabs.tabBar().setVisible(self._tabs.count() > 1)

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
        self._tabs.tabBar().setVisible(self._tabs.count() > 1)
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

    def _save_as(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save screenshot",
            tab.saved_name or "screenshot.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if not path:
            return
        if tab.image.save(path):
            name = Path(path).name
            tab.saved_name = name
            index = self._tabs.currentIndex()
            self._tabs.setTabText(index, name)
            self._status.setText(f"Saved: {path}")
            self._update_window_title()

    def _save_dated_png(self, folder: Path) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        path = next_dated_image_path(folder)
        if not tab.image.save(str(path)):
            self._status.setText(f"Could not save to {path}")
            return
        tab.saved_name = path.name
        index = self._tabs.currentIndex()
        self._tabs.setTabText(index, path.name)
        self._status.setText(f"Saved: {path}")
        self._update_window_title()

    def _save_temp_png(self) -> str | None:
        tab = self._current_tab()
        if tab is None:
            return None
        with NamedTemporaryFile(suffix=".png", delete=False) as handle:
            temp_path = Path(handle.name)
        if tab.image.save(str(temp_path)):
            return str(temp_path)
        return None

    def _save_to_desktop(self) -> None:
        desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        if not desktop:
            self._status.setText("Desktop folder not found")
            return
        self._save_dated_png(Path(desktop))

    def _save_to_images(self) -> None:
        self._save_dated_png(images_folder(h.dev.get_project_root()))

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
        self._tabs.tabBar().setVisible(not active and self._tabs.count() > 1)

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

    def _update_window_title(self) -> None:
        tab = self._current_tab()
        if tab is not None and tab.saved_name:
            self.setWindowTitle(f"{_DEFAULT_TITLE} — {tab.saved_name}")
            return
        self.setWindowTitle(_DEFAULT_TITLE)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build an empty preview window; call [`add_image`](#%EF%B8%8F-method-add_image) before showing.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
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
        desktop_button = make_lucide_push_button(_SAVE_DESKTOP_BUTTON_LABEL, _SAVE_DESKTOP_BUTTON_ICON)
        desktop_button.setToolTip("Save as YYYY-MM-DD_NN.png on the Desktop")
        self._add_footer_button(desktop_button, self._save_to_desktop)
        self._add_footer_button(
            make_lucide_push_button(_SAVE_BUTTON_LABEL, _SAVE_BUTTON_ICON),
            self._save_as,
        )
        ai_button = make_lucide_push_button(
            "Recognize text (AI)",
            _MARKDOWN_AI_ICON,
            color=AI_BUTTON_ICON_COLOR,
        )
        ai_button.setToolTip("Recognize text (AI)…")
        self._add_footer_button(ai_button, self._run_markdown_with_ai)
        ocr_button = make_lucide_push_button("Recognize text (OCR)", _MARKDOWN_OCR_ICON)
        ocr_button.setToolTip("Recognize text (OCR, local)…")
        self._add_footer_button(ocr_button, self._run_markdown_with_ocr)
        translate_button = make_lucide_push_button("OCR + translate", _TRANSLATE_ICON)
        translate_button.setToolTip("Recognize text and translate to the local language…")
        self._add_footer_button(translate_button, self._run_ocr_translate)
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
```

</details>

### ⚙️ Method `add_image`

```python
def add_image(self, image: QImage) -> None
```

Append a new tab for `image` and select it.

<details>
<summary>Code:</summary>

```python
def add_image(self, image: QImage) -> None:
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
        self._tabs.tabBar().setVisible(self._tabs.count() > 1)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Clear the process-wide preview reference when the window closes.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if _preview_holder["window"] is self:
            _preview_holder["window"] = None
        super().closeEvent(event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Save on Ctrl+S; Delete selected; Enter/Esc for crop.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reflow the top tool row when the window width changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._refit_tools_host()
```

</details>

## 🔧 Function `show_screenshot_preview`

```python
def show_screenshot_preview(image: QImage) -> ScreenshotPreviewWindow
```

Show `image` in the shared preview window, adding a tab if it is already open.

<details>
<summary>Code:</summary>

```python
def show_screenshot_preview(image: QImage) -> ScreenshotPreviewWindow:
    window = _preview_holder["window"]
    if window is None or not isValid(window):
        window = ScreenshotPreviewWindow()
        _preview_holder["window"] = window
    window.add_image(image)
    window.show()
    window.raise_()
    window.activateWindow()
    return window
```

</details>
