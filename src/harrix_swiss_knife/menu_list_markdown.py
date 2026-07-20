"""Generate README List of commands Markdown from the tray menu structure (no Qt)."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.cli_menu import CLI_MENU_SUFFIX

_MENU_DEFINITION_LENGTH = 3
_README_SECTION = "## 📋 List of commands"


def generate_markdown_from_menu_structure(structure: list[Any], level: int = 0) -> list[str]:
    """Turn menu structure (same shape as get_menu_structure) into README list lines.

    Mirrors MainMenuBase.add_menu_structure / add_items: submenus first, then items;
    separators are omitted; action groups between separators are sorted by title.

    """
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


def update_readme_list_of_commands() -> str:
    """Rewrite README.md section List of commands from get_menu_structure().

    Returns:

    - `str`: Markdown body written into the section (without the heading).

    """
    # Lazy import: menu_structure imports action classes that may import this module.
    from harrix_swiss_knife.menu_structure import get_menu_structure  # noqa: PLC0415

    filename = h.dev.get_project_root() / "README.md"
    list_of_menu = "\n".join(generate_markdown_from_menu_structure(get_menu_structure()))
    h.md.replace_section(filename, list_of_menu, _README_SECTION)
    return list_of_menu


def _action_line(action_cls: type, level: int) -> str:
    """Format a single action as a Markdown list line."""
    icon = _icon_for_markdown(getattr(action_cls, "icon", "") or "")
    title = _decorate_action_title(action_cls)
    if icon:
        return f"{'  ' * level}- {icon} {title}"
    return f"{'  ' * level}- {title}"


def _decorate_action_title(action_cls: type) -> str:
    """Build title with ★ and CLI suffix, matching MainMenuBase._add_item."""
    text = getattr(action_cls, "title", "")
    if getattr(action_cls, "bold_title", False):
        text = f"★ {text}"
    if getattr(action_cls, "cli_available", False):
        text = f"{text}{CLI_MENU_SUFFIX}"
    return text


def _icon_for_markdown(icon: str) -> str:
    """Return emoji for Markdown; skip SVG / file-based icons (same as QMenu export)."""
    if icon and "." not in icon:
        return icon
    return ""


def _markdown_from_item_groups(items: list[Any], level: int) -> list[str]:
    """Emit Markdown for action classes, sorting within groups split by separators."""
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
