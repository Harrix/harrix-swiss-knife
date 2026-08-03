"""Tests for harrix.dev-style site article link helpers."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.site_article_links import (
    SiteLinkSettings,
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


def test_parse_site_url_or_path_detects_russian_section() -> None:
    settings = SiteLinkSettings()
    ref = parse_site_url_or_path("/ru/articles/2021/install-git/", settings)
    assert ref is not None
    assert ref.lang == "ru"
    assert is_forbidden_cross_language_link("en", ref.lang) is True
