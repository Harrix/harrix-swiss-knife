---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_screenshot_fab.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FinanceAiScreenshotFab`](#%EF%B8%8F-class-financeaiscreenshotfab)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `hide_for_finance`](#%EF%B8%8F-method-hide_for_finance)
  - [⚙️ Method `place_on_screen`](#%EF%B8%8F-method-place_on_screen)
  - [⚙️ Method `show_for_finance`](#%EF%B8%8F-method-show_for_finance)

</details>

## 🏛️ Class `FinanceAiScreenshotFab`

```python
class FinanceAiScreenshotFab(QWidget)
```

Circular stay-on-top camera control on the right edge of the screen.

Unparented `Tool` window so it does not minimize with the Finance window or
other apps. Finance shows and hides this while the tracker is open.

<details>
<summary>Code:</summary>

```python
class FinanceAiScreenshotFab(QWidget):

    def __init__(self, on_click: Callable[[], None]) -> None:
        """Create the floating button; call `show_for_finance` when Finance opens."""
        super().__init__(None)
        self.setObjectName("financeAiScreenshotFab")
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setFixedSize(_FAB_SIZE, _FAB_SIZE)

        button = QPushButton(self)
        button.setObjectName("financeAiScreenshotFabButton")
        button.setFixedSize(_FAB_SIZE, _FAB_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolTip("Capture screen region for Add with AI")
        button.setStyleSheet(_fab_button_qss())
        apply_lucide_button_icon(button, _SCREENSHOT_ICON, icon_size=ICON_SIZE_LARGE)
        button.clicked.connect(on_click)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)

    def hide_for_finance(self) -> None:
        """Hide when Finance closes or is intentionally hidden."""
        self.hide()

    def place_on_screen(self) -> None:
        """Pin to the right edge, vertically centered on the current screen."""
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.right() - self.width() - _EDGE_MARGIN
        y = geo.center().y() - self.height() // 2
        self.move(x, y)

    def show_for_finance(self) -> None:
        """Show and re-place the floating control."""
        self.place_on_screen()
        self.show()
        self.raise_()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, on_click: Callable[[], None]) -> None
```

Create the floating button; call [`show_for_finance`](#%EF%B8%8F-method-show_for_finance) when Finance opens.

<details>
<summary>Code:</summary>

```python
def __init__(self, on_click: Callable[[], None]) -> None:
        super().__init__(None)
        self.setObjectName("financeAiScreenshotFab")
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setFixedSize(_FAB_SIZE, _FAB_SIZE)

        button = QPushButton(self)
        button.setObjectName("financeAiScreenshotFabButton")
        button.setFixedSize(_FAB_SIZE, _FAB_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolTip("Capture screen region for Add with AI")
        button.setStyleSheet(_fab_button_qss())
        apply_lucide_button_icon(button, _SCREENSHOT_ICON, icon_size=ICON_SIZE_LARGE)
        button.clicked.connect(on_click)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)
```

</details>

### ⚙️ Method `hide_for_finance`

```python
def hide_for_finance(self) -> None
```

Hide when Finance closes or is intentionally hidden.

<details>
<summary>Code:</summary>

```python
def hide_for_finance(self) -> None:
        self.hide()
```

</details>

### ⚙️ Method `place_on_screen`

```python
def place_on_screen(self) -> None
```

Pin to the right edge, vertically centered on the current screen.

<details>
<summary>Code:</summary>

```python
def place_on_screen(self) -> None:
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.right() - self.width() - _EDGE_MARGIN
        y = geo.center().y() - self.height() // 2
        self.move(x, y)
```

</details>

### ⚙️ Method `show_for_finance`

```python
def show_for_finance(self) -> None
```

Show and re-place the floating control.

<details>
<summary>Code:</summary>

```python
def show_for_finance(self) -> None:
        self.place_on_screen()
        self.show()
        self.raise_()
```

</details>
