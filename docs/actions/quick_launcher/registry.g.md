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
- [🔧 Function `iter_menu_actions_with_category`](#-function-iter_menu_actions_with_category)
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

## 🔧 Function `iter_menu_actions_with_category`

```python
def iter_menu_actions_with_category(structure: list[Any], category: str = "") -> Iterator[tuple[type[ActionBase], str]]
```

Yield `(action_class, category_title)` from a nested menu structure.

Root-level actions (outside a submenu) get an empty category string.

<details>
<summary>Code:</summary>

```python
def iter_menu_actions_with_category(
    structure: list[Any],
    category: str = "",
) -> Iterator[tuple[type[ActionBase], str]]:
    for element in structure:
        if isinstance(element, tuple) and len(element) == _MENU_SUBMENU_TUPLE_LEN:
            title, _icon, items = element
            yield from iter_menu_actions_with_category(items, title)
            continue
        if element == "-":
            continue
        if isinstance(element, type) and issubclass(element, ActionBase):
            yield element, category
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
    for action_cls, _category in iter_menu_actions_with_category(structure):
        yield action_cls
```

</details>
