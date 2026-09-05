---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `backup.py`

## 🔧 Function `create_bookmarks_backup`

```python
def create_bookmarks_backup(chrome_path: Path, yandex_path: Path) -> Path
```

Copy both Bookmarks files (and `.bak` if present) into a timestamped folder.

<details>
<summary>Code:</summary>

```python
def create_bookmarks_backup(chrome_path: Path, yandex_path: Path) -> Path:
    stamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    dest = backup_root() / stamp
    dest.mkdir(parents=True, exist_ok=True)
    _copy_side(chrome_path, dest / "chrome")
    _copy_side(yandex_path, dest / "yandex")
    return dest
```

</details>
