---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recipes_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecipesDialog`](#%EF%B8%8F-class-recipesdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `recipes_widget (property)`](#%EF%B8%8F-method-recipes_widget-property)

</details>

## 🏛️ Class `RecipesDialog`

```python
class RecipesDialog(QDialog)
```

Show and edit recipes with the same UI formerly on the Recipes tab.

<details>
<summary>Code:</summary>

```python
class RecipesDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        select_recipe_id: int | None = None,
    ) -> None:
        """Build the dialog, attach `db_manager`, and optionally select a recipe."""
        super().__init__(parent)
        self.setWindowTitle("Recipes")
        qt_modality.set_owner_window_modal(self)
        self._match_parent_window()

        self._widget = RecipesWidget(self)
        self._widget.set_database_manager(db_manager)
        if select_recipe_id is not None:
            self._widget.select_recipe_by_id(select_recipe_id)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_button = make_lucide_push_button("Close", CANCEL_BUTTON_ICON)
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    @property
    def recipes_widget(self) -> RecipesWidget:
        """Embedded recipes editor."""
        return self._widget

    def _match_parent_window(self) -> None:
        """Use the same size and screen position as the owning Food window."""
        parent = self.parentWidget()
        if parent is None:
            self.resize(*_FALLBACK_SIZE)
            return
        owner = parent.window()
        if owner.windowState() & Qt.WindowState.WindowMaximized:
            self.setWindowState(Qt.WindowState.WindowMaximized)
            return
        top_left = owner.mapToGlobal(QPoint(0, 0))
        self.setGeometry(top_left.x(), top_left.y(), owner.width(), owner.height())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, db_manager: DatabaseManager, *, select_recipe_id: int | None = None) -> None
```

Build the dialog, attach `db_manager`, and optionally select a recipe.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        select_recipe_id: int | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Recipes")
        qt_modality.set_owner_window_modal(self)
        self._match_parent_window()

        self._widget = RecipesWidget(self)
        self._widget.set_database_manager(db_manager)
        if select_recipe_id is not None:
            self._widget.select_recipe_by_id(select_recipe_id)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_button = make_lucide_push_button("Close", CANCEL_BUTTON_ICON)
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
```

</details>

### ⚙️ Method `recipes_widget (property)`

```python
def recipes_widget(self) -> RecipesWidget
```

Embedded recipes editor.

<details>
<summary>Code:</summary>

```python
def recipes_widget(self) -> RecipesWidget:
        return self._widget
```

</details>
