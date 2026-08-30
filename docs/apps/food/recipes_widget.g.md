---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recipes_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecipesWidget`](#%EF%B8%8F-class-recipeswidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `select_recipe_by_id`](#%EF%B8%8F-method-select_recipe_by_id)
  - [⚙️ Method `set_database_manager`](#%EF%B8%8F-method-set_database_manager)

</details>

## 🏛️ Class `RecipesWidget`

```python
class RecipesWidget(QWidget)
```

Three-pane view: ingredient add on the left, recipe list in the middle, editor on the right.

<details>
<summary>Code:</summary>

```python
class RecipesWidget(QWidget):

    recipes_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the recipes UI; call `set_database_manager` before loading data."""
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_recipe_id: int | None = None
        self._ingredients: list[RecipeIngredientInput] = []
        self._completer_source = QStandardItemModel(self)
        self._completer_proxy = FoodNameAutocompleteProxyModel(self)
        self._completer_proxy.setSourceModel(self._completer_source)
        self._build_ui()
        self._setup_ingredient_completer()

    def refresh(self) -> None:
        """Reload recipe list and ingredient-name autocomplete from the database."""
        self._update_ingredient_autocomplete()
        self._reload_recipe_list(keep_selection=True)

    def select_recipe_by_id(self, recipe_id: int) -> None:
        """Select a recipe in the list after a refresh, if present."""
        for row in range(self._recipes_model.rowCount()):
            item = self._recipes_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == recipe_id:
                index = self._recipes_model.indexFromItem(item)
                self.list_recipes.setCurrentIndex(index)
                self._load_recipe(recipe_id)
                return

    def set_database_manager(self, db_manager: DatabaseManager | None) -> None:
        """Attach the food database and refresh the recipe list."""
        self._db = db_manager
        self.refresh()

    def _add_ingredient(self) -> None:
        name = extract_food_name_from_display(self.line_ingredient_name.text().strip())
        if not name:
            message_box.warning(self, "Error", "Enter ingredient name")
            return
        weight = float(self.spin_ingredient_weight.value())
        if weight <= 0:
            message_box.warning(self, "Error", "Weight is required")
            return
        calories = float(self.spin_ingredient_calories.value())
        use_weight = self.radio_use_weight.isChecked()
        if not use_weight and calories <= 0:
            message_box.warning(self, "Error", "Calories are required when using portion mode")
            return

        if use_weight:
            ingredient = RecipeIngredientInput(
                name=name,
                weight=weight,
                calories_per_100g=calories if calories > 0 else None,
                portion_calories=None,
                is_drink=self.check_ingredient_drink.isChecked(),
            )
        else:
            ingredient = RecipeIngredientInput(
                name=name,
                weight=weight,
                calories_per_100g=None,
                portion_calories=calories,
                is_drink=self.check_ingredient_drink.isChecked(),
            )
        self._ingredients.append(ingredient)
        self._refresh_ingredients_table()
        self.line_ingredient_name.clear()
        self.spin_ingredient_weight.setValue(100)
        self.spin_ingredient_calories.setValue(0)
        self.check_ingredient_drink.setChecked(False)
        self.radio_use_weight.setChecked(True)
        self.line_ingredient_name.setFocus()

    def _apply_ingredient_row_background(self, row: int) -> None:
        color = _ROW_COLOR_ODD if row % 2 else _ROW_COLOR_EVEN
        brush = QBrush(color)
        for column in range(_INGREDIENT_COLUMN_COUNT):
            item = self.table_ingredients.item(row, column)
            if item is not None:
                item.setBackground(brush)

    def _apply_ingredients_column_metrics(self) -> None:
        header = self.table_ingredients.horizontalHeader()
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_WEIGHT, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_KCAL_100G, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_PORTION, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_CALC, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_DRINK, QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        self.table_ingredients.setColumnWidth(_COL_WEIGHT, _COL_WEIGHT_WIDTH)
        self.table_ingredients.setColumnWidth(_COL_KCAL_100G, _COL_KCAL_WIDTH)
        self.table_ingredients.setColumnWidth(_COL_PORTION, _COL_PORTION_WIDTH)
        self.table_ingredients.setColumnWidth(_COL_CALC, _COL_CALC_WIDTH)
        self.table_ingredients.setColumnWidth(_COL_DRINK, _COL_DRINK_WIDTH)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        font_12_bold = QFont()
        font_12_bold.setPointSize(12)
        font_12_bold.setBold(True)
        font_12 = QFont()
        font_12.setPointSize(12)
        font_30_bold = QFont()
        font_30_bold.setPointSize(30)
        font_30_bold.setBold(True)

        controls = QFrame()
        controls.setMinimumWidth(_CONTROLS_MIN_WIDTH)
        controls.setFrameShape(QFrame.Shape.StyledPanel)
        controls.setFrameShadow(QFrame.Shadow.Raised)
        controls_layout = QVBoxLayout(controls)

        group_add = QGroupBox("Add ingredient")
        add_layout = QVBoxLayout(group_add)

        self.line_ingredient_name = QLineEdit()
        self.line_ingredient_name.setFont(font_12)
        self.line_ingredient_name.setPlaceholderText("Enter ingredient name")
        add_layout.addWidget(self.line_ingredient_name)

        amount_row = QHBoxLayout()
        self.spin_ingredient_weight = QSpinBox()
        self.spin_ingredient_weight.setFont(font_12_bold)
        self.spin_ingredient_weight.setStyleSheet(_SPINBOX_STYLE)
        self.spin_ingredient_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spin_ingredient_weight.setRange(1, 100_000)
        self.spin_ingredient_weight.setValue(100)
        self.spin_ingredient_calories = QDoubleSpinBox()
        self.spin_ingredient_calories.setFont(font_12_bold)
        self.spin_ingredient_calories.setStyleSheet(_DOUBLE_SPINBOX_STYLE)
        self.spin_ingredient_calories.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spin_ingredient_calories.setRange(0, 100_000)
        self.spin_ingredient_calories.setDecimals(1)
        amount_row.addWidget(self.spin_ingredient_weight)
        amount_row.addWidget(QLabel("g"))
        amount_row.addWidget(self.spin_ingredient_calories)
        amount_row.addWidget(QLabel("kcal"))
        self.check_ingredient_drink = QCheckBox("Drink")
        amount_row.addWidget(self.check_ingredient_drink)
        add_layout.addLayout(amount_row)

        mode_row = QHBoxLayout()
        self.radio_use_weight = QRadioButton("Calculate by weight")
        self.radio_use_calories = QRadioButton("Enter calories directly")
        self.radio_use_weight.setChecked(True)
        mode_row.addWidget(self.radio_use_weight)
        mode_row.addWidget(self.radio_use_calories)
        add_layout.addLayout(mode_row)

        self.button_add_ingredient = QPushButton("Add ingredient")
        self.button_add_ingredient.setMinimumHeight(41)
        self.button_add_ingredient.setFont(font_12_bold)
        self.button_add_ingredient.setStyleSheet(_FOOD_BUTTON_STYLE)
        self.button_add_ingredient.clicked.connect(self._add_ingredient)
        add_layout.addWidget(self.button_add_ingredient)
        controls_layout.addWidget(group_add)

        group_totals = QGroupBox("Total")
        totals_layout = QHBoxLayout(group_totals)
        self.label_recipe_totals = QLabel("0 g\n0 kcal")
        self.label_recipe_totals.setFont(font_30_bold)
        self.label_recipe_totals.setAlignment(Qt.AlignmentFlag.AlignCenter)
        totals_layout.addWidget(self.label_recipe_totals)
        controls_layout.addWidget(group_totals)
        controls_layout.addStretch()

        middle = QWidget()
        middle_layout = QVBoxLayout(middle)
        middle_layout.setContentsMargins(8, 8, 8, 8)
        middle_layout.addWidget(QLabel("Recipes"))
        self.list_recipes = QListView()
        self.list_recipes.setStyleSheet(_LIST_STYLE)
        self._recipes_model = QStandardItemModel(self.list_recipes)
        self.list_recipes.setModel(self._recipes_model)
        self.list_recipes.clicked.connect(self._on_recipe_clicked)
        self.list_recipes.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_recipes.customContextMenuRequested.connect(self._show_recipe_context_menu)
        middle_layout.addWidget(self.list_recipes, 1)

        list_buttons = QHBoxLayout()
        self.button_new = make_emoji_push_button("New", "➕")  # noqa: RUF001
        self.button_new.clicked.connect(self._new_recipe)
        list_buttons.addWidget(self.button_new)
        middle_layout.addLayout(list_buttons)
        splitter.addWidget(middle)
        splitter.addWidget(controls)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)

        form = QFormLayout()
        self.line_recipe_name = QLineEdit()
        self.line_recipe_name.setPlaceholderText("Recipe name")
        self.check_recipe_drink = QCheckBox("This is a drink")
        form.addRow("Name:", self.line_recipe_name)
        form.addRow("", self.check_recipe_drink)
        right_layout.addLayout(form)

        self.table_ingredients = QTableWidget(0, _INGREDIENT_COLUMN_COUNT)
        self.table_ingredients.setObjectName("recipesIngredientsTable")
        self.table_ingredients.setHorizontalHeaderLabels(
            ["Name", "Weight", "kcal/100g", "Portion kcal", "Calculated", "Drink"]
        )
        self.table_ingredients.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_ingredients.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_ingredients.setAlternatingRowColors(False)
        self.table_ingredients.verticalHeader().setVisible(False)
        self._apply_ingredients_column_metrics()
        right_layout.addWidget(self.table_ingredients, 1)

        remove_row = QHBoxLayout()
        self.button_remove_ingredient = make_emoji_push_button("Remove selected", "🗑️")
        self.button_remove_ingredient.clicked.connect(self._remove_selected_ingredient)
        remove_row.addWidget(self.button_remove_ingredient)
        remove_row.addStretch()
        right_layout.addLayout(remove_row)

        self.button_save = make_emoji_push_button("Save recipe", "💾")
        self.button_save.clicked.connect(self._save_recipe)
        right_layout.addWidget(self.button_save)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 3)

    def _clear_editor(self) -> None:
        self._current_recipe_id = None
        self._ingredients = []
        self.line_recipe_name.clear()
        self.check_recipe_drink.setChecked(False)
        self._refresh_ingredients_table()

    def _delete_recipe(self, *, recipe_id: int, name: str) -> None:
        if self._db is None:
            return
        reply = message_box.question(
            self,
            "Delete recipe?",
            f"Delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not self._db.delete_recipe(recipe_id):
            message_box.warning(self, "Error", "Failed to delete recipe")
            return
        if self._current_recipe_id == recipe_id:
            self._clear_editor()
        self._reload_recipe_list(keep_selection=False)
        self.recipes_changed.emit()

    def _load_recipe(self, recipe_id: int) -> None:
        if self._db is None:
            return
        recipe = self._db.get_recipe_by_id(recipe_id)
        if recipe is None:
            return
        self._current_recipe_id = recipe.id
        self.line_recipe_name.setText(recipe.name)
        self.check_recipe_drink.setChecked(recipe.is_drink)
        rows = self._db.get_recipe_ingredients(recipe_id)
        self._ingredients = [
            RecipeIngredientInput(
                name=row.name,
                weight=row.weight,
                calories_per_100g=row.calories_per_100g,
                portion_calories=row.portion_calories,
                name_en=row.name_en,
                is_drink=row.is_drink,
            )
            for row in rows
        ]
        self._refresh_ingredients_table()

    def _new_recipe(self) -> None:
        self.list_recipes.clearSelection()
        self._clear_editor()
        self.line_recipe_name.setFocus()

    def _on_ingredient_completer_selected(self, text: str) -> None:
        bare = extract_food_name_from_display(text)
        self.line_ingredient_name.setText(bare)
        self._populate_ingredient_from_name(bare)

    def _on_ingredient_name_edited(self, text: str) -> None:
        self._completer_proxy.set_filter_text(text)
        if text:
            self._ingredient_completer.setCompletionPrefix(text)
            self._ingredient_completer.complete()
        else:
            self._completer_proxy.set_filter_text("")
            popup = self._ingredient_completer.popup()
            if popup is not None and popup.isVisible():
                popup.hide()

    def _on_recipe_clicked(self, index: QModelIndex) -> None:
        found = self._recipe_id_and_name_from_index(index)
        if found is not None:
            self._load_recipe(found[0])

    def _populate_ingredient_from_name(self, food_name: str) -> None:
        if self._db is None or not food_name:
            return
        food_item = self._db.get_food_item_by_name(food_name)
        if food_item is not None:
            self.spin_ingredient_weight.setValue(
                int(food_item.default_portion_weight) if food_item.default_portion_weight else 100
            )
            self.check_ingredient_drink.setChecked(food_item.is_drink)
            if food_item.default_portion_calories and food_item.default_portion_calories > 0:
                self.radio_use_calories.setChecked(True)
                self.spin_ingredient_calories.setValue(food_item.default_portion_calories)
            else:
                self.radio_use_weight.setChecked(True)
                self.spin_ingredient_calories.setValue(food_item.calories_per_100g or 0)
            return
        log_item = self._db.get_food_log_item_by_name(food_name)
        if log_item is None:
            return
        self.spin_ingredient_weight.setValue(int(log_item.weight) if log_item.weight else 100)
        self.check_ingredient_drink.setChecked(log_item.is_drink)
        if log_item.portion_calories and log_item.portion_calories > 0:
            self.radio_use_calories.setChecked(True)
            self.spin_ingredient_calories.setValue(log_item.portion_calories)
        else:
            self.radio_use_weight.setChecked(True)
            self.spin_ingredient_calories.setValue(log_item.calories_per_100g or 0)

    def _recipe_id_and_name_from_index(self, index: QModelIndex) -> tuple[int, str] | None:
        if not index.isValid():
            return None
        item = self._recipes_model.itemFromIndex(index)
        if item is None:
            return None
        recipe_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(recipe_id, int):
            return None
        return recipe_id, item.text()

    def _refresh_ingredients_table(self) -> None:
        self.table_ingredients.setRowCount(0)
        for ingredient in self._ingredients:
            row = self.table_ingredients.rowCount()
            self.table_ingredients.insertRow(row)
            calc = calculate_food_log_calories(
                ingredient.weight,
                ingredient.calories_per_100g,
                ingredient.portion_calories,
            )
            values = [
                ingredient.name,
                f"{ingredient.weight:.0f}" if ingredient.weight is not None else "",
                f"{ingredient.calories_per_100g:.2f}" if ingredient.calories_per_100g is not None else "",
                f"{ingredient.portion_calories:.2f}" if ingredient.portion_calories is not None else "",
                f"{calc:.1f}",
                "Yes" if ingredient.is_drink else "",
            ]
            for col, value in enumerate(values):
                self.table_ingredients.setItem(row, col, QTableWidgetItem(value))
            self._apply_ingredient_row_background(row)
        nutrition = calculate_recipe_nutrition(self._ingredients)
        per_100 = (
            f"{nutrition.calories_per_100g:.1f} kcal/100g" if nutrition.calories_per_100g is not None else "— kcal/100g"
        )
        self.label_recipe_totals.setText(
            f"{nutrition.total_weight:.0f} g\n{nutrition.total_calories:.1f} kcal\n{per_100}"
        )

    def _reload_recipe_list(self, *, keep_selection: bool) -> None:
        selected_id = self._current_recipe_id if keep_selection else None
        self._recipes_model.clear()
        if self._db is None:
            return
        recipes: list[RecipeRow] = self._db.get_all_recipes()
        for recipe in recipes:
            display = format_food_name_with_calories(
                recipe.name,
                recipe.calories_per_100g,
                None,
                is_drink=recipe.is_drink,
                is_recipe=True,
            )
            item = QStandardItem(display)
            item.setData(recipe.id, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self._recipes_model.appendRow(item)
        if selected_id is not None:
            self.select_recipe_by_id(selected_id)

    def _remove_selected_ingredient(self) -> None:
        rows = sorted({index.row() for index in self.table_ingredients.selectedIndexes()}, reverse=True)
        if not rows:
            return
        for row in rows:
            if 0 <= row < len(self._ingredients):
                del self._ingredients[row]
        self._refresh_ingredients_table()

    def _save_recipe(self) -> None:
        if self._db is None:
            message_box.warning(self, "Error", "Database connection not available")
            return
        name = self.line_recipe_name.text().strip()
        if not name:
            message_box.warning(self, "Error", "Enter recipe name")
            return
        if len(self._ingredients) < 1:
            message_box.warning(self, "Error", "Add at least one ingredient")
            return

        existing = self._db.get_recipe_by_name(name)
        recipe_id = self._current_recipe_id
        if existing is not None and (recipe_id is None or existing.id != recipe_id):
            message_box.warning(self, "Error", f"Recipe '{name}' already exists")
            return

        saved_id = self._db.save_recipe(
            name,
            self._ingredients,
            recipe_id=recipe_id,
            is_drink=self.check_recipe_drink.isChecked(),
        )
        if saved_id is None:
            message_box.warning(self, "Error", "Failed to save recipe")
            return
        self._current_recipe_id = saved_id
        self._reload_recipe_list(keep_selection=True)
        self.recipes_changed.emit()
        message_box.information(self, "Saved", f"Recipe '{name}' saved")

    def _setup_ingredient_completer(self) -> None:
        self._ingredient_completer = QCompleter(self._completer_proxy, self)
        self._ingredient_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._ingredient_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._ingredient_completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self._ingredient_completer.setCompletionRole(Qt.ItemDataRole.EditRole)
        self.line_ingredient_name.setCompleter(self._ingredient_completer)
        setup_completer_item_tooltips(self._ingredient_completer)
        self.line_ingredient_name.textEdited.connect(self._on_ingredient_name_edited)
        self._ingredient_completer.activated.connect(self._on_ingredient_completer_selected)

    def _show_recipe_context_menu(self, position: QPoint) -> None:
        index = self.list_recipes.indexAt(position)
        found = self._recipe_id_and_name_from_index(index)
        if found is None:
            return
        recipe_id, name = found
        self.list_recipes.setCurrentIndex(index)
        self._load_recipe(recipe_id)
        menu = QMenu(self)
        delete_action = add_delete_action(menu)
        delete_action.triggered.connect(lambda: self._delete_recipe(recipe_id=recipe_id, name=name))
        apply_leading_emoji_icons(menu)
        viewport = self.list_recipes.viewport()
        if viewport is None:
            return
        menu.popup(viewport.mapToGlobal(position))

    def _update_ingredient_autocomplete(self) -> None:
        self._completer_source.clear()
        if self._db is None:
            return
        try:
            log_names = self._db.get_recent_food_names_for_autocomplete(500)
            item_names = self._db.get_food_item_names_for_autocomplete()
            merged = merge_food_autocomplete_entries(log_names, item_names)
            for entry in merged:
                display = format_food_name_with_calories(
                    entry.name,
                    entry.calories_per_100g,
                    None,
                    is_recipe=entry.is_recipe,
                )
                item = QStandardItem(display if entry.is_recipe else entry.name)
                item.setData(entry.name, Qt.ItemDataRole.EditRole)
                item.setData(entry.name_en or "", Qt.ItemDataRole.UserRole)
                self._completer_source.appendRow(item)
            self._completer_proxy.invalidateFilter()
        except Exception:
            logger.exception("Error updating recipe ingredient autocomplete")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the recipes UI; call `set_database_manager` before loading data.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_recipe_id: int | None = None
        self._ingredients: list[RecipeIngredientInput] = []
        self._completer_source = QStandardItemModel(self)
        self._completer_proxy = FoodNameAutocompleteProxyModel(self)
        self._completer_proxy.setSourceModel(self._completer_source)
        self._build_ui()
        self._setup_ingredient_completer()
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self) -> None
```

Reload recipe list and ingredient-name autocomplete from the database.

<details>
<summary>Code:</summary>

```python
def refresh(self) -> None:
        self._update_ingredient_autocomplete()
        self._reload_recipe_list(keep_selection=True)
```

</details>

### ⚙️ Method `select_recipe_by_id`

```python
def select_recipe_by_id(self, recipe_id: int) -> None
```

Select a recipe in the list after a refresh, if present.

<details>
<summary>Code:</summary>

```python
def select_recipe_by_id(self, recipe_id: int) -> None:
        for row in range(self._recipes_model.rowCount()):
            item = self._recipes_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == recipe_id:
                index = self._recipes_model.indexFromItem(item)
                self.list_recipes.setCurrentIndex(index)
                self._load_recipe(recipe_id)
                return
```

</details>

### ⚙️ Method `set_database_manager`

```python
def set_database_manager(self, db_manager: DatabaseManager | None) -> None
```

Attach the food database and refresh the recipe list.

<details>
<summary>Code:</summary>

```python
def set_database_manager(self, db_manager: DatabaseManager | None) -> None:
        self._db = db_manager
        self.refresh()
```

</details>
