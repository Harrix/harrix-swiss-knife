"""Collect menu actions marked for the quick launcher overlay."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

from harrix_swiss_knife.actions.common.base import ActionBase

_MENU_SUBMENU_TUPLE_LEN = 3


def collect_quick_launcher_actions(structure: list[Any]) -> list[type[ActionBase]]:
    """Return action classes with `quick_launcher=True`, sorted by title."""
    actions = [
        action_cls for action_cls in iter_menu_structure(structure) if getattr(action_cls, "quick_launcher", False)
    ]
    return sorted(actions, key=lambda cls: cls.title)


def iter_menu_actions_with_category(
    structure: list[Any],
    category: str = "",
) -> Iterator[tuple[type[ActionBase], str]]:
    """Yield `(action_class, category_title)` from a nested menu structure.

    Root-level actions (outside a submenu) get an empty category string.

    """
    for element in structure:
        if isinstance(element, tuple) and len(element) == _MENU_SUBMENU_TUPLE_LEN:
            title, _icon, items = element
            yield from iter_menu_actions_with_category(items, title)
            continue
        if element == "-":
            continue
        if isinstance(element, type) and issubclass(element, ActionBase):
            yield element, category


def iter_menu_structure(structure: list[Any]) -> Iterator[type[ActionBase]]:
    """Yield action classes from a nested menu structure (submenus and root items)."""
    for action_cls, _category in iter_menu_actions_with_category(structure):
        yield action_cls
