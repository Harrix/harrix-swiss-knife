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
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
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
        self.setFixedSize(CARD_GRID_CELL_WIDTH, CARD_GRID_CELL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(title)

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 2, 4, 2)
        root.setSpacing(2)

        host_size = icon_size + 4
        icon_host = QWidget(self)
        icon_host.setFixedSize(host_size, host_size)

        icon_label = QLabel(icon_host)
        icon_label.setPixmap(create_emoji_icon(icon_emoji or "📝", icon_size).pixmap(icon_size, icon_size))
        icon_label.setGeometry(2, 2, icon_size, icon_size)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        if show_ai_screenshot:
            button = QPushButton(icon_host)
            button.setIcon(create_emoji_icon(AI_SCREENSHOT_CARD_EMOJI, 14))
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

        root.addWidget(icon_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        root.addWidget(title_label, stretch=1)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Treat a left click on the card body as selecting the choice."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
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
        self.setFixedSize(CARD_GRID_CELL_WIDTH, CARD_GRID_CELL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(title)

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 2, 4, 2)
        root.setSpacing(2)

        host_size = icon_size + 4
        icon_host = QWidget(self)
        icon_host.setFixedSize(host_size, host_size)

        icon_label = QLabel(icon_host)
        icon_label.setPixmap(create_emoji_icon(icon_emoji or "📝", icon_size).pixmap(icon_size, icon_size))
        icon_label.setGeometry(2, 2, icon_size, icon_size)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        if show_ai_screenshot:
            button = QPushButton(icon_host)
            button.setIcon(create_emoji_icon(AI_SCREENSHOT_CARD_EMOJI, 14))
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

        root.addWidget(icon_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        root.addWidget(title_label, stretch=1)
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

    if list_widget.count() > 0:
        list_widget.setCurrentRow(0)
```

</details>
