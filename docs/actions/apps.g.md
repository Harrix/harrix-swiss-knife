---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `apps.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFitness`](#%EF%B8%8F-class-onfitness)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnFitness`

```python
class OnFitness(ActionBase)
```

Launch the fitness tracking application.

This action opens the fitness tracker application in a new window or brings
the existing window to the foreground if it's already open. The fitness tracker
allows users to record, monitor, and analyze their physical activities and
exercise routines.

<details>
<summary>Code:</summary>

```python
class OnFitness(ActionBase):

    icon = "🏃🏻"
    title = "Fitness tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFitness action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching fitness tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnFitness action.

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

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>
