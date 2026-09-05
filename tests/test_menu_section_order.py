"""Tests for alphabetical menu section ordering."""

from __future__ import annotations

from harrix_swiss_knife.menu_list_markdown import generate_markdown_from_menu_structure
from harrix_swiss_knife.menu_structure import get_menu_structure


def _submenu_titles(structure: list) -> list[str]:
    return [element[0] for element in structure if isinstance(element, tuple) and len(element) == 3]


def test_menu_structure_submenu_titles_sort_alphabetically_in_markdown() -> None:
    lines = generate_markdown_from_menu_structure(get_menu_structure())
    section_titles = [line.removeprefix("- **").removesuffix("**") for line in lines if line.startswith("- **")]
    assert section_titles == sorted(section_titles, key=str.casefold)


def test_get_menu_structure_has_expected_submenus() -> None:
    titles = _submenu_titles(get_menu_structure())
    assert "Dev" in titles
    assert "File operations" in titles
    assert "Android" in titles
