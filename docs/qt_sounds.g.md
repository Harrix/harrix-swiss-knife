---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_sounds.py`

## 🔧 Function `qt_sounds_muted`

```python
def qt_sounds_muted() -> bool
```

Return whether UI sounds should stay silent (pytest and check runners).

<details>
<summary>Code:</summary>

```python
def qt_sounds_muted() -> bool:
    flag = os.environ.get(_MUTE_ENV, "").strip().lower()
    if flag in {"1", "true", "yes"}:
        return True
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))
```

</details>
