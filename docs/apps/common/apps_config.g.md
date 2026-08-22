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
- [🔧 Function `get_open_quick_tab_on_startup`](#-function-get_open_quick_tab_on_startup)
- [🔧 Function `open_quick_tab_on_startup_key`](#-function-open_quick_tab_on_startup_key)
- [🔧 Function `set_open_quick_tab_on_startup`](#-function-set_open_quick_tab_on_startup)
- [🔧 Function `startup_tab_index`](#-function-startup_tab_index)

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

## 🔧 Function `get_open_quick_tab_on_startup`

```python
def get_open_quick_tab_on_startup(config: dict[str, Any], app: QuickTabAppName) -> bool
```

Return whether the Quick tab should open first for `app`.

Args:

- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any]`): Loaded application config.
- `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.

Returns:

- `bool`: `True` to open Quick first; `False` to open the second tab.

<details>
<summary>Code:</summary>

```python
def get_open_quick_tab_on_startup(config: dict[str, Any], app: QuickTabAppName) -> bool:
    apps = config.get("apps") or {}
    raw = apps.get(open_quick_tab_on_startup_key(app), OPEN_QUICK_TAB_ON_STARTUP_DEFAULT)
    return raw if isinstance(raw, bool) else OPEN_QUICK_TAB_ON_STARTUP_DEFAULT
```

</details>

## 🔧 Function `open_quick_tab_on_startup_key`

```python
def open_quick_tab_on_startup_key(app: QuickTabAppName) -> str
```

Return the `apps` config key for the Quick-tab startup preference.

<details>
<summary>Code:</summary>

```python
def open_quick_tab_on_startup_key(app: QuickTabAppName) -> str:
    if app not in _QUICK_TAB_APPS:
        msg = f"Unknown Quick-tab app: {app}"
        raise ValueError(msg)
    return f"{OPEN_QUICK_TAB_ON_STARTUP_KEY_PREFIX}{app}"
```

</details>

## 🔧 Function `set_open_quick_tab_on_startup`

```python
def set_open_quick_tab_on_startup(app: QuickTabAppName, *, enabled: bool, config: dict[str, Any] | None = None, config_path: str | None = None) -> None
```

Write the Quick-tab startup preference for `app` into `config.json`.

Args:

- `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.
- `enabled` (`bool`): `True` to open Quick first on startup.
- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
- `config_path` (`str | None`): Config file path. Defaults to the project config.

<details>
<summary>Code:</summary>

```python
def set_open_quick_tab_on_startup(
    app: QuickTabAppName,
    *,
    enabled: bool,
    config: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> None:
    key = open_quick_tab_on_startup_key(app)
    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    apps = data.get("apps")
    if not isinstance(apps, dict):
        apps = {}
        data["apps"] = apps
    apps[key] = bool(enabled)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    if config is not None:
        live_apps = config.setdefault("apps", {})
        if isinstance(live_apps, dict):
            live_apps[key] = bool(enabled)
```

</details>

## 🔧 Function `startup_tab_index`

```python
def startup_tab_index(*, open_quick: bool) -> int
```

Return the tab index to select when an app starts.

<details>
<summary>Code:</summary>

```python
def startup_tab_index(*, open_quick: bool) -> int:
    return 0 if open_quick else 1
```

</details>
