"""Collect menu actions marked for the quick launcher overlay."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

from harrix_swiss_knife.actions.base import ActionBase

_MENU_SUBMENU_TUPLE_LEN = 3


def collect_quick_launcher_actions(structure: list[Any]) -> list[type[ActionBase]]:
    """Return action classes with ``quick_launcher=True``, sorted by title."""
    actions = [
        action_cls for action_cls in iter_menu_structure(structure) if getattr(action_cls, "quick_launcher", False)
    ]
    return sorted(actions, key=lambda cls: cls.title)


def iter_menu_structure(structure: list[Any]) -> Iterator[type[ActionBase]]:
    """Yield action classes from a nested menu structure (submenus and root items)."""
    for element in structure:
        if isinstance(element, tuple) and len(element) == _MENU_SUBMENU_TUPLE_LEN:
            _title, _icon, items = element
            yield from iter_menu_structure(items)
            continue
        if element == "-":
            continue
        if isinstance(element, type) and issubclass(element, ActionBase):
            yield element
