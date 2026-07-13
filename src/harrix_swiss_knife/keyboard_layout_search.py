"""Search helpers that tolerate EN/RU keyboard layout mistakes."""

from __future__ import annotations

from harrix_swiss_knife.cli_menu import CLI_MENU_SUFFIX

# Physical QWERTY ↔ ЙЦУКЕН key pairs (lowercase and uppercase).
_LAYOUT_PAIRS: tuple[tuple[str, str], ...] = (
    ("q", "й"),
    ("w", "ц"),
    ("e", "у"),
    ("r", "к"),
    ("t", "е"),
    ("y", "н"),
    ("u", "г"),
    ("i", "ш"),
    ("o", "щ"),
    ("p", "з"),
    ("[", "х"),
    ("]", "ъ"),
    ("a", "ф"),
    ("s", "ы"),
    ("d", "в"),
    ("f", "а"),
    ("g", "п"),
    ("h", "р"),
    ("j", "о"),
    ("k", "л"),
    ("l", "д"),
    (";", "ж"),
    ("'", "э"),
    ("z", "я"),
    ("x", "ч"),
    ("c", "с"),
    ("v", "м"),
    ("b", "и"),
    ("n", "т"),
    ("m", "ь"),
    (",", "б"),
    (".", "ю"),
    ("`", "ё"),
    ("Q", "Й"),
    ("W", "Ц"),
    ("E", "У"),
    ("R", "К"),
    ("T", "Е"),
    ("Y", "Н"),
    ("U", "Г"),
    ("I", "Ш"),
    ("O", "Щ"),
    ("P", "З"),
    ("{", "Х"),
    ("}", "Ъ"),
    ("A", "Ф"),
    ("S", "Ы"),
    ("D", "В"),
    ("F", "А"),
    ("G", "П"),
    ("H", "Р"),
    ("J", "О"),
    ("K", "Л"),
    ("L", "Д"),
    (":", "Ж"),
    ('"', "Э"),
    ("Z", "Я"),
    ("X", "Ч"),
    ("C", "С"),
    ("V", "М"),
    ("B", "И"),
    ("N", "Т"),
    ("M", "Ь"),
    ("<", "Б"),
    (">", "Ю"),
    ("~", "Ё"),
)

_LAYOUT_SWAP: dict[str, str] = {}
for _en, _ru in _LAYOUT_PAIRS:
    _LAYOUT_SWAP[_en] = _ru
    _LAYOUT_SWAP[_ru] = _en

_BOLD_TITLE_PREFIX = "★ "


def command_matches_search(title: str, query: str) -> bool:
    """Return True if query matches title, including EN/RU layout mistakes.

    Empty query matches everything.
    """
    needle = query.strip()
    if not needle:
        return True

    haystack = normalize_command_title(title)
    needle_fold = needle.casefold()
    swapped_fold = swap_keyboard_layout(needle).casefold()
    return needle_fold in haystack or swapped_fold in haystack


def normalize_command_title(title: str) -> str:
    """Normalize a menu title for search comparison."""
    text = title.strip()
    if text.startswith(_BOLD_TITLE_PREFIX):
        text = text[len(_BOLD_TITLE_PREFIX) :]
    if CLI_MENU_SUFFIX and text.endswith(CLI_MENU_SUFFIX):
        text = text[: -len(CLI_MENU_SUFFIX)]
    return text.strip().casefold()


def swap_keyboard_layout(text: str) -> str:
    """Swap characters as if typed on the other EN/RU keyboard layout."""
    return "".join(_LAYOUT_SWAP.get(char, char) for char in text)
