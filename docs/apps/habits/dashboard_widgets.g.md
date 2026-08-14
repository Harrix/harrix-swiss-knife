---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dashboard_widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CheckCircle`](#%EF%B8%8F-class-checkcircle)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `day_state`](#%EF%B8%8F-method-day_state)
  - [⚙️ Method `is_done`](#%EF%B8%8F-method-is_done)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_value`](#%EF%B8%8F-method-set_value)
  - [⚙️ Method `value`](#%EF%B8%8F-method-value)
- [🏛️ Class `HabitIconBadge`](#%EF%B8%8F-class-habiticonbadge)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `set_habit`](#%EF%B8%8F-method-set_habit)
- [🏛️ Class `HabitRow`](#%EF%B8%8F-class-habitrow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `habit_id`](#%EF%B8%8F-method-habit_id)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent-1)
  - [⚙️ Method `set_habit_data`](#%EF%B8%8F-method-set_habit_data)
- [🏛️ Class `MonthCalendarGrid`](#%EF%B8%8F-class-monthcalendargrid)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `set_month`](#%EF%B8%8F-method-set_month)
- [🏛️ Class `ProgressRing`](#%EF%B8%8F-class-progressring)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `set_ratio`](#%EF%B8%8F-method-set_ratio)
- [🏛️ Class `StatCard`](#%EF%B8%8F-class-statcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `set_value`](#%EF%B8%8F-method-set_value-1)
- [🏛️ Class `WeekDayHeader`](#%EF%B8%8F-class-weekdayheader)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `set_day`](#%EF%B8%8F-method-set_day)
- [🔧 Function `habit_accent_color`](#-function-habit_accent_color)
- [🔧 Function `habit_day_state`](#-function-habit_day_state)
- [🔧 Function `habit_glyph`](#-function-habit_glyph)
- [🔧 Function `weekday_short`](#-function-weekday_short)

</details>

## 🏛️ Class `CheckCircle`

```python
class CheckCircle(QWidget)
```

Clickable day circle for absent, not done, done, or numeric values.

<details>
<summary>Code:</summary>

```python
class CheckCircle(QWidget):

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None, *, size: int = 22) -> None:  # noqa: D107
        super().__init__(parent)
        self._value: int | None = None
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_tooltip()

    def day_state(self) -> HabitDayState:
        """Return visual state for the stored value."""
        return habit_day_state(self._value)

    def is_done(self) -> bool:
        """Return whether the day is marked completed (value > 0)."""
        return self._value is not None and self._value > 0

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit clicked on left press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw absent, zero, completed, or numeric day circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        margin = 1.0
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)
        state = self.day_state()

        if state == "absent":
            pen = QPen(COLOR_TRACK, 1.5)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rect)
            return

        if state == "zero":
            painter.setPen(QPen(COLOR_TRACK, 1.5))
            painter.setBrush(COLOR_BG_MUTED)
            painter.drawEllipse(rect)
            return

        if state == "one":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(COLOR_PRIMARY)
            painter.drawEllipse(rect)
            pen = QPen(QColor("white"), max(1.8, self._size * 0.1))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            x0 = rect.left() + rect.width() * 0.28
            y0 = rect.top() + rect.height() * 0.52
            x1 = rect.left() + rect.width() * 0.42
            y1 = rect.top() + rect.height() * 0.68
            x2 = rect.left() + rect.width() * 0.72
            y2 = rect.top() + rect.height() * 0.32
            painter.drawLine(QPointF(x0, y0), QPointF(x1, y1))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(COLOR_SUCCESS)
        painter.drawEllipse(rect)
        text = str(self._value)
        font = QFont(self.font())
        digit_count = max(len(text), 1)
        font.setPointSizeF(max(5.0, self._size * min(0.42, 0.64 / digit_count)))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)

    def set_value(self, value: int | None) -> None:
        """Set stored process-habit value (``None`` = no database record)."""
        self._value = value
        self._apply_tooltip()
        self.update()

    def value(self) -> int | None:
        """Return stored process-habit value, or ``None`` if there is no record."""
        return self._value

    def _apply_tooltip(self) -> None:
        state = self.day_state()
        if state == "absent":
            self.setToolTip("No record")
        elif state == "zero":
            self.setToolTip("Not completed (0)")
        elif state == "one":
            self.setToolTip("Completed")
        else:
            self.setToolTip(f"Value: {self._value}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 22) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 22) -> None:  # noqa: D107
        super().__init__(parent)
        self._value: int | None = None
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_tooltip()
```

</details>

### ⚙️ Method `day_state`

```python
def day_state(self) -> HabitDayState
```

Return visual state for the stored value.

<details>
<summary>Code:</summary>

```python
def day_state(self) -> HabitDayState:
        return habit_day_state(self._value)
```

</details>

### ⚙️ Method `is_done`

```python
def is_done(self) -> bool
```

Return whether the day is marked completed (value > 0).

<details>
<summary>Code:</summary>

```python
def is_done(self) -> bool:
        return self._value is not None and self._value > 0
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Emit clicked on left press.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Draw absent, zero, completed, or numeric day circle.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        margin = 1.0
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)
        state = self.day_state()

        if state == "absent":
            pen = QPen(COLOR_TRACK, 1.5)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rect)
            return

        if state == "zero":
            painter.setPen(QPen(COLOR_TRACK, 1.5))
            painter.setBrush(COLOR_BG_MUTED)
            painter.drawEllipse(rect)
            return

        if state == "one":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(COLOR_PRIMARY)
            painter.drawEllipse(rect)
            pen = QPen(QColor("white"), max(1.8, self._size * 0.1))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            x0 = rect.left() + rect.width() * 0.28
            y0 = rect.top() + rect.height() * 0.52
            x1 = rect.left() + rect.width() * 0.42
            y1 = rect.top() + rect.height() * 0.68
            x2 = rect.left() + rect.width() * 0.72
            y2 = rect.top() + rect.height() * 0.32
            painter.drawLine(QPointF(x0, y0), QPointF(x1, y1))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(COLOR_SUCCESS)
        painter.drawEllipse(rect)
        text = str(self._value)
        font = QFont(self.font())
        digit_count = max(len(text), 1)
        font.setPointSizeF(max(5.0, self._size * min(0.42, 0.64 / digit_count)))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
```

</details>

### ⚙️ Method `set_value`

```python
def set_value(self, value: int | None) -> None
```

Set stored process-habit value (``None`` = no database record).

<details>
<summary>Code:</summary>

```python
def set_value(self, value: int | None) -> None:
        self._value = value
        self._apply_tooltip()
        self.update()
```

</details>

### ⚙️ Method `value`

```python
def value(self) -> int | None
```

Return stored process-habit value, or ``None`` if there is no record.

<details>
<summary>Code:</summary>

```python
def value(self) -> int | None:
        return self._value
```

</details>

## 🏛️ Class `HabitIconBadge`

```python
class HabitIconBadge(QWidget)
```

Circular colored badge with a glyph for a habit.

<details>
<summary>Code:</summary>

```python
class HabitIconBadge(QWidget):

    def __init__(self, parent: QWidget | None = None, *, size: int = 40) -> None:  # noqa: D107
        super().__init__(parent)
        self._bg = HABIT_ICON_COLORS[0]
        self._glyph = "★"
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw colored circle and centered glyph."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg)
        painter.drawEllipse(0, 0, self.width(), self.height())

        painter.setPen(COLOR_TEXT)
        font = QFont(self.font())
        font.setPointSize(max(10, int(self._size * 0.35)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)

    def set_habit(self, habit_id: int, glyph: str | None = None) -> None:
        """Style badge from habit ID and optional stored emoji/glyph."""
        self._bg = habit_accent_color(habit_id)
        self._glyph = glyph or habit_glyph(habit_id)
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 40) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 40) -> None:  # noqa: D107
        super().__init__(parent)
        self._bg = HABIT_ICON_COLORS[0]
        self._glyph = "★"
        self._size = size
        self.setFixedSize(size, size)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Draw colored circle and centered glyph.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg)
        painter.drawEllipse(0, 0, self.width(), self.height())

        painter.setPen(COLOR_TEXT)
        font = QFont(self.font())
        font.setPointSize(max(10, int(self._size * 0.35)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)
```

</details>

### ⚙️ Method `set_habit`

```python
def set_habit(self, habit_id: int, glyph: str | None = None) -> None
```

Style badge from habit ID and optional stored emoji/glyph.

<details>
<summary>Code:</summary>

```python
def set_habit(self, habit_id: int, glyph: str | None = None) -> None:
        self._bg = habit_accent_color(habit_id)
        self._glyph = glyph or habit_glyph(habit_id)
        self.update()
```

</details>

## 🏛️ Class `HabitRow`

```python
class HabitRow(QFrame)
```

Selectable habit list row with week check circles.

<details>
<summary>Code:</summary>

```python
class HabitRow(QFrame):

    selected = Signal(int)
    day_toggled = Signal(int, int)  # habit_id, day_index 0..6

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._habit_id = -1
        self._selected = False
        self.setObjectName("habitRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(64)
        self._apply_style()

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(12)

        self._icon = HabitIconBadge(size=40)
        root.addWidget(self._icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        text_col.addWidget(self._name_label)
        text_col.addWidget(self._meta_label)
        root.addLayout(text_col, 1)

        self._checks_layout = QHBoxLayout()
        self._checks_layout.setSpacing(6)
        self._checks: list[CheckCircle] = []
        for day_index in range(7):
            circle = CheckCircle(size=22)
            circle.clicked.connect(lambda idx=day_index: self._on_day_clicked(idx))
            self._checks.append(circle)
            self._checks_layout.addWidget(circle)
        root.addLayout(self._checks_layout)

    def habit_id(self) -> int:
        """Return bound habit ID."""
        return self._habit_id

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select this habit when clicking the row (not only circles)."""
        if event.button() == Qt.MouseButton.LeftButton and self._habit_id >= 0:
            self.selected.emit(self._habit_id)
        super().mousePressEvent(event)

    def set_habit_data(
        self,
        habit_id: int,
        name: str,
        total_days: int,
        streak_days: int,
        week_values: Sequence[int | None],
        *,
        selected: bool,
        emoji: str = "",
    ) -> None:
        """Populate row content."""
        self._habit_id = habit_id
        self._selected = selected
        self._icon.set_habit(habit_id, emoji or None)
        self._name_label.setText(name)
        self._meta_label.setText(f"⚡ {total_days} Days   🔥 {streak_days} Days")
        for i, circle in enumerate(self._checks):
            value = week_values[i] if i < len(week_values) else None
            circle.set_value(value)
        self._apply_style()

    def _apply_style(self) -> None:
        border = COLOR_PRIMARY.name() if self._selected else "transparent"
        bg = "#EFF6FF" if self._selected else "#FFFFFF"
        self.setStyleSheet(
            f"""
            QFrame#habitRow {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            """
        )

    def _on_day_clicked(self, day_index: int) -> None:
        if self._habit_id >= 0:
            self.day_toggled.emit(self._habit_id, day_index)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._habit_id = -1
        self._selected = False
        self.setObjectName("habitRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(64)
        self._apply_style()

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(12)

        self._icon = HabitIconBadge(size=40)
        root.addWidget(self._icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        text_col.addWidget(self._name_label)
        text_col.addWidget(self._meta_label)
        root.addLayout(text_col, 1)

        self._checks_layout = QHBoxLayout()
        self._checks_layout.setSpacing(6)
        self._checks: list[CheckCircle] = []
        for day_index in range(7):
            circle = CheckCircle(size=22)
            circle.clicked.connect(lambda idx=day_index: self._on_day_clicked(idx))
            self._checks.append(circle)
            self._checks_layout.addWidget(circle)
        root.addLayout(self._checks_layout)
```

</details>

### ⚙️ Method `habit_id`

```python
def habit_id(self) -> int
```

Return bound habit ID.

<details>
<summary>Code:</summary>

```python
def habit_id(self) -> int:
        return self._habit_id
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Select this habit when clicking the row (not only circles).

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._habit_id >= 0:
            self.selected.emit(self._habit_id)
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `set_habit_data`

```python
def set_habit_data(self, habit_id: int, name: str, total_days: int, streak_days: int, week_values: Sequence[int | None], *, selected: bool, emoji: str = '') -> None
```

Populate row content.

<details>
<summary>Code:</summary>

```python
def set_habit_data(
        self,
        habit_id: int,
        name: str,
        total_days: int,
        streak_days: int,
        week_values: Sequence[int | None],
        *,
        selected: bool,
        emoji: str = "",
    ) -> None:
        self._habit_id = habit_id
        self._selected = selected
        self._icon.set_habit(habit_id, emoji or None)
        self._name_label.setText(name)
        self._meta_label.setText(f"⚡ {total_days} Days   🔥 {streak_days} Days")
        for i, circle in enumerate(self._checks):
            value = week_values[i] if i < len(week_values) else None
            circle.set_value(value)
        self._apply_style()
```

</details>

## 🏛️ Class `MonthCalendarGrid`

```python
class MonthCalendarGrid(QWidget)
```

Month grid of check circles with weekday headers.

<details>
<summary>Code:</summary>

```python
class MonthCalendarGrid(QWidget):

    day_toggled = Signal(str)  # YYYY-MM-DD
    month_changed = Signal(int, int)  # year, month

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._year = 0
        self._month = 0
        self._day_values: dict[str, int] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QHBoxLayout()
        self._prev_btn = QPushButton("←")
        self._next_btn = QPushButton("→")
        for btn in (self._prev_btn, self._next_btn):
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    background: #F9FAFB;
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                    color: #374151;
                    font-size: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: #EFF6FF;
                    border-color: #93C5FD;
                    color: #1D4ED8;
                }
                """
            )
        self._prev_btn.setToolTip("Previous month")
        self._next_btn.setToolTip("Next month")
        self._title = QLabel("")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(self._title.font())
        title_font.setPointSize(12)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet("color: #111827;")
        header.addWidget(self._prev_btn)
        header.addWidget(self._title, 1)
        header.addWidget(self._next_btn)
        root.addLayout(header)

        self._prev_btn.clicked.connect(self._on_prev)
        self._next_btn.clicked.connect(self._on_next)

        weekdays = QHBoxLayout()
        for name in ("M", "T", "W", "T", "F", "S", "S"):
            lab = QLabel(name)
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_font = QFont(lab.font())
            weekday_font.setPointSize(9)
            weekday_font.setBold(True)
            lab.setFont(weekday_font)
            lab.setStyleSheet("color: #6B7280;")
            weekdays.addWidget(lab, 1)
        root.addLayout(weekdays)

        self._grid = QGridLayout()
        self._grid.setHorizontalSpacing(4)
        self._grid.setVerticalSpacing(6)
        for column in range(7):
            self._grid.setColumnStretch(column, 1)
        root.addLayout(self._grid)
        self._day_cells: list[tuple[CheckCircle | None, QLabel, str | None]] = []

    def set_month(self, year: int, month: int, day_values: dict[str, int] | None = None) -> None:
        """Rebuild grid for year/month with stored values keyed by ``YYYY-MM-DD``."""
        self._year = year
        self._month = month
        self._day_values = dict(day_values or {})
        self._title.setText(f"{_month_short(month)} {year}")
        self._rebuild_grid()

    def _clear_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._day_cells.clear()

    def _on_next(self) -> None:
        year, month = self._year, self._month + 1
        if month > MONTHS_IN_YEAR:
            month = 1
            year += 1
        self.month_changed.emit(year, month)

    def _on_prev(self) -> None:
        year, month = self._year, self._month - 1
        if month < 1:
            month = MONTHS_IN_YEAR
            year -= 1
        self.month_changed.emit(year, month)

    def _rebuild_grid(self) -> None:
        self._clear_grid()

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        weeks = cal.monthdayscalendar(self._year, self._month)
        for row_index, week in enumerate(weeks):
            self._grid.setRowStretch(row_index, 1)
            for column_index, day in enumerate(week):
                cell = QWidget()
                cell.setMinimumHeight(48)
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(2)
                cell_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                if day == 0:
                    self._grid.addWidget(cell, row_index, column_index)
                    continue

                date_str = f"{self._year:04d}-{self._month:02d}-{day:02d}"
                circle = CheckCircle(size=26)
                circle.set_value(self._day_values.get(date_str))
                circle.clicked.connect(lambda d=date_str: self.day_toggled.emit(d))
                day_label = QLabel(str(day))
                day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                day_label.setFixedHeight(18)
                day_font = QFont(day_label.font())
                day_font.setPointSize(10)
                day_font.setWeight(QFont.Weight.DemiBold)
                day_label.setFont(day_font)
                day_label.setStyleSheet("color: #4B5563;")
                cell_layout.addWidget(circle, 0, Qt.AlignmentFlag.AlignHCenter)
                cell_layout.addWidget(day_label)
                self._grid.addWidget(cell, row_index, column_index)
                self._day_cells.append((circle, day_label, date_str))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._year = 0
        self._month = 0
        self._day_values: dict[str, int] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QHBoxLayout()
        self._prev_btn = QPushButton("←")
        self._next_btn = QPushButton("→")
        for btn in (self._prev_btn, self._next_btn):
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    background: #F9FAFB;
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                    color: #374151;
                    font-size: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: #EFF6FF;
                    border-color: #93C5FD;
                    color: #1D4ED8;
                }
                """
            )
        self._prev_btn.setToolTip("Previous month")
        self._next_btn.setToolTip("Next month")
        self._title = QLabel("")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(self._title.font())
        title_font.setPointSize(12)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet("color: #111827;")
        header.addWidget(self._prev_btn)
        header.addWidget(self._title, 1)
        header.addWidget(self._next_btn)
        root.addLayout(header)

        self._prev_btn.clicked.connect(self._on_prev)
        self._next_btn.clicked.connect(self._on_next)

        weekdays = QHBoxLayout()
        for name in ("M", "T", "W", "T", "F", "S", "S"):
            lab = QLabel(name)
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_font = QFont(lab.font())
            weekday_font.setPointSize(9)
            weekday_font.setBold(True)
            lab.setFont(weekday_font)
            lab.setStyleSheet("color: #6B7280;")
            weekdays.addWidget(lab, 1)
        root.addLayout(weekdays)

        self._grid = QGridLayout()
        self._grid.setHorizontalSpacing(4)
        self._grid.setVerticalSpacing(6)
        for column in range(7):
            self._grid.setColumnStretch(column, 1)
        root.addLayout(self._grid)
        self._day_cells: list[tuple[CheckCircle | None, QLabel, str | None]] = []
```

</details>

### ⚙️ Method `set_month`

```python
def set_month(self, year: int, month: int, day_values: dict[str, int] | None = None) -> None
```

Rebuild grid for year/month with stored values keyed by ``YYYY-MM-DD``.

<details>
<summary>Code:</summary>

```python
def set_month(self, year: int, month: int, day_values: dict[str, int] | None = None) -> None:
        self._year = year
        self._month = month
        self._day_values = dict(day_values or {})
        self._title.setText(f"{_month_short(month)} {year}")
        self._rebuild_grid()
```

</details>

## 🏛️ Class `ProgressRing`

```python
class ProgressRing(QWidget)
```

Circular progress ring showing a 0.0-1.0 completion ratio.

<details>
<summary>Code:</summary>

```python
class ProgressRing(QWidget):

    def __init__(self, parent: QWidget | None = None, *, size: int = 36) -> None:  # noqa: D107
        super().__init__(parent)
        self._ratio = 0.0
        self._ring_size = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw track ring and progress arc."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen_width = max(3.0, self._ring_size * 0.12)
        margin = pen_width / 2 + 1
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)

        track_pen = QPen(COLOR_TRACK, pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        if self._ratio <= 0:
            return

        progress_pen = QPen(COLOR_PRIMARY, pen_width)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        # Qt arcs: 0° at 3 o'clock, counter-clockwise; start at 12 o'clock
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * self._ratio)
        painter.drawArc(rect, start_angle, span_angle)

    def set_ratio(self, ratio: float) -> None:
        """Update completion ratio in ``[0, 1]`` and repaint."""
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 36) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, size: int = 36) -> None:  # noqa: D107
        super().__init__(parent)
        self._ratio = 0.0
        self._ring_size = size
        self.setFixedSize(size, size)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Draw track ring and progress arc.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen_width = max(3.0, self._ring_size * 0.12)
        margin = pen_width / 2 + 1
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)

        track_pen = QPen(COLOR_TRACK, pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        if self._ratio <= 0:
            return

        progress_pen = QPen(COLOR_PRIMARY, pen_width)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        # Qt arcs: 0° at 3 o'clock, counter-clockwise; start at 12 o'clock
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * self._ratio)
        painter.drawArc(rect, start_angle, span_angle)
```

</details>

### ⚙️ Method `set_ratio`

```python
def set_ratio(self, ratio: float) -> None
```

Update completion ratio in ``[0, 1]`` and repaint.

<details>
<summary>Code:</summary>

```python
def set_ratio(self, ratio: float) -> None:
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()
```

</details>

## 🏛️ Class `StatCard`

```python
class StatCard(QFrame)
```

Small metric card: icon, label, value.

<details>
<summary>Code:</summary>

```python
class StatCard(QFrame):

    def __init__(  # noqa: D107
        self,
        title: str,
        icon_text: str,
        icon_color: QColor,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("habitStatCard")
        self.setStyleSheet(
            """
            QFrame#habitStatCard {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(6)
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"color: {icon_color.name()}; font-size: 14px; font-weight: 700;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        title_label.setWordWrap(True)
        top.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)
        top.addWidget(title_label, 1)
        layout.addLayout(top)

        self._value_label = QLabel("-")
        self._value_label.setStyleSheet("color: #111827; font-size: 18px; font-weight: 700;")
        layout.addWidget(self._value_label)

    def set_value(self, text: str) -> None:
        """Update the large value text."""
        self._value_label.setText(text)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, icon_text: str, icon_color: QColor, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(  # noqa: D107
        self,
        title: str,
        icon_text: str,
        icon_color: QColor,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("habitStatCard")
        self.setStyleSheet(
            """
            QFrame#habitStatCard {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(6)
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"color: {icon_color.name()}; font-size: 14px; font-weight: 700;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        title_label.setWordWrap(True)
        top.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)
        top.addWidget(title_label, 1)
        layout.addLayout(top)

        self._value_label = QLabel("-")
        self._value_label.setStyleSheet("color: #111827; font-size: 18px; font-weight: 700;")
        layout.addWidget(self._value_label)
```

</details>

### ⚙️ Method `set_value`

```python
def set_value(self, text: str) -> None
```

Update the large value text.

<details>
<summary>Code:</summary>

```python
def set_value(self, text: str) -> None:
        self._value_label.setText(text)
```

</details>

## 🏛️ Class `WeekDayHeader`

```python
class WeekDayHeader(QWidget)
```

One day column in the week progress bar: label + progress ring.

<details>
<summary>Code:</summary>

```python
class WeekDayHeader(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._label = QLabel("-")
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._label.setStyleSheet("color: #6B7280; font-size: 11px;")
        self._ring = ProgressRing(size=34)
        layout.addWidget(self._label)
        layout.addWidget(self._ring, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_day(self, caption: str, ratio: float, *, is_today: bool) -> None:
        """Update caption, ring, and today highlight."""
        self._label.setText(caption)
        self._ring.set_ratio(ratio)
        if is_today:
            self._label.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 700;")
        else:
            self._label.setStyleSheet("color: #6B7280; font-size: 11px;")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._label = QLabel("-")
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._label.setStyleSheet("color: #6B7280; font-size: 11px;")
        self._ring = ProgressRing(size=34)
        layout.addWidget(self._label)
        layout.addWidget(self._ring, 0, Qt.AlignmentFlag.AlignHCenter)
```

</details>

### ⚙️ Method `set_day`

```python
def set_day(self, caption: str, ratio: float, *, is_today: bool) -> None
```

Update caption, ring, and today highlight.

<details>
<summary>Code:</summary>

```python
def set_day(self, caption: str, ratio: float, *, is_today: bool) -> None:
        self._label.setText(caption)
        self._ring.set_ratio(ratio)
        if is_today:
            self._label.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 700;")
        else:
            self._label.setStyleSheet("color: #6B7280; font-size: 11px;")
```

</details>

## 🔧 Function `habit_accent_color`

```python
def habit_accent_color(habit_id: int) -> QColor
```

Return a soft background color for a habit icon.

<details>
<summary>Code:</summary>

```python
def habit_accent_color(habit_id: int) -> QColor:
    return HABIT_ICON_COLORS[habit_id % len(HABIT_ICON_COLORS)]
```

</details>

## 🔧 Function `habit_day_state`

```python
def habit_day_state(value: int | None) -> HabitDayState
```

Map a stored process-habit value to a dashboard day state.

<details>
<summary>Code:</summary>

```python
def habit_day_state(value: int | None) -> HabitDayState:
    if value is None:
        return "absent"
    if value == 0:
        return "zero"
    if value == 1:
        return "one"
    return "number"
```

</details>

## 🔧 Function `habit_glyph`

```python
def habit_glyph(habit_id: int) -> str
```

Return a simple glyph for a habit icon.

<details>
<summary>Code:</summary>

```python
def habit_glyph(habit_id: int) -> str:
    return default_habit_emoji(habit_id)
```

</details>

## 🔧 Function `weekday_short`

```python
def weekday_short(weekday: int) -> str
```

Return short weekday name for ``date.weekday()`` (Mon=0).

<details>
<summary>Code:</summary>

```python
def weekday_short(weekday: int) -> str:
    names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    return names[weekday % 7]
```

</details>
