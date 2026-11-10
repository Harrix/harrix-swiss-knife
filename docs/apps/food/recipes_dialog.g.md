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
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

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
        self.setObjectName("recipesDialog")
        self.setWindowTitle("Recipes")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        qt_modality.set_owner_window_modal(self)

        prepare_fluent_app_window(self)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        self._win11_caption = install_win11_caption(self)

        body = QWidget(self)
        body.setObjectName("recipesDialogBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(8)

        self._widget = RecipesWidget(body)
        self._widget.set_database_manager(db_manager)
        if select_recipe_id is not None:
            self._widget.select_recipe_by_id(select_recipe_id)
        body_layout.addWidget(self._widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_button = make_lucide_push_button("Close", CANCEL_BUTTON_ICON)
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        body_layout.addLayout(buttons)

        self._root.addWidget(body, 1)
        install_fluent_app_window(self)
        self._match_parent_window()

    @property
    def recipes_widget(self) -> RecipesWidget:
        """Embedded recipes editor."""
        return self._widget

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Keep Fluent chrome after the first polish pass."""
        super().showEvent(event)
        install_fluent_app_window(self)

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
        self.setObjectName("recipesDialog")
        self.setWindowTitle("Recipes")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        qt_modality.set_owner_window_modal(self)

        prepare_fluent_app_window(self)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        self._win11_caption = install_win11_caption(self)

        body = QWidget(self)
        body.setObjectName("recipesDialogBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(8)

        self._widget = RecipesWidget(body)
        self._widget.set_database_manager(db_manager)
        if select_recipe_id is not None:
            self._widget.select_recipe_by_id(select_recipe_id)
        body_layout.addWidget(self._widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_button = make_lucide_push_button("Close", CANCEL_BUTTON_ICON)
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        body_layout.addLayout(buttons)

        self._root.addWidget(body, 1)
        install_fluent_app_window(self)
        self._match_parent_window()
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

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Keep Fluent chrome after the first polish pass.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        install_fluent_app_window(self)
```

</details>
