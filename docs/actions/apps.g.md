---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `apps.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFinance`](#%EF%B8%8F-class-onfinance)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🏛️ Class `OnFitness`](#%EF%B8%8F-class-onfitness)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
- [🏛️ Class `OnFood`](#%EF%B8%8F-class-onfood)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)

</details>

## 🏛️ Class `OnFinance`

```python
class OnFinance(ActionBase)
```

Launch the finance tracking application.

This action opens the finance tracker application in a new window or brings
the existing window to the foreground if it's already open. The finance tracker
allows users to record, monitor, and analyze their finance.

<details>
<summary>Code:</summary>

```python
class OnFinance(ActionBase):

    icon = "💰"
    title = "Finance tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFinance action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching finance tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = finance_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnFinance action.

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
            self.main_window = finance_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

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
            self.main_window = fitness_main.MainWindow()

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
            self.main_window = fitness_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

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

    icon = "🍎"
    title = "Food tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFood action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching food tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
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

Execute the code. Main method for the action.

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
