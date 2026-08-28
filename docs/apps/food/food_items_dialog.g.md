---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_items_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodItemsDialog`](#%EF%B8%8F-class-fooditemsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `FoodItemsDialog`

```python
class FoodItemsDialog(QDialog)
```

Show and edit the food items catalog in a table.

<details>
<summary>Code:</summary>

```python
class FoodItemsDialog(QDialog):

    def __init__(self, parent: QWidget | None, db_manager: DatabaseManager) -> None:
        """Build the catalog dialog and load rows from `db_manager`."""
        super().__init__(parent)
        self.db_manager = db_manager
        self.catalog_changed = False
        self._edit_dialog_open = False
        self.setWindowTitle("Food Items")
        qt_modality.set_owner_window_modal(self)
        self.resize(900, 560)
        self._setup_ui()
        self._reload_table()

    def _food_item_id_from_index(self, index: QModelIndex) -> int | None:
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

    def _food_item_row_by_id(self, food_item_id: int) -> FoodItemByNameRow | None:
        for row in self.db_manager.get_all_food_items():
            if int(row[0]) != food_item_id:
                continue
            return FoodItemByNameRow(
                id=int(row[0]),
                name=str(row[1] or ""),
                name_en=str(row[2]) if row[2] else None,
                is_drink=bool(row[3]),
                calories_per_100g=float(row[4]) if row[4] is not None else None,
                default_portion_weight=float(row[5]) if row[5] is not None else None,
                default_portion_calories=float(row[6]) if row[6] is not None else None,
            )
        return None

    def _on_add(self) -> None:
        dialog = FoodItemDialog(self, None, is_create=True)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_edited_data()
        if not self.db_manager.add_food_item(
            name=str(data["name"]),
            name_en=data["name_en"],
            is_drink=bool(data["is_drink"]),
            calories_per_100g=data["calories_per_100g"],
            default_portion_weight=data["default_portion_weight"],
            default_portion_calories=data["default_portion_calories"],
        ):
            message_box.warning(self, "Error", "Failed to add food item")
            return
        self.catalog_changed = True
        self._reload_table()

    def _on_delete(self, food_item_id: int) -> None:
        item = self._food_item_row_by_id(food_item_id)
        name = item.name if item is not None else "this item"
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not self.db_manager.delete_food_item(food_item_id):
            message_box.warning(self, "Error", f"Failed to delete food item '{name}'")
            return
        self.catalog_changed = True
        self._reload_table()

    def _on_double_clicked(self, index: QModelIndex) -> None:
        food_item_id = self._food_item_id_from_index(index)
        if food_item_id is not None:
            self._open_edit_dialog(food_item_id)

    def _open_edit_dialog(self, food_item_id: int) -> None:
        if self._edit_dialog_open:
            return
        food_item = self._food_item_row_by_id(food_item_id)
        if food_item is None:
            message_box.warning(self, "Error", "Food item not found")
            return
        self._edit_dialog_open = True
        dialog = FoodItemDialog(self, food_item, is_create=False)
        result = dialog.exec()
        self._edit_dialog_open = False
        if result != QDialog.DialogCode.Accepted:
            return
        if dialog.delete_confirmed:
            if not self.db_manager.delete_food_item(food_item_id):
                message_box.warning(self, "Error", f"Failed to delete food item '{food_item.name}'")
                return
            self.catalog_changed = True
            self._reload_table()
            return
        data = dialog.get_edited_data()
        if not self.db_manager.update_food_item(
            food_item_id=food_item_id,
            name=str(data["name"]),
            name_en=data["name_en"],
            is_drink=bool(data["is_drink"]),
            calories_per_100g=data["calories_per_100g"],
            default_portion_weight=data["default_portion_weight"],
            default_portion_calories=data["default_portion_calories"],
        ):
            message_box.warning(self, "Error", f"Failed to update food item '{data['name']}'")
            return
        self.catalog_changed = True
        self._reload_table()

    def _reload_table(self) -> None:
        rows: list[list[Any]] = []
        for index, row in enumerate(self.db_manager.get_all_food_items()):
            color = _ROW_COLOR_ODD if index % 2 else _ROW_COLOR_EVEN
            rows.append(
                [
                    str(row[1] or ""),
                    str(row[2] or ""),
                    "Yes" if row[3] else "",
                    f"{float(row[4]):.1f}" if row[4] is not None else "",
                    f"{float(row[5]):.0f}" if row[5] is not None else "",
                    f"{float(row[6]):.1f}" if row[6] is not None else "",
                    row[0],
                    color,
                ]
            )
        proxy = create_colored_table_proxy_model(rows, _HEADERS)
        self.table.setModel(proxy)
        header = self.table.horizontalHeader()
        if header.count() > 0:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for column in range(1, header.count()):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(False)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.table = QTableView(self)
        install_word_wrap_header(self.table)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        self.refresh_button = make_emoji_push_button("Refresh", "🔄")
        self.close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        self.add_button.clicked.connect(self._on_add)
        self.refresh_button.clicked.connect(self._reload_table)
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.refresh_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def _show_table_context_menu(self, position: QPoint) -> None:
        index = self.table.indexAt(position)
        food_item_id = self._food_item_id_from_index(index)
        if food_item_id is not None:
            self.table.selectRow(index.row())

        context_menu = QMenu(self)
        if food_item_id is not None:
            edit_action = context_menu.addAction(LABEL_EDIT)
            edit_action.triggered.connect(lambda: self._open_edit_dialog(food_item_id))
        add_separator(context_menu)
        add_action = context_menu.addAction("➕ Add")  # noqa: RUF001
        add_action.triggered.connect(self._on_add)
        refresh_action = context_menu.addAction(LABEL_REFRESH)
        refresh_action.triggered.connect(self._reload_table)
        delete_action = add_delete_action(context_menu)
        delete_action.setEnabled(food_item_id is not None)
        if food_item_id is not None:
            delete_action.triggered.connect(lambda: self._on_delete(food_item_id))
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

Build the catalog dialog and load rows from `db_manager`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager) -> None:
        super().__init__(parent)
        self.db_manager = db_manager
        self.catalog_changed = False
        self._edit_dialog_open = False
        self.setWindowTitle("Food Items")
        qt_modality.set_owner_window_modal(self)
        self.resize(900, 560)
        self._setup_ui()
        self._reload_table()
```

</details>
