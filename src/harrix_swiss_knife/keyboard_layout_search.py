"""Search helpers that tolerate EN/RU keyboard layout mistakes."""

from __future__ import annotations

from harrix_swiss_knife.cli_menu import CLI_MENU_SUFFIX

# Physical QWERTY <-> Russian JCUKEN key pairs (lowercase and uppercase).
_LAYOUT_PAIRS: tuple[tuple[str, str], ...] = (
    ("q", "\u0439"),
    ("w", "\u0446"),
    ("e", "\u0443"),
    ("r", "\u043a"),
    ("t", "\u0435"),
    ("y", "\u043d"),
    ("u", "\u0433"),
    ("i", "\u0448"),
    ("o", "\u0449"),
    ("p", "\u0437"),
    ("[", "\u0445"),
    ("]", "\u044a"),
    ("a", "\u0444"),
    ("s", "\u044b"),
    ("d", "\u0432"),
    ("f", "\u0430"),
    ("g", "\u043f"),
    ("h", "\u0440"),
    ("j", "\u043e"),
    ("k", "\u043b"),
    ("l", "\u0434"),
    (";", "\u0436"),
    ("'", "\u044d"),
    ("z", "\u044f"),
    ("x", "\u0447"),
    ("c", "\u0441"),
    ("v", "\u043c"),
    ("b", "\u0438"),
    ("n", "\u0442"),
    ("m", "\u044c"),
    (",", "\u0431"),
    (".", "\u044e"),
    ("`", "\u0451"),
    ("Q", "\u0419"),
    ("W", "\u0426"),
    ("E", "\u0423"),
    ("R", "\u041a"),
    ("T", "\u0415"),
    ("Y", "\u041d"),
    ("U", "\u0413"),
    ("I", "\u0428"),
    ("O", "\u0429"),
    ("P", "\u0417"),
    ("{", "\u0425"),
    ("}", "\u042a"),
    ("A", "\u0424"),
    ("S", "\u042b"),
    ("D", "\u0412"),
    ("F", "\u0410"),
    ("G", "\u041f"),
    ("H", "\u0420"),
    ("J", "\u041e"),
    ("K", "\u041b"),
    ("L", "\u0414"),
    (":", "\u0416"),
    ('"', "\u042d"),
    ("Z", "\u042f"),
    ("X", "\u0427"),
    ("C", "\u0421"),
    ("V", "\u041c"),
    ("B", "\u0418"),
    ("N", "\u0422"),
    ("M", "\u042c"),
    ("<", "\u0411"),
    (">", "\u042e"),
    ("~", "\u0401"),
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
    text = text.removeprefix(_BOLD_TITLE_PREFIX)
    if CLI_MENU_SUFFIX and text.endswith(CLI_MENU_SUFFIX):
        text = text[: -len(CLI_MENU_SUFFIX)]
    return text.strip().casefold()


def swap_keyboard_layout(text: str) -> str:
    """Swap characters as if typed on the other EN/RU keyboard layout."""
    return "".join(_LAYOUT_SWAP.get(char, char) for char in text)
