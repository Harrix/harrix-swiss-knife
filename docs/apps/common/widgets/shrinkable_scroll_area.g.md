---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shrinkable_scroll_area.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ShrinkableScrollArea`](#%EF%B8%8F-class-shrinkablescrollarea)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
- [🔧 Function `wrap_tab_pages_in_shrinkable_scroll`](#-function-wrap_tab_pages_in_shrinkable_scroll)
- [🔧 Function `wrap_widget_contents_in_shrinkable_scroll`](#-function-wrap_widget_contents_in_shrinkable_scroll)

</details>

## 🏛️ Class `ShrinkableScrollArea`

```python
class ShrinkableScrollArea(QScrollArea)
```

`QScrollArea` whose minimum size ignores the inner widget.

Child widgets keep their own minimum widths. When the viewport is smaller,
scrollbars appear instead of blocking the window from shrinking.

<details>
<summary>Code:</summary>

```python
class ShrinkableScrollArea(QScrollArea):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Allow the parent to shrink below the inner widget minimum."""
        return QSize(_MIN_VIEWPORT, _MIN_VIEWPORT)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Allow the parent to shrink below the inner widget minimum.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_MIN_VIEWPORT, _MIN_VIEWPORT)
```

</details>

## 🔧 Function `wrap_tab_pages_in_shrinkable_scroll`

```python
def wrap_tab_pages_in_shrinkable_scroll(tab_widget: QTabWidget) -> None
```

Wrap every tab page so a narrow window shows scrollbars instead of a min-width clamp.

<details>
<summary>Code:</summary>

```python
def wrap_tab_pages_in_shrinkable_scroll(tab_widget: QTabWidget) -> None:
    for index in range(tab_widget.count()):
        page = tab_widget.widget(index)
        if page is not None:
            wrap_widget_contents_in_shrinkable_scroll(page)
```

</details>

## 🔧 Function `wrap_widget_contents_in_shrinkable_scroll`

```python
def wrap_widget_contents_in_shrinkable_scroll(host: QWidget) -> ShrinkableScrollArea
```

Move `host`'s current layout into a shrinkable scroll area.

Args:

- `host` (`QWidget`): Tab page or other container that currently owns the content layout.

Returns:

- [`ShrinkableScrollArea`](#%EF%B8%8F-class-shrinkablescrollarea): The scroll area now filling `host`.

<details>
<summary>Code:</summary>

```python
def wrap_widget_contents_in_shrinkable_scroll(host: QWidget) -> ShrinkableScrollArea:
    existing = host.layout()
    inner = QWidget()
    if existing is not None:
        inner.setLayout(existing)
    scroll = ShrinkableScrollArea(host)
    scroll.setWidget(inner)
    outer = QVBoxLayout(host)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)
    outer.addWidget(scroll)
    return scroll
```

</details>
