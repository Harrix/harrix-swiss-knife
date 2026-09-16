---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_macros_prefs.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_macros_preferred_text_language`](#-function-load_macros_preferred_text_language)
- [🔧 Function `save_macros_preferred_text_language`](#-function-save_macros_preferred_text_language)

</details>

## 🔧 Function `load_macros_preferred_text_language`

```python
def load_macros_preferred_text_language() -> MacrosTextLanguage
```

Return preferred macros text tab (`local` or `en`; default `local`).

<details>
<summary>Code:</summary>

```python
def load_macros_preferred_text_language() -> MacrosTextLanguage:
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return _DEFAULT
    raw = loaded.get(_CONFIG_KEY, _DEFAULT)
    if isinstance(raw, str) and raw.strip().casefold() in {"en", "english"}:
        return "en"
    return "local"
```

</details>

## 🔧 Function `save_macros_preferred_text_language`

```python
def save_macros_preferred_text_language(value: MacrosTextLanguage) -> None
```

Persist preferred macros text tab into `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_macros_preferred_text_language(value: MacrosTextLanguage) -> None:
    h.dev.config_update_value(_CONFIG_KEY, value, get_config_path_str(), is_temp=True)
```

</details>
