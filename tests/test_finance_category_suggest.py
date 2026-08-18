"""Tests for finance category suggestion scoring."""

from harrix_swiss_knife.apps.finance.category_suggest import suggest_categories

_CATEGORIES = ["Cafe", "Food", "Transport", "Healthcare", "Household Goods", "Education"]
_ALIASES = {
    "Cafe": ["Cafe", "Кафе"],
    "Food": ["Food", "Еда"],
    "Transport": ["Transport", "Транспорт"],
    "Healthcare": ["Healthcare", "Здоровье"],
    "Household Goods": ["Household Goods", "Хозтовары"],
    "Education": ["Education", "Образование"],
}


def test_suggests_category_from_local_name() -> None:
    assert suggest_categories("кафе", [], _CATEGORIES, category_aliases=_ALIASES)[0] == "Cafe"


def test_suggests_category_from_close_local_typo() -> None:
    suggested = suggest_categories("кофе", [], _CATEGORIES, category_aliases=_ALIASES)
    assert "Cafe" in suggested


def test_prefers_frequent_history_over_rare_same_text() -> None:
    history: list[tuple[str, str, int]] = [
        ("Магнит", "Household Goods", 1),
        ("Магнит", "Food", 20),
    ]
    suggested = suggest_categories("магнит", history, _CATEGORIES, category_aliases=_ALIASES)
    assert suggested[0] == "Food"


def test_matches_standard_item_with_extra_words() -> None:
    history = [("Такси", "Transport", 25)]
    suggested = suggest_categories("такси яндекс", history, _CATEGORIES, category_aliases=_ALIASES)
    assert suggested[0] == "Transport"


def test_matches_partial_prefix_while_typing() -> None:
    history = [("Квартплата", "Household Goods", 8)]
    suggested = suggest_categories("квартпл", history, _CATEGORIES, category_aliases=_ALIASES)
    assert suggested[0] == "Household Goods"


def test_does_not_match_infix_noise() -> None:
    assert suggest_categories("tea", [("steak dinner", "Food", 3)], _CATEGORIES) == []


def test_short_query_returns_nothing() -> None:
    assert suggest_categories("ab", [("Taxi", "Transport", 5)], _CATEGORIES) == []
