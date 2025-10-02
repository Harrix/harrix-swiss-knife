---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `toast_countdown_notification.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ToastCountdownNotification`](#%EF%B8%8F-class-toastcountdownnotification)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `start_countdown`](#%EF%B8%8F-method-start_countdown)
  - [⚙️ Method `update_time`](#%EF%B8%8F-method-update_time)
  - [⚙️ Method `_refresh_label_text`](#%EF%B8%8F-method-_refresh_label_text)

</details>

## 🏛️ Class `ToastCountdownNotification`

```python
class ToastCountdownNotification(toast_notification_base.ToastNotificationBase)
```

A toast notification that displays an elapsed time counter.

This class extends ToastNotificationBase to show a notification with a running
counter that tracks elapsed time in seconds. Useful for indicating ongoing
processes while showing how much time has passed.

Attributes:

- `elapsed_seconds` (`int`): The number of seconds that have elapsed since starting the countdown.
- `timer` (`QTimer`): Timer object that triggers the time update every second.
- `start_time` (`QTime`): The time when the countdown was started.

Args:

- `message` (`str`, optional): The text to be displayed in the notification.
  Defaults to `"Process is running…"`.
- `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
class ToastCountdownNotification(toast_notification_base.ToastNotificationBase):

    def __init__(self, message: str = "Process is running…", parent: QWidget | None = None) -> None:
        """Initialize the countdown notification with timer functionality.

        Args:

        - `message` (`str`, optional): The text to be displayed in the notification.
          Defaults to `"Process is running…"`.
        - `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

        """
        super().__init__(message, parent)

        self.elapsed_seconds: int = 0
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle the notification close event.

        Stops the timer when the notification is closed to prevent memory leaks.

        Args:

        - `event` (`QCloseEvent`): The close event object.

        """
        self.timer.stop()
        super().closeEvent(event)

    def start_countdown(self) -> None:
        """Start the countdown timer and initialize the display."""
        self.start_time: QTime = QTime.currentTime()
        self.timer.start(1000)
        self._refresh_label_text()

    def update_time(self) -> None:
        """Update the elapsed time counter.

        This method is called automatically every second when the timer is active.
        """
        now: QTime = QTime.currentTime()
        self.elapsed_seconds = self.start_time.secsTo(now)
        self._refresh_label_text()

    def _refresh_label_text(self) -> None:
        """Update the notification text with the current elapsed time.

        Refreshes the label to show the original message and the number of seconds
        that have elapsed since the countdown started.
        """
        self.label.setText(f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = "Process is running…", parent: QWidget | None = None) -> None
```

Initialize the countdown notification with timer functionality.

Args:

- `message` (`str`, optional): The text to be displayed in the notification.
  Defaults to `"Process is running…"`.
- `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str = "Process is running…", parent: QWidget | None = None) -> None:
        super().__init__(message, parent)

        self.elapsed_seconds: int = 0
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Handle the notification close event.

Stops the timer when the notification is closed to prevent memory leaks.

Args:

- `event` (`QCloseEvent`): The close event object.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.timer.stop()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `start_countdown`

```python
def start_countdown(self) -> None
```

Start the countdown timer and initialize the display.

<details>
<summary>Code:</summary>

```python
def start_countdown(self) -> None:
        self.start_time: QTime = QTime.currentTime()
        self.timer.start(1000)
        self._refresh_label_text()
```

</details>

### ⚙️ Method `update_time`

```python
def update_time(self) -> None
```

Update the elapsed time counter.

This method is called automatically every second when the timer is active.

<details>
<summary>Code:</summary>

```python
def update_time(self) -> None:
        now: QTime = QTime.currentTime()
        self.elapsed_seconds = self.start_time.secsTo(now)
        self._refresh_label_text()
```

</details>

### ⚙️ Method `_refresh_label_text`

```python
def _refresh_label_text(self) -> None
```

Update the notification text with the current elapsed time.

Refreshes the label to show the original message and the number of seconds
that have elapsed since the countdown started.

<details>
<summary>Code:</summary>

```python
def _refresh_label_text(self) -> None:
        self.label.setText(f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}")
```

</details>
