---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `categories_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoriesDialog`](#%EF%B8%8F-class-categoriesdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `CategoriesDialog`

```python
class CategoriesDialog(QDialog)
```

Show and edit the categories catalog.

<details>
<summary>Code:</summary>

```python
class CategoriesDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        """Initialize the categories catalog dialog."""
        super().__init__(parent)
        self.db_manager = db_manager
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self.catalog_changed = False
        self._edit_dialog_open = False
        self.setWindowTitle("Categories")
        qt_modality.set_owner_window_modal(self)
        self.resize(720, 520)
        self._setup_ui()
        self._reload_table()

    def _category_id_from_index(self, index: QModelIndex) -> int | None:
        """Return category database ID for a table model index."""
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
        """Add a category and reload the table."""
        dialog = CategoryAddDialog(self, app_config=self._app_config, bothub_state=self._bothub_state)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        result = dialog.get_result()
        if result is None:
            return
        name, category_type, icon, name_local = result
        try:
            if not self.db_manager.add_category(name, category_type, icon, name_local=name_local):
                message_box.warning(self, "Error", "Failed to add category")
                return
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add category: {e}")
            return
        self.catalog_changed = True
        self._reload_table()

    def _on_copy_as_text(self) -> None:
        """Copy category names to the clipboard."""
        try:
            categories_data = self.db_manager.get_all_categories()
            if not categories_data:
                message_box.information(self, "No Categories", "No categories found in the database.")
                return
            categories_text = [str(row[1]) for row in categories_data]
            clipboard_text = "\n".join(categories_text)
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)
            message_box.information(
                self,
                "Categories Copied",
                f"✅ Successfully copied {len(categories_text)} categories to clipboard:\n\n{clipboard_text}",
            )
        except Exception as e:
            message_box.critical(self, "Error", f"❌ Error copying categories to clipboard:\n\n{e!s}")

    def _on_delete(self, category_id: int) -> None:
        """Delete the selected category after confirmation."""
        category = self.db_manager.get_category_by_id(category_id)
        category_name = category[1] if category else ""
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete category '{category_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not self.db_manager.delete_category(category_id):
            message_box.warning(self, "Error", "Failed to delete category")
            return
        self.catalog_changed = True
        self._reload_table()

    def _on_double_clicked(self, index: QModelIndex) -> None:
        """Open the edit dialog for the double-clicked row."""
        category_id = self._category_id_from_index(index)
        if category_id is not None:
            self._open_edit_dialog(category_id)

    def _open_edit_dialog(self, category_id: int) -> None:
        """Open the edit dialog for `category_id`."""
        if self._edit_dialog_open:
            return
        category_data = self.db_manager.get_category_by_id(category_id)
        if not category_data:
            message_box.warning(self, "Error", "Category not found")
            return
        category_dict = {
            "id": category_data[0],
            "name": category_data[1] or "",
            "type": int(category_data[2] or 0),
            "icon": category_data[3] or "",
            "name_local": category_data[4] or "",
        }
        self._edit_dialog_open = True
        dialog = CategoryEditDialog(
            self,
            category_dict,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
        )
        result_code = dialog.exec()
        self._edit_dialog_open = False
        if result_code != QDialog.DialogCode.Accepted:
            return
        result = dialog.get_result()
        if result.get("action") == "save":
            success = self.db_manager.update_category(
                category_id,
                result["name"],
                int(result["type"]),
                result.get("icon", "") or "",
                result.get("name_local", "") or "",
            )
            if success:
                self.catalog_changed = True
                self._reload_table()
            else:
                message_box.warning(self, "Error", "Failed to update category")
            return
        if result.get("action") == "delete":
            success = self.db_manager.delete_category(category_id)
            if success:
                self.catalog_changed = True
                self._reload_table()
                message_box.information(self, "Success", "Category deleted successfully")
            else:
                message_box.warning(self, "Error", "Failed to delete category")

    def _reload_table(self) -> None:
        """Reload the categories table from the database."""
        rows: list[tuple[str, str, int, str, str, object, object]] = []
        for row in self.db_manager.get_all_categories():
            category_id, name, category_type, icon, name_local = (
                row[0],
                str(row[1] or ""),
                int(row[2] or 0),
                str(row[3] or ""),
                str(row[4] or "") if row[4] is not None else "",
            )
            type_label = "Expense" if category_type == 0 else "Income"
            color = QColor(255, 200, 200) if category_type == 0 else QColor(200, 255, 200)
            display_name = f"{icon} {name}".strip() if icon else name
            rows.append((display_name, type_label, category_type, name, name_local, color, category_id))
        proxy = create_categories_table_proxy_model(rows, _HEADERS)
        self.table.setModel(proxy)
        header = self.table.horizontalHeader()
        if header.count() > 0:
            for i in range(header.count()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        layout = QVBoxLayout(self)
        self.table = QTableView(self)
        install_word_wrap_header(self.table)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        self.refresh_button = make_emoji_push_button("Refresh", "🔄")
        self.copy_button = make_emoji_push_button("Copy as Text", COPY_BUTTON_EMOJI)
        self.close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        self.add_button.clicked.connect(self._on_add)
        self.refresh_button.clicked.connect(self._reload_table)
        self.copy_button.clicked.connect(self._on_copy_as_text)
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.copy_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def _show_table_context_menu(self, position: QPoint) -> None:
        """Show the categories table context menu."""
        index = self.table.indexAt(position)
        category_id = self._category_id_from_index(index)
        if category_id is not None:
            self.table.selectRow(index.row())

        context_menu = QMenu(self)
        if category_id is not None:
            edit_action = context_menu.addAction(LABEL_EDIT)
            edit_action.triggered.connect(lambda: self._open_edit_dialog(category_id))
        add_separator(context_menu)
        add_action = context_menu.addAction("➕ Add")  # noqa: RUF001
        add_action.triggered.connect(self._on_add)
        refresh_action = context_menu.addAction(LABEL_REFRESH)
        refresh_action.triggered.connect(self._reload_table)
        copy_action = context_menu.addAction("📋 Copy as Text")
        copy_action.triggered.connect(self._on_copy_as_text)
        delete_action = add_delete_action(context_menu)
        delete_action.setEnabled(category_id is not None)
        if category_id is not None:
            delete_action.triggered.connect(lambda: self._on_delete(category_id))
        apply_leading_emoji_icons(context_menu)

        viewport = self.table.viewport()
        if viewport is None:
            return
        context_menu.exec_(viewport.mapToGlobal(position))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager, *, app_config: dict[str, Any] | None = None, bothub_state: BothubRequestState | None = None) -> None
```

Initialize the categories catalog dialog.

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
        self.catalog_changed = False
        self._edit_dialog_open = False
        self.setWindowTitle("Categories")
        qt_modality.set_owner_window_modal(self)
        self.resize(720, 520)
        self._setup_ui()
        self._reload_table()
```

</details>
