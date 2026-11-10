---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_name_autocomplete.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CompleterPopupTooltipHelper`](#%EF%B8%8F-class-completerpopuptooltiphelper)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
- [🏛️ Class `FoodNameAutocompleteProxyModel`](#%EF%B8%8F-class-foodnameautocompleteproxymodel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `filterAcceptsRow`](#%EF%B8%8F-method-filteracceptsrow)
  - [⚙️ Method `lessThan`](#%EF%B8%8F-method-lessthan)
  - [⚙️ Method `set_filter_text`](#%EF%B8%8F-method-set_filter_text)
- [🔧 Function `food_autocomplete_icon_emojis`](#-function-food_autocomplete_icon_emojis)
- [🔧 Function `food_autocomplete_popup_icon_size`](#-function-food_autocomplete_popup_icon_size)
- [🔧 Function `make_food_autocomplete_item`](#-function-make_food_autocomplete_item)
- [🔧 Function `setup_completer_item_tooltips`](#-function-setup_completer_item_tooltips)

</details>

## 🏛️ Class `CompleterPopupTooltipHelper`

```python
class CompleterPopupTooltipHelper(QObject)
```

Show full text near the cursor when a completer popup item is elided.

<details>
<summary>Code:</summary>

```python
class CompleterPopupTooltipHelper(QObject):

    _TEXT_MARGIN_PX = 16
    _SHOW_DELAY_MS = 400
    _CURSOR_OFFSET = QPoint(12, 18)

    def __init__(self, completer: QCompleter) -> None:
        """Attach tooltip handling to the completer popup list.

        Parent is the completer (not the popup): parenting to the popup made this
        helper die with the list view, so late `eventFilter` / `destroyed` calls
        hit a half-cleared Python object (`_popup` missing, empty slot name).

        """
        # Attributes first — filters/signals can run before the rest of __init__.
        super().__init__(completer)
        self._popup: QAbstractItemView | None = None
        self._viewport: QWidget | None = None
        self._hover_index = QPersistentModelIndex()
        self._tooltip: QLabel | None = None
        self._show_timer: QTimer | None = None

        popup = completer.popup()
        if popup is None:
            return

        self._popup = popup
        self._viewport = popup.viewport()
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.setInterval(self._SHOW_DELAY_MS)
        self._show_timer.timeout.connect(self._show_tooltip_if_still_hovering)

        self._tooltip = QLabel()
        self._tooltip.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self._tooltip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._tooltip.setWordWrap(True)
        self._tooltip.setMaximumWidth(480)
        self._tooltip.setStyleSheet(
            "QLabel { background-color: #ffffe1; color: #000000; border: 1px solid #767676; padding: 4px 6px; }",
        )
        self._tooltip.hide()

        popup.setMouseTracking(True)
        popup.entered.connect(self._on_item_entered)
        popup.installEventFilter(self)
        if self._viewport is not None:
            self._viewport.installEventFilter(self)
        # Explicit QObject* overload; ignore args so teardown stays callable.
        popup.destroyed.connect(self._on_popup_destroyed)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Hide tooltip when popup closes or mouse leaves the hovered item."""
        if not self._is_popup_alive():
            return False

        if event.type() == QEvent.Type.Hide:
            self._hide_tooltip()
            return False

        viewport = getattr(self, "_viewport", None)
        if viewport is not None and watched is viewport and event.type() == QEvent.Type.MouseMove:
            self._on_viewport_mouse_move(event.position().toPoint())

        return False

    def _detach_from_popup(self) -> None:
        self._hide_tooltip()
        popup = getattr(self, "_popup", None)
        viewport = getattr(self, "_viewport", None)
        if popup is not None and isValid(popup):
            popup.removeEventFilter(self)
            with contextlib.suppress(RuntimeError, TypeError):
                popup.entered.disconnect(self._on_item_entered)
            with contextlib.suppress(RuntimeError, TypeError):
                popup.destroyed.disconnect(self._on_popup_destroyed)
        if viewport is not None and isValid(viewport):
            viewport.removeEventFilter(self)
        self._popup = None
        self._viewport = None

    def _hide_tooltip(self) -> None:
        show_timer = getattr(self, "_show_timer", None)
        tooltip = getattr(self, "_tooltip", None)
        if show_timer is not None and isValid(show_timer):
            show_timer.stop()
        if tooltip is not None and isValid(tooltip):
            tooltip.hide()
        self._hover_index = QPersistentModelIndex()

    def _is_popup_alive(self) -> bool:
        popup = getattr(self, "_popup", None)
        return popup is not None and isValid(popup)

    def _is_text_elided(self, index: QModelIndex | QPersistentModelIndex) -> tuple[bool, str]:
        if not self._is_popup_alive() or not index.isValid():
            return False, ""

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return False, ""

        text_str = str(text)
        # `visualRect` expects `QModelIndex`; `sibling` yields one from either index type.
        model_index = index.sibling(index.row(), index.column())
        rect = self._popup.visualRect(model_index)
        if rect.width() <= 0:
            return False, text_str

        option = QStyleOptionViewItem()
        option.rect = rect
        option.fontMetrics = self._popup.fontMetrics()
        available_width = max(1, rect.width() - self._TEXT_MARGIN_PX)
        elided = option.fontMetrics.elidedText(text_str, Qt.TextElideMode.ElideRight, available_width)
        return elided != text_str, text_str

    def _on_item_entered(self, index: QModelIndex) -> None:
        self._hide_tooltip()
        if not self._is_popup_alive() or not index.isValid():
            return

        is_elided, _ = self._is_text_elided(index)
        if not is_elided:
            return

        self._hover_index = QPersistentModelIndex(index)
        if self._show_timer is not None:
            self._show_timer.start()

    def _on_popup_destroyed(self, *_args: object) -> None:
        """Clear popup refs when the list view is deleted (helper stays on completer)."""
        self._popup = None
        self._viewport = None
        self._hide_tooltip()

    def _on_viewport_mouse_move(self, pos: QPoint) -> None:
        if not self._is_popup_alive() or not self._hover_index.isValid():
            return

        index = self._popup.indexAt(pos)
        if (
            self._tooltip is not None
            and self._tooltip.isVisible()
            and index.isValid()
            and index.row() == self._hover_index.row()
        ):
            self._tooltip.move(QCursor.pos() + self._CURSOR_OFFSET)
            return

        if not index.isValid() or index.row() != self._hover_index.row():
            self._hide_tooltip()

    def _show_tooltip_if_still_hovering(self) -> None:
        if not self._is_popup_alive() or self._tooltip is None or not self._hover_index.isValid():
            return

        if self._viewport is None:
            return

        index_at_cursor = self._popup.indexAt(self._viewport.mapFromGlobal(QCursor.pos()))
        if not index_at_cursor.isValid() or index_at_cursor.row() != self._hover_index.row():
            self._hide_tooltip()
            return

        is_elided, text_str = self._is_text_elided(self._hover_index)
        if not is_elided:
            self._hide_tooltip()
            return

        self._tooltip.setText(text_str)
        self._tooltip.adjustSize()
        self._tooltip.move(QCursor.pos() + self._CURSOR_OFFSET)
        self._tooltip.show()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, completer: QCompleter) -> None
```

Attach tooltip handling to the completer popup list.

Parent is the completer (not the popup): parenting to the popup made this
helper die with the list view, so late `eventFilter` / `destroyed` calls
hit a half-cleared Python object (`_popup` missing, empty slot name).

<details>
<summary>Code:</summary>

```python
def __init__(self, completer: QCompleter) -> None:
        # Attributes first — filters/signals can run before the rest of __init__.
        super().__init__(completer)
        self._popup: QAbstractItemView | None = None
        self._viewport: QWidget | None = None
        self._hover_index = QPersistentModelIndex()
        self._tooltip: QLabel | None = None
        self._show_timer: QTimer | None = None

        popup = completer.popup()
        if popup is None:
            return

        self._popup = popup
        self._viewport = popup.viewport()
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.setInterval(self._SHOW_DELAY_MS)
        self._show_timer.timeout.connect(self._show_tooltip_if_still_hovering)

        self._tooltip = QLabel()
        self._tooltip.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self._tooltip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._tooltip.setWordWrap(True)
        self._tooltip.setMaximumWidth(480)
        self._tooltip.setStyleSheet(
            "QLabel { background-color: #ffffe1; color: #000000; border: 1px solid #767676; padding: 4px 6px; }",
        )
        self._tooltip.hide()

        popup.setMouseTracking(True)
        popup.entered.connect(self._on_item_entered)
        popup.installEventFilter(self)
        if self._viewport is not None:
            self._viewport.installEventFilter(self)
        # Explicit QObject* overload; ignore args so teardown stays callable.
        popup.destroyed.connect(self._on_popup_destroyed)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Hide tooltip when popup closes or mouse leaves the hovered item.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if not self._is_popup_alive():
            return False

        if event.type() == QEvent.Type.Hide:
            self._hide_tooltip()
            return False

        viewport = getattr(self, "_viewport", None)
        if viewport is not None and watched is viewport and event.type() == QEvent.Type.MouseMove:
            self._on_viewport_mouse_move(event.position().toPoint())

        return False
```

</details>

## 🏛️ Class `FoodNameAutocompleteProxyModel`

```python
class FoodNameAutocompleteProxyModel(QSortFilterProxyModel)
```

Proxy model for food name autocomplete with exact/starts-with/contains ordering.

Matches against both display name (`DisplayRole`) and English name (`UserRole`).

<details>
<summary>Code:</summary>

```python
class FoodNameAutocompleteProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        """Determine if a row should be accepted by the filter."""
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        if source_model is None:
            return False

        index = source_model.index(source_row, 0, source_parent)
        return _row_match_tier(source_model, index, self.filter_text) is not None

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort by match tier, then alphabetically (case-insensitive) within tier."""
        source_model = self.sourceModel()
        if source_model is None:
            return False

        if not self.filter_text:
            left_data = source_model.data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = source_model.data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
            return source_left.row() < source_right.row()

        left_tier = _row_match_tier(source_model, source_left, self.filter_text)
        right_tier = _row_match_tier(source_model, source_right, self.filter_text)
        left_rank = 2 if left_tier is None else left_tier
        right_rank = 2 if right_tier is None else right_tier

        if left_rank != right_rank:
            return left_rank < right_rank

        left_data = source_model.data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = source_model.data(source_right, Qt.ItemDataRole.DisplayRole)
        if left_data is None or right_data is None:
            return False

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

        return source_left.row() < source_right.row()

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering and sorting."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the proxy model.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
```

</details>

### ⚙️ Method `filterAcceptsRow`

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool
```

