---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `folder_library_combo.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FolderLibraryCombo`](#%EF%B8%8F-class-folderlibrarycombo)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `hidePopup`](#%EF%B8%8F-method-hidepopup)
  - [⚙️ Method `showPopup`](#%EF%B8%8F-method-showpopup)

</details>

## 🏛️ Class `FolderLibraryCombo`

```python
class FolderLibraryCombo(QComboBox)
```

Combo of icon library roots with a sticky footer to open another folder.

The footer sits below the scrollable popup list so it stays visible even when
there are many pinned libraries.

<details>
<summary>Code:</summary>

```python
class FolderLibraryCombo(QComboBox):

    add_folder_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the combo; call `showPopup` to attach the sticky footer."""
        super().__init__(parent)
        self._footer: QPushButton | None = None
        self._footer_attached = False

    def hidePopup(self) -> None:  # noqa: N802
        """Hide the sticky footer with the popup."""
        footer = self._footer
        if footer is not None:
            footer.hide()
        super().hidePopup()

    def showPopup(self) -> None:  # noqa: N802
        """Show the popup, then attach or reveal the sticky Add folder footer."""
        super().showPopup()
        QTimer.singleShot(0, self._attach_or_show_footer)

    def _attach_or_show_footer(self) -> None:
        view = self.view()
        if view is None:
            return
        container = view.parentWidget()
        if container is None:
            return
        layout = container.layout()
        footer = self._ensure_footer(container)
        if isinstance(layout, QBoxLayout) and not self._footer_attached:
            layout.addWidget(footer)
            self._footer_attached = True
            # Grow the popup so the footer is not clipped under the list view.
            extra = footer.sizeHint().height()
            if extra <= 0:
                extra = _FOOTER_MIN_HEIGHT
            container.resize(container.width(), container.height() + extra)
        elif footer.parent() is not container:
            footer.setParent(container)
        footer.show()
        footer.raise_()

    def _ensure_footer(self, container: QWidget) -> QPushButton:
        footer = self._footer
        if footer is not None:
            return footer
        footer = QPushButton(_ADD_FOLDER_LABEL, container)
        footer.setObjectName("vectorIconsAddFolderFooter")
        footer.setCursor(Qt.CursorShape.PointingHandCursor)
        footer.setMinimumHeight(_FOOTER_MIN_HEIGHT)
        footer.setStyleSheet(
            button_idle_qss() + f" QPushButton#vectorIconsAddFolderFooter {{"
            f" border-top: 1px solid {INPUT_BORDER};"
            f" border-left: none; border-right: none; border-bottom: none;"
            f" border-radius: 0px;"
            f" background-color: {SURFACE};"
            f" text-align: left;"
            f" padding-left: 10px;"
            f"}}"
            f" QPushButton#vectorIconsAddFolderFooter:hover {{"
            f" background-color: {HAIRLINE};"
            f"}}"
        )
        apply_lucide_button_icon(footer, _ADD_FOLDER_ICON, icon_size=_FOOTER_ICON_SIZE)
        footer.setToolTip("Choose another icons library folder to open")
        footer.clicked.connect(self._on_footer_clicked)
        self._footer = footer
        return footer

    def _on_footer_clicked(self) -> None:
        self.hidePopup()
        self.add_folder_requested.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create the combo; call [`showPopup`](#%EF%B8%8F-method-showpopup) to attach the sticky footer.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._footer: QPushButton | None = None
        self._footer_attached = False
```

</details>

### ⚙️ Method `hidePopup`

```python
def hidePopup(self) -> None
```

Hide the sticky footer with the popup.

<details>
<summary>Code:</summary>

```python
def hidePopup(self) -> None:  # noqa: N802
        footer = self._footer
        if footer is not None:
            footer.hide()
        super().hidePopup()
```

</details>

### ⚙️ Method `showPopup`

```python
def showPopup(self) -> None
```

Show the popup, then attach or reveal the sticky Add folder footer.

<details>
<summary>Code:</summary>

```python
def showPopup(self) -> None:  # noqa: N802
        super().showPopup()
        QTimer.singleShot(0, self._attach_or_show_footer)
```

</details>
