"""Meta filters from the Vector Icons variants header (category / tag / date)."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING
from urllib.parse import quote, unquote

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.icons.catalog import IconFamily

META_KIND_CATEGORY = "category"
META_KIND_TAG = "tag"
META_KIND_DATE = "date"
META_LINK_SCHEME = "hsk-meta"
_META_KINDS = frozenset({META_KIND_CATEGORY, META_KIND_TAG, META_KIND_DATE})


def build_meta_date_html(icons: Sequence[IconFamily], date: str) -> str:
    """Return HTML for a date value, with a count link when shared by other icons."""
    cleaned = date.strip()
    if not cleaned:
        return "—"
    return _meta_value_html(icons, META_KIND_DATE, cleaned)


def build_meta_list_html(icons: Sequence[IconFamily], kind: str, values: Sequence[str]) -> str:
    """Return HTML for category/tag lists with count links when shared."""
    cleaned = [item.strip() for item in values if item.strip()]
    if not cleaned:
        return "—"
    return ", ".join(_meta_value_html(icons, kind, item) for item in cleaned)


def build_variants_header_html(family: IconFamily, icons: Sequence[IconFamily]) -> str:
    """Return rich-text header with blue links when multiple icons share meta values."""
    lines = [
        html.escape(family.title),
        html.escape(family.id),
    ]
    if family.date.strip():
        lines.append(f"Date: {build_meta_date_html(icons, family.date)}")
    categories = [item.strip() for item in family.categories if item.strip()]
    if categories:
        lines.append(f"Categories: {build_meta_list_html(icons, META_KIND_CATEGORY, categories)}")
    else:
        lines.append("Categories: —")
    tags = [item.strip() for item in family.tags if item.strip()]
    if tags:
        lines.append(f"Tags: {build_meta_list_html(icons, META_KIND_TAG, tags)}")
    else:
        lines.append("Tags: —")
    return "<br/>".join(lines)


def count_families_for_meta(icons: Sequence[IconFamily], kind: str, value: str) -> int:
    """Return how many families match the meta filter."""
    needle = value.strip()
    if not needle or kind not in _META_KINDS:
        return 0
    return sum(1 for family in icons if family_matches_meta(family, kind, needle))


def family_matches_meta(family: IconFamily, kind: str, value: str) -> bool:
    """Return whether `family` matches a category, tag, or date filter."""
    needle = value.strip()
    if not needle:
        return False
    if kind == META_KIND_CATEGORY:
        return any(item.strip().casefold() == needle.casefold() for item in family.categories)
    if kind == META_KIND_TAG:
        return any(item.strip().casefold() == needle.casefold() for item in family.tags)
    if kind == META_KIND_DATE:
        return family.date.strip() == needle
    return False


def filter_families_by_meta(icons: Sequence[IconFamily], kind: str, value: str) -> list[IconFamily]:
    """Return families matching the meta filter, preserving input order."""
    return [family for family in icons if family_matches_meta(family, kind, value)]


def meta_filter_label(kind: str, value: str) -> str:
    """Return a short human-readable label for the active meta filter bar."""
    cleaned = value.strip()
    if kind == META_KIND_CATEGORY:
        return f"Category: {cleaned}"
    if kind == META_KIND_TAG:
        return f"Tag: {cleaned}"
    if kind == META_KIND_DATE:
        return f"Date: {cleaned}"
    return cleaned


def meta_link_href(kind: str, value: str) -> str:
    """Return a custom URL for a variants-header meta link."""
    return f"{META_LINK_SCHEME}:{kind}/{quote(value.strip(), safe='')}"


def parse_meta_link(href: str) -> tuple[str, str] | None:
    """Parse `hsk-meta:kind/value` from a QLabel link activation."""
    text = href.strip()
    prefix = f"{META_LINK_SCHEME}:"
    if not text.startswith(prefix):
        return None
    rest = text[len(prefix) :]
    kind, sep, raw_value = rest.partition("/")
    if not sep or kind not in _META_KINDS:
        return None
    value = unquote(raw_value).strip()
    if not value:
        return None
    return kind, value


def _meta_value_html(icons: Sequence[IconFamily], kind: str, value: str) -> str:
    escaped = html.escape(value)
    total = count_families_for_meta(icons, kind, value)
    if total <= 1:
        return escaped
    href = html.escape(meta_link_href(kind, value), quote=True)
    return f'<a href="{href}">{escaped} ({total})</a>'
