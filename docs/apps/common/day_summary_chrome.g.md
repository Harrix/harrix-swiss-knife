---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_summary_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_day_summary_caption`](#-function-apply_day_summary_caption)
- [🔧 Function `apply_day_summary_value`](#-function-apply_day_summary_value)
- [🔧 Function `apply_food_day_summary_label`](#-function-apply_food_day_summary_label)
- [🔧 Function `format_food_day_summary_html`](#-function-format_food_day_summary_html)

</details>

## 🔧 Function `apply_day_summary_caption`

```python
def apply_day_summary_caption(label: QLabel) -> None
```

Style a period caption (Today / Yesterday) smaller than the value.

<details>
<summary>Code:</summary>

```python
def apply_day_summary_caption(label: QLabel) -> None:
    label.setFont(fluent_font(_summary_base_font(label), _CAPTION_SCALE))
    label.setStyleSheet(muted_caption_qss())
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
```

</details>

## 🔧 Function `apply_day_summary_value`

```python
def apply_day_summary_value(label: QLabel, *, today: bool = True) -> None
```

Style a numeric day-summary value; today is the primary emphasis.

<details>
<summary>Code:</summary>

```python
def apply_day_summary_value(label: QLabel, *, today: bool = True) -> None:
    scale = _TODAY_VALUE_SCALE if today else _YESTERDAY_VALUE_SCALE
    label.setFont(fluent_font(_summary_base_font(label), scale, weight=QFont.Weight.DemiBold))
    palette = palette_for(label)
    color = css(mix(palette.window_bg, palette.text_primary))
    label.setStyleSheet(f"color: {color}; border: none; background: transparent;")
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    metrics = label.fontMetrics()
    label.setMinimumHeight(max(label.minimumHeight(), metrics.height() + SPACE_XS))
```

</details>

## 🔧 Function `apply_food_day_summary_label`

```python
def apply_food_day_summary_label(label: QLabel, calories: float, drinks_weight: int, *, today: bool) -> None
```

Paint kcal (primary) and drink volume (secondary) with units bound to values.

<details>
<summary>Code:</summary>

```python
def apply_food_day_summary_label(
    label: QLabel,
    calories: float,
    drinks_weight: int,
    *,
    today: bool,
) -> None:
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    # Font/min-height from the value role; HTML colors and sizes carry the hierarchy.
    apply_day_summary_value(label, today=today)
    label.setText(format_food_day_summary_html(label, calories, drinks_weight, today=today))
```

</details>

## 🔧 Function `format_food_day_summary_html`

```python
def format_food_day_summary_html(widget: QWidget, calories: float, drinks_weight: int, *, today: bool) -> str
```

Return rich text: large kcal line, then drinks; nbsp keeps units with numbers.

<details>
<summary>Code:</summary>

```python
def format_food_day_summary_html(
    widget: QWidget,
    calories: float,
    drinks_weight: int,
    *,
    today: bool,
) -> str:
    drinks_liters = drinks_weight / 1000 if drinks_weight else 0.0
    base = _summary_base_font(widget)
    kcal_font = fluent_font(
        base,
        _TODAY_VALUE_SCALE if today else _YESTERDAY_VALUE_SCALE,
        weight=QFont.Weight.DemiBold,
    )
    drink_font = fluent_font(
        base,
        _TODAY_SECONDARY_SCALE if today else _YESTERDAY_SECONDARY_SCALE,
        weight=QFont.Weight.DemiBold,
    )
    palette = palette_for(widget)
    primary = css(mix(palette.window_bg, palette.text_primary))
    # Secondary line stays readable (not disabled); slightly quieter than kcal.
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    kcal_text = f"{calories:.1f}&nbsp;kcal"
    drink_text = f"{drinks_liters:.1f}&nbsp;L"
    return (
        f'<div style="color:{primary}; font-size:{_font_size_css(kcal_font)}; '
        f'font-weight:600;">{kcal_text}</div>'
        f'<div style="color:{secondary}; font-size:{_font_size_css(drink_font)}; '
        f'font-weight:600; margin-top:2px;">{drink_text}</div>'
    )
```

</details>
