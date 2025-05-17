---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `fitness_funcs.py`

## Function `validate_date`

```python
def validate_date(method: Callable) -> Callable
```

Decorate to validate date before executing a method.

This decorator checks if the date in the lineEdit_date field has a valid format
before executing the decorated method. If the date is invalid, it shows a warning
message and prevents the method execution.

Args:

- `method` (`Callable`): The method to be decorated.

Returns:

- `Callable`: The wrapped method that includes date validation.

Example:

```python
@validate_date
def save_record(self):
    # This will only execute if the date is valid
    pass
```

<details>
<summary>Code:</summary>

```python
def validate_date(method: Callable) -> Callable:

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        date = self.lineEdit_date.text()
        if not self._is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return None
        return method(self, *args, **kwargs)

    return wrapper
```

</details>
