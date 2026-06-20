---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `db_guard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `_SupportsDbValidation`](#%EF%B8%8F-class-_supportsdbvalidation)
  - [⚙️ Method `_validate_database_connection`](#%EF%B8%8F-method-_validate_database_connection)
- [🏛️ Class `_SupportsShowError`](#%EF%B8%8F-class-_supportsshowerror)
  - [⚙️ Method `_show_error`](#%EF%B8%8F-method-_show_error)
- [🔧 Function `requires_database`](#-function-requires_database)

</details>

## 🏛️ Class `_SupportsDbValidation`

```python
class _SupportsDbValidation(Protocol)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
class _SupportsDbValidation(Protocol):
    def _validate_database_connection(self) -> bool: ...
```

</details>

### ⚙️ Method `_validate_database_connection`

```python
def _validate_database_connection(self) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _validate_database_connection(self) -> bool: ...
```

</details>

## 🏛️ Class `_SupportsShowError`

```python
class _SupportsShowError(Protocol)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
class _SupportsShowError(Protocol):
    def _show_error(self, title: str, message: str) -> None: ...
```

</details>

### ⚙️ Method `_show_error`

```python
def _show_error(self, title: str, message: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _show_error(self, title: str, message: str) -> None: ...
```

</details>

## 🔧 Function `requires_database`

```python
def requires_database() -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]
```

Ensure database connection is available before executing method.

<details>
<summary>Code:</summary>

```python
def requires_database(
    *, is_show_warning: bool = True
) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:

    def decorator(
        func: Callable[Concatenate[SelfT, P], R],
    ) -> Callable[Concatenate[SelfT, P], R | None]:
        @wraps(func)
        def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R | None:
            validator = cast("_SupportsDbValidation", self)
            if not validator._validate_database_connection():  # noqa: SLF001
                if is_show_warning:
                    if isinstance(self, _SupportsShowError):
                        self._show_error("❌ Database Error", "❌ Database connection not available")
                    else:
                        message_box.warning(None, "❌ Database Error", "❌ Database connection not available")
                return None

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
```

</details>
