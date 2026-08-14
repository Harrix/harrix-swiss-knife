---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_described_choice_cards.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DescribedCardMetrics`](#%EF%B8%8F-class-describedcardmetrics)
- [🏛️ Class `DescribedChoiceCard`](#%EF%B8%8F-class-describedchoicecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `apply_metrics`](#%EF%B8%8F-method-apply_metrics)
  - [⚙️ Method `content_height`](#%EF%B8%8F-method-content_height)
  - [⚙️ Method `contextMenuEvent`](#%EF%B8%8F-method-contextmenuevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
- [🔧 Function `add_described_action_card`](#-function-add_described_action_card)
- [🔧 Function `apply_described_card_grid_metrics`](#-function-apply_described_card_grid_metrics)
- [🔧 Function `configure_described_choice_card_grid`](#-function-configure_described_choice_card_grid)
- [🔧 Function `described_card_metrics_of`](#-function-described_card_metrics_of)
- [🔧 Function `described_card_text_width`](#-function-described_card_text_width)
- [🔧 Function `metrics_for_scale`](#-function-metrics_for_scale)
- [🔧 Function `populate_described_choice_cards`](#-function-populate_described_choice_cards)
- [🔧 Function `resolve_described_card_metrics`](#-function-resolve_described_card_metrics)
- [🔧 Function `sync_described_choice_card_grid`](#-function-sync_described_choice_card_grid)

</details>

## 🏛️ Class `DescribedCardMetrics`

```python
class DescribedCardMetrics
```

Pixel metrics for one described card at a given scale.

<details>
<summary>Code:</summary>

```python
class DescribedCardMetrics:

    scale: float
    width: int
    height: int
    icon_size: int
    title_pt: int
    desc_pt: int
    margin_h: int
    margin_v: int
    icon_gap: int
    text_gap: int
```

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
    context_menu_requested = Signal(QPoint)

    def __init__(
        self,
        icon_emoji: str,
        title: str,
        description: str,
        *,
        icon_size: int = DESCRIBED_CARD_ICON_SIZE,
        metrics: DescribedCardMetrics | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Build a bordered card matching DevToys-style command tiles."""
        super().__init__(parent)
        self._icon_emoji = icon_emoji or "📝"
        self._title = title
        self._description = description
        self._root = QHBoxLayout(self)
        self._icon_label = QLabel(self)
        self._title_label = QLabel(title)
        self._desc_label: QLabel | None = None
        self._text_column = QVBoxLayout()

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

        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        self._text_column.setContentsMargins(0, 0, 0, 0)
        self._text_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._title_label.setWordWrap(True)
        self._title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._text_column.addWidget(self._title_label)

        if description:
            self._desc_label = QLabel(description)
            self._desc_label.setWordWrap(True)
            self._desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self._desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            self._desc_label.setStyleSheet("color: palette(mid);")
            self._desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
            self._text_column.addWidget(self._desc_label)

        resolved = metrics if metrics is not None else metrics_for_scale(icon_size / DESCRIBED_CARD_ICON_SIZE)
        self.apply_metrics(resolved)

    def apply_metrics(self, metrics: DescribedCardMetrics) -> None:
        """Apply scaled size, icon, fonts, and paddings."""
        self.setFixedSize(metrics.width - CARD_SPACING, metrics.height - CARD_SPACING)
        self._root.setContentsMargins(metrics.margin_h, metrics.margin_v, metrics.margin_h, metrics.margin_v)
        self._root.setSpacing(metrics.icon_gap)
        self._text_column.setSpacing(metrics.text_gap)

        self._icon_label.setPixmap(
            create_emoji_icon(self._icon_emoji, metrics.icon_size).pixmap(metrics.icon_size, metrics.icon_size),
        )
        self._icon_label.setFixedSize(metrics.icon_size, metrics.icon_size)

        text_width = described_card_text_width(metrics)

        title_font = self._title_label.font()
        title_font.setPointSize(metrics.title_pt)
        title_font.setBold(True)
        self._title_label.setFont(title_font)
        # A word-wrapped label in a fixed-size card gets no heightForWidth from the layout,
        # so pin every wrapped line explicitly to keep the last line from being cut off.
        self._title_label.setFixedHeight(self._title_label.heightForWidth(text_width))

        if self._desc_label is not None:
            desc_font = self._desc_label.font()
            desc_font.setPointSize(metrics.desc_pt)
            self._desc_label.setFont(desc_font)
            self._desc_label.setFixedHeight(self._desc_label.heightForWidth(text_width))

        if self._root.count() == 0:
            self._root.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)
            self._root.addLayout(self._text_column, stretch=1)

    def content_height(self, metrics: DescribedCardMetrics) -> int:
        """Return the grid cell height that shows the wrapped title and description in full.

        Args:

        - `metrics` (`DescribedCardMetrics`): Metrics already applied to this card.

        """
        text_width = described_card_text_width(metrics)
        text_height = self._title_label.heightForWidth(text_width)
        if self._desc_label is not None:
            text_height += metrics.text_gap + self._desc_label.heightForWidth(text_width)
        return max(text_height, metrics.icon_size) + 2 * metrics.margin_v + CARD_SPACING

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        """Emit a context-menu request with the global cursor position."""
        self.context_menu_requested.emit(event.globalPos())
        event.accept()

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
def __init__(self, icon_emoji: str, title: str, description: str, *, icon_size: int = DESCRIBED_CARD_ICON_SIZE, metrics: DescribedCardMetrics | None = None, parent: QWidget | None = None) -> None
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
        metrics: DescribedCardMetrics | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_emoji = icon_emoji or "📝"
        self._title = title
        self._description = description
        self._root = QHBoxLayout(self)
        self._icon_label = QLabel(self)
        self._title_label = QLabel(title)
        self._desc_label: QLabel | None = None
        self._text_column = QVBoxLayout()

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

        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)

        self._text_column.setContentsMargins(0, 0, 0, 0)
        self._text_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._title_label.setWordWrap(True)
        self._title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._text_column.addWidget(self._title_label)

        if description:
            self._desc_label = QLabel(description)
            self._desc_label.setWordWrap(True)
            self._desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self._desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            self._desc_label.setStyleSheet("color: palette(mid);")
            self._desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
            self._text_column.addWidget(self._desc_label)

        resolved = metrics if metrics is not None else metrics_for_scale(icon_size / DESCRIBED_CARD_ICON_SIZE)
        self.apply_metrics(resolved)
```

