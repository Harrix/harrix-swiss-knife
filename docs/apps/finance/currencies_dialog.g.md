---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `currencies_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CurrenciesDialog`](#%EF%B8%8F-class-currenciesdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `CurrenciesDialog`

```python
class CurrenciesDialog(QDialog)
```

Show and edit the currencies catalog and default currency.

<details>
<summary>Code:</summary>

```python
class CurrenciesDialog(QDialog):

    def __init__(self, parent: QWidget | None, db_manager: DatabaseManager) -> None:
        """Initialize the currencies catalog dialog."""
        super().__init__(parent)
        self.db_manager = db_manager
        self.catalog_changed = False
        self.default_currency_changed = False
        self.setWindowTitle("Currencies")
        qt_modality.set_owner_window_modal(self)
        self.resize(640, 500)
        self._setup_ui()
        self._reload_table()
        self._reload_default_currency_combo()

    def _currency_id_from_index(self, index: QModelIndex) -> int | None:
        """Return currency database ID for a table model index."""
        if not index.isValid():
            return None
        proxy_model = self.table.model()
        if not isinstance(proxy_model, QSortFilterProxyModel):
            return None
        source_model = proxy_model.sourceModel()
        if source_model is None or not isinstance(source_model, QStandardItemModel):
            return None
        source_index = proxy_model.mapToSource(index)
        if not source_index.isValid():
            return None
        row_id_item = source_model.verticalHeaderItem(source_index.row())
        if row_id_item is None:
            return None
        try:
            return int(row_id_item.text())
        except (TypeError, ValueError):
            return None

    def _on_add(self) -> None:
        """Add a currency and reload the table."""
        dialog = CurrencyAddDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        result = dialog.get_result()
        if result is None:
            return
        try:
            if not self.db_manager.add_currency(
                str(result["code"]),
                str(result["name"]),
                str(result["symbol"]),
                int(result["subdivision"]),
            ):
                message_box.warning(self, "Error", "Failed to add currency")
                return
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add currency: {e}")
            return
        self.catalog_changed = True
        self._reload_table()
        self._reload_default_currency_combo()

    def _on_delete(self, currency_id: int) -> None:
        """Delete the selected currency after confirmation."""
        currency = self.db_manager.get_currency_by_id(currency_id)
        currency_label = currency[0] if currency else ""
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete currency '{currency_label}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not self.db_manager.delete_currency(currency_id):
            message_box.warning(self, "Error", "Failed to delete currency")
            return
        self.catalog_changed = True
        self._reload_table()
        self._reload_default_currency_combo()

    def _on_refresh(self) -> None:
        """Reload the table and default-currency combo."""
        self._reload_table()
        self._reload_default_currency_combo()

    def _on_set_default_currency(self) -> None:
        """Set the selected combo value as the default currency."""
        currency_code = self.combo_default_currency.currentText()
        if not currency_code:
            message_box.warning(self, "Error", "Select a currency")
            return
        try:
            if not self.db_manager.set_default_currency(currency_code):
                message_box.warning(self, "Error", "Failed to set default currency")
                return
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to set default currency: {e}")
            return
        self.default_currency_changed = True
        message_box.information(self, "Success", f"Default currency set to {currency_code}")

    def _reload_default_currency_combo(self) -> None:
        """Fill the default-currency combo from the database."""
        currencies = [row[1] for row in self.db_manager.get_all_currencies()]
        current = self.combo_default_currency.currentText()
        self.combo_default_currency.blockSignals(True)  # noqa: FBT003
        self.combo_default_currency.clear()
        self.combo_default_currency.addItems(currencies)
        default_currency = self.db_manager.get_default_currency()
        index = self.combo_default_currency.findText(default_currency)
        if index < 0 and current:
            index = self.combo_default_currency.findText(current)
        if index >= 0:
            self.combo_default_currency.setCurrentIndex(index)
        self.combo_default_currency.blockSignals(False)  # noqa: FBT003

    def _reload_table(self) -> None:
        """Reload the currencies table from the database."""
        transformed: list[list] = []
        for row in self.db_manager.get_all_currencies():
            color = QColor(255, 255, 220)
            transformed.append([row[1], row[2], row[3], row[0], color])
        proxy = create_colored_table_proxy_model(transformed, _HEADERS)
        self.table.setModel(proxy)
        header = self.table.horizontalHeader()
        if header.count() > 0:
            for i in range(header.count()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        layout = QVBoxLayout(self)

        default_group = QGroupBox("Default Currency", self)
        default_row = QHBoxLayout(default_group)
        self.combo_default_currency = QComboBox(default_group)
        self.combo_default_currency.setMinimumWidth(170)
        self.set_default_button = make_emoji_push_button("Set Default", "⭐")
        self.set_default_button.clicked.connect(self._on_set_default_currency)
        default_row.addWidget(self.combo_default_currency, 1)
        default_row.addWidget(self.set_default_button)
        layout.addWidget(default_group)

        self.table = QTableView(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        self.refresh_button = make_emoji_push_button("Refresh", "🔄")
        self.close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        self.add_button.clicked.connect(self._on_add)
        self.refresh_button.clicked.connect(self._on_refresh)
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.refresh_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def _show_table_context_menu(self, position: QPoint) -> None:
        """Show the currencies table context menu."""
        index = self.table.indexAt(position)
        currency_id = self._currency_id_from_index(index)
        if currency_id is not None:
            self.table.selectRow(index.row())

        context_menu = QMenu(self)
        add_action = context_menu.addAction("➕ Add")  # noqa: RUF001
        add_action.triggered.connect(self._on_add)
        refresh_action = context_menu.addAction(LABEL_REFRESH)
        refresh_action.triggered.connect(self._on_refresh)
        delete_action = add_delete_action(context_menu)
        delete_action.setEnabled(currency_id is not None)
        if currency_id is not None:
            delete_action.triggered.connect(lambda: self._on_delete(currency_id))
        apply_leading_emoji_icons(context_menu)

        viewport = self.table.viewport()
        if viewport is None:
            return
        context_menu.exec_(viewport.mapToGlobal(position))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager) -> None
```

Initialize the currencies catalog dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager) -> None:
        super().__init__(parent)
        self.db_manager = db_manager
        self.catalog_changed = False
        self.default_currency_changed = False
        self.setWindowTitle("Currencies")
        qt_modality.set_owner_window_modal(self)
        self.resize(640, 500)
        self._setup_ui()
        self._reload_table()
        self._reload_default_currency_combo()
```

</details>
