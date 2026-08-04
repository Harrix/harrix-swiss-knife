"""Tests for harrix.dev-style site article link helpers."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.site_article_links import (
    SiteLinkSettings,
    github_https_url_for_repo,
    is_forbidden_cross_language_link,
    parse_content_repo_name,
    parse_site_url_or_path,
)


def test_is_forbidden_cross_language_link_only_en_to_ru() -> None:
    assert is_forbidden_cross_language_link("en", "ru") is True
    assert is_forbidden_cross_language_link("ru", "en") is False
    assert is_forbidden_cross_language_link("en", "en") is False
    assert is_forbidden_cross_language_link("ru", "ru") is False


def test_parse_content_repo_name_detects_default_russian_and_english() -> None:
    settings = SiteLinkSettings()
    ru = parse_content_repo_name("harrix.dev-articles-2021", settings)
    en = parse_content_repo_name("harrix.dev-articles-2025-en", settings)
    assert ru is not None
    assert en is not None
    assert ru.lang == "ru"
    assert en.lang == "en"
    assert is_forbidden_cross_language_link(en.lang, ru.lang) is True


def test_parse_content_repo_name_submodule_relpath() -> None:
    settings = SiteLinkSettings()
    en = parse_content_repo_name("harrix.dev-articles-2021-en", settings)
    ru = parse_content_repo_name("harrix.dev-articles-2021", settings)
    games = parse_content_repo_name("harrix.dev-games-en", settings)
    assert en is not None
    assert ru is not None
    assert games is not None
    assert en.submodule_relpath(settings) == "content/en/articles/2021"
    assert ru.submodule_relpath(settings) == "content/ru/articles/2021"
    assert games.submodule_relpath(settings) == "content/en/games"
    assert github_https_url_for_repo("harrix.dev-articles-2021-en", settings) == (
        "https://github.com/Harrix/harrix.dev-articles-2021-en"
    )


def test_parse_site_url_or_path_detects_russian_section() -> None:
    settings = SiteLinkSettings()
    ref = parse_site_url_or_path("/ru/articles/2021/install-git/", settings)
    assert ref is not None
    assert ref.lang == "ru"
    assert is_forbidden_cross_language_link("en", ref.lang) is True
