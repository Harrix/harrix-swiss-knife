---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_markdown_choice_cards.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IconChoiceCard`](#%EF%B8%8F-class-iconchoicecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `apply_grid_metrics`](#%EF%B8%8F-method-apply_grid_metrics)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `preferred_height`](#%EF%B8%8F-method-preferred_height)
- [🔧 Function `populate_icon_choice_cards`](#-function-populate_icon_choice_cards)

</details>

## 🏛️ Class `IconChoiceCard`

```python
class IconChoiceCard(QWidget)
```

Compact icon+title card; optional corner button starts AI screenshot fill.

<details>
<summary>Code:</summary>

```python
class IconChoiceCard(QWidget):

    selected = Signal()
    ai_screenshot_requested = Signal()

    def __init__(
        self,
        icon_emoji: str,
        title: str,
        *,
        show_ai_screenshot: bool = False,
        icon_size: int = CARD_ICON_SIZE,
        parent: QWidget | None = None,
    ) -> None:
        """Build a card matching the shared action-card grid cell size."""
        super().__init__(parent)
        self._icon_emoji = icon_emoji or "📝"
        self._title = title
        self._icon_size = icon_size
        self._ai_button: QPushButton | None = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(title)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(_CARD_MARGIN_H, _CARD_MARGIN_V, _CARD_MARGIN_H, _CARD_MARGIN_V)
        self._root.setSpacing(_CARD_SPACING)

        host_size = icon_size + _ICON_HOST_PAD
        self._icon_host = QWidget(self)
        self._icon_host.setFixedSize(host_size, host_size)

        self._icon_label = QLabel(self._icon_host)
        self._icon_label.setPixmap(create_emoji_icon(self._icon_emoji, icon_size).pixmap(icon_size, icon_size))
        self._icon_label.setGeometry(2, 2, icon_size, icon_size)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        if show_ai_screenshot:
            button = QPushButton(self._icon_host)
            button.setIcon(create_lucide_icon(AI_SCREENSHOT_CARD_ICON, 14))
            button.setIconSize(QSize(14, 14))
            button.setFixedSize(22, 22)
            button.setFlat(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(AI_SCREENSHOT_TOOLTIP)
            button.move(max(0, host_size - 22), 0)
            button.setStyleSheet(
                "QPushButton {"
                " background: palette(base);"
                " border-radius: 4px;"
                " border: 1px solid palette(mid);"
                " padding: 0;"
                "}"
                "QPushButton:hover { background: palette(alternate-base); }"
            )
            button.clicked.connect(self.ai_screenshot_requested.emit)
            self._ai_button = button

        self._root.addWidget(self._icon_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._title_label = QLabel(title)
        self._title_label.setWordWrap(True)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._root.addWidget(self._title_label, stretch=1)

        self.apply_grid_metrics(CARD_GRID_CELL_WIDTH, icon_size, CARD_GRID_CELL_HEIGHT)

    def apply_grid_metrics(self, cell_width: int, icon_size: int, cell_height: int) -> None:
        """Resize icon, host, and fixed card size to the shared grid cell."""
        self._icon_size = icon_size
        host_size = icon_size + _ICON_HOST_PAD
        self._icon_host.setFixedSize(host_size, host_size)
        self._icon_label.setPixmap(create_emoji_icon(self._icon_emoji, icon_size).pixmap(icon_size, icon_size))
        self._icon_label.setGeometry(2, 2, icon_size, icon_size)
        if self._ai_button is not None:
            self._ai_button.move(max(0, host_size - 22), 0)
        self.setFixedSize(max(1, cell_width), max(1, cell_height))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Treat a left click on the card body as selecting the choice."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def preferred_height(self, cell_width: int, icon_size: int) -> int:
        """Return height needed for the icon and fully wrapped title."""
        host_size = icon_size + _ICON_HOST_PAD
        text_width = max(1, cell_width - 2 * _CARD_MARGIN_H)
        text_height = self._title_label.heightForWidth(text_width)
        if text_height <= 0:
            metrics = self._title_label.fontMetrics()
            text_height = metrics.boundingRect(
                0,
                0,
                text_width,
                10_000,
                Qt.TextFlag.TextWordWrap,
                self._title,
            ).height()
        return 2 * _CARD_MARGIN_V + host_size + _CARD_SPACING + text_height + _TITLE_BOTTOM_PAD
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon_emoji: str, title: str, *, show_ai_screenshot: bool = False, icon_size: int = CARD_ICON_SIZE, parent: QWidget | None = None) -> None
```

Build a card matching the shared action-card grid cell size.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        icon_emoji: str,
        title: str,
        *,
        show_ai_screenshot: bool = False,
        icon_size: int = CARD_ICON_SIZE,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_emoji = icon_emoji or "📝"
        self._title = title
        self._icon_size = icon_size
        self._ai_button: QPushButton | None = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(title)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(_CARD_MARGIN_H, _CARD_MARGIN_V, _CARD_MARGIN_H, _CARD_MARGIN_V)
        self._root.setSpacing(_CARD_SPACING)

        host_size = icon_size + _ICON_HOST_PAD
        self._icon_host = QWidget(self)
        self._icon_host.setFixedSize(host_size, host_size)

        self._icon_label = QLabel(self._icon_host)
        self._icon_label.setPixmap(create_emoji_icon(self._icon_emoji, icon_size).pixmap(icon_size, icon_size))
        self._icon_label.setGeometry(2, 2, icon_size, icon_size)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        if show_ai_screenshot:
            button = QPushButton(self._icon_host)
            button.setIcon(create_lucide_icon(AI_SCREENSHOT_CARD_ICON, 14))
            button.setIconSize(QSize(14, 14))
            button.setFixedSize(22, 22)
            button.setFlat(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(AI_SCREENSHOT_TOOLTIP)
            button.move(max(0, host_size - 22), 0)
            button.setStyleSheet(
                "QPushButton {"
                " background: palette(base);"
                " border-radius: 4px;"
                " border: 1px solid palette(mid);"
                " padding: 0;"
                "}"
                "QPushButton:hover { background: palette(alternate-base); }"
            )
            button.clicked.connect(self.ai_screenshot_requested.emit)
            self._ai_button = button

        self._root.addWidget(self._icon_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._title_label = QLabel(title)
        self._title_label.setWordWrap(True)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._root.addWidget(self._title_label, stretch=1)

        self.apply_grid_metrics(CARD_GRID_CELL_WIDTH, icon_size, CARD_GRID_CELL_HEIGHT)
```

</details>

### ⚙️ Method `apply_grid_metrics`

```python
def apply_grid_metrics(self, cell_width: int, icon_size: int, cell_height: int) -> None
```

Resize icon, host, and fixed card size to the shared grid cell.

<details>
<summary>Code:</summary>

```python
def apply_grid_metrics(self, cell_width: int, icon_size: int, cell_height: int) -> None:
        self._icon_size = icon_size
        host_size = icon_size + _ICON_HOST_PAD
        self._icon_host.setFixedSize(host_size, host_size)
        self._icon_label.setPixmap(create_emoji_icon(self._icon_emoji, icon_size).pixmap(icon_size, icon_size))
        self._icon_label.setGeometry(2, 2, icon_size, icon_size)
        if self._ai_button is not None:
            self._ai_button.move(max(0, host_size - 22), 0)
        self.setFixedSize(max(1, cell_width), max(1, cell_height))
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Treat a left click on the card body as selecting the choice.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `preferred_height`

```python
def preferred_height(self, cell_width: int, icon_size: int) -> int
```

Return height needed for the icon and fully wrapped title.

<details>
<summary>Code:</summary>

```python
def preferred_height(self, cell_width: int, icon_size: int) -> int:
        host_size = icon_size + _ICON_HOST_PAD
        text_width = max(1, cell_width - 2 * _CARD_MARGIN_H)
        text_height = self._title_label.heightForWidth(text_width)
        if text_height <= 0:
            metrics = self._title_label.fontMetrics()
            text_height = metrics.boundingRect(
                0,
                0,
                text_width,
                10_000,
                Qt.TextFlag.TextWordWrap,
                self._title,
            ).height()
        return 2 * _CARD_MARGIN_V + host_size + _CARD_SPACING + text_height + _TITLE_BOTTOM_PAD
```

</details>

## 🔧 Function `populate_icon_choice_cards`

```python
def populate_icon_choice_cards(list_widget: QListWidget, choices: list[tuple[str, str]], *, icon_size: int = CARD_ICON_SIZE, ai_screenshot_titles: Collection[str] | None = None, on_select: Callable[[str], None] | None = None, on_ai_screenshot: Callable[[str], None] | None = None) -> None
```

Fill `list_widget` with icon cards; optional AI-screenshot buttons on templates.

<details>
<summary>Code:</summary>

```python
def populate_icon_choice_cards(
    list_widget: QListWidget,
    choices: list[tuple[str, str]],
    *,
    icon_size: int = CARD_ICON_SIZE,
    ai_screenshot_titles: Collection[str] | None = None,
    on_select: Callable[[str], None] | None = None,
    on_ai_screenshot: Callable[[str], None] | None = None,
) -> None:
    list_widget.clear()
    ai_titles = set(ai_screenshot_titles or ())

    for icon_emoji, title in choices:
        item = QListWidgetItem(list_widget)
        item.setData(Qt.ItemDataRole.UserRole, title)
        item.setData(ICON_CHOICE_ACTION_ROLE, ICON_CHOICE_ACTION_SELECT)
        item.setSizeHint(QSize(CARD_GRID_CELL_WIDTH, CARD_GRID_CELL_HEIGHT))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        show_ai = title in ai_titles and on_ai_screenshot is not None
        card = IconChoiceCard(
            icon_emoji,
            title,
            show_ai_screenshot=show_ai,
            icon_size=icon_size,
            parent=list_widget,
        )

        def _select(choice_title: str = title, list_item: QListWidgetItem = item) -> None:
            list_widget.setCurrentItem(list_item)
            list_item.setData(ICON_CHOICE_ACTION_ROLE, ICON_CHOICE_ACTION_SELECT)
            if on_select is not None:
                on_select(choice_title)

        def _ai(choice_title: str = title, list_item: QListWidgetItem = item) -> None:
            list_widget.setCurrentItem(list_item)
            list_item.setData(ICON_CHOICE_ACTION_ROLE, ICON_CHOICE_ACTION_AI_SCREENSHOT)
            if on_ai_screenshot is not None:
                on_ai_screenshot(choice_title)

        card.selected.connect(_select)
        if show_ai:
            card.ai_screenshot_requested.connect(_ai)

        list_widget.setItemWidget(item, card)

    sync_action_card_grid(list_widget)
    if list_widget.count() > 0:
        list_widget.setCurrentRow(0)
```

</details>
