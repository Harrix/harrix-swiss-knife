---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScreenshotPreviewDialog`](#%EF%B8%8F-class-screenshotpreviewdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `ScreenshotPreviewDialog`

```python
class ScreenshotPreviewDialog(QDialog)
```

Show a captured image with Copy / Save as / OK actions.

<details>
<summary>Code:</summary>

```python
class ScreenshotPreviewDialog(QDialog):

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create the preview dialog for `image`."""
        super().__init__(parent)
        self.setWindowTitle("Screenshot")
        self.setModal(True)
        self._image = image

        preview = QLabel()
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap.fromImage(image)
        if max(pixmap.width(), pixmap.height()) > _MAX_PREVIEW_SIDE:
            pixmap = pixmap.scaled(
                _MAX_PREVIEW_SIDE,
                _MAX_PREVIEW_SIDE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        preview.setPixmap(pixmap)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(preview)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)

        save_button = make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI)
        save_button.clicked.connect(self._save_as)
        button_layout.addWidget(save_button)

        add_ok_button(self, button_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addLayout(button_layout)

        self.resize(min(pixmap.width() + 40, 960), min(pixmap.height() + 100, 720))

    def _copy_to_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(self._image)

    def _save_as(self) -> None:
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save screenshot",
            "screenshot.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if not path:
            return
        self._image.save(path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, image: QImage, parent: QWidget | None = None) -> None
```

Create the preview dialog for `image`.

<details>
<summary>Code:</summary>

```python
def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Screenshot")
        self.setModal(True)
        self._image = image

        preview = QLabel()
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap.fromImage(image)
        if max(pixmap.width(), pixmap.height()) > _MAX_PREVIEW_SIDE:
            pixmap = pixmap.scaled(
                _MAX_PREVIEW_SIDE,
                _MAX_PREVIEW_SIDE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        preview.setPixmap(pixmap)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(preview)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)

        save_button = make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI)
        save_button.clicked.connect(self._save_as)
        button_layout.addWidget(save_button)

        add_ok_button(self, button_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addLayout(button_layout)

        self.resize(min(pixmap.width() + 40, 960), min(pixmap.height() + 100, 720))
```

</details>
