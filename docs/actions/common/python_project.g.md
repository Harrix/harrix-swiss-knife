---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `python_project.py`

## 🔧 Function `reject_python_project_for_md_beautify`

```python
def reject_python_project_for_md_beautify(action: ActionBase, folder_path: Path | str, *, noninteractive: bool) -> bool
```

Log an error and return `True` if Markdown beautify must not run on a Python project.

<details>
<summary>Code:</summary>

```python
def reject_python_project_for_md_beautify(
    action: ActionBase,
    folder_path: Path | str,
    *,
    noninteractive: bool,
) -> bool:
    path = Path(folder_path)
    if not is_python_project(path):
        return False
    action.add_line(
        f"❌ {path} is a Python project (has pyproject.toml). Use `hsk py ruff-sort-docs` instead.",
    )
    if not noninteractive:
        action.show_result()
    return True
```

</details>
