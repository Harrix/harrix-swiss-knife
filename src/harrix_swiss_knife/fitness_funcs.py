from functools import wraps
from typing import Callable

from PySide6.QtWidgets import QMessageBox


def validate_date(method: Callable) -> Callable:
    """
    Decorator to validate date before executing a method.

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
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        date = self.lineEdit_date.text()
        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return
        return method(self, *args, **kwargs)

    return wrapper
