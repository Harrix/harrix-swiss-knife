---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_auto_listen_enabled`](#-function-is_auto_listen_enabled)
- [🔧 Function `load_saved_credentials`](#-function-load_saved_credentials)
- [🔧 Function `persist_credentials`](#-function-persist_credentials)
- [🔧 Function `photos_dir_from_config`](#-function-photos_dir_from_config)
- [🔧 Function `write_config_values`](#-function-write_config_values)

</details>

## 🔧 Function `is_auto_listen_enabled`

```python
def is_auto_listen_enabled(config: dict[str, Any]) -> bool
```

Return whether Photo Sync should keep listening in the background.

<details>
<summary>Code:</summary>

```python
def is_auto_listen_enabled(config: dict[str, Any]) -> bool:
    return bool(config.get(CONFIG_AUTO_LISTEN))
```

</details>

## 🔧 Function `load_saved_credentials`

```python
def load_saved_credentials(config: dict[str, Any]) -> tuple[str, str] | None
```

Return `(token, confirm_code)` when both are non-empty in config.

<details>
<summary>Code:</summary>

```python
def load_saved_credentials(config: dict[str, Any]) -> tuple[str, str] | None:
    token = str(config.get(CONFIG_TOKEN) or "").strip()
    confirm_code = str(config.get(CONFIG_CONFIRM_CODE) or "").strip()
    if not token or not confirm_code:
        return None
    return token, confirm_code
```

</details>

## 🔧 Function `persist_credentials`

```python
def persist_credentials(config_path: Path | str, *, token: str, confirm_code: str) -> None
```

Save pairing credentials so auto-listen can reuse them after restart.

<details>
<summary>Code:</summary>

```python
def persist_credentials(config_path: Path | str, *, token: str, confirm_code: str) -> None:
    write_config_values(
        config_path,
        {
            CONFIG_TOKEN: token.strip(),
            CONFIG_CONFIRM_CODE: confirm_code.strip(),
        },
    )
```

</details>

## 🔧 Function `photos_dir_from_config`

```python
def photos_dir_from_config(config: dict[str, Any]) -> Path | None
```

Return a usable photos folder from config, or `None`.

<details>
<summary>Code:</summary>

```python
def photos_dir_from_config(config: dict[str, Any]) -> Path | None:
    raw = str(config.get(CONFIG_FOLDER) or "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    try:
        path = path.resolve()
    except OSError:
        return None
    if not path.is_dir():
        return None
    return path
```

</details>

## 🔧 Function `write_config_values`

```python
def write_config_values(config_path: Path | str, updates: dict[str, Any]) -> None
```

Merge `updates` into the JSON config file and write it back.

<details>
<summary>Code:</summary>

```python
def write_config_values(config_path: Path | str, updates: dict[str, Any]) -> None:
    path = Path(config_path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        data = {}
    data.update(updates)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
```

</details>
