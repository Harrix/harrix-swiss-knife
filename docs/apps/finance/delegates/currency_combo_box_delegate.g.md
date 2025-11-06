---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `currency_combo_box_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CurrencyComboBoxDelegate`](#%EF%B8%8F-class-currencycomboboxdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `CurrencyComboBoxDelegate`

```python
class CurrencyComboBoxDelegate(QStyledItemDelegate)
```

Delegate for currency column in transactions table with dropdown list.

<details>
<summary>Code:</summary>

```python
class CurrencyComboBoxDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject, currencies: list[str] | None = None) -> None:
        """Initialize CurrencyComboBoxDelegate.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `currencies` (`list[str] | None`): List of currency codes. Defaults to empty list if None.

        """
        super().__init__(parent)
        self.currencies = currencies or []

    def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QComboBox:  # noqa: N802, ANN001
        """Create a combo box editor for the currency column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option`: Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QComboBox`: The created combo box editor.

        """
        combo = QComboBox(parent)
        combo.setEditable(False)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add currencies to combo box
        for currency in self.currencies:
            combo.addItem(currency)

        return combo

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = editor.findText(current_value)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        selected_text = editor.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject, currencies: list[str] | None = None) -> None
```

Initialize CurrencyComboBoxDelegate.

Args:

- `parent` (`QObject`): Parent widget.
- `currencies` (`list[str] | None`): List of currency codes. Defaults to empty list if None.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject, currencies: list[str] | None = None) -> None:
        super().__init__(parent)
        self.currencies = currencies or []
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QComboBox
```

Create a combo box editor for the currency column.

Args:

- `parent` (`QObject`): Parent widget.
- `_option`: Style option.
- `_index` (`QModelIndex`): Model index.

Returns:

- `QComboBox`: The created combo box editor.

<details>
<summary>Code:</summary>

```python
def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QComboBox:  # noqa: N802, ANN001
        combo = QComboBox(parent)
        combo.setEditable(False)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add currencies to combo box
        for currency in self.currencies:
            combo.addItem(currency)

        return combo
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None
```

Set the current value in the editor.

Args:

- `editor` (`QComboBox`): The editor widget.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # noqa: N802
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = editor.findText(current_value)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None
```

Set the data from the editor back to the model.

Args:

- `editor` (`QComboBox`): The editor widget.
- `model` (`QAbstractItemModel`): The data model.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        selected_text = editor.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>
