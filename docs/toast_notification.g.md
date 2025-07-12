---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `toast_notification.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Class `ToastNotification`](#class-toastnotification)
  - [Method `__init__`](#method-__init__)

</details>

## Class `ToastNotification`

```python
class ToastNotification(toast_notification_base.ToastNotificationBase)
```

A temporary toast notification that automatically closes after a specified duration.

This class extends ToastNotificationBase to add automatic closing functionality.
The notification will appear on screen and automatically disappear after
the specified duration.

Attributes:

- Inherits all attributes from `ToastNotificationBase`

Args:

- `message` (`str`): The text to be displayed in the notification.
- `duration` (`int`, optional): Time in milliseconds before the notification
  automatically closes. Defaults to `1000`.
- `parent` (`QWidget`, optional): The parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
class ToastNotification(toast_notification_base.ToastNotificationBase):

    def __init__(self, message: str, duration: int = 1000, parent: QWidget | None = None) -> None:
        """Initialize the toast notification with automatic closing functionality.

        Args:

        - `message` (`str`): The text to be displayed in the notification.
        - `duration` (`int`, optional): Time in milliseconds before the notification
          automatically closes. Defaults to `1000`.
        - `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

        """
        super().__init__(message, parent)
        QTimer.singleShot(duration, self.close)
```

</details>

### Method `__init__`

```python
def __init__(self, message: str, duration: int = 1000, parent: QWidget | None = None) -> None
```

Initialize the toast notification with automatic closing functionality.

Args:

- `message` (`str`): The text to be displayed in the notification.
- `duration` (`int`, optional): Time in milliseconds before the notification
  automatically closes. Defaults to `1000`.
- `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str, duration: int = 1000, parent: QWidget | None = None) -> None:
        super().__init__(message, parent)
        QTimer.singleShot(duration, self.close)
```

</details>
