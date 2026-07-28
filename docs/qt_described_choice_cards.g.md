---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_described_choice_cards.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DescribedChoiceCard`](#%EF%B8%8F-class-describedchoicecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
- [🔧 Function `add_described_action_card`](#-function-add_described_action_card)
- [🔧 Function `configure_described_choice_card_grid`](#-function-configure_described_choice_card_grid)
- [🔧 Function `populate_described_choice_cards`](#-function-populate_described_choice_cards)

</details>

## 🏛️ Class `DescribedChoiceCard`

```python
class DescribedChoiceCard(QWidget)
```

Horizontal card: emoji icon on the left, title and hint on the right.

<details>
<summary>Code:</summary>

```python
class DescribedChoiceCard(QWidget):

    selected = Signal()

    def __init__(
        self,
        icon_emoji: str,
        title: str,
        description: str,
        *,
        icon_size: int = DESCRIBED_CARD_ICON_SIZE,
        parent: QWidget | None = None,
    ) -> None:
        """Build a bordered card matching DevToys-style command tiles."""
        super().__init__(parent)
        self.setFixedSize(DESCRIBED_CARD_WIDTH - CARD_SPACING, DESCRIBED_CARD_HEIGHT - CARD_SPACING)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title}\n{description}" if description else title)
        self.setObjectName("DescribedChoiceCard")
        self.setStyleSheet(
            "#DescribedChoiceCard {"
            " background: palette(base);"
            " border: 1px solid palette(mid);"
            " border-radius: 8px;"
            "}"
            "#DescribedChoiceCard:hover {"
            " background: palette(alternate-base);"
            "}"
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)

        icon_label = QLabel(self)
        icon_label.setPixmap(create_emoji_icon(icon_emoji or "📝", icon_size).pixmap(icon_size, icon_size))
        icon_label.setFixedSize(icon_size, icon_size)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        root.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        text_column.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_font = desc_label.font()
            desc_font.setPointSize(9)
            desc_label.setFont(desc_font)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: palette(mid);")
            desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
            text_column.addWidget(desc_label)

        text_column.addStretch(1)
        root.addLayout(text_column, stretch=1)

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
def __init__(self, icon_emoji: str, title: str, description: str) -> None
```

Build a bordered card matching DevToys-style command tiles.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        icon_emoji: str,
        title: str,
        description: str,
        *,
        icon_size: int = DESCRIBED_CARD_ICON_SIZE,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(DESCRIBED_CARD_WIDTH - CARD_SPACING, DESCRIBED_CARD_HEIGHT - CARD_SPACING)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{title}\n{description}" if description else title)
        self.setObjectName("DescribedChoiceCard")
        self.setStyleSheet(
            "#DescribedChoiceCard {"
            " background: palette(base);"
            " border: 1px solid palette(mid);"
            " border-radius: 8px;"
            "}"
            "#DescribedChoiceCard:hover {"
            " background: palette(alternate-base);"
            "}"
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)

        icon_label = QLabel(self)
        icon_label.setPixmap(create_emoji_icon(icon_emoji or "📝", icon_size).pixmap(icon_size, icon_size))
        icon_label.setFixedSize(icon_size, icon_size)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        root.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        text_column.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_font = desc_label.font()
            desc_font.setPointSize(9)
            desc_label.setFont(desc_font)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: palette(mid);")
            desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
            text_column.addWidget(desc_label)

        text_column.addStretch(1)
        root.addLayout(text_column, stretch=1)
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

## 🔧 Function `add_described_action_card`

```python
def add_described_action_card(list_widget: QListWidget) -> QListWidgetItem
```

Append one described card with arbitrary `UserRole` payload.

<details>
<summary>Code:</summary>

```python
def add_described_action_card(
    list_widget: QListWidget,
    *,
    icon: str,
    title: str,
    description: str,
    user_data: object,
    on_select: Callable[[], None] | None = None,
) -> QListWidgetItem:
    item = QListWidgetItem(list_widget)
    item.setData(Qt.ItemDataRole.UserRole, user_data)
    item.setSizeHint(QSize(DESCRIBED_CARD_WIDTH, DESCRIBED_CARD_HEIGHT))

    card = DescribedChoiceCard(
        icon,
        title,
        description,
        parent=list_widget,
    )

    def _select(list_item: QListWidgetItem = item) -> None:
        list_widget.setCurrentItem(list_item)
        if on_select is not None:
            on_select()

    card.selected.connect(_select)
    list_widget.setItemWidget(item, card)
    return item
```

</details>

## 🔧 Function `configure_described_choice_card_grid`

```python
def configure_described_choice_card_grid(list_widget: QListWidget) -> None
```

Apply a wide horizontal-card grid layout for described choices.

<details>
<summary>Code:</summary>

```python
def configure_described_choice_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None:
    configure_action_card_grid(list_widget, min_height=min_height)
    list_widget.setIconSize(QSize(DESCRIBED_CARD_ICON_SIZE, DESCRIBED_CARD_ICON_SIZE))
    list_widget.setGridSize(QSize(DESCRIBED_CARD_WIDTH, DESCRIBED_CARD_HEIGHT))
```

</details>

## 🔧 Function `populate_described_choice_cards`

```python
def populate_described_choice_cards(list_widget: QListWidget, choices: list[tuple[str, str, str]]) -> None
```

Fill `list_widget` with horizontal icon+title+description cards.

<details>
<summary>Code:</summary>

```python
def populate_described_choice_cards(
    list_widget: QListWidget,
    choices: list[tuple[str, str, str]],
    *,
    icon_size: int = DESCRIBED_CARD_ICON_SIZE,
    on_select: Callable[[str], None] | None = None,
) -> None:
    list_widget.clear()

    for icon_emoji, title, description in choices:
        item = QListWidgetItem(list_widget)
        item.setData(Qt.ItemDataRole.UserRole, title)
        item.setSizeHint(QSize(DESCRIBED_CARD_WIDTH, DESCRIBED_CARD_HEIGHT))

        card = DescribedChoiceCard(
            icon_emoji,
            title,
            description,
            icon_size=icon_size,
            parent=list_widget,
        )

        def _select(choice_title: str = title, list_item: QListWidgetItem = item) -> None:
            list_widget.setCurrentItem(list_item)
            if on_select is not None:
                on_select(choice_title)

        card.selected.connect(_select)
        list_widget.setItemWidget(item, card)

    if list_widget.count() > 0:
        list_widget.setCurrentRow(0)
```

</details>
