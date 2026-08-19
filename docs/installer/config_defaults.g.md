---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config_defaults.py`

## 🔧 Function `apply_config_defaults`

```python
def apply_config_defaults(hsk_path: Path, log: OutcomeLog) -> None
```

Apply first-run defaults to `config/config.json` and database paths.

<details>
<summary>Code:</summary>

```python
def apply_config_defaults(hsk_path: Path, log: OutcomeLog) -> None:
    log.step("Default config (show main window on startup)")
    config_path = hsk_path / "config" / "config.json"
    if not config_path.is_file():
        log.add("skipped", "Could not set show_main_window_on_startup (config.json missing)")
        return
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.add("skipped", f"Could not read config.json: {exc}")
        return
    if not isinstance(data, dict):
        log.add("skipped", "config.json root is not an object")
        return
    data["show_main_window_on_startup"] = True
    log.add("installed", "Configured show_main_window_on_startup=true")

    log.step("Default databases paths (fresh PC fallback)")
    db_dir = hsk_path / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    apps = (
        ("sqlite_finance", "finance.db"),
        ("sqlite_fitness", "fitness.db"),
        ("sqlite_habits", "habits.db"),
        ("sqlite_food", "food.db"),
    )
    for key, filename in apps:
        current = data.get(key)
        need = True
        if isinstance(current, str) and current.strip():
            parent = Path(current).parent
            try:
                if parent.is_dir() or parent.exists():
                    need = False
            except OSError:
                need = True
        if need:
            new_path = (db_dir / filename).as_posix()
            data[key] = new_path
            log.add("installed", f"Set {key}={new_path}")
    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
```

</details>
