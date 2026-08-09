---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `apps_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_apps_fitness_image_max_size`](#-function-get_apps_fitness_image_max_size)
- [🔧 Function `get_apps_list_limits`](#-function-get_apps_list_limits)
- [🔧 Function `get_apps_local_language`](#-function-get_apps_local_language)
- [🔧 Function `get_apps_local_language_display_name`](#-function-get_apps_local_language_display_name)

</details>

## 🔧 Function `get_apps_fitness_image_max_size`

```python
def get_apps_fitness_image_max_size(config: dict[str, Any]) -> int
```

Return max exercise image width/height in pixels from `apps.fitness_image_max_size`.

Larger media is scaled down so neither side exceeds this value (default `330`).

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_image_max_size(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_max_size", DEFAULT_FITNESS_IMAGE_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_MAX_SIZE
```

</details>

## 🔧 Function `get_apps_list_limits`

```python
def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]
```

Return `(initial_count, load_more_count)` from the shared `apps` config block.

Used for table first-page size, scroll load-more size, and similar limits
(autocomplete sample size, frequency window) that share the same defaults.

<details>
<summary>Code:</summary>

```python
def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]:
    apps = config.get("apps") or {}
    return (
        int(apps.get("initial_count", DEFAULT_INITIAL_COUNT)),
        int(apps.get("load_more_count", DEFAULT_LOAD_MORE_COUNT)),
    )
```

</details>

## 🔧 Function `get_apps_local_language`

```python
def get_apps_local_language(config: dict[str, Any]) -> str
```

Return local language code from `apps.local_language` (default `ru`).

<details>
<summary>Code:</summary>

```python
def get_apps_local_language(config: dict[str, Any]) -> str:
    apps = config.get("apps") or {}
    raw = apps.get("local_language", DEFAULT_LOCAL_LANGUAGE)
    code = str(raw or DEFAULT_LOCAL_LANGUAGE).strip().lower()
    return code or DEFAULT_LOCAL_LANGUAGE
```

</details>

## 🔧 Function `get_apps_local_language_display_name`

```python
def get_apps_local_language_display_name(config: dict[str, Any]) -> str
```

Return English display name for `apps.local_language` (e.g. `Russian`).

<details>
<summary>Code:</summary>

```python
def get_apps_local_language_display_name(config: dict[str, Any]) -> str:
    code = get_apps_local_language(config)
    if code in _LANGUAGE_DISPLAY_NAMES:
        return _LANGUAGE_DISPLAY_NAMES[code]
    return code.upper()
```

</details>
