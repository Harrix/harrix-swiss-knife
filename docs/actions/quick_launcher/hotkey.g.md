---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `hotkey.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_quick_launcher_hotkey`](#-function-load_quick_launcher_hotkey)
- [🔧 Function `save_quick_launcher_hotkey`](#-function-save_quick_launcher_hotkey)

</details>

## 🔧 Function `load_quick_launcher_hotkey`

```python
def load_quick_launcher_hotkey() -> str
```

Return the saved hotkey string, or empty if unset or config-temp is missing.

<details>
<summary>Code:</summary>

```python
def load_quick_launcher_hotkey() -> str:
    try:
        temp_config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ""
    return str(temp_config.get(QUICK_LAUNCHER_HOTKEY_KEY) or "").strip()
```

</details>

## 🔧 Function `save_quick_launcher_hotkey`

```python
def save_quick_launcher_hotkey(hotkey: str) -> None
```

Save hotkey to `config-temp.json` without touching the main config file.

<details>
<summary>Code:</summary>

```python
def save_quick_launcher_hotkey(hotkey: str) -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
    h.dev.config_update_value(
        QUICK_LAUNCHER_HOTKEY_KEY,
        hotkey.strip(),
        get_config_path_str(),
        is_temp=True,
    )
```

</details>
