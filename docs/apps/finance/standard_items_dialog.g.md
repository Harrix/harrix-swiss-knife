---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `standard_items_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `StandardItemsDialog`](#%EF%B8%8F-class-standarditemsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `StandardItemsDialog`

```python
class StandardItemsDialog(QDialog)
```

Show and edit standard purchases/incomes catalog.

<details>
<summary>Code:</summary>

```python
class StandardItemsDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        """Initialize the standard items catalog dialog."""
        super().__init__(parent)
        self.db_manager = db_manager
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self.setWindowTitle("Standard Items")
        self.resize(820, 560)
        self._setup_ui()
        self._reload_table()

    def _categories(self) -> list[list[Any]]:
        return self.db_manager.get_all_categories()

    def _item_dict_for_row(self, row: int) -> dict[str, Any] | None:
        if row < 0:
            return None
        name_item = self.table.item(row, 0)
        en_item = self.table.item(row, 1)
        if name_item is None:
            return None
        item_id = name_item.data(_COL_ID)
        category_id = name_item.data(_COL_CATEGORY_ID)
        if item_id is None or category_id is None:
            return None
        return {
            "id": int(item_id),
            "name": name_item.text(),
            "name_en": en_item.text() if en_item is not None else "",
            "category_id": int(category_id),
        }

    def _on_add(self) -> None:
        dialog = _StandardItemEditDialog(self, self._categories())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_result()
        if not self.db_manager.add_standard_item(data["name"], data["category_id"], data["name_en"]):
            message_box.warning(self, "Error", "Failed to add standard item (duplicate name?)")
            return
        self._reload_table()

    def _on_delete(self) -> None:
        items = self._selected_item_dicts()
        if not items:
            message_box.warning(self, "Error", "Select a row to delete")
            return
        if len(items) == 1:
            confirm_text = f"Delete standard item '{items[0]['name']}'?"
        else:
            confirm_text = f"Delete {len(items)} selected standard items?"
        reply = message_box.question(
            self,
            "Confirm Delete",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        failed = 0
        for item in items:
            if not self.db_manager.delete_standard_item(int(item["id"])):
                failed += 1
        self._reload_table()
        if failed:
            message_box.warning(self, "Error", f"Failed to delete {failed} standard item(s)")

    def _on_edit(self) -> None:
        item = self._selected_item_dict()
        if item is None:
            message_box.warning(self, "Error", "Select a row to edit")
            return
        dialog = _StandardItemEditDialog(self, self._categories(), item=item)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_result()
        if not self.db_manager.update_standard_item(
            int(data["id"]),
            data["name"],
            data["category_id"],
            data["name_en"],
        ):
            message_box.warning(self, "Error", "Failed to update standard item")
            return
        self._reload_table()

    def _on_translate_with_ai(self) -> None:
        limit = self._translate_limit()
        names = self.db_manager.get_standard_items_missing_name_en(limit=limit)
        if not names:
            message_box.information(self, "Translate with AI", "All standard items already have English names.")
            return
        known = self.db_manager.lookup_existing_description_en_for_descriptions(names)
        filled = 0
        for name, name_en in known.items():
            if self.db_manager.update_standard_item_name_en_by_name(name, name_en):
                filled += 1
        names_for_ai = [name for name in names if name not in known]
        if not names_for_ai:
            self._reload_table()
            message_box.information(
                self,
                "Translate with AI",
                f"Filled {filled} name(s) from existing database translations.",
            )
            return
        try:
            prompt_text = build_prompt(
                self._app_config,
                "finance_standard_items_translate_names",
                {"STANDARD_ITEM_NAMES": "\n".join(names_for_ai)},
            )
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            parsed = parse_transaction_translate_response(response_text)
            translations = align_translations_to_descriptions(names_for_ai, parsed)
            preview = TransactionTranslatePreviewDialog(
                self,
                names_for_ai,
                translations,
                limit,
                filled_from_existing=filled,
            )
            preview.setWindowTitle("Translate standard items — preview")
            if preview.exec() != QDialog.DialogCode.Accepted:
                self._reload_table()
                return
            applied = 0
            for name, name_en in preview.get_translations_to_apply().items():
                if self.db_manager.update_standard_item_name_en_by_name(name, name_en):
                    applied += 1
            self._reload_table()
            message_box.information(
                self,
                "Translate with AI",
                f"Applied {applied} translation(s). Previously filled from DB: {filled}.",
            )

        run_bothub_request(
            self,
            self._app_config,
            prompt_text,
            on_success,
            toast_message="Translating standard items…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
        )

    def _reload_table(self) -> None:
        rows = self.db_manager.get_all_standard_items()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            item_id, name, name_en, category_id, category_name, icon, category_type = row
            name_item = QTableWidgetItem(str(name))
            name_item.setData(_COL_ID, int(item_id))
            name_item.setData(_COL_CATEGORY_ID, int(category_id))
            en_item = QTableWidgetItem(str(name_en or ""))
            suffix = " (Income)" if int(category_type) == 1 else ""
            category_display = f"{icon or ''} {category_name}{suffix}".strip()
            category_item = QTableWidgetItem(category_display)
            self.table.setItem(row_idx, 0, name_item)
            self.table.setItem(row_idx, 1, en_item)
            self.table.setItem(row_idx, 2, category_item)

    def _selected_item_dict(self) -> dict[str, Any] | None:
        items = self._selected_item_dicts()
        if len(items) == 1:
            return items[0]
        return self._item_dict_for_row(self.table.currentRow())

    def _selected_item_dicts(self) -> list[dict[str, Any]]:
        selection_model = self.table.selectionModel()
        if selection_model is None:
            return []
        selected_rows = sorted({index.row() for index in selection_model.selectedRows()})
        items: list[dict[str, Any]] = []
        for row in selected_rows:
            item = self._item_dict_for_row(row)
            if item is not None:
                items.append(item)
        return items

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Catalog of standard purchases and incomes (name, English, category). "
                "Used as suggestions in the description field.",
                self,
            )
        )

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "English", "Category"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.doubleClicked.connect(self._on_edit)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        self.edit_button = make_emoji_push_button("Edit", "✏️")
        self.delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self.translate_button = make_emoji_push_button("Translate with AI", "🤖")
        self.close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button.clicked.connect(self._on_delete)
        self.translate_button.clicked.connect(self._on_translate_with_ai)
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.translate_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def _show_table_context_menu(self, position: QPoint) -> None:
        selected = self._selected_item_dicts()
        if not selected:
            index = self.table.indexAt(position)
            if index.isValid():
                self.table.selectRow(index.row())
                selected = self._selected_item_dicts()
        if not selected:
            return
        menu = QMenu(self)
        if len(selected) == 1:
            delete_action = menu.addAction(f"{DELETE_BUTTON_EMOJI} Delete selected row")
        else:
            delete_action = menu.addAction(f"{DELETE_BUTTON_EMOJI} Delete selected rows")
        viewport = self.table.viewport()
        if viewport is None:
            return
        action = menu.exec_(viewport.mapToGlobal(position))
        if action == delete_action:
            self._on_delete()

    def _translate_limit(self) -> int:
        raw = self._app_config.get("finance_standard_items_translate_names_limit", _DEFAULT_TRANSLATE_LIMIT)
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            return _DEFAULT_TRANSLATE_LIMIT
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager, *, app_config: dict[str, Any] | None = None, bothub_state: BothubRequestState | None = None) -> None
```

Initialize the standard items catalog dialog.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        super().__init__(parent)
        self.db_manager = db_manager
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self.setWindowTitle("Standard Items")
        self.resize(820, 560)
        self._setup_ui()
        self._reload_table()
```

</details>
