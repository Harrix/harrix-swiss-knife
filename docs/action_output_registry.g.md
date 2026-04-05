---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_output_registry.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_active_action_output`](#-function-get_active_action_output)
- [🔧 Function `register_active_action_output`](#-function-register_active_action_output)

</details>

## 🔧 Function `get_active_action_output`

```python
def get_active_action_output() -> Path | None
```

Return the active output path, or `None` if no action has run yet.

<details>
<summary>Code:</summary>

```python
def get_active_action_output() -> Path | None:
    with _lock:
        return _active_holder[0]
```

</details>

## 🔧 Function `register_active_action_output`

```python
def register_active_action_output(path: Path) -> None
```

Mark `path` as the file the UI should poll for action output.

<details>
<summary>Code:</summary>

```python
def register_active_action_output(path: Path) -> None:
    with _lock:
        _active_holder[0] = path.resolve()
```

</details>
