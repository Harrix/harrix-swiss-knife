---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_screenshot_fab_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clamp_fab_top_left`](#-function-clamp_fab_top_left)
- [🔧 Function `clear_fab_position`](#-function-clear_fab_position)
- [🔧 Function `default_fab_top_left`](#-function-default_fab_top_left)
- [🔧 Function `ensure_fab_enabled_setting`](#-function-ensure_fab_enabled_setting)
- [🔧 Function `load_fab_enabled`](#-function-load_fab_enabled)
- [🔧 Function `load_fab_position`](#-function-load_fab_position)
- [🔧 Function `resolve_fab_top_left`](#-function-resolve_fab_top_left)
- [🔧 Function `save_fab_enabled`](#-function-save_fab_enabled)
- [🔧 Function `save_fab_position`](#-function-save_fab_position)

</details>

## 🔧 Function `clamp_fab_top_left`

```python
def clamp_fab_top_left(left: int, top: int, *, size: int, available: QRect) -> QPoint
```

Return a top-left point that keeps a square widget of `size` inside `available`.

<details>
<summary>Code:</summary>

```python
def clamp_fab_top_left(left: int, top: int, *, size: int, available: QRect) -> QPoint:
    max_left = max(available.left(), available.right() - size + 1)
    max_top = max(available.top(), available.bottom() - size + 1)
    return QPoint(
        min(max(left, available.left()), max_left),
        min(max(top, available.top()), max_top),
    )
```

</details>

## 🔧 Function `clear_fab_position`

```python
def clear_fab_position() -> None
```

Forget the saved position so the default placement is used next.

<details>
<summary>Code:</summary>

```python
def clear_fab_position() -> None:
    _ensure_temp_config()
    h.dev.config_update_value(POS_KEY, list(_POS_FALLBACK), get_config_path_str(), is_temp=True)
```

</details>

## 🔧 Function `default_fab_top_left`

```python
def default_fab_top_left(*, size: int, available: QRect, edge_margin: int = 20) -> QPoint
```

Return the default right-edge, vertically centered top-left point.

<details>
<summary>Code:</summary>

```python
def default_fab_top_left(*, size: int, available: QRect, edge_margin: int = 20) -> QPoint:
    left = available.right() - size - edge_margin
    top = available.center().y() - size // 2
    return clamp_fab_top_left(left, top, size=size, available=available)
```

</details>

## 🔧 Function `ensure_fab_enabled_setting`

```python
def ensure_fab_enabled_setting() -> bool
```

Ensure `finance_ai_screenshot_fab_enabled` exists in `config.json`; return it.

<details>
<summary>Code:</summary>

```python
def ensure_fab_enabled_setting() -> bool:
    path = get_config_path_str()
    try:
        config = h.dev.config_load(path, resolve_snippets=False)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        config = {}
    if not isinstance(config, dict):
        config = {}
    raw = config.get(ENABLED_KEY)
    if isinstance(raw, bool):
        return raw
    h.dev.config_update_value(ENABLED_KEY, True, path)  # noqa: FBT003
    return True
```

</details>

## 🔧 Function `load_fab_enabled`

```python
def load_fab_enabled() -> bool
```

Return whether the floating screenshot button should be shown.

<details>
<summary>Code:</summary>

```python
def load_fab_enabled() -> bool:
    try:
        config = h.dev.config_load(get_config_path_str(), resolve_snippets=False)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return True
    if not isinstance(config, dict):
        return True
    raw = config.get(ENABLED_KEY)
    return True if not isinstance(raw, bool) else raw
```

</details>

## 🔧 Function `load_fab_position`

```python
def load_fab_position() -> tuple[int, int] | None
```

Return saved absolute `[left, top]`, or `None` when unset / invalid.

<details>
<summary>Code:</summary>

```python
def load_fab_position() -> tuple[int, int] | None:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return None
    raw = config.get(POS_KEY)
    if not isinstance(raw, list) or len(raw) != _POS_COORD_COUNT:
        return None
    parsed: list[int] = []
    for item in raw:
        if isinstance(item, bool):
            return None
        if isinstance(item, int):
            parsed.append(item)
        elif isinstance(item, float):
            parsed.append(int(item))
        else:
            return None
    return parsed[0], parsed[1]
```

</details>

## 🔧 Function `resolve_fab_top_left`

```python
def resolve_fab_top_left(*, size: int, available: QRect, edge_margin: int = 20) -> QPoint
```

Return clamped saved position, or the default when unset / sentinel.

Uses the screen that still contains the saved point; if that monitor is gone
(for example 4K coords on a 1024-by-768 display), clamps into `available`.

<details>
<summary>Code:</summary>

```python
def resolve_fab_top_left(*, size: int, available: QRect, edge_margin: int = 20) -> QPoint:
    saved = load_fab_position()
    if saved is None or saved == _POS_FALLBACK or saved[0] < 0 or saved[1] < 0:
        return default_fab_top_left(size=size, available=available, edge_margin=edge_margin)
    screen = QGuiApplication.screenAt(QPoint(saved[0], saved[1]))
    target = screen.availableGeometry() if screen is not None else available
    return clamp_fab_top_left(saved[0], saved[1], size=size, available=target)
```

</details>

## 🔧 Function `save_fab_enabled`

```python
def save_fab_enabled(*, enabled: bool) -> None
```

Persist whether the floating screenshot button is shown.

<details>
<summary>Code:</summary>

```python
def save_fab_enabled(*, enabled: bool) -> None:
    h.dev.config_update_value(ENABLED_KEY, enabled, get_config_path_str())
```

</details>

## 🔧 Function `save_fab_position`

```python
def save_fab_position(left: int, top: int) -> tuple[int, int]
```

Persist absolute top-left desktop coordinates for the floating button.

<details>
<summary>Code:</summary>

```python
def save_fab_position(left: int, top: int) -> tuple[int, int]:
    cleaned = (int(left), int(top))
    _ensure_temp_config()
    h.dev.config_update_value(POS_KEY, list(cleaned), get_config_path_str(), is_temp=True)
    return cleaned
```

</details>
