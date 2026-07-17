---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `_launcher.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppLauncherAction`](#️-class-applauncheraction)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `get_main_window_class`](#️-method-get_main_window_class)
  - [⚙️ Method `_clear_main_window_ref`](#️-method-_clear_main_window_ref)

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

    main_window_module: ClassVar[str] = ""
    main_window_class_name: ClassVar[str] = "MainWindow"
    _resolved_main_window_class: ClassVar[type | None] = None
    show_in_compact_mode: ClassVar[bool] = True

    hide_on_close: ClassVar[bool] = False

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None
        self._is_creating_window = False

    @ActionBase.handle_exceptions("launching application")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.main_window is not None and isValid(self.main_window):
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            return

        if self._is_creating_window:
            return

        app = QApplication.instance()
        if app is not None:
            self.main_window = None
            for _ in range(10):
                app.processEvents()

        self._is_creating_window = True
        try:
            window = type(self).get_main_window_class()(hide_on_close=type(self).hide_on_close)
            self.main_window = window
            window.destroyed.connect(self._clear_main_window_ref)
        except Exception:
            self.main_window = None
            traceback.print_exc()
            raise
        finally:
            self._is_creating_window = False

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    @classmethod
    def get_main_window_class(cls) -> type:
        """Import and cache the tracker ``MainWindow`` class on first use."""
        if cls._resolved_main_window_class is None:
            module = importlib.import_module(cls.main_window_module)
            cls._resolved_main_window_class = getattr(module, cls.main_window_class_name)
        return cls._resolved_main_window_class

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
        self._is_creating_window = False
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
        if self.main_window is not None and isValid(self.main_window):
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            return

        if self._is_creating_window:
            return

        app = QApplication.instance()
        if app is not None:
            self.main_window = None
            for _ in range(10):
                app.processEvents()

        self._is_creating_window = True
        try:
            window = type(self).get_main_window_class()(hide_on_close=type(self).hide_on_close)
            self.main_window = window
            window.destroyed.connect(self._clear_main_window_ref)
        except Exception:
            self.main_window = None
            traceback.print_exc()
            raise
        finally:
            self._is_creating_window = False

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
```

</details>

### ⚙️ Method `get_main_window_class`

```python
def get_main_window_class(cls) -> type
```

Import and cache the tracker `MainWindow` class on first use.

<details>
<summary>Code:</summary>

```python
def get_main_window_class(cls) -> type:
        if cls._resolved_main_window_class is None:
            module = importlib.import_module(cls.main_window_module)
            cls._resolved_main_window_class = getattr(module, cls.main_window_class_name)
        return cls._resolved_main_window_class
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
