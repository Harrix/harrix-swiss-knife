"""Pin favorite fitness exercises to the top of exercise lists."""

from __future__ import annotations

DUMBBELL_PREFIX = "🏋️ "
FAVORITE_PREFIX = "⭐ "


def format_favorite_exercise_label(
    name: str,
    *,
    favorite: bool,
    extra: str = "",
    dumbbell: bool = False,
) -> str:
    """Build a list label, prefixing icons for favorite and dumbbell exercises.

    Args:

    - `name` (`str`): English exercise name.
    - `favorite` (`bool`): Whether the exercise is pinned as a favorite.
    - `extra` (`str`): Optional suffix such as a daily goal. Defaults to `""`.
    - `dumbbell` (`bool`): Whether the exercise uses template dumbbell weights.
      Defaults to `False`.

    Returns:

    - `str`: Display text. The real name must still be stored in `UserRole`.

    """
    prefixes = ""
    if favorite:
        prefixes += FAVORITE_PREFIX
    if dumbbell:
        prefixes += DUMBBELL_PREFIX
    extra_part = f" {extra}" if extra else ""
    return f"{prefixes}{name}{extra_part}"


def parse_exercise_display_name(label: str) -> str:
    """Return the English name with favorite and dumbbell icon prefixes removed.

    Args:

    - `label` (`str`): Display text that may start with `⭐` and/or `🏋️`.

    Returns:

    - `str`: Exercise name without icon prefixes.

    """
    text = str(label).strip()
    changed = True
    while changed:
        changed = False
        for prefix in (FAVORITE_PREFIX, DUMBBELL_PREFIX):
            if text.startswith(prefix):
                text = text[len(prefix) :].lstrip()
                changed = True
    return text


def prefer_favorite_names(names: list[str], favorite_names: set[str]) -> list[str]:
    """Return `names` with favorites first, keeping relative order in each group.

    Args:

    - `names` (`list[str]`): Exercise names in the current list order.
    - `favorite_names` (`set[str]`): Names marked as favorites.

    Returns:

    - `list[str]`: Favorites, then the remaining names.

    """
    if not favorite_names:
        return list(names)
    favorites = [name for name in names if name in favorite_names]
    others = [name for name in names if name not in favorite_names]
    return favorites + others
