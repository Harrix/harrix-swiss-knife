---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lucide_checkable_item_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LucideCheckableItemDelegate`](#%EF%B8%8F-class-lucidecheckableitemdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)

</details>

## 🏛️ Class `LucideCheckableItemDelegate`

```python
class LucideCheckableItemDelegate(QStyledItemDelegate)
```

Draw Lucide square / square-check over checkable item-view rows.

Parent window stylesheets often leave `PE_IndicatorItemViewItemCheck` blank.
This delegate keeps the normal row paint, then overlays a Lucide checkbox.

<details>
<summary>Code:</summary>

```python
class LucideCheckableItemDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the row, then overlay a Lucide checkbox when the item is checkable."""
        self.initStyleOption(option, index)
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, widget)

        check_value = index.data(Qt.ItemDataRole.CheckStateRole)
        if check_value is None and not (option.features & QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator):
            return

        rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, option, widget)
        if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
            size = CHECKBOX_INDICATOR_PX
            rect = QRect(
                option.rect.x() + 4,
                option.rect.y() + (option.rect.height() - size) // 2,
                size,
                size,
            )

        state = Qt.CheckState.Unchecked
        if check_value is not None:
            state = check_value if isinstance(check_value, Qt.CheckState) else Qt.CheckState(int(check_value))
        paint_lucide_checkbox(
            painter,
            rect,
            checked=state == Qt.CheckState.Checked,
            partial=state == Qt.CheckState.PartiallyChecked,
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint the row, then overlay a Lucide checkbox when the item is checkable.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, widget)

        check_value = index.data(Qt.ItemDataRole.CheckStateRole)
        if check_value is None and not (option.features & QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator):
            return

        rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, option, widget)
        if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
            size = CHECKBOX_INDICATOR_PX
            rect = QRect(
                option.rect.x() + 4,
                option.rect.y() + (option.rect.height() - size) // 2,
                size,
                size,
            )

        state = Qt.CheckState.Unchecked
        if check_value is not None:
            state = check_value if isinstance(check_value, Qt.CheckState) else Qt.CheckState(int(check_value))
        paint_lucide_checkbox(
            painter,
            rect,
            checked=state == Qt.CheckState.Checked,
            partial=state == Qt.CheckState.PartiallyChecked,
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )
```

</details>
