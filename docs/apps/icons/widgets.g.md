---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DraggableIconList`](#%EF%B8%8F-class-draggableiconlist)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_display_icon_size`](#%EF%B8%8F-method-set_display_icon_size)
  - [⚙️ Method `set_family_items`](#%EF%B8%8F-method-set_family_items)
  - [⚙️ Method `startDrag`](#%EF%B8%8F-method-startdrag)
  - [⚙️ Method `update_family_pixmap`](#%EF%B8%8F-method-update_family_pixmap)
- [🏛️ Class `VariantsPanel`](#%EF%B8%8F-class-variantspanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `clear_variants`](#%EF%B8%8F-method-clear_variants)
  - [⚙️ Method `set_thumb_size`](#%EF%B8%8F-method-set_thumb_size)
  - [⚙️ Method `show_family`](#%EF%B8%8F-method-show_family)

</details>

## 🏛️ Class `DraggableIconList`

```python
class DraggableIconList(QListWidget)
```

Icon grid/list that drags the underlying SVG file URL outward.

<details>
<summary>Code:</summary>

```python
class DraggableIconList(QListWidget):

    family_selected = Signal(object)  # IconFamily | None
    copy_path_requested = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
    ) -> None:
        """Configure icon mode and drag-only outward behavior."""
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        if emit_family_selection:
            self.currentItemChanged.connect(self._on_current_item_changed)

    def set_display_icon_size(self, icon_size: int) -> None:
        """Update icon and grid sizes used by the list."""
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))

    def set_family_items(
        self,
        families: list[IconFamily],
        *,
        pixmaps: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Rebuild the grid from filtered families and available thumbnails."""
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        for family in families:
            pixmap = pixmaps.get(family.id) or placeholder
            item = QListWidgetItem(QIcon(pixmap), family.title)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setToolTip(f"{family.id}\n{', '.join(family.tags)}")
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + 40))
            self.addItem(item)
        self.blockSignals(False)  # noqa: FBT003
        if self._emit_family_selection:
            self.family_selected.emit(None)

    def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        """Start an OS file drag for the selected SVG path."""
        item = self.currentItem()
        if item is None:
            return
        svg_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(svg_path, str) or not svg_path:
            return
        path = Path(svg_path)
        if not path.is_file():
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
        drag = QDrag(self)
        drag.setMimeData(mime)
        icon = item.icon()
        if not icon.isNull():
            drag.setPixmap(icon.pixmap(64, 64))
            drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)

    def update_family_pixmap(self, family_id: str, pixmap: QPixmap) -> None:
        """Update the icon for a family already present in the list."""
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            if getattr(family, "id", None) == family_id:
                item.setIcon(QIcon(pixmap))
                break

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(path, str) or not path:
            return
        menu = QMenu(self)
        copy_action = menu.addAction("📋 Copy path")
        chosen = menu.exec_(self.mapToGlobal(pos))
        if chosen is copy_action:
            QApplication.clipboard().setText(path)
            self.copy_path_requested.emit(path)

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self.family_selected.emit(None)
            return
        family = current.data(Qt.ItemDataRole.UserRole)
        if family is not None and hasattr(family, "variants"):
            self.family_selected.emit(family)
        else:
            self.family_selected.emit(None)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, icon_size: int = DEFAULT_THUMB_SIZE, emit_family_selection: bool = True) -> None
```

Configure icon mode and drag-only outward behavior.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
    ) -> None:
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        if emit_family_selection:
            self.currentItemChanged.connect(self._on_current_item_changed)
```

</details>

### ⚙️ Method `set_display_icon_size`

```python
def set_display_icon_size(self, icon_size: int) -> None
```

Update icon and grid sizes used by the list.

<details>
<summary>Code:</summary>

```python
def set_display_icon_size(self, icon_size: int) -> None:
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))
```

</details>

### ⚙️ Method `set_family_items`

```python
def set_family_items(self, families: list[IconFamily], *, pixmaps: dict[str, QPixmap], placeholder: QPixmap) -> None
```

Rebuild the grid from filtered families and available thumbnails.

<details>
<summary>Code:</summary>

```python
def set_family_items(
        self,
        families: list[IconFamily],
        *,
        pixmaps: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        for family in families:
            pixmap = pixmaps.get(family.id) or placeholder
            item = QListWidgetItem(QIcon(pixmap), family.title)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setToolTip(f"{family.id}\n{', '.join(family.tags)}")
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + 40))
            self.addItem(item)
        self.blockSignals(False)  # noqa: FBT003
        if self._emit_family_selection:
            self.family_selected.emit(None)
```

</details>

### ⚙️ Method `startDrag`

```python
def startDrag(self, supported_actions: Qt.DropAction) -> None
```

Start an OS file drag for the selected SVG path.

<details>
<summary>Code:</summary>

```python
def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        item = self.currentItem()
        if item is None:
            return
        svg_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(svg_path, str) or not svg_path:
            return
        path = Path(svg_path)
        if not path.is_file():
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
        drag = QDrag(self)
        drag.setMimeData(mime)
        icon = item.icon()
        if not icon.isNull():
            drag.setPixmap(icon.pixmap(64, 64))
            drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)
```

</details>

### ⚙️ Method `update_family_pixmap`

```python
def update_family_pixmap(self, family_id: str, pixmap: QPixmap) -> None
```

Update the icon for a family already present in the list.

<details>
<summary>Code:</summary>

```python
def update_family_pixmap(self, family_id: str, pixmap: QPixmap) -> None:
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            if getattr(family, "id", None) == family_id:
                item.setIcon(QIcon(pixmap))
                break
```

</details>

## 🏛️ Class `VariantsPanel`

```python
class VariantsPanel(QWidget)
```

Right-side panel showing SVG variants for the selected icon family.

<details>
<summary>Code:</summary>

```python
class VariantsPanel(QWidget):

    def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None:
        """Build header + draggable variants list."""
        super().__init__(parent)
        self._thumb_size = thumb_size
        self._repo_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QLabel("Select an icon to see variants")
        self.header.setWordWrap(True)
        layout.addWidget(self.header)

        self.list = DraggableIconList(icon_size=thumb_size, emit_family_selection=False)
        layout.addWidget(self.list)

    def clear_variants(self) -> None:
        """Clear the variants list and reset the header."""
        self.list.clear()
        self.header.setText("Select an icon to see variants")

    def set_thumb_size(self, thumb_size: int) -> None:
        """Update variant thumbnail size (does not rebuild items)."""
        self._thumb_size = thumb_size
        self.list.set_display_icon_size(thumb_size)

    def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None:
        """Populate the panel with variants of `family`."""
        self._repo_root = repo_root
        self.list.clear()
        if family is None or repo_root is None:
            self.header.setText("Select an icon to see variants")
            return

        tags = ", ".join(family.tags) if family.tags else "—"
        self.header.setText(
            f"{family.title}\n{family.id}\nCategories: {', '.join(family.categories)}\nTags: {tags}",
        )
        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            pixmap = self._preview(path, self._thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(Qt.ItemDataRole.UserRole + 1, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)

    @staticmethod
    def _preview(path: Path, size: int) -> QPixmap:
        image = render_svg_to_image(path, size)
        if image is None:
            return placeholder_pixmap(size)
        return QPixmap.fromImage(image)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None
```

Build header + draggable variants list.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None:
        super().__init__(parent)
        self._thumb_size = thumb_size
        self._repo_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QLabel("Select an icon to see variants")
        self.header.setWordWrap(True)
        layout.addWidget(self.header)

        self.list = DraggableIconList(icon_size=thumb_size, emit_family_selection=False)
        layout.addWidget(self.list)
```

</details>

### ⚙️ Method `clear_variants`

```python
def clear_variants(self) -> None
```

Clear the variants list and reset the header.

<details>
<summary>Code:</summary>

```python
def clear_variants(self) -> None:
        self.list.clear()
        self.header.setText("Select an icon to see variants")
```

</details>

### ⚙️ Method `set_thumb_size`

```python
def set_thumb_size(self, thumb_size: int) -> None
```

Update variant thumbnail size (does not rebuild items).

<details>
<summary>Code:</summary>

```python
def set_thumb_size(self, thumb_size: int) -> None:
        self._thumb_size = thumb_size
        self.list.set_display_icon_size(thumb_size)
```

</details>

### ⚙️ Method `show_family`

```python
def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None
```

Populate the panel with variants of `family`.

<details>
<summary>Code:</summary>

```python
def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None:
        self._repo_root = repo_root
        self.list.clear()
        if family is None or repo_root is None:
            self.header.setText("Select an icon to see variants")
            return

        tags = ", ".join(family.tags) if family.tags else "—"
        self.header.setText(
            f"{family.title}\n{family.id}\nCategories: {', '.join(family.categories)}\nTags: {tags}",
        )
        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            pixmap = self._preview(path, self._thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(Qt.ItemDataRole.UserRole + 1, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)
```

</details>
