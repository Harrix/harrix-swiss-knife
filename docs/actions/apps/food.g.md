---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFood`](#%EF%B8%8F-class-onfood)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnFood`

```python
class OnFood(ActionBase)
```

Launch the food tracking application.

This action opens the food tracker application in a new window or brings
the existing window to the foreground if it's already open. The food tracker
allows users to record, monitor, and analyze their food intake and nutrition.

<details>
<summary>Code:</summary>

```python
class OnFood(ActionBase):

    icon = "🍔"
    title = "Food tracker"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFood action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching food tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Launch the food tracking application."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = food_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnFood action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Launch the food tracking application.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = food_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>
