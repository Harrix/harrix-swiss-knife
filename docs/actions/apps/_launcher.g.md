---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `_launcher.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppLauncherAction`](#%EF%B8%8F-class-applauncheraction)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_clear_main_window_ref`](#%EF%B8%8F-method-_clear_main_window_ref)

</details>

## 🏛️ Class `AppLauncherAction`

```python
class AppLauncherAction(ActionBase)
```

Launch a tracker application window, reusing an existing instance when valid.

<details>
<summary>Code:</summary>

```python
class AppLauncherAction(ActionBase):

    main_window_class: ClassVar[type]
    show_in_compact_mode: ClassVar[bool] = True

    hide_on_close: ClassVar[bool] = False

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching application")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = self.main_window_class(hide_on_close=type(self).hide_on_close)
            self.main_window.destroyed.connect(self._clear_main_window_ref)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _clear_main_window_ref(self, *_args: object) -> None:
        self.main_window = None
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = self.main_window_class(hide_on_close=type(self).hide_on_close)
            self.main_window.destroyed.connect(self._clear_main_window_ref)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>

### ⚙️ Method `_clear_main_window_ref`

```python
def _clear_main_window_ref(self, *_args: object) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _clear_main_window_ref(self, *_args: object) -> None:
        self.main_window = None
```

</details>
