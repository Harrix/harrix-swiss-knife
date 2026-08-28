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
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `set_marked_for_removal`](#%EF%B8%8F-method-set_marked_for_removal)

</details>

## 🏛️ Class `ImageThumbnailItem`

```python
class ImageThumbnailItem(QFrame)
```

Single image thumbnail with remove (or soft-remove / undo) in the top-right corner.

<details>
<summary>Code:</summary>

```python
class ImageThumbnailItem(QFrame):

    def __init__(
        self,
        image_path: str,
        *,
        on_hard_remove: Callable[[str], None],
        soft_remove: bool = False,
        on_soft_removal_changed: Callable[..., None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Build a thumbnail tile with remove / undo controls."""
        super().__init__(parent)
        self.image_path = image_path
        self._on_hard_remove = on_hard_remove
        self._soft_remove = soft_remove
        self._on_soft_removal_changed = on_soft_removal_changed
        self._marked_for_removal = False
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to preview")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        pixmap = load_image_pixmap(image_path)
        if pixmap is not None and not pixmap.isNull():
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
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet(_REMOVE_BUTTON_STYLE)
        remove_btn.setToolTip("Remove image" if not soft_remove else "Mark for removal")
        remove_btn.clicked.connect(self._handle_remove_clicked)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self._remove_button = remove_btn

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Open lightbox on left click; ignore clicks on the remove button."""
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child is self._remove_button or (child is not None and self._remove_button.isAncestorOf(child)):
                super().mouseReleaseEvent(event)
                return
            show_image_lightbox(self.image_path, parent=self.window())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_marked_for_removal(self, *, marked: bool) -> None:
        """Gray out the thumbnail when marked for removal; show undo control."""
        if not self._soft_remove:
            return
        self._marked_for_removal = marked
        if marked:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.35)
            self.setGraphicsEffect(effect)
            self._remove_button.setText("↺")
            self._remove_button.setStyleSheet(_UNDO_BUTTON_STYLE)
            self._remove_button.setToolTip("Undo removal")
            self.setToolTip("Marked for removal — undo or save to delete from the note")
        else:
            self.setGraphicsEffect(None)  # ty: ignore[invalid-argument-type]
            self._remove_button.setText("×")  # noqa: RUF001
            self._remove_button.setStyleSheet(_REMOVE_BUTTON_STYLE)
            self._remove_button.setToolTip("Mark for removal")
            self.setToolTip("Click to preview")

    def _handle_remove_clicked(self) -> None:
        if self._soft_remove:
            self.set_marked_for_removal(marked=not self._marked_for_removal)
            if self._on_soft_removal_changed is not None:
                self._on_soft_removal_changed(self.image_path, marked=self._marked_for_removal)
            return
        self._on_hard_remove(self.image_path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, image_path: str, *, on_hard_remove: Callable[[str], None], soft_remove: bool = False, on_soft_removal_changed: Callable[..., None] | None = None, parent: QWidget | None = None) -> None
```

Build a thumbnail tile with remove / undo controls.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        image_path: str,
        *,
        on_hard_remove: Callable[[str], None],
        soft_remove: bool = False,
        on_soft_removal_changed: Callable[..., None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_path = image_path
        self._on_hard_remove = on_hard_remove
        self._soft_remove = soft_remove
        self._on_soft_removal_changed = on_soft_removal_changed
        self._marked_for_removal = False
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to preview")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        pixmap = load_image_pixmap(image_path)
        if pixmap is not None and not pixmap.isNull():
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
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet(_REMOVE_BUTTON_STYLE)
        remove_btn.setToolTip("Remove image" if not soft_remove else "Mark for removal")
        remove_btn.clicked.connect(self._handle_remove_clicked)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self._remove_button = remove_btn
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Open lightbox on left click; ignore clicks on the remove button.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child is self._remove_button or (child is not None and self._remove_button.isAncestorOf(child)):
                super().mouseReleaseEvent(event)
                return
            show_image_lightbox(self.image_path, parent=self.window())
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `set_marked_for_removal`

```python
def set_marked_for_removal(self, *, marked: bool) -> None
```

Gray out the thumbnail when marked for removal; show undo control.

<details>
<summary>Code:</summary>

```python
def set_marked_for_removal(self, *, marked: bool) -> None:
        if not self._soft_remove:
            return
        self._marked_for_removal = marked
        if marked:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.35)
            self.setGraphicsEffect(effect)
            self._remove_button.setText("↺")
            self._remove_button.setStyleSheet(_UNDO_BUTTON_STYLE)
            self._remove_button.setToolTip("Undo removal")
            self.setToolTip("Marked for removal — undo or save to delete from the note")
        else:
            self.setGraphicsEffect(None)  # ty: ignore[invalid-argument-type]
            self._remove_button.setText("×")  # noqa: RUF001
            self._remove_button.setStyleSheet(_REMOVE_BUTTON_STYLE)
            self._remove_button.setToolTip("Mark for removal")
            self.setToolTip("Click to preview")
```

</details>
