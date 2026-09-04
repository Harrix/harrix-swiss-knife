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

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

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
            make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI),
            self._copy_to_clipboard,
        )
        desktop_button = make_emoji_push_button(_SAVE_DESKTOP_BUTTON_LABEL, _SAVE_DESKTOP_BUTTON_EMOJI)
        desktop_button.setToolTip("Save as YYYY-MM-DD_NN.png on the Desktop")
        self._add_footer_button(desktop_button, self._save_to_desktop)
        self._add_footer_button(
            make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI),
            self._save_as,
        )
        ai_button = make_emoji_push_button("Recognize text (AI)", _MARKDOWN_AI_EMOJI)
        ai_button.setToolTip("Recognize text (AI)…")
        self._add_footer_button(ai_button, self._run_markdown_with_ai)
        ocr_button = make_emoji_push_button("Recognize text (OCR)", _MARKDOWN_OCR_EMOJI)
        ocr_button.setToolTip("Recognize text (OCR, local)…")
        self._add_footer_button(ocr_button, self._run_markdown_with_ocr)
        translate_button = make_emoji_push_button("OCR + translate", _TRANSLATE_EMOJI)
        translate_button.setToolTip("Recognize text and translate to the local language…")
        self._add_footer_button(translate_button, self._run_ocr_translate)
        self._add_footer_button(
            make_emoji_push_button(OK_BUTTON_LABEL, OK_BUTTON_EMOJI),
            self._close_current_tab,
        )
        footer.addWidget(buttons_host)

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
        apply_app_window_size_and_position(self)

    def add_image(self, image: QImage) -> None:
        """Append a new tab for `image` and select it."""
        tab = _ScreenshotTab(image, self._tabs)
        index = self._tabs.addTab(tab, self._tab_label(None, self._tabs.count() + 1))
        self._tabs.setCurrentIndex(index)
        self._update_window_title()
        self._tabs.tabBar().setVisible(self._tabs.count() > 1)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Clear the process-wide preview reference when the window closes."""
        if _preview_holder["window"] is self:
            _preview_holder["window"] = None
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Save on Ctrl+S / Ctrl+Yeru (layout-independent via virtual key)."""  # ignore: HP001
        if _is_ctrl_s(event):
            self._save_to_images()
            event.accept()
            return
        super().keyPressEvent(event)

    def _add_footer_button(self, button: QPushButton, slot: Callable[[], None]) -> None:
        button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        button.clicked.connect(slot)
        self._buttons.addWidget(button)
        self._action_buttons.append(button)

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

    def _on_tab_changed(self, _index: int) -> None:
        self._update_window_title()

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

    def _tab_label(self, saved_name: str | None, number: int) -> str:
        return saved_name or f"Screenshot {number}"

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

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

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
            make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI),
            self._copy_to_clipboard,
        )
        desktop_button = make_emoji_push_button(_SAVE_DESKTOP_BUTTON_LABEL, _SAVE_DESKTOP_BUTTON_EMOJI)
        desktop_button.setToolTip("Save as YYYY-MM-DD_NN.png on the Desktop")
        self._add_footer_button(desktop_button, self._save_to_desktop)
        self._add_footer_button(
            make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI),
            self._save_as,
        )
        ai_button = make_emoji_push_button("Recognize text (AI)", _MARKDOWN_AI_EMOJI)
        ai_button.setToolTip("Recognize text (AI)…")
        self._add_footer_button(ai_button, self._run_markdown_with_ai)
        ocr_button = make_emoji_push_button("Recognize text (OCR)", _MARKDOWN_OCR_EMOJI)
        ocr_button.setToolTip("Recognize text (OCR, local)…")
        self._add_footer_button(ocr_button, self._run_markdown_with_ocr)
        translate_button = make_emoji_push_button("OCR + translate", _TRANSLATE_EMOJI)
        translate_button.setToolTip("Recognize text and translate to the local language…")
        self._add_footer_button(translate_button, self._run_ocr_translate)
        self._add_footer_button(
            make_emoji_push_button(OK_BUTTON_LABEL, OK_BUTTON_EMOJI),
            self._close_current_tab,
        )
        footer.addWidget(buttons_host)

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
        apply_app_window_size_and_position(self)
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
        index = self._tabs.addTab(tab, self._tab_label(None, self._tabs.count() + 1))
        self._tabs.setCurrentIndex(index)
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

Save on Ctrl+S / Ctrl+Yeru (layout-independent via virtual key).

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if _is_ctrl_s(event):
            self._save_to_images()
            event.accept()
            return
        super().keyPressEvent(event)
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
