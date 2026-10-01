---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_lucide_checkbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LucideCheckboxStyle`](#%EF%B8%8F-class-lucidecheckboxstyle)
  - [⚙️ Method `drawPrimitive`](#%EF%B8%8F-method-drawprimitive)
  - [⚙️ Method `pixelMetric`](#%EF%B8%8F-method-pixelmetric)
- [🔧 Function `apply_lucide_checkbox_style`](#-function-apply_lucide_checkbox_style)
- [🔧 Function `apply_lucide_checkboxes`](#-function-apply_lucide_checkboxes)
- [🔧 Function `lucide_checkbox_pixmap`](#-function-lucide_checkbox_pixmap)
- [🔧 Function `lucide_checkbox_widget_style`](#-function-lucide_checkbox_widget_style)
- [🔧 Function `paint_lucide_checkbox`](#-function-paint_lucide_checkbox)
- [🔧 Function `paint_lucide_checkbox_from_style_option`](#-function-paint_lucide_checkbox_from_style_option)

</details>

## 🏛️ Class `LucideCheckboxStyle`

```python
class LucideCheckboxStyle(QProxyStyle)
```

Draw Lucide glyphs for checkbox indicators; leave every other primitive alone.

<details>
<summary>Code:</summary>

```python
class LucideCheckboxStyle(QProxyStyle):

    def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Paint Lucide for check indicators; otherwise delegate to the base style."""
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option)
            return
        super().drawPrimitive(element, option, painter, widget)

    def pixelMetric(  # noqa: N802
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        """Reserve a fixed box for check indicators so item views keep layout space."""
        if metric in (
            QStyle.PixelMetric.PM_IndicatorWidth,
            QStyle.PixelMetric.PM_IndicatorHeight,
        ):
            return CHECKBOX_INDICATOR_PX
        return super().pixelMetric(metric, option, widget)
```

</details>

### ⚙️ Method `drawPrimitive`

```python
def drawPrimitive(self, element: QStyle.PrimitiveElement, option: QStyleOption, painter: QPainter, widget: QWidget | None = None) -> None
```

Paint Lucide for check indicators; otherwise delegate to the base style.

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
        super().drawPrimitive(element, option, painter, widget)
```

</details>

### ⚙️ Method `pixelMetric`

```python
def pixelMetric(self, metric: QStyle.PixelMetric, option: QStyleOption | None = None, widget: QWidget | None = None) -> int
```

Reserve a fixed box for check indicators so item views keep layout space.

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
        return super().pixelMetric(metric, option, widget)
```

</details>

## 🔧 Function `apply_lucide_checkbox_style`

```python
def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None
```

Apply the shared Lucide checkbox style to one `QCheckBox`.

<details>
<summary>Code:</summary>

```python
def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None:
    style = lucide_checkbox_widget_style()
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
def lucide_checkbox_widget_style() -> LucideCheckboxStyle
```

Return the shared Lucide checkbox style (lazy, process-wide).

<details>
<summary>Code:</summary>

```python
def lucide_checkbox_widget_style() -> LucideCheckboxStyle:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        held = app.property(_STYLE_PROP)
        if isinstance(held, LucideCheckboxStyle):
            return held
    base = QStyleFactory.create("Fusion")
    style = LucideCheckboxStyle(base)
    if isinstance(app, QApplication):
        app.setProperty(_STYLE_PROP, style)
    return style
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
    if pixmap.isNull():
        return
    target = QRect(
        rect.x() + (rect.width() - size) // 2,
        rect.y() + (rect.height() - size) // 2,
        size,
        size,
    )
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.drawPixmap(target, pixmap)
    painter.restore()
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
