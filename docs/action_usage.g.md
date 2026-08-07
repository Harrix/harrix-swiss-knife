---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_usage.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionUsageEntry`](#%EF%B8%8F-class-actionusageentry)
- [🔧 Function `load_action_usage`](#-function-load_action_usage)
- [🔧 Function `record_action_usage`](#-function-record_action_usage)

</details>

## 🏛️ Class `ActionUsageEntry`

```python
class ActionUsageEntry(TypedDict)
```

Usage counters for one action class.

<details>
<summary>Code:</summary>

```python
class ActionUsageEntry(TypedDict):

    count: int
    gui: int
    cli: int
    last_used: str
```

</details>

## 🔧 Function `load_action_usage`

```python
def load_action_usage(path: Path | None = None) -> ActionUsageMap
```

Load usage map from JSON; return empty dict if missing or invalid.

<details>
<summary>Code:</summary>

```python
def load_action_usage(path: Path | None = None) -> ActionUsageMap:
    usage_path = path if path is not None else get_action_usage_path()
    if not usage_path.is_file():
        return {}
    try:
        raw = json.loads(usage_path.read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Failed to load action usage from %s", usage_path)
        return {}
    if not isinstance(raw, dict):
        return {}
    result: ActionUsageMap = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        entry = _normalize_entry(value)
        if entry is not None:
            result[key] = entry
    return result
```

</details>

## 🔧 Function `record_action_usage`

```python
def record_action_usage(class_name: str, *, via_cli: bool, path: Path | None = None) -> None
```

Increment counters for `class_name` and persist atomically.

Errors are logged and swallowed so statistics never break actions.

<details>
<summary>Code:</summary>

```python
def record_action_usage(class_name: str, *, via_cli: bool, path: Path | None = None) -> None:
    if not class_name:
        return
    usage_path = path if path is not None else get_action_usage_path()
    try:
        with _lock:
            data = load_action_usage(usage_path)
            entry = data.get(class_name) or ActionUsageEntry(count=0, gui=0, cli=0, last_used="")
            entry["count"] = int(entry["count"]) + 1
            if via_cli:
                entry["cli"] = int(entry["cli"]) + 1
            else:
                entry["gui"] = int(entry["gui"]) + 1
            entry["last_used"] = datetime.now(UTC).astimezone().isoformat(timespec="seconds")
            data[class_name] = entry
            _write_atomic(usage_path, data)
    except Exception:
        logger.exception("Failed to record action usage for %s", class_name)
```

</details>
