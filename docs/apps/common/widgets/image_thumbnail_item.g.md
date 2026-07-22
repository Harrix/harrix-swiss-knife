---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_thumbnail_item.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ImageThumbnailItem`](#%EF%B8%8F-class-imagethumbnailitem)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `ImageThumbnailItem`

```python
class ImageThumbnailItem(QFrame)
```

Single image thumbnail with a remove button in the top-right corner.

<details>
<summary>Code:</summary>

```python
class ImageThumbnailItem(QFrame):

    def __init__(
        self,
        image_path: str,
        *,
        on_remove: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        """Build a thumbnail tile with a remove button."""
        super().__init__(parent)
        self.image_path = image_path
        self._on_remove = on_remove
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = load_image_pixmap(image_path)
        if not pixmap.isNull():
            thumb_label.setPixmap(
                pixmap.scaled(
                    _THUMB_SIZE - 8,
                    _THUMB_SIZE - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            thumb_label.setText(Path(image_path).name)
        grid.addWidget(thumb_label, 0, 0)

        remove_btn = QPushButton("×")  # noqa: RUF001
        remove_btn.setFixedSize(_REMOVE_BTN_SIZE, _REMOVE_BTN_SIZE)
        remove_btn.setStyleSheet(
            "QPushButton { background: #e53935; color: white; border: none; border-radius: 12px; "
            "font-size: 16px; font-weight: bold; padding: 0; min-width: 0; min-height: 0; }"
            "QPushButton:hover { background: #c62828; }"
        )
        remove_btn.clicked.connect(self._handle_remove)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def _handle_remove(self) -> None:
        self._on_remove(self.image_path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, image_path: str) -> None
```

Build a thumbnail tile with a remove button.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        image_path: str,
        *,
        on_remove: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_path = image_path
        self._on_remove = on_remove
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = load_image_pixmap(image_path)
        if not pixmap.isNull():
            thumb_label.setPixmap(
                pixmap.scaled(
                    _THUMB_SIZE - 8,
                    _THUMB_SIZE - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            thumb_label.setText(Path(image_path).name)
        grid.addWidget(thumb_label, 0, 0)

        remove_btn = QPushButton("×")  # noqa: RUF001
        remove_btn.setFixedSize(_REMOVE_BTN_SIZE, _REMOVE_BTN_SIZE)
        remove_btn.setStyleSheet(
            "QPushButton { background: #e53935; color: white; border: none; border-radius: 12px; "
            "font-size: 16px; font-weight: bold; padding: 0; min-width: 0; min-height: 0; }"
            "QPushButton:hover { background: #c62828; }"
        )
        remove_btn.clicked.connect(self._handle_remove)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
```

</details>