</details>

### ⚙️ Method `apply_metrics`

```python
def apply_metrics(self, metrics: DescribedCardMetrics) -> None
```

Apply scaled size, icon, fonts, and paddings.

<details>
<summary>Code:</summary>

```python
def apply_metrics(self, metrics: DescribedCardMetrics) -> None:
        self.setFixedSize(metrics.width - CARD_SPACING, metrics.height - CARD_SPACING)
        self._root.setContentsMargins(metrics.margin_h, metrics.margin_v, metrics.margin_h, metrics.margin_v)
        self._root.setSpacing(metrics.icon_gap)
        self._text_column.setSpacing(metrics.text_gap)

        self._icon_label.setPixmap(
            create_emoji_icon(self._icon_emoji, metrics.icon_size).pixmap(metrics.icon_size, metrics.icon_size),
        )
        self._icon_label.setFixedSize(metrics.icon_size, metrics.icon_size)

        text_width = described_card_text_width(metrics)

        title_font = self._title_label.font()
        title_font.setPointSize(metrics.title_pt)
        title_font.setBold(True)
        self._title_label.setFont(title_font)
        # A word-wrapped label in a fixed-size card gets no heightForWidth from the layout,
        # so pin every wrapped line explicitly to keep the last line from being cut off.
        self._title_label.setFixedHeight(self._title_label.heightForWidth(text_width))

        if self._desc_label is not None:
            desc_font = self._desc_label.font()
            desc_font.setPointSize(metrics.desc_pt)
            self._desc_label.setFont(desc_font)
            self._desc_label.setFixedHeight(self._desc_label.heightForWidth(text_width))

        if self._root.count() == 0:
            self._root.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)
            self._root.addLayout(self._text_column, stretch=1)
```

</details>

### ⚙️ Method `content_height`

```python
def content_height(self, metrics: DescribedCardMetrics) -> int
```

Return the grid cell height that shows the wrapped title and description in full.

Args:

