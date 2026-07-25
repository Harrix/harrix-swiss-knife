---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `python_project.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_python_project`](#-function-is_python_project)
- [🔧 Function `reject_python_project_for_md_beautify`](#-function-reject_python_project_for_md_beautify)

</details>

## 🔧 Function `is_python_project`

```python
def is_python_project(folder_path: Path | str) -> bool
```

Return whether `folder_path` looks like a Python project (`pyproject.toml`).

<details>
<summary>Code:</summary>

```python
def is_python_project(folder_path: Path | str) -> bool:
    return (Path(folder_path) / "pyproject.toml").is_file()
```

</details>

## 🔧 Function `reject_python_project_for_md_beautify`

```python
def reject_python_project_for_md_beautify(action: ActionBase, folder_path: Path | str) -> bool
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
