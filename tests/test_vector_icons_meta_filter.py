"""Tests for Vector Icons meta filters from the variants header."""

from __future__ import annotations

from harrix_swiss_knife.apps.icons.catalog import IconFamily
from harrix_swiss_knife.apps.icons.meta_filter import (
    META_KIND_CATEGORY,
    META_KIND_DATE,
    META_KIND_TAG,
    build_meta_date_html,
    build_meta_list_html,
    build_variants_header_html,
    count_families_for_meta,
    filter_families_by_meta,
    meta_filter_label,
    meta_link_href,
    parse_meta_link,
)


def _family(
    family_id: str,
    *,
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    date: str = "",
) -> IconFamily:
    return IconFamily(
        id=family_id,
        title=family_id,
        categories=categories or [],
        tags=tags or [],
        folder=f"icons/{family_id}",
        featured="featured-image.svg",
        featured_hash="",
        date=date,
    )


def test_count_and_filter_meta() -> None:
    icons = [
        _family("a", categories=["building"], tags=["garage"], date="2020-07-19"),
        _family("b", categories=["building"], tags=["house"], date="2020-07-19"),
        _family("c", categories=["food"], tags=["garage"], date="2021-01-01"),
    ]
    assert count_families_for_meta(icons, META_KIND_CATEGORY, "building") == 2
    assert count_families_for_meta(icons, META_KIND_TAG, "garage") == 2
    assert count_families_for_meta(icons, META_KIND_DATE, "2020-07-19") == 2
    assert [item.id for item in filter_families_by_meta(icons, META_KIND_TAG, "garage")] == ["a", "c"]


def test_build_variants_header_html_links_when_others_exist() -> None:
    icons = [
        _family("a", categories=["building"], tags=["garage"], date="2020-07-19"),
        _family("b", categories=["building"], tags=["house"], date="2020-07-19"),
    ]
    html = build_variants_header_html(icons[0], icons)
    assert 'href="hsk-meta:category/building"' in html
    assert "building (2)" in html
    assert 'href="hsk-meta:date/2020-07-19"' in html
    assert "garage" in html
    assert "garage (" not in html  # unique tag, no link


def test_build_meta_field_html_helpers() -> None:
    icons = [
        _family("a", categories=["building"], tags=["garage"], date="2020-07-19"),
        _family("b", categories=["building"], tags=["house"], date="2020-07-19"),
    ]
    assert "building (2)" in build_meta_list_html(icons, META_KIND_CATEGORY, ["building"])
    assert build_meta_list_html(icons, META_KIND_TAG, []) == "—"
    assert "2020-07-19 (2)" in build_meta_date_html(icons, "2020-07-19")
    assert build_meta_date_html(icons, "") == "—"


def test_parse_meta_link_roundtrip() -> None:
    href = meta_link_href(META_KIND_TAG, "foo/bar")
    assert parse_meta_link(href) == (META_KIND_TAG, "foo/bar")
    assert parse_meta_link("https://example.com") is None
    assert meta_filter_label(META_KIND_CATEGORY, "building") == "Category: building"