- `metrics` ([`DescribedCardMetrics`](#%EF%B8%8F-class-describedcardmetrics)): Metrics already applied to this card.

<details>
<summary>Code:</summary>

```python
def content_height(self, metrics: DescribedCardMetrics) -> int:
        text_width = described_card_text_width(metrics)
        text_height = self._title_label.heightForWidth(text_width)
        if self._desc_label is not None:
            text_height += metrics.text_gap + self._desc_label.heightForWidth(text_width)
        return max(text_height, metrics.icon_size) + 2 * metrics.margin_v + CARD_SPACING
```

</details>

### ⚙️ Method `contextMenuEvent`

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None
```

Emit a context-menu request with the global cursor position.

<details>
<summary>Code:</summary>

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        self.context_menu_requested.emit(event.globalPos())
        event.accept()
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
def add_described_action_card(list_widget: QListWidget, *, icon: str, title: str, description: str, user_data: object, on_select: Callable[[], None] | None = None, on_context_menu: Callable[[object, QPoint], None] | None = None) -> QListWidgetItem
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
    on_context_menu: Callable[[object, QPoint], None] | None = None,
) -> QListWidgetItem:
    metrics = described_card_metrics_of(list_widget)
    item = QListWidgetItem(list_widget)
    item.setData(Qt.ItemDataRole.UserRole, user_data)
    item.setSizeHint(QSize(metrics.width, metrics.height))

    card = DescribedChoiceCard(
        icon,
        title,
        description,
        metrics=metrics,
        parent=list_widget,
    )

    def _select(list_item: QListWidgetItem = item) -> None:
        list_widget.setCurrentItem(list_item)
        if on_select is not None:
            on_select()

    def _on_card_context_menu(global_pos: QPoint, data: object = user_data) -> None:
        if on_context_menu is not None:
            on_context_menu(data, global_pos)

    card.selected.connect(_select)
    card.context_menu_requested.connect(_on_card_context_menu)
    list_widget.setItemWidget(item, card)
    if card.content_height(metrics) > metrics.height:
        _apply_fitted_grid_height(list_widget, metrics)
    return item
```

</details>

## 🔧 Function `apply_described_card_grid_metrics`

```python
def apply_described_card_grid_metrics(list_widget: QListWidget, metrics: DescribedCardMetrics) -> DescribedCardMetrics
```

Set grid cell size and update every described card widget.

Returns:

- [`DescribedCardMetrics`](#%EF%B8%8F-class-describedcardmetrics): Applied metrics, with the height grown to the tallest card text.

<details>
<summary>Code:</summary>

```python
def apply_described_card_grid_metrics(
    list_widget: QListWidget,
    metrics: DescribedCardMetrics,
) -> DescribedCardMetrics:
    list_widget.setIconSize(QSize(metrics.icon_size, metrics.icon_size))
    for _item, card in _described_cards(list_widget):
        card.apply_metrics(metrics)
    return _apply_fitted_grid_height(list_widget, metrics)
```

</details>

## 🔧 Function `configure_described_choice_card_grid`

```python
def configure_described_choice_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None
```

Apply a wide horizontal-card grid layout for described choices.

<details>
<summary>Code:</summary>

```python
def configure_described_choice_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None:
    configure_action_card_grid(list_widget, min_height=min_height)
    apply_described_card_grid_metrics(list_widget, metrics_for_scale(1.0))
```

</details>

## 🔧 Function `described_card_metrics_of`

```python
def described_card_metrics_of(list_widget: QListWidget) -> DescribedCardMetrics
```

Return metrics last applied to `list_widget`, or full-size defaults.

<details>
<summary>Code:</summary>

```python
def described_card_metrics_of(list_widget: QListWidget) -> DescribedCardMetrics:
    metrics = getattr(list_widget, _METRICS_ATTR, None)
    if isinstance(metrics, DescribedCardMetrics):
        return metrics
    return metrics_for_scale(1.0)
```

</details>

## 🔧 Function `described_card_text_width`

```python
def described_card_text_width(metrics: DescribedCardMetrics) -> int
```

Return the width of the title and description column inside a card.

<details>
<summary>Code:</summary>

```python
def described_card_text_width(metrics: DescribedCardMetrics) -> int:
    return max(1, metrics.width - CARD_SPACING - 2 * metrics.margin_h - metrics.icon_size - metrics.icon_gap)
```

</details>

## 🔧 Function `metrics_for_scale`

```python
def metrics_for_scale(scale: float) -> DescribedCardMetrics
```

Build card metrics for `scale` (clamped to `(0, 1]`).

<details>
<summary>Code:</summary>

```python
def metrics_for_scale(scale: float) -> DescribedCardMetrics:
    scale = min(1.0, max(0.01, scale))
    return DescribedCardMetrics(
        scale=scale,
        width=max(1, round(DESCRIBED_CARD_WIDTH * scale)),
        height=max(1, round(DESCRIBED_CARD_HEIGHT * scale)),
        icon_size=max(16, round(DESCRIBED_CARD_ICON_SIZE * scale)),
        title_pt=max(8, round(DESCRIBED_CARD_TITLE_PT * scale)),
        desc_pt=max(7, round(DESCRIBED_CARD_DESC_PT * scale)),
        margin_h=max(6, round(DESCRIBED_CARD_MARGIN_H * scale)),
        margin_v=max(6, round(DESCRIBED_CARD_MARGIN_V * scale)),
        icon_gap=max(6, round(DESCRIBED_CARD_ICON_GAP * scale)),
        text_gap=max(2, round(DESCRIBED_CARD_TEXT_GAP * scale)),
    )
```

</details>

## 🔧 Function `populate_described_choice_cards`

```python
def populate_described_choice_cards(list_widget: QListWidget, choices: list[tuple[str, str, str]], *, icon_size: int = DESCRIBED_CARD_ICON_SIZE, on_select: Callable[[str], None] | None = None) -> None
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
    metrics = described_card_metrics_of(list_widget)
    if icon_size != DESCRIBED_CARD_ICON_SIZE:
        metrics = metrics_for_scale(icon_size / DESCRIBED_CARD_ICON_SIZE)
        apply_described_card_grid_metrics(list_widget, metrics)
    # Drop the height fitted to the removed cards; the new ones refit it below.
    metrics = replace(metrics, height=metrics_for_scale(metrics.scale).height)

    for icon_emoji, title, description in choices:
        item = QListWidgetItem(list_widget)
        item.setData(Qt.ItemDataRole.UserRole, title)
        item.setSizeHint(QSize(metrics.width, metrics.height))

        card = DescribedChoiceCard(
            icon_emoji,
            title,
            description,
            metrics=metrics,
            parent=list_widget,
        )

        def _select(choice_title: str = title, list_item: QListWidgetItem = item) -> None:
            list_widget.setCurrentItem(list_item)
            if on_select is not None:
                on_select(choice_title)

        card.selected.connect(_select)
        list_widget.setItemWidget(item, card)

    _apply_fitted_grid_height(list_widget, metrics)

    if list_widget.count() > 0:
        list_widget.setCurrentRow(0)
```

</details>

## 🔧 Function `resolve_described_card_metrics`

```python
def resolve_described_card_metrics(available_width: int) -> DescribedCardMetrics
```

Pick full-size cards, or mild shrink to fit one extra column when almost enough.

Args:

- `available_width` (`int`): Grid viewport width in pixels.

<details>
<summary>Code:</summary>

```python
def resolve_described_card_metrics(available_width: int) -> DescribedCardMetrics:
    if available_width <= 0:
        return metrics_for_scale(1.0)

    spacing = CARD_SPACING
    base_width = DESCRIBED_CARD_WIDTH
    # IconMode pitch: n * cell + (n - 1) * spacing <= available.
    columns_full = max(1, (available_width + spacing) // (base_width + spacing))
    columns_extra = columns_full + 1
    width_for_extra = columns_extra * base_width + (columns_extra - 1) * spacing
    if width_for_extra <= available_width:
        return metrics_for_scale(1.0)

    scale_for_extra = (available_width - (columns_extra - 1) * spacing) / (columns_extra * base_width)
    if scale_for_extra < 1.0 and scale_for_extra >= DESCRIBED_CARD_MIN_SCALE:
        return metrics_for_scale(scale_for_extra)
    return metrics_for_scale(1.0)
```

</details>

## 🔧 Function `sync_described_choice_card_grid`

```python
def sync_described_choice_card_grid(list_widget: QListWidget) -> bool
```

Rescale cards to the current viewport width. Return whether metrics changed.

<details>
<summary>Code:</summary>

```python
def sync_described_choice_card_grid(list_widget: QListWidget) -> bool:
    target = resolve_described_card_metrics(list_widget.viewport().width())
    previous = described_card_metrics_of(list_widget)
    if previous.scale == target.scale and previous.width == target.width and previous.icon_size == target.icon_size:
        # Fonts and icons already match: only the text-driven cell height can still change.
        applied = _apply_fitted_grid_height(list_widget, replace(previous, height=target.height))
    else:
        applied = apply_described_card_grid_metrics(list_widget, target)
    return applied != previous
```

</details>