Determine if a row should be accepted by the filter.

<details>
<summary>Code:</summary>

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        if source_model is None:
            return False

        index = source_model.index(source_row, 0, source_parent)
        return _row_match_tier(source_model, index, self.filter_text) is not None
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Sort by match tier, then alphabetically (case-insensitive) within tier.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        source_model = self.sourceModel()
        if source_model is None:
            return False

        if not self.filter_text:
            left_data = source_model.data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = source_model.data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
            return source_left.row() < source_right.row()

        left_tier = _row_match_tier(source_model, source_left, self.filter_text)
        right_tier = _row_match_tier(source_model, source_right, self.filter_text)
        left_rank = 2 if left_tier is None else left_tier
        right_rank = 2 if right_tier is None else right_tier

        if left_rank != right_rank:
            return left_rank < right_rank

        left_data = source_model.data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = source_model.data(source_right, Qt.ItemDataRole.DisplayRole)
        if left_data is None or right_data is None:
            return False

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

        return source_left.row() < source_right.row()
```

</details>

### ⚙️ Method `set_filter_text`

```python
def set_filter_text(self, text: str) -> None
```

Set the filter text and trigger re-filtering and sorting.

<details>
<summary>Code:</summary>

```python
def set_filter_text(self, text: str) -> None:
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

