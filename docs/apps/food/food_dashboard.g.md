---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_dashboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodDashboardWidget`](#%EF%B8%8F-class-fooddashboardwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_today_calories`](#%EF%B8%8F-method-set_today_calories)
- [🔧 Function `format_today_calories`](#-function-format_today_calories)

</details>

## 🏛️ Class `FoodDashboardWidget`

```python
class FoodDashboardWidget(QWidget)
```

Habits-style call-to-action card for adding food and showing today's calories.

<details>
<summary>Code:</summary>

```python
class FoodDashboardWidget(QWidget):

    add_photo_requested = Signal()
    add_voice_requested = Signal()
    add_text_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FoodDashboardWidget { background: #FFFFFF; }")
        self._build_ui()

    def set_today_calories(self, kcal: float) -> None:
        """Update the large calorie figure shown under the action buttons.

        Args:

        - `kcal` (`float`): Calories consumed today.

        """
        self._calories_value.setText(format_today_calories(kcal))

    def _build_action_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(280, 64)
        return button

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        pane = QFrame()
        pane.setObjectName("foodDashEmptyState")
        pane.setStyleSheet(
            """
            QFrame#foodDashEmptyState {
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
            """
        )
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(16)

        title = QLabel("Add food")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #111827; font-size: 28px; font-weight: 800;")

        subtitle = QLabel("Log a meal with a photo, voice, or text.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6B7280; font-size: 16px;")

        photo_button = self._build_action_button("📷 Add photo", "foodDashAddPhotoButton")
        voice_button = self._build_action_button("🎙️ Speak", "foodDashAddVoiceButton")
        text_button = self._build_action_button("📝 Write text", "foodDashAddTextButton")
        photo_button.clicked.connect(self.add_photo_requested.emit)
        voice_button.clicked.connect(self.add_voice_requested.emit)
        text_button.clicked.connect(self.add_text_requested.emit)

        self._calories_value = QLabel("0")
        self._calories_value.setObjectName("foodDashCaloriesValue")
        self._calories_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._calories_value.setStyleSheet("color: #111827; font-size: 64px; font-weight: 800;")

        calories_hint = QLabel("kcal today")
        calories_hint.setObjectName("foodDashCaloriesHint")
        calories_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calories_hint.setStyleSheet("color: #6B7280; font-size: 20px; font-weight: 600;")

        buttons = QWidget()
        buttons.setStyleSheet(_DASH_BUTTON_STYLE)
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)
        buttons_layout.setSpacing(12)
        buttons_layout.addWidget(photo_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(voice_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(text_button, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(16)
        layout.addWidget(self._calories_value)
        layout.addWidget(calories_hint)
        layout.addStretch(1)

        outer.addWidget(pane)
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
        self.setAutoFillBackground(True)
        self.setStyleSheet("FoodDashboardWidget { background: #FFFFFF; }")
        self._build_ui()
```

</details>

### ⚙️ Method `set_today_calories`

```python
def set_today_calories(self, kcal: float) -> None
```

Update the large calorie figure shown under the action buttons.

Args:

- `kcal` (`float`): Calories consumed today.

<details>
<summary>Code:</summary>

```python
def set_today_calories(self, kcal: float) -> None:
        self._calories_value.setText(format_today_calories(kcal))
```

</details>

## 🔧 Function `format_today_calories`

```python
def format_today_calories(kcal: float) -> str
```

Format today's calories for the large dashboard number.

Args:

- `kcal` (`float`): Calories consumed today.

Returns:

- `str`: Compact calorie text without a unit suffix.

<details>
<summary>Code:</summary>

```python
def format_today_calories(kcal: float) -> str:
    return str(int(round(kcal)))
```

</details>
