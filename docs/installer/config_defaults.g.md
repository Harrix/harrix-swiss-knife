---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config_defaults.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_config_defaults`](#-function-apply_config_defaults)
- [🔧 Function `is_unset_config_path`](#-function-is_unset_config_path)

</details>

## 🔧 Function `apply_config_defaults`

```python
def apply_config_defaults(hsk_path: Path, log: OutcomeLog) -> None
```

Apply first-run defaults: stack paths, DBs, and show-main-window.

Writes install-relative paths so Update / Python checks / Android actions find
the three sibling repos under the install parent. Personal folders (notes,
photos, vector icons, sites, …) stay as placeholders for the user to set.

<details>
<summary>Code:</summary>

```python
def apply_config_defaults(hsk_path: Path, log: OutcomeLog) -> None:
    config_path = _ensure_config_json(hsk_path, log)
    if config_path is None:
        return
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.add("skipped", f"Could not read config.json: {exc}")
        return
    if not isinstance(data, dict):
        log.add("skipped", "config.json root is not an object")
        return

    hsk = hsk_path.resolve()
    install_root = hsk.parent
    siblings = {name: (install_root / name).resolve() for name in REPO_NAMES}

    log.step("Default config (show main window on startup)")
    data["show_main_window_on_startup"] = True
    log.add("installed", "Configured show_main_window_on_startup=true")

    _apply_stack_paths(data, install_root=install_root, siblings=siblings, hsk=hsk, log=log)
    _apply_data_for_hsk_paths(data=data, install_root=install_root, log=log)

    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
```

</details>

## 🔧 Function `is_unset_config_path`

```python
def is_unset_config_path(value: object) -> bool
```

Return whether a config path looks empty, a `<YOUR_…>` placeholder, or missing.

<details>
<summary>Code:</summary>

```python
def is_unset_config_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return True
    if _PLACEHOLDER_RE.search(value):
        return True
    try:
        return not Path(value).expanduser().exists()
    except OSError:
        return True
```

</details>
