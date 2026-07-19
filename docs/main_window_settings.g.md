---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main_window_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_main_window_icon_grid`](#-function-load_main_window_icon_grid)
- [🔧 Function `save_main_window_icon_grid`](#-function-save_main_window_icon_grid)

</details>

## 🔧 Function `load_main_window_icon_grid`

```python
def load_main_window_icon_grid() -> bool
```

Return whether the tray window uses icon grid view. Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def load_main_window_icon_grid() -> bool:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(MAIN_WINDOW_ICON_GRID_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)
```

</details>

## 🔧 Function `save_main_window_icon_grid`

```python
def save_main_window_icon_grid() -> None
```

Persist tray window view mode in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_main_window_icon_grid(*, icon_grid: bool) -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
    h.dev.config_update_value(
        MAIN_WINDOW_ICON_GRID_KEY,
        icon_grid,
        get_config_path_str(),
        is_temp=True,
    )
```

</details>
