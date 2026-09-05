---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `annotation_colors.py`

## 🔧 Function `load_annotation_colors`

```python
def load_annotation_colors() -> list[tuple[str, str]]
```

Return `(hex, hint)` colors from Quick paste DB, else the seed list.

<details>
<summary>Code:</summary>

```python
def load_annotation_colors() -> list[tuple[str, str]]:
    try:
        config = h.dev.config_load(get_config_path_str())
    except (OSError, TypeError, ValueError):
        return list(SEED_COLORS)
    raw = str(config.get("sqlite_snippets") or "").strip()
    if not raw:
        return list(SEED_COLORS)
    db_path = Path(raw)
    if not db_path.is_file():
        return list(SEED_COLORS)
    try:
        from harrix_swiss_knife.apps.snippets.database_manager import DatabaseManager  # noqa: PLC0415

        manager = DatabaseManager(str(db_path))
        items = manager.list_items(ZONE_COLOR)
        manager.close()
    except (OSError, RuntimeError, ValueError):
        return list(SEED_COLORS)
    colors = [(item.value.strip(), (item.hint or "").strip()) for item in items if item.value.strip()]
    return colors or list(SEED_COLORS)
```

</details>
