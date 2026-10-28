---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `theme.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentTheme`](#%EF%B8%8F-class-fluenttheme)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `instance (classmethod)`](#%EF%B8%8F-method-instance-classmethod)
  - [⚙️ Method `is_dark`](#%EF%B8%8F-method-is_dark)
  - [⚙️ Method `load_from_config`](#%EF%B8%8F-method-load_from_config)
  - [⚙️ Method `mode`](#%EF%B8%8F-method-mode)
  - [⚙️ Method `palette`](#%EF%B8%8F-method-palette)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
  - [⚙️ Method `toggle`](#%EF%B8%8F-method-toggle)
- [🏛️ Class `ThemeMode`](#%EF%B8%8F-class-thememode)
- [🔧 Function `bind_theme`](#-function-bind_theme)
- [🔧 Function `css`](#-function-css)
- [🔧 Function `enable_fluent_theme`](#-function-enable_fluent_theme)
- [🔧 Function `fluent_font`](#-function-fluent_font)
- [🔧 Function `is_fluent_themed`](#-function-is_fluent_themed)
- [🔧 Function `mix`](#-function-mix)
- [🔧 Function `palette_for`](#-function-palette_for)
- [🔧 Function `to_qpalette`](#-function-to_qpalette)

</details>

## 🏛️ Class `FluentTheme`

```python
class FluentTheme(QObject)
```

Singleton holding the current Fluent theme mode.

<details>
<summary>Code:</summary>

```python
class FluentTheme(QObject):

    changed = Signal(str)

    _instance: FluentTheme | None = None

    def __init__(self) -> None:
        """Start in light mode; call `load_from_config` to apply `ui_theme`."""
        super().__init__()
        self._mode = ThemeMode.LIGHT

    @classmethod
    def instance(cls) -> FluentTheme:
        """Return the shared theme object (created on first use)."""
        if cls._instance is None:
            cls._instance = FluentTheme()
        return cls._instance

    def is_dark(self) -> bool:
        """Return whether the dark palette is active."""
        return self._mode == ThemeMode.DARK

    def load_from_config(self, config: dict | None = None) -> ThemeMode:
        """Apply `ui_theme` from `config.json` (or the given dict) and return it."""
        # Lazy: widgets import this module from the installer, which has no `harrix_pylib`.
        from harrix_swiss_knife.config_model import get_ui_theme  # noqa: PLC0415

        mode = ThemeMode(get_ui_theme(config))
        self.set_mode(mode)
        return mode

    def mode(self) -> ThemeMode:
        """Return the current theme mode."""
        return self._mode

    def palette(self) -> FluentPalette:
        """Return the token set for the current mode."""
        return DARK_PALETTE if self.is_dark() else LIGHT_PALETTE

    def set_mode(self, mode: ThemeMode | str, *, persist: bool = False) -> None:
        """Switch the theme and notify every bound widget.

        Args:

        - `mode` (`ThemeMode | str`): `light` or `dark`.
        - `persist` (`bool`): Also write `ui_theme` to `config.json`. Defaults to `False`.

        """
        resolved = ThemeMode(mode)
        if persist:
            # Lazy for the same installer reason as `load_from_config`.
            from harrix_swiss_knife.config_model import set_ui_theme  # noqa: PLC0415

            set_ui_theme(theme=resolved.value)
        if resolved == self._mode:
            return
        self._mode = resolved
        self.changed.emit(resolved.value)

    def toggle(self, *, persist: bool = True) -> ThemeMode:
        """Flip between light and dark and return the new mode."""
        target = ThemeMode.LIGHT if self.is_dark() else ThemeMode.DARK
        self.set_mode(target, persist=persist)
        return target
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Start in light mode; call [`load_from_config`](#%EF%B8%8F-method-load_from_config) to apply `ui_theme`.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()
        self._mode = ThemeMode.LIGHT
```

</details>

### ⚙️ Method `instance (classmethod)`

```python
def instance(cls) -> FluentTheme
```

Return the shared theme object (created on first use).

<details>
<summary>Code:</summary>

```python
def instance(cls) -> FluentTheme:
        if cls._instance is None:
            cls._instance = FluentTheme()
        return cls._instance
```

</details>

### ⚙️ Method `is_dark`

```python
def is_dark(self) -> bool
```

Return whether the dark palette is active.

<details>
<summary>Code:</summary>

```python
def is_dark(self) -> bool:
        return self._mode == ThemeMode.DARK
```

</details>

### ⚙️ Method `load_from_config`

```python
def load_from_config(self, config: dict | None = None) -> ThemeMode
```

Apply `ui_theme` from `config.json` (or the given dict) and return it.

<details>
<summary>Code:</summary>

```python
def load_from_config(self, config: dict | None = None) -> ThemeMode:
        # Lazy: widgets import this module from the installer, which has no `harrix_pylib`.
        from harrix_swiss_knife.config_model import get_ui_theme  # noqa: PLC0415

        mode = ThemeMode(get_ui_theme(config))
        self.set_mode(mode)
        return mode
```

</details>

### ⚙️ Method `mode`

```python
def mode(self) -> ThemeMode
```

Return the current theme mode.

<details>
<summary>Code:</summary>

```python
def mode(self) -> ThemeMode:
        return self._mode
```

</details>

### ⚙️ Method `palette`

```python
def palette(self) -> FluentPalette
```

Return the token set for the current mode.

<details>
<summary>Code:</summary>

```python
def palette(self) -> FluentPalette:
        return DARK_PALETTE if self.is_dark() else LIGHT_PALETTE
```

</details>

### ⚙️ Method `set_mode`

```python
def set_mode(self, mode: ThemeMode | str, *, persist: bool = False) -> None
```

Switch the theme and notify every bound widget.

Args:

- `mode` (`ThemeMode | str`): `light` or `dark`.
- `persist` (`bool`): Also write `ui_theme` to `config.json`. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def set_mode(self, mode: ThemeMode | str, *, persist: bool = False) -> None:
        resolved = ThemeMode(mode)
        if persist:
            # Lazy for the same installer reason as `load_from_config`.
            from harrix_swiss_knife.config_model import set_ui_theme  # noqa: PLC0415

            set_ui_theme(theme=resolved.value)
        if resolved == self._mode:
            return
        self._mode = resolved
        self.changed.emit(resolved.value)
```

</details>

### ⚙️ Method `toggle`

```python
def toggle(self, *, persist: bool = True) -> ThemeMode
```

Flip between light and dark and return the new mode.

<details>
<summary>Code:</summary>

```python
def toggle(self, *, persist: bool = True) -> ThemeMode:
        target = ThemeMode.LIGHT if self.is_dark() else ThemeMode.DARK
        self.set_mode(target, persist=persist)
        return target
```

</details>

## 🏛️ Class `ThemeMode`

```python
class ThemeMode(StrEnum)
```

Supported Fluent theme modes.

<details>
<summary>Code:</summary>

```python
class ThemeMode(StrEnum):

    LIGHT = "light"
    DARK = "dark"
```

</details>

## 🔧 Function `bind_theme`

```python
def bind_theme(widget: QWidget, refresh: Callable[[], None]) -> None
```

Call `refresh` now and whenever `widget`'s resolved palette changes.

`refresh` should read colors through `palette_for(widget)`.
Multiple bindings on one widget are allowed (each keeps its own refresher).

<details>
<summary>Code:</summary>

```python
def bind_theme(widget: QWidget, refresh: Callable[[], None]) -> None:
    refresher = _ThemeRefresher(widget, refresh)
    refresher.run(force=True)
```

</details>

## 🔧 Function `css`

```python
def css(color: QColor) -> str
```

Return [`color`](widgets/dialogs.g.md#%EF%B8%8F-method-color) as a QSS `rgba(...)` value (keeps alpha).

<details>
<summary>Code:</summary>

```python
def css(color: QColor) -> str:
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
```

</details>

## 🔧 Function `enable_fluent_theme`

```python
def enable_fluent_theme(window: QWidget) -> None
```

Opt `window` (and everything under it) into the current light/dark mode.

<details>
<summary>Code:</summary>

```python
def enable_fluent_theme(window: QWidget) -> None:
    window.setProperty(FLUENT_THEMED_PROPERTY, True)  # noqa: FBT003
    bind_theme(window, lambda: _apply_window_palette(window))
```

</details>

## 🔧 Function `fluent_font`

```python
def fluent_font(source: QFont, scale: float, *, weight: QFont.Weight | None = None) -> QFont
```

Return `source` scaled along the Fluent type ramp.

Args:

- `source` (`QFont`): Base font (usually the application Roboto font).
- `scale` (`float`): One of the `TYPE_*` ratios from `fluent.tokens`.
- `weight` (`QFont.Weight | None`): Optional weight override.

<details>
<summary>Code:</summary>

```python
def fluent_font(source: QFont, scale: float, *, weight: QFont.Weight | None = None) -> QFont:
    font = QFont(source)
    if font.pointSizeF() > 0:
        font.setPointSizeF(max(1.0, font.pointSizeF() * scale))
    elif font.pixelSize() > 0:
        font.setPixelSize(max(1, round(font.pixelSize() * scale)))
    if weight is not None:
        font.setWeight(weight)
    return font
```

</details>

## 🔧 Function `is_fluent_themed`

```python
def is_fluent_themed(widget: QWidget | None) -> bool
```

Return whether `widget` lives under a window that opted into the theme.

<details>
<summary>Code:</summary>

```python
def is_fluent_themed(widget: QWidget | None) -> bool:
    current = widget
    while current is not None:
        if bool(current.property(FLUENT_THEMED_PROPERTY)):
            return True
        current = current.parentWidget()
    return False
```

</details>

## 🔧 Function `mix`

```python
def mix(base: QColor, overlay: QColor) -> QColor
```

Return the opaque color of `overlay` painted over opaque `base`.

<details>
<summary>Code:</summary>

```python
def mix(base: QColor, overlay: QColor) -> QColor:
    alpha = overlay.alphaF()
    return QColor(
        round(base.red() * (1 - alpha) + overlay.red() * alpha),
        round(base.green() * (1 - alpha) + overlay.green() * alpha),
        round(base.blue() * (1 - alpha) + overlay.blue() * alpha),
    )
```

</details>

## 🔧 Function `palette_for`

```python
def palette_for(widget: QWidget | None) -> FluentPalette
```

Return the palette `widget` should paint with (light outside opted-in Windows).

<details>
<summary>Code:</summary>

```python
def palette_for(widget: QWidget | None) -> FluentPalette:
    theme = FluentTheme.instance()
    if theme.is_dark() and is_fluent_themed(widget):
        return DARK_PALETTE
    return LIGHT_PALETTE
```

</details>

## 🔧 Function `to_qpalette`

```python
def to_qpalette(palette: FluentPalette, base: QPalette | None = None) -> QPalette
```

Build a `QPalette` with opaque Fluent colors for native-drawn children.

<details>
<summary>Code:</summary>

```python
def to_qpalette(palette: FluentPalette, base: QPalette | None = None) -> QPalette:
    result = QPalette(base) if base is not None else QPalette()
    window = palette.window_bg
    surface = mix(window, palette.layer_bg)
    text = mix(window, palette.text_primary)
    secondary = mix(window, palette.text_secondary)
    disabled = mix(window, palette.text_disabled)
    roles = {
        QPalette.ColorRole.Window: window,
        QPalette.ColorRole.WindowText: text,
        QPalette.ColorRole.Base: palette.solid_quarternary_bg if not palette.dark else palette.solid_tertiary_bg,
        QPalette.ColorRole.AlternateBase: surface,
        QPalette.ColorRole.Text: text,
        QPalette.ColorRole.Button: surface,
        QPalette.ColorRole.ButtonText: text,
        QPalette.ColorRole.BrightText: palette.text_on_accent,
        QPalette.ColorRole.Highlight: palette.accent,
        QPalette.ColorRole.HighlightedText: palette.text_on_accent,
        QPalette.ColorRole.ToolTipBase: palette.popup_bg,
        QPalette.ColorRole.ToolTipText: text,
        QPalette.ColorRole.PlaceholderText: secondary,
        QPalette.ColorRole.Link: palette.accent_text,
        QPalette.ColorRole.Mid: mix(window, palette.divider),
    }
    for role, color in roles.items():
        result.setColor(role, color)
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
        result.setColor(QPalette.ColorGroup.Disabled, role, disabled)
    return result
```

</details>
