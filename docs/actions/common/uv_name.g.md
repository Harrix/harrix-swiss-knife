---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_name.py`

## 🔧 Function `validate_uv_project_name`

```python
def validate_uv_project_name(name: str) -> str | None
```

Return an error message when `name` is invalid, otherwise `None`.

<details>
<summary>Code:</summary>

```python
def validate_uv_project_name(name: str) -> str | None:
    stripped = name.strip()
    if not stripped:
        return "Name must not be empty."
    if " " in name:
        return "Name must not contain spaces."
    if not _UV_PROJECT_NAME_RE.fullmatch(stripped):
        return "Name must contain only English letters, digits, hyphens, and underscores."
    return None
```

</details>
