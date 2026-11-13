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
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)

</details>

## 🏛️ Class `LucideCheckableItemDelegate`

```python
class LucideCheckableItemDelegate(QStyledItemDelegate)
```

Draw Lucide square / square-check for checkable item-view rows.

Applies the shared [`LucideToggleStyle`](../../../qt_lucide_checkbox.g.md#%EF%B8%8F-class-lucidetogglestyle) to the parent view so
`PE_IndicatorItemViewItemCheck` is Lucide only (no native gray box underneath).

<details>
<summary>Code:</summary>

```python
class LucideCheckableItemDelegate(QStyledItemDelegate):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Install on `parent` and give that view the Lucide toggle style."""
        super().__init__(parent)
        if parent is not None and not isinstance(parent.style(), LucideToggleStyle):
            parent.setStyle(lucide_toggle_widget_style())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the row; the view style draws the Lucide check indicator."""
        super().paint(painter, option, index)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Install on `parent` and give that view the Lucide toggle style.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if parent is not None and not isinstance(parent.style(), LucideToggleStyle):
            parent.setStyle(lucide_toggle_widget_style())
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint the row; the view style draws the Lucide check indicator.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        super().paint(painter, option, index)
```

</details>