## 🔧 Function `food_autocomplete_icon_emojis`

```python
def food_autocomplete_icon_emojis(entry: FoodAutocompleteEntry) -> list[str]
```

Return leading marker emojis for a completer row (catalog, then drink).

<details>
<summary>Code:</summary>

```python
def food_autocomplete_icon_emojis(entry: FoodAutocompleteEntry) -> list[str]:
    emojis: list[str] = []
    if entry.is_recipe:
        emojis.append(RECIPE_EMOJI)
    elif entry.is_food_item:
        emojis.append(FOOD_ITEM_EMOJI)
    if entry.is_drink:
        emojis.append(DRINK_EMOJI)
    return emojis
```

</details>

## 🔧 Function `food_autocomplete_popup_icon_size`

```python
def food_autocomplete_popup_icon_size() -> QSize
```

Icon slot wide enough for a catalog marker plus a drink marker.

<details>
<summary>Code:</summary>

```python
def food_autocomplete_popup_icon_size() -> QSize:
    width = FOOD_AUTOCOMPLETE_ICON_SIZE * FOOD_AUTOCOMPLETE_ICON_MAX_COUNT + FOOD_AUTOCOMPLETE_ICON_GAP * (
        FOOD_AUTOCOMPLETE_ICON_MAX_COUNT - 1
    )
    return QSize(width, FOOD_AUTOCOMPLETE_ICON_SIZE)
```

</details>

## 🔧 Function `make_food_autocomplete_item`

```python
def make_food_autocomplete_item(entry: FoodAutocompleteEntry) -> QStandardItem
```

Build a completer row; catalog and drink markers are icons, not text prefixes.

<details>
<summary>Code:</summary>

```python
def make_food_autocomplete_item(entry: FoodAutocompleteEntry) -> QStandardItem:
    display = format_food_name_with_calories(
        entry.name,
        entry.calories_per_100g,
        None,
    )
    item = QStandardItem(display if entry.is_recipe else entry.name)
    item.setData(entry.name, Qt.ItemDataRole.EditRole)
    item.setData(entry.name_en or "", Qt.ItemDataRole.UserRole)
    emojis = food_autocomplete_icon_emojis(entry)
    if emojis:
        item.setIcon(
            create_emoji_row_icon(
                emojis,
                FOOD_AUTOCOMPLETE_ICON_SIZE,
                gap=FOOD_AUTOCOMPLETE_ICON_GAP,
            ),
        )
    return item
```

</details>

## 🔧 Function `setup_completer_item_tooltips`

```python
def setup_completer_item_tooltips(completer: QCompleter) -> CompleterPopupTooltipHelper
```

Enable tooltips for elided items in a QCompleter popup list.

<details>
<summary>Code:</summary>

```python
def setup_completer_item_tooltips(completer: QCompleter) -> CompleterPopupTooltipHelper:
    popup = completer.popup()
    if popup is not None:
        popup.setIconSize(food_autocomplete_popup_icon_size())
    helper = CompleterPopupTooltipHelper(completer)
    completer._tooltip_helper = helper  # keep reference alive  # noqa: SLF001
    return helper
```

</details>
