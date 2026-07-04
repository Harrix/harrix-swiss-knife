---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `registry.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `collect_quick_launcher_actions`](#-function-collect_quick_launcher_actions)
- [🔧 Function `iter_menu_structure`](#-function-iter_menu_structure)

</details>

## 🔧 Function `collect_quick_launcher_actions`

```python
def collect_quick_launcher_actions(structure: list[Any]) -> list[type[ActionBase]]
```

Return action classes with `quick_launcher=True`, sorted by title.

<details>
<summary>Code:</summary>

```python
def collect_quick_launcher_actions(structure: list[Any]) -> list[type[ActionBase]]:
    actions = [
        action_cls for action_cls in iter_menu_structure(structure) if getattr(action_cls, "quick_launcher", False)
    ]
    return sorted(actions, key=lambda cls: cls.title)
```

</details>

## 🔧 Function `iter_menu_structure`

```python
def iter_menu_structure(structure: list[Any]) -> Iterator[type[ActionBase]]
```

Yield action classes from a nested menu structure (submenus and root items).

<details>
<summary>Code:</summary>

```python
def iter_menu_structure(structure: list[Any]) -> Iterator[type[ActionBase]]:
    for element in structure:
        if isinstance(element, tuple) and len(element) == _MENU_SUBMENU_TUPLE_LEN:
            _title, _icon, items = element
            yield from iter_menu_structure(items)
            continue
        if element == "-":
            continue
        if isinstance(element, type) and issubclass(element, ActionBase):
            yield element
```

</details>
