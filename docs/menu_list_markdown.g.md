---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `menu_list_markdown.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `generate_markdown_from_menu_structure`](#-function-generate_markdown_from_menu_structure)
- [🔧 Function `update_readme_list_of_commands`](#-function-update_readme_list_of_commands)
- [🔧 Function `_action_line`](#-function-_action_line)
- [🔧 Function `_decorate_action_title`](#-function-_decorate_action_title)
- [🔧 Function `_icon_for_markdown`](#-function-_icon_for_markdown)
- [🔧 Function `_markdown_from_item_groups`](#-function-_markdown_from_item_groups)

</details>

## 🔧 Function `generate_markdown_from_menu_structure`

```python
def generate_markdown_from_menu_structure(structure: list[Any], level: int = 0) -> list[str]
```

Turn menu structure (same shape as get_menu_structure) into README list lines.

Mirrors MainMenuBase.add_menu_structure / add_items: submenus first, then items;
separators are omitted; action groups between separators are sorted by title.

<details>
<summary>Code:</summary>

```python
def generate_markdown_from_menu_structure(structure: list[Any], level: int = 0) -> list[str]:
    markdown_lines: list[str] = []
    menus_to_add: list[tuple[str, str, list[Any]]] = []
    items_to_add: list[Any] = []

    for element in structure:
        if isinstance(element, tuple) and len(element) == _MENU_DEFINITION_LENGTH:
            title, icon, items = element
            menus_to_add.append((title, icon, items))
        elif element == "-":
            if menus_to_add and not items_to_add:
                for title, _icon, items in menus_to_add:
                    markdown_lines.append(f"{'  ' * level}- **{title}**")
                    markdown_lines.extend(generate_markdown_from_menu_structure(items, level + 1))
                menus_to_add = []
            else:
                items_to_add.append("-")
        elif isinstance(element, type):
            items_to_add.append(element)

    for title, _icon, items in menus_to_add:
        markdown_lines.append(f"{'  ' * level}- **{title}**")
        markdown_lines.extend(generate_markdown_from_menu_structure(items, level + 1))

    markdown_lines.extend(_markdown_from_item_groups(items_to_add, level))
    return markdown_lines
```

</details>

## 🔧 Function `update_readme_list_of_commands`

```python
def update_readme_list_of_commands() -> str
```

Rewrite README.md section List of commands from get_menu_structure().

Returns:

- `str`: Markdown body written into the section (without the heading).

<details>
<summary>Code:</summary>

```python
def update_readme_list_of_commands() -> str:
    # Lazy import: menu_structure imports action classes that may import this module.
    from harrix_swiss_knife.menu_structure import get_menu_structure  # noqa: PLC0415

    filename = h.dev.get_project_root() / "README.md"
    list_of_menu = "\n".join(generate_markdown_from_menu_structure(get_menu_structure()))
    h.md.replace_section(filename, list_of_menu, _README_SECTION)
    return list_of_menu
```

</details>

## 🔧 Function `_action_line`

```python
def _action_line(action_cls: type, level: int) -> str
```

Format a single action as a markdown list line.

<details>
<summary>Code:</summary>

```python
def _action_line(action_cls: type, level: int) -> str:
    icon = _icon_for_markdown(getattr(action_cls, "icon", "") or "")
    title = _decorate_action_title(action_cls)
    if icon:
        return f"{'  ' * level}- {icon} {title}"
    return f"{'  ' * level}- {title}"
```

</details>

## 🔧 Function `_decorate_action_title`

```python
def _decorate_action_title(action_cls: type) -> str
```

Build title with ★ and CLI suffix, matching MainMenuBase.\_add_item.

<details>
<summary>Code:</summary>

```python
def _decorate_action_title(action_cls: type) -> str:
    text = getattr(action_cls, "title", "")
    if getattr(action_cls, "bold_title", False):
        text = f"★ {text}"
    if getattr(action_cls, "cli_available", False):
        text = f"{text}{CLI_MENU_SUFFIX}"
    return text
```

</details>

## 🔧 Function `_icon_for_markdown`

```python
def _icon_for_markdown(icon: str) -> str
```

Return emoji for markdown; skip SVG / file-based icons (same as QMenu export).

<details>
<summary>Code:</summary>

```python
def _icon_for_markdown(icon: str) -> str:
    if icon and "." not in icon:
        return icon
    return ""
```

</details>

## 🔧 Function `_markdown_from_item_groups`

```python
def _markdown_from_item_groups(items: list[Any], level: int) -> list[str]
```

Emit markdown for action classes, sorting within groups split by separators.

<details>
<summary>Code:</summary>

```python
def _markdown_from_item_groups(items: list[Any], level: int) -> list[str]:
    groups: list[list[type]] = []
    current_group: list[type] = []

    for item in items:
        if item == "-":
            if current_group:
                groups.append(current_group)
                current_group = []
        elif isinstance(item, type):
            current_group.append(item)

    if current_group:
        groups.append(current_group)

    lines: list[str] = []
    for group in groups:
        sorted_group = sorted(group, key=lambda cls: getattr(cls, "title", ""))
        lines.extend(_action_line(action_cls, level) for action_cls in sorted_group)
    return lines
```

</details>
