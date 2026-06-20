---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exit_.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnExit`](#️-class-onexit)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnExit`

```python
class OnExit(ActionBase)
```

Exit the application.

This action terminates the current Qt application instance,
closing all windows and ending the program execution.

<details>
<summary>Code:</summary>

```python
class OnExit(ActionBase):

    icon = "×"  # noqa: RUF001
    title = "Exit"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Exit the application."""
        QApplication.quit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnExit action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Exit the application.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        QApplication.quit()
```

</details>
