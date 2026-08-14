---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_identity.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `action_identity_name`](#-function-action_identity_name)
- [🔧 Function `action_relative_source_path`](#-function-action_relative_source_path)
- [🔧 Function `format_action_identity_text`](#-function-format_action_identity_text)

</details>

## 🔧 Function `action_identity_name`

```python
def action_identity_name(class_action: type) -> str
```

Return the action display name from the class docstring, else `title`.

<details>
<summary>Code:</summary>

```python
def action_identity_name(class_action: type) -> str:
    for line in inspect.cleandoc(class_action.__doc__ or "").splitlines():
        text = line.strip().rstrip(".")
        if text:
            return text
    title = strip_md_inline_code_markers(str(getattr(class_action, "title", "") or ""))
    return title.strip() or class_action.__name__
```

</details>

## 🔧 Function `action_relative_source_path`

```python
def action_relative_source_path(class_action: type) -> str
```

Return the action module path relative to the project root, using POSIX slashes.

<details>
<summary>Code:</summary>

```python
def action_relative_source_path(class_action: type) -> str:
    try:
        source = Path(inspect.getfile(class_action)).resolve()
    except (OSError, TypeError):
        return ""
    if source.suffix == ".pyc":
        source = source.with_suffix(".py")

    try:
        return source.relative_to(get_project_root().resolve()).as_posix()
    except ValueError:
        pass

    parts = source.parts
    if _PACKAGE_ROOT_NAME in parts:
        index = parts.index(_PACKAGE_ROOT_NAME)
        if index > 0 and parts[index - 1] == _SRC_DIR_NAME:
            index -= 1
        return Path(*parts[index:]).as_posix()
    return source.as_posix()
```

</details>

## 🔧 Function `format_action_identity_text`

```python
def format_action_identity_text(class_action: type) -> str
```

Return three lines: action name, class name, and relative source path.

<details>
<summary>Code:</summary>

```python
def format_action_identity_text(class_action: type) -> str:
    return "\n".join(
        (
            action_identity_name(class_action),
            class_action.__name__,
            action_relative_source_path(class_action),
        )
    )
```

</details>
