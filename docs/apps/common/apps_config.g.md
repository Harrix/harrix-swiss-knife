---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `apps_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `DEFAULT_INITIAL_COUNT`](#-constant-default_initial_count)
- [📎 Constant `DEFAULT_LOAD_MORE_COUNT`](#-constant-default_load_more_count)
- [🔧 Function `get_apps_list_limits`](#-function-get_apps_list_limits)

</details>

## 📎 Constant `DEFAULT_INITIAL_COUNT`

```python
DEFAULT_INITIAL_COUNT = 1000
```

_No docstring provided._

## 📎 Constant `DEFAULT_LOAD_MORE_COUNT`

```python
DEFAULT_LOAD_MORE_COUNT = 500
```

_No docstring provided._

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
