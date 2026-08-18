---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `toast_progress_notification.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ToastProgressNotification`](#%EF%B8%8F-class-toastprogressnotification)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `done (property)`](#%EF%B8%8F-method-done-property)
  - [⚙️ Method `set_progress`](#%EF%B8%8F-method-set_progress)
  - [⚙️ Method `total (property)`](#%EF%B8%8F-method-total-property)

</details>

## 🏛️ Class `ToastProgressNotification`

```python
class ToastProgressNotification(toast_countdown_notification.ToastCountdownNotification)
```

Countdown toast that also shows `done / total` progress.

Attributes:

- [`done`](#%EF%B8%8F-method-done-property) (`int`): Completed work units.
- [`total`](#%EF%B8%8F-method-total-property) (`int`): Total work units (0 means unknown / indeterminate).
- `progress_bar` (`QProgressBar`): Determinate progress indicator under the label.

<details>
<summary>Code:</summary>

```python
class ToastProgressNotification(toast_countdown_notification.ToastCountdownNotification):

    def __init__(
        self,
        message: str = "Process is running…",
        *,
        total: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize progress toast with countdown and progress bar."""
        self._done = 0
        self._total = max(0, total)
        super().__init__(message, parent)

        self._progress_container = QWidget(self)
        self._progress_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar = QProgressBar(self._progress_container)
        self.progress_bar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setMinimumWidth(220)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout = QVBoxLayout(self._progress_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.progress_bar)

        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.setSpacing(0)
            layout.addWidget(self._progress_container)

        self._apply_progress_style(compact=False)
        self.set_progress(0, self._total)

    @property
    def done(self) -> int:
        """Number of completed work units."""
        return self._done

    def set_progress(self, done: int, total: int | None = None) -> None:
        """Update progress values and refresh the progress bar.

        Args:

        - `done` (`int`): Completed work units.
        - `total` (`int | None`): Optional new total. When `None`, keep the current total.

        """
        if total is not None:
            self._total = max(0, total)
        if self._total <= 0:
            self._done = max(0, done)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setValue(0)
        else:
            self._done = max(0, min(done, self._total))
            self.progress_bar.setRange(0, self._total)
            self.progress_bar.setValue(self._done)
        self._refresh_label_text()

    @property
    def total(self) -> int:
        """Total number of work units."""
        return self._total

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and progress bar."""
        super()._apply_compact_style()
        self._apply_progress_style(compact=True)
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and progress bar."""
        super()._apply_default_style()
        self._apply_progress_style(compact=False)
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_progress_style(self, *, compact: bool) -> None:
        """Style the progress chrome: rounded track with vertically centered text."""
        if not hasattr(self, "progress_bar") or not hasattr(self, "_progress_container"):
            return

        if compact:
            radius = 8
            bar_radius = 5
            bar_height = 16
            h_pad = 12
            top_pad = 2
            bottom_pad = 8
            font_size = "9pt"
            label_padding = "8px 12px 4px 12px"
        else:
            radius = 10
            bar_radius = 6
            bar_height = 22
            h_pad = 20
            top_pad = 4
            bottom_pad = 14
            font_size = "11pt"
            label_padding = "15px 20px 6px 20px"

        self._progress_container.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "border-top-left-radius: 0px;"
            "border-top-right-radius: 0px;"
            f"border-bottom-left-radius: {radius}px;"
            f"border-bottom-right-radius: {radius}px;",
        )
        container_layout = self._progress_container.layout()
        if isinstance(container_layout, QVBoxLayout):
            container_layout.setContentsMargins(h_pad, top_pad, h_pad, bottom_pad)
            container_layout.setAlignment(self.progress_bar, Qt.AlignmentFlag.AlignVCenter)

        self.progress_bar.setFixedHeight(bar_height)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "background-color: rgba(70, 70, 70, 255);"
            "color: white;"
            "border: none;"
            f"border-radius: {bar_radius}px;"
            "padding: 0px;"
            "margin: 0px;"
            "text-align: center;"
            f"font-size: {font_size};"
            "font-weight: bold;"
            "}"
            "QProgressBar::chunk {"
            "background-color: rgba(90, 170, 255, 220);"
            f"border-radius: {bar_radius}px;"
            "margin: 0px;"
            "}",
        )
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            f"padding: {label_padding};"
            f"border-top-left-radius: {radius}px;"
            f"border-top-right-radius: {radius}px;"
            "border-bottom-left-radius: 0px;"
            "border-bottom-right-radius: 0px;"
            f"font-size: {'10pt' if compact else '16pt'};"
            "font-weight: bold;",
        )

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed time, and progress summary."""
        if not hasattr(self, "progress_bar"):
            return
        elapsed = getattr(self, "elapsed_seconds", 0)
        if self._is_pinned:
            progress = f"{self._done}/{self._total}" if self._total > 0 else str(self._done)
            self.label.setText(f"{self.message}\n{elapsed}s · {progress}")
        elif self._total > 0:
            self.label.setText(
                f"{self.message}\nSeconds elapsed: {elapsed}\nProgress: {self._done} / {self._total}",
            )
        else:
            self.label.setText(f"{self.message}\nSeconds elapsed: {elapsed}")
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = 'Process is running…', *, total: int = 0, parent: QWidget | None = None) -> None
```

Initialize progress toast with countdown and progress bar.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        message: str = "Process is running…",
        *,
        total: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        self._done = 0
        self._total = max(0, total)
        super().__init__(message, parent)

        self._progress_container = QWidget(self)
        self._progress_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar = QProgressBar(self._progress_container)
        self.progress_bar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setMinimumWidth(220)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout = QVBoxLayout(self._progress_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.progress_bar)

        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.setSpacing(0)
            layout.addWidget(self._progress_container)

        self._apply_progress_style(compact=False)
        self.set_progress(0, self._total)
```

</details>

### ⚙️ Method `done (property)`

```python
def done(self) -> int
```

Number of completed work units.

<details>
<summary>Code:</summary>

```python
def done(self) -> int:
        return self._done
```

</details>

### ⚙️ Method `set_progress`

```python
def set_progress(self, done: int, total: int | None = None) -> None
```

Update progress values and refresh the progress bar.

Args:

- [`done`](#%EF%B8%8F-method-done-property) (`int`): Completed work units.
- [`total`](#%EF%B8%8F-method-total-property) (`int | None`): Optional new total. When `None`, keep the current total.

<details>
<summary>Code:</summary>

```python
def set_progress(self, done: int, total: int | None = None) -> None:
        if total is not None:
            self._total = max(0, total)
        if self._total <= 0:
            self._done = max(0, done)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setValue(0)
        else:
            self._done = max(0, min(done, self._total))
            self.progress_bar.setRange(0, self._total)
            self.progress_bar.setValue(self._done)
        self._refresh_label_text()
```

</details>

### ⚙️ Method `total (property)`

```python
def total(self) -> int
```

Total number of work units.

<details>
<summary>Code:</summary>

```python
def total(self) -> int:
        return self._total
```

</details>
