---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `menus.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentCommandBar`](#%EF%B8%8F-class-fluentcommandbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_command`](#%EF%B8%8F-method-add_command)
  - [⚙️ Method `add_separator`](#%EF%B8%8F-method-add_separator)
  - [⚙️ Method `overflow_count`](#%EF%B8%8F-method-overflow_count)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
- [🏛️ Class `FluentMenu`](#%EF%B8%8F-class-fluentmenu)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `add_lucide_action`](#%EF%B8%8F-method-add_lucide_action)
  - [⚙️ Method `add_sub_menu`](#%EF%B8%8F-method-add_sub_menu)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
- [🏛️ Class `FluentMenuBar`](#%EF%B8%8F-class-fluentmenubar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `add_fluent_menu`](#%EF%B8%8F-method-add_fluent_menu)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-1)
- [🏛️ Class `FluentRibbonBar`](#%EF%B8%8F-class-fluentribbonbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `add_group`](#%EF%B8%8F-method-add_group)
  - [⚙️ Method `add_tab`](#%EF%B8%8F-method-add_tab)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
- [🏛️ Class `FluentRibbonGroup`](#%EF%B8%8F-class-fluentribbongroup)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `add_button`](#%EF%B8%8F-method-add_button)
  - [⚙️ Method `title`](#%EF%B8%8F-method-title)
- [🏛️ Class `FluentRibbonTabBar`](#%EF%B8%8F-class-fluentribbontabbar)
- [🏛️ Class `FluentStatusBar`](#%EF%B8%8F-class-fluentstatusbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-2)
- [🏛️ Class `FluentToolBar`](#%EF%B8%8F-class-fluenttoolbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `add_lucide_action`](#%EF%B8%8F-method-add_lucide_action-1)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-3)

</details>

## 🏛️ Class `FluentCommandBar`

```python
class FluentCommandBar(QWidget)
```

Row of command buttons that moves overflowing commands into a `more` menu.

<details>
<summary>Code:</summary>

```python
class FluentCommandBar(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty command bar."""
        super().__init__(parent)
        self._actions: list[QAction] = []
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._row.setSpacing(SPACE_XS)
        self._buttons: list[FluentToolButton] = []
        self._more_menu = FluentMenu("", self)
        self._more = FluentToolButton("", self, icon="ellipsis", menu=self._more_menu)
        self._more.setToolTip("More")
        self._row.addStretch(1)
        self._row.addWidget(self._more)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)

    def add_command(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append a command."""
        action = _lucide_action(self, self, text, icon, slot)
        self._actions.append(action)
        button = FluentToolButton(text, self, icon=icon)
        button.clicked.connect(action.trigger)
        self._buttons.append(button)
        self._row.insertWidget(len(self._buttons) - 1, button)
        self._relayout()
        return action

    def add_separator(self) -> None:
        """Append a vertical hairline between commands."""
        divider = FluentDivider(self, orientation=Qt.Orientation.Vertical)
        divider.setFixedHeight(CONTROL_HEIGHT - SPACE_S)
        self._row.insertWidget(self._row.count() - 2, divider)

    def overflow_count(self) -> int:
        """Return how many commands are in the `more` menu."""
        return sum(1 for button in self._buttons if button.isHidden())

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the bar surface."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Re-flow commands into the overflow menu."""
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self) -> None:
        available = self.width() - CONTROL_HEIGHT - 3 * SPACE_XS
        used = 0
        self._more_menu.clear()
        for button, action in zip(self._buttons, self._actions, strict=True):
            width = max(button.sizeHint().width(), CONTROL_HEIGHT)
            fits = used + width <= available
            button.setVisible(fits)
            if fits:
                used += width + SPACE_XS
            else:
                self._more_menu.addAction(action)
        self._more.setVisible(bool(self._more_menu.actions()))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty command bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._actions: list[QAction] = []
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._row.setSpacing(SPACE_XS)
        self._buttons: list[FluentToolButton] = []
        self._more_menu = FluentMenu("", self)
        self._more = FluentToolButton("", self, icon="ellipsis", menu=self._more_menu)
        self._more.setToolTip("More")
        self._row.addStretch(1)
        self._row.addWidget(self._more)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `add_command`

```python
def add_command(self, text: str, icon: str = '', slot: Callable[[], None] | None = None) -> QAction
```

Append a command.

<details>
<summary>Code:</summary>

```python
def add_command(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        action = _lucide_action(self, self, text, icon, slot)
        self._actions.append(action)
        button = FluentToolButton(text, self, icon=icon)
        button.clicked.connect(action.trigger)
        self._buttons.append(button)
        self._row.insertWidget(len(self._buttons) - 1, button)
        self._relayout()
        return action
```

</details>

### ⚙️ Method `add_separator`

```python
def add_separator(self) -> None
```

Append a vertical hairline between commands.

<details>
<summary>Code:</summary>

```python
def add_separator(self) -> None:
        divider = FluentDivider(self, orientation=Qt.Orientation.Vertical)
        divider.setFixedHeight(CONTROL_HEIGHT - SPACE_S)
        self._row.insertWidget(self._row.count() - 2, divider)
```

</details>

### ⚙️ Method `overflow_count`

```python
def overflow_count(self) -> int
```

Return how many commands are in the `more` menu.

<details>
<summary>Code:</summary>

```python
def overflow_count(self) -> int:
        return sum(1 for button in self._buttons if button.isHidden())
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the bar surface.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Re-flow commands into the overflow menu.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._relayout()
```

</details>

## 🏛️ Class `FluentMenu`

```python
class FluentMenu(QMenu)
```

Context / drop-down menu with rounded translucent corners and Lucide icons.

<details>
<summary>Code:</summary>

```python
class FluentMenu(QMenu):

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        """Create a menu."""
        super().__init__(title, parent)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.aboutToShow.connect(self.refresh_theme)
        bind_theme(self, self.refresh_theme)

    def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append an action with a Lucide icon that follows the theme."""
        action = _lucide_action(self, self._palette_source(), text, icon, slot)
        self.addAction(action)
        return action

    def add_sub_menu(self, title: str, icon: str = "") -> FluentMenu:
        """Append a sub-menu and return it."""
        menu = FluentMenu(title, self)
        if icon:
            menu.setIcon(themed_icon(icon, palette_for(self._palette_source())))
        self.addMenu(menu)
        return menu

    def refresh_theme(self) -> None:
        """Re-apply chrome and recolor Lucide icons for the owner's palette."""
        source = self._palette_source()
        palette = palette_for(source)
        self.setStyleSheet(menu_qss(palette, "QMenu"))
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))

    def _palette_source(self) -> QWidget:
        parent = self.parentWidget()
        return parent if parent is not None else self
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str = '', parent: QWidget | None = None) -> None
```

Create a menu.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.aboutToShow.connect(self.refresh_theme)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `add_lucide_action`

```python
def add_lucide_action(self, text: str, icon: str = '', slot: Callable[[], None] | None = None) -> QAction
```

Append an action with a Lucide icon that follows the theme.

<details>
<summary>Code:</summary>

```python
def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        action = _lucide_action(self, self._palette_source(), text, icon, slot)
        self.addAction(action)
        return action
```

</details>

### ⚙️ Method `add_sub_menu`

```python
def add_sub_menu(self, title: str, icon: str = '') -> FluentMenu
```

Append a sub-menu and return it.

<details>
<summary>Code:</summary>

```python
def add_sub_menu(self, title: str, icon: str = "") -> FluentMenu:
        menu = FluentMenu(title, self)
        if icon:
            menu.setIcon(themed_icon(icon, palette_for(self._palette_source())))
        self.addMenu(menu)
        return menu
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and recolor Lucide icons for the owner's palette.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        source = self._palette_source()
        palette = palette_for(source)
        self.setStyleSheet(menu_qss(palette, "QMenu"))
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))
```

</details>

## 🏛️ Class `FluentMenuBar`

```python
class FluentMenuBar(QMenuBar)
```

Flat menu bar with subtle hover; menus use [`FluentMenu`](#%EF%B8%8F-class-fluentmenu) chrome.

<details>
<summary>Code:</summary>

```python
class FluentMenuBar(QMenuBar):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a menu bar."""
        super().__init__(parent)
        bind_theme(self, self.refresh_theme)

    def add_fluent_menu(self, title: str) -> FluentMenu:
        """Append a `FluentMenu` and return it."""
        menu = FluentMenu(title, self)
        self.addMenu(menu)
        return menu

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        self.setStyleSheet(f"""
QMenuBar {{ background: transparent; color: {css(palette.text_primary)}; border: none; padding: 2px; }}
QMenuBar::item {{ background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 6px 10px; }}
QMenuBar::item:selected {{ background: {css(palette.subtle_hover)}; }}
QMenuBar::item:pressed {{ background: {css(palette.subtle_pressed)}; }}
{menu_qss(palette, "QMenu")}
""")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a menu bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `add_fluent_menu`

```python
def add_fluent_menu(self, title: str) -> FluentMenu
```

Append a [`FluentMenu`](#%EF%B8%8F-class-fluentmenu) and return it.

<details>
<summary>Code:</summary>

```python
def add_fluent_menu(self, title: str) -> FluentMenu:
        menu = FluentMenu(title, self)
        self.addMenu(menu)
        return menu
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(f"""
QMenuBar {{ background: transparent; color: {css(palette.text_primary)}; border: none; padding: 2px; }}
QMenuBar::item {{ background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 6px 10px; }}
QMenuBar::item:selected {{ background: {css(palette.subtle_hover)}; }}
QMenuBar::item:pressed {{ background: {css(palette.subtle_pressed)}; }}
{menu_qss(palette, "QMenu")}
""")
```

</details>

## 🏛️ Class `FluentRibbonBar`

```python
class FluentRibbonBar(QWidget)
```

Ribbon: tab strip above a card of groups per tab.

<details>
<summary>Code:</summary>

```python
class FluentRibbonBar(QWidget):

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty ribbon."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        self.tab_bar = FluentRibbonTabBar(self)
        self.stack = QStackedWidget(self)
        self.stack.setFixedHeight(96)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack)
        self.tab_bar.current_changed.connect(self._on_tab)
        bind_theme(self, self.update)

    def add_group(self, tab: int, title: str) -> FluentRibbonGroup:
        """Append a group to tab `tab` and return it."""
        page = self.stack.widget(tab)
        layout = page.layout() if page is not None else None
        if not isinstance(layout, QHBoxLayout):
            message = f"Ribbon tab {tab} does not exist"
            raise IndexError(message)
        group = FluentRibbonGroup(title, page)
        layout.insertWidget(layout.count() - 1, group)
        return group

    def add_tab(self, title: str) -> int:
        """Append a tab and return its index."""
        page = QWidget(self.stack)
        row = QHBoxLayout(page)
        row.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        row.setSpacing(SPACE_M)
        row.addStretch(1)
        self.stack.addWidget(page)
        self.tab_bar.add_item(title)
        return self.stack.count() - 1

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card behind the groups."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.stack.geometry(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()

    def _on_tab(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.current_changed.emit(index)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty ribbon.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        self.tab_bar = FluentRibbonTabBar(self)
        self.stack = QStackedWidget(self)
        self.stack.setFixedHeight(96)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack)
        self.tab_bar.current_changed.connect(self._on_tab)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `add_group`

```python
def add_group(self, tab: int, title: str) -> FluentRibbonGroup
```

Append a group to tab `tab` and return it.

<details>
<summary>Code:</summary>

```python
def add_group(self, tab: int, title: str) -> FluentRibbonGroup:
        page = self.stack.widget(tab)
        layout = page.layout() if page is not None else None
        if not isinstance(layout, QHBoxLayout):
            message = f"Ribbon tab {tab} does not exist"
            raise IndexError(message)
        group = FluentRibbonGroup(title, page)
        layout.insertWidget(layout.count() - 1, group)
        return group
```

</details>

### ⚙️ Method `add_tab`

```python
def add_tab(self, title: str) -> int
```

Append a tab and return its index.

<details>
<summary>Code:</summary>

```python
def add_tab(self, title: str) -> int:
        page = QWidget(self.stack)
        row = QHBoxLayout(page)
        row.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        row.setSpacing(SPACE_M)
        row.addStretch(1)
        self.stack.addWidget(page)
        self.tab_bar.add_item(title)
        return self.stack.count() - 1
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the card behind the groups.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.stack.geometry(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()
```

</details>

## 🏛️ Class `FluentRibbonGroup`

```python
class FluentRibbonGroup(QWidget)
```

Titled cluster of large ribbon buttons (icon above text).

<details>
<summary>Code:</summary>

```python
class FluentRibbonGroup(QWidget):

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a ribbon group."""
        super().__init__(parent)
        self._title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(2)
        self._buttons = QHBoxLayout()
        self._buttons.setSpacing(2)
        layout.addLayout(self._buttons, 1)
        caption = CaptionLabel(title, self)
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(caption)

    def add_button(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QToolButton:
        """Append a large button."""
        button = FluentToolButton(text, self, icon=icon)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIconSize(QSize(ICON_SIZE_LARGE, ICON_SIZE_LARGE))
        button.setMinimumSize(56, 64)
        font = fluent_font(button.font(), TYPE_CAPTION)
        button.setFont(font)
        if slot is not None:
            button.clicked.connect(slot)
        self._buttons.addWidget(button)
        return button

    def title(self) -> str:
        """Return the group title."""
        return self._title
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None
```

Create a ribbon group.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(2)
        self._buttons = QHBoxLayout()
        self._buttons.setSpacing(2)
        layout.addLayout(self._buttons, 1)
        caption = CaptionLabel(title, self)
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(caption)
```

</details>

### ⚙️ Method `add_button`

```python
def add_button(self, text: str, icon: str = '', slot: Callable[[], None] | None = None) -> QToolButton
```

Append a large button.

<details>
<summary>Code:</summary>

```python
def add_button(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QToolButton:
        button = FluentToolButton(text, self, icon=icon)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIconSize(QSize(ICON_SIZE_LARGE, ICON_SIZE_LARGE))
        button.setMinimumSize(56, 64)
        font = fluent_font(button.font(), TYPE_CAPTION)
        button.setFont(font)
        if slot is not None:
            button.clicked.connect(slot)
        self._buttons.addWidget(button)
        return button
```

</details>

### ⚙️ Method `title`

```python
def title(self) -> str
```

Return the group title.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        return self._title
```

</details>

## 🏛️ Class `FluentRibbonTabBar`

```python
class FluentRibbonTabBar(FluentPivot)
```

Ribbon tab strip (a pivot with ribbon spacing).

<details>
<summary>Code:</summary>

```python
class FluentRibbonTabBar(FluentPivot):
```

</details>

## 🏛️ Class `FluentStatusBar`

```python
class FluentStatusBar(QStatusBar)
```

Status bar on the layer surface with a hairline top border.

<details>
<summary>Code:</summary>

```python
class FluentStatusBar(QStatusBar):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a status bar."""
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QStatusBar {{ background: transparent; color: {css(palette.text_secondary)};"
            f" border-top: 1px solid {css(palette.divider)}; }}"
            " QStatusBar::item { border: none; }",
        )
        font = QFont(self.font())
        self.setFont(fluent_font(font, TYPE_CAPTION))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a status bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QStatusBar {{ background: transparent; color: {css(palette.text_secondary)};"
            f" border-top: 1px solid {css(palette.divider)}; }}"
            " QStatusBar::item { border: none; }",
        )
        font = QFont(self.font())
        self.setFont(fluent_font(font, TYPE_CAPTION))
```

</details>

## 🏛️ Class `FluentToolBar`

```python
class FluentToolBar(QToolBar)
```

Tool bar with subtle buttons and hairline separators.

<details>
<summary>Code:</summary>

```python
class FluentToolBar(QToolBar):

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        """Create a tool bar."""
        super().__init__(title, parent)
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        bind_theme(self, self.refresh_theme)

    def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        """Append an action with a Lucide icon."""
        action = _lucide_action(self, self, text, icon, slot)
        self.addAction(action)
        return action

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon colors."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QToolBar {{ background: transparent; border: none; spacing: {SPACE_XS}px; padding: {SPACE_XS}px; }}"
            f" QToolBar::separator {{ background: {css(palette.divider)}; width: 1px; margin: 6px 4px; }}"
            f"{subtle_button_qss(palette, 'QToolBar QToolButton')}",
        )
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str = '', parent: QWidget | None = None) -> None
```

Create a tool bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `add_lucide_action`

```python
def add_lucide_action(self, text: str, icon: str = '', slot: Callable[[], None] | None = None) -> QAction
```

Append an action with a Lucide icon.

<details>
<summary>Code:</summary>

```python
def add_lucide_action(self, text: str, icon: str = "", slot: Callable[[], None] | None = None) -> QAction:
        action = _lucide_action(self, self, text, icon, slot)
        self.addAction(action)
        return action
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and icon colors.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QToolBar {{ background: transparent; border: none; spacing: {SPACE_XS}px; padding: {SPACE_XS}px; }}"
            f" QToolBar::separator {{ background: {css(palette.divider)}; width: 1px; margin: 6px 4px; }}"
            f"{subtle_button_qss(palette, 'QToolBar QToolButton')}",
        )
        for action in self.actions():
            name = action.property("hskLucideIcon")
            if isinstance(name, str) and name:
                action.setIcon(themed_icon(name, palette))
```

</details>
