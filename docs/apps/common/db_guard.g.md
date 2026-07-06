---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `db_guard.py`

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
