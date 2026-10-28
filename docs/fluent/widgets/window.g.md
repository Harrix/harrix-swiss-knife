---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentLayerPanel`](#%EF%B8%8F-class-fluentlayerpanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
- [🏛️ Class `FluentNavigationWindow`](#%EF%B8%8F-class-fluentnavigationwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `add_page`](#%EF%B8%8F-method-add_page)
  - [⚙️ Method `install_caption`](#%EF%B8%8F-method-install_caption)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `page`](#%EF%B8%8F-method-page)
  - [⚙️ Method `show_page`](#%EF%B8%8F-method-show_page)

</details>

## 🏛️ Class `FluentLayerPanel`

```python
class FluentLayerPanel(QWidget)
```

Content layer of a Fluent window: `layer_bg` with a rounded top-left corner.

Mirrors the stacked-widget area of PyQt-Fluent-Widgets `FluentWindow`: the
window background shows on the left and top, and the layer has a 1 px
stroke on those two edges only.

<details>
<summary>Code:</summary>

```python
class FluentLayerPanel(QWidget):

    def __init__(self, parent: QWidget | None = None, *, rounded: bool = True) -> None:
        """Create a layer panel."""
        super().__init__(parent)
        self._rounded = rounded
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the layer fill and its top / left stroke."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        radius = float(RADIUS_CARD if self._rounded else 0)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, radius + 1, radius + 1)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(palette.layer_bg)
        painter.drawPath(path)
        painter.setPen(palette.layer_stroke)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, rounded: bool = True) -> None
```

Create a layer panel.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, rounded: bool = True) -> None:
        super().__init__(parent)
        self._rounded = rounded
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the layer fill and its top / left stroke.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        radius = float(RADIUS_CARD if self._rounded else 0)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, radius + 1, radius + 1)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(palette.layer_bg)
        painter.drawPath(path)
        painter.setPen(palette.layer_stroke)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.end()
```

</details>

## 🏛️ Class `FluentNavigationWindow`

```python
class FluentNavigationWindow(QMainWindow)
```

Top-level Fluent window: Win11 caption, navigation bar, and a layer with pages.

The shell is a `QMainWindow` so the caption uses the same menu-bar path as
the other Harrix Windows (drag, resize, and the min / max / close buttons).
Call `menuBar()` before [`install_caption`](#%EF%B8%8F-method-install_caption) when the window should show a menu.

<details>
<summary>Code:</summary>

```python
class FluentNavigationWindow(QMainWindow):

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        trailing_widgets: Sequence[QWidget] = (),
        install_caption: bool = True,
    ) -> None:
        """Create the window (pages are added with `add_page`)."""
        super().__init__(parent)
        self.setWindowTitle(title)
        enable_fluent_theme(self)
        body = QWidget(self)
        row = QHBoxLayout(body)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(body)
        self.navigation.setFixedWidth(_NAVIGATION_WIDTH)
        self.layer = FluentLayerPanel(body)
        layer_layout = QVBoxLayout(self.layer)
        layer_layout.setContentsMargins(1, 1, 0, 0)
        self.stack = QStackedWidget(self.layer)
        layer_layout.addWidget(self.stack)
        row.addWidget(self.navigation)
        row.addWidget(self.layer, 1)
        self.setCentralWidget(body)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self.show_page)
        self.caption_installed = False
        if install_caption:
            self.install_caption(trailing_widgets)

    def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "", scroll: bool = True) -> QWidget:
        """Register a page (wrapped in a transparent scroll area by default)."""
        page: QWidget = widget
        if scroll:
            area = FluentScrollArea(self.stack)
            area.setWidget(widget)
            page = area
        self._pages[key] = page
        self.stack.addWidget(page)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(page)
        return page

    def install_caption(self, trailing_widgets: Sequence[QWidget] = ()) -> bool:
        """Install the Win11 caption. Add menus with `menuBar()` before calling this."""
        self.caption_installed = install_win11_caption(self, trailing_widgets=list(trailing_widgets))
        return self.caption_installed

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Route caption hit-testing to the Win11 caption."""
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def page(self, key: str) -> QWidget | None:
        """Return the page registered under `key`."""
        return self._pages.get(key)

    def show_page(self, key: str) -> None:
        """Switch to the page registered under `key`."""
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)
            if self.navigation.current() != key:
                self.navigation.set_current(key)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None, *, trailing_widgets: Sequence[QWidget] = (), install_caption: bool = True) -> None
```

Create the window (pages are added with `add_page`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        trailing_widgets: Sequence[QWidget] = (),
        install_caption: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        enable_fluent_theme(self)
        body = QWidget(self)
        row = QHBoxLayout(body)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(body)
        self.navigation.setFixedWidth(_NAVIGATION_WIDTH)
        self.layer = FluentLayerPanel(body)
        layer_layout = QVBoxLayout(self.layer)
        layer_layout.setContentsMargins(1, 1, 0, 0)
        self.stack = QStackedWidget(self.layer)
        layer_layout.addWidget(self.stack)
        row.addWidget(self.navigation)
        row.addWidget(self.layer, 1)
        self.setCentralWidget(body)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self.show_page)
        self.caption_installed = False
        if install_caption:
            self.install_caption(trailing_widgets)
```

</details>

### ⚙️ Method `add_page`

```python
def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = '', scroll: bool = True) -> QWidget
```

Register a page (wrapped in a transparent scroll area by default).

<details>
<summary>Code:</summary>

```python
def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "", scroll: bool = True) -> QWidget:
        page: QWidget = widget
        if scroll:
            area = FluentScrollArea(self.stack)
            area.setWidget(widget)
            page = area
        self._pages[key] = page
        self.stack.addWidget(page)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(page)
        return page
```

</details>

### ⚙️ Method `install_caption`

```python
def install_caption(self, trailing_widgets: Sequence[QWidget] = ()) -> bool
```

Install the Win11 caption. Add menus with `menuBar()` before calling this.

<details>
<summary>Code:</summary>

```python
def install_caption(self, trailing_widgets: Sequence[QWidget] = ()) -> bool:
        self.caption_installed = install_win11_caption(self, trailing_widgets=list(trailing_widgets))
        return self.caption_installed
```

</details>

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]
```

Route caption hit-testing to the Win11 caption.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `page`

```python
def page(self, key: str) -> QWidget | None
```

Return the page registered under `key`.

<details>
<summary>Code:</summary>

```python
def page(self, key: str) -> QWidget | None:
        return self._pages.get(key)
```

</details>

### ⚙️ Method `show_page`

```python
def show_page(self, key: str) -> None
```

Switch to the page registered under `key`.

<details>
<summary>Code:</summary>

```python
def show_page(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)
            if self.navigation.current() != key:
                self.navigation.set_current(key)
```

</details>
