---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_lucide_checkbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LucideToggleStyle`](#%EF%B8%8F-class-lucidetogglestyle)
  - [⚙️ Method `drawPrimitive`](#%EF%B8%8F-method-drawprimitive)
  - [⚙️ Method `pixelMetric`](#%EF%B8%8F-method-pixelmetric)
- [🔧 Function `apply_lucide_checkbox_style`](#-function-apply_lucide_checkbox_style)
- [🔧 Function `apply_lucide_checkboxes`](#-function-apply_lucide_checkboxes)
- [🔧 Function `apply_lucide_indicators`](#-function-apply_lucide_indicators)
- [🔧 Function `apply_lucide_radio_style`](#-function-apply_lucide_radio_style)
- [🔧 Function `apply_lucide_radios`](#-function-apply_lucide_radios)
- [🔧 Function `lucide_checkbox_pixmap`](#-function-lucide_checkbox_pixmap)
- [🔧 Function `lucide_checkbox_widget_style`](#-function-lucide_checkbox_widget_style)
- [🔧 Function `lucide_radio_pixmap`](#-function-lucide_radio_pixmap)
- [🔧 Function `lucide_toggle_widget_style`](#-function-lucide_toggle_widget_style)
- [🔧 Function `paint_lucide_checkbox`](#-function-paint_lucide_checkbox)
- [🔧 Function `paint_lucide_checkbox_from_style_option`](#-function-paint_lucide_checkbox_from_style_option)
- [🔧 Function `paint_lucide_radio`](#-function-paint_lucide_radio)
- [🔧 Function `paint_lucide_radio_from_style_option`](#-function-paint_lucide_radio_from_style_option)

</details>

## 🏛️ Class `LucideToggleStyle`

```python
class LucideToggleStyle(QProxyStyle)
```

Draw Lucide glyphs for checkbox/radio indicators; leave other primitives alone.

<details>
<summary>Code:</summary>

```python
class LucideToggleStyle(QProxyStyle):

    def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Paint Lucide for check/radio indicators; otherwise delegate to the base style."""
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option)
            return
        if element == QStyle.PrimitiveElement.PE_IndicatorRadioButton:
            paint_lucide_radio_from_style_option(painter, option)
            return
        super().drawPrimitive(element, option, painter, widget)

    def pixelMetric(  # noqa: N802
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        """Reserve a fixed box for check and radio indicators."""
        if metric in (
            QStyle.PixelMetric.PM_IndicatorWidth,
            QStyle.PixelMetric.PM_IndicatorHeight,
        ):
            return CHECKBOX_INDICATOR_PX
        if metric in (
            QStyle.PixelMetric.PM_ExclusiveIndicatorWidth,
            QStyle.PixelMetric.PM_ExclusiveIndicatorHeight,
        ):
            return RADIO_INDICATOR_PX
        return super().pixelMetric(metric, option, widget)
```

</details>

### ⚙️ Method `drawPrimitive`

```python
def drawPrimitive(self, element: QStyle.PrimitiveElement, option: QStyleOption, painter: QPainter, widget: QWidget | None = None) -> None
```

Paint Lucide for check/radio indicators; otherwise delegate to the base style.

<details>
<summary>Code:</summary>

```python
def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option)
            return
        if element == QStyle.PrimitiveElement.PE_IndicatorRadioButton:
            paint_lucide_radio_from_style_option(painter, option)
            return
        super().drawPrimitive(element, option, painter, widget)
```

</details>

### ⚙️ Method `pixelMetric`

```python
def pixelMetric(self, metric: QStyle.PixelMetric, option: QStyleOption | None = None, widget: QWidget | None = None) -> int
```

Reserve a fixed box for check and radio indicators.

<details>
<summary>Code:</summary>

```python
def pixelMetric(  # noqa: N802
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        if metric in (
            QStyle.PixelMetric.PM_IndicatorWidth,
            QStyle.PixelMetric.PM_IndicatorHeight,
        ):
            return CHECKBOX_INDICATOR_PX
        if metric in (
            QStyle.PixelMetric.PM_ExclusiveIndicatorWidth,
            QStyle.PixelMetric.PM_ExclusiveIndicatorHeight,
        ):
            return RADIO_INDICATOR_PX
        return super().pixelMetric(metric, option, widget)
```

</details>

## 🔧 Function `apply_lucide_checkbox_style`

```python
def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None
```

Apply the shared Lucide toggle style to one `QCheckBox`.

<details>
<summary>Code:</summary>

```python
def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None:
    style = lucide_toggle_widget_style()
    if checkbox.style() is style:
        return
    checkbox.setStyle(style)
```

</details>

## 🔧 Function `apply_lucide_checkboxes`

```python
def apply_lucide_checkboxes(root: QWidget) -> None
```

Apply Lucide checkbox style to every `QCheckBox` under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_lucide_checkboxes(root: QWidget) -> None:
    if isinstance(root, QCheckBox):
        apply_lucide_checkbox_style(root)
    for checkbox in root.findChildren(QCheckBox):
        apply_lucide_checkbox_style(checkbox)
```

</details>

## 🔧 Function `apply_lucide_indicators`

```python
def apply_lucide_indicators(root: QWidget) -> None
```

Apply Lucide styles to checkboxes and radio buttons under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_lucide_indicators(root: QWidget) -> None:
    apply_lucide_checkboxes(root)
    apply_lucide_radios(root)
```

</details>

## 🔧 Function `apply_lucide_radio_style`

```python
def apply_lucide_radio_style(radio: QRadioButton) -> None
```

Apply the shared Lucide toggle style to one `QRadioButton`.

<details>
<summary>Code:</summary>

```python
def apply_lucide_radio_style(radio: QRadioButton) -> None:
    style = lucide_toggle_widget_style()
    if radio.style() is style:
        return
    radio.setStyle(style)
```

</details>

## 🔧 Function `apply_lucide_radios`

```python
def apply_lucide_radios(root: QWidget) -> None
```

Apply Lucide radio style to every `QRadioButton` under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_lucide_radios(root: QWidget) -> None:
    if isinstance(root, QRadioButton):
        apply_lucide_radio_style(root)
    for radio in root.findChildren(QRadioButton):
        apply_lucide_radio_style(radio)
```

</details>

## 🔧 Function `lucide_checkbox_pixmap`

```python
def lucide_checkbox_pixmap(*, checked: bool = False, partial: bool = False, enabled: bool = True, size: int = CHECKBOX_INDICATOR_PX) -> QPixmap
```

Return a Lucide checkbox pixmap for the given check state.

<details>
<summary>Code:</summary>

```python
def lucide_checkbox_pixmap(
    *,
    checked: bool = False,
    partial: bool = False,
    enabled: bool = True,
    size: int = CHECKBOX_INDICATOR_PX,
) -> QPixmap:
    if partial:
        name = "square-minus"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    elif checked:
        name = "square-check"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_GREEN
    else:
        name = "square"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    return create_lucide_icon(name, size, color=color).pixmap(size, size)
```

</details>

## 🔧 Function `lucide_checkbox_widget_style`

```python
def lucide_checkbox_widget_style() -> LucideToggleStyle
```

Return the shared Lucide toggle style (lazy, process-wide).

<details>
<summary>Code:</summary>

```python
def lucide_checkbox_widget_style() -> LucideToggleStyle:
    return lucide_toggle_widget_style()
```

</details>

## 🔧 Function `lucide_radio_pixmap`

```python
def lucide_radio_pixmap(*, checked: bool = False, enabled: bool = True, size: int = RADIO_INDICATOR_PX) -> QPixmap
```

Return a Lucide radio pixmap for the given check state.

<details>
<summary>Code:</summary>

```python
def lucide_radio_pixmap(
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
) -> QPixmap:
    if checked:
        name = "circle-dot"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_GREEN
    else:
        name = "circle"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    return create_lucide_icon(name, size, color=color).pixmap(size, size)
```

</details>

## 🔧 Function `lucide_toggle_widget_style`

```python
def lucide_toggle_widget_style() -> LucideToggleStyle
```

Return the shared Lucide checkbox/radio style (lazy, process-wide).

<details>
<summary>Code:</summary>

```python
def lucide_toggle_widget_style() -> LucideToggleStyle:
    if _SharedToggleStyle.instance is None:
        base = QStyleFactory.create("Fusion")
        if base is None:
            base = QStyleFactory.create("Windows")
        _SharedToggleStyle.instance = LucideToggleStyle(base)
    return _SharedToggleStyle.instance
```

</details>

## 🔧 Function `paint_lucide_checkbox`

```python
def paint_lucide_checkbox(painter: QPainter, rect: QRect, *, checked: bool = False, partial: bool = False, enabled: bool = True, size: int = CHECKBOX_INDICATOR_PX) -> None
```

Center a Lucide checkbox pixmap inside `rect`.

<details>
<summary>Code:</summary>

```python
def paint_lucide_checkbox(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool = False,
    partial: bool = False,
    enabled: bool = True,
    size: int = CHECKBOX_INDICATOR_PX,
) -> None:
    pixmap = lucide_checkbox_pixmap(checked=checked, partial=partial, enabled=enabled, size=size)
    _paint_centered_pixmap(painter, rect, pixmap, size)
```

</details>

## 🔧 Function `paint_lucide_checkbox_from_style_option`

```python
def paint_lucide_checkbox_from_style_option(painter: QPainter, option: QStyleOption) -> None
```

Paint a Lucide checkbox using `option.state` and `option.rect`.

<details>
<summary>Code:</summary>

```python
def paint_lucide_checkbox_from_style_option(painter: QPainter, option: QStyleOption) -> None:
    state = option.state
    partial = bool(state & QStyle.StateFlag.State_NoChange)
    checked = bool(state & QStyle.StateFlag.State_On) and not partial
    enabled = bool(state & QStyle.StateFlag.State_Enabled)
    paint_lucide_checkbox(
        painter,
        option.rect,
        checked=checked,
        partial=partial,
        enabled=enabled,
    )
```

</details>

## 🔧 Function `paint_lucide_radio`

```python
def paint_lucide_radio(painter: QPainter, rect: QRect, *, checked: bool = False, enabled: bool = True, size: int = RADIO_INDICATOR_PX) -> None
```

Center a Lucide radio pixmap inside `rect`.

<details>
<summary>Code:</summary>

```python
def paint_lucide_radio(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
) -> None:
    pixmap = lucide_radio_pixmap(checked=checked, enabled=enabled, size=size)
    _paint_centered_pixmap(painter, rect, pixmap, size)
```

</details>

## 🔧 Function `paint_lucide_radio_from_style_option`

```python
def paint_lucide_radio_from_style_option(painter: QPainter, option: QStyleOption) -> None
```

Paint a Lucide radio using `option.state` and `option.rect`.

<details>
<summary>Code:</summary>

```python
def paint_lucide_radio_from_style_option(painter: QPainter, option: QStyleOption) -> None:
    state = option.state
    checked = bool(state & QStyle.StateFlag.State_On)
    enabled = bool(state & QStyle.StateFlag.State_Enabled)
    paint_lucide_radio(painter, option.rect, checked=checked, enabled=enabled)
```

</details>
