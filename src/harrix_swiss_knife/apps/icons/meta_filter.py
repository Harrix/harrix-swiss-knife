"""Meta filters from the Vector Icons variants header (category / tag / date)."""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote, unquote

from PySide6.QtGui import QColor

from harrix_swiss_knife.apps.common.ui_chrome import BRAND_INK, MUTED_TEXT, SELECTION_BG
from harrix_swiss_knife.fluent.theme import css, mix

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.icons.catalog import IconFamily
    from harrix_swiss_knife.fluent.tokens import FluentPalette

META_KIND_CATEGORY = "category"
META_KIND_TAG = "tag"
META_KIND_DATE = "date"
META_LINK_SCHEME = "hsk-meta"
_META_KINDS = frozenset({META_KIND_CATEGORY, META_KIND_TAG, META_KIND_DATE})


@dataclass(frozen=True, slots=True)
class MetaChrome:
    """Inline HTML colors for the variants meta header."""

    chip_bg: str
    chip_fg: str
    chip_count: str
    plain: str
    id_color: str


def light_meta_chrome() -> MetaChrome:
    """Return chip colors for the light theme (also used as HTML defaults)."""
    return MetaChrome(
        chip_bg=SELECTION_BG,
        chip_fg=BRAND_INK,
        chip_count="#6a6a6a",
        plain="#444444",
        id_color=MUTED_TEXT,
    )


def meta_chrome_for_palette(palette: FluentPalette) -> MetaChrome:
    """Return meta chip colors that stay readable on the active Fluent palette."""
    if not palette.dark:
        return light_meta_chrome()
    chip_fill = mix(palette.window_bg, QColor(palette.accent.red(), palette.accent.green(), palette.accent.blue(), 72))
    return MetaChrome(
        chip_bg=css(chip_fill),
        chip_fg=css(mix(palette.window_bg, palette.accent_text)),
        chip_count=css(mix(palette.window_bg, palette.text_secondary)),
        plain=css(mix(palette.window_bg, palette.text_primary)),
        id_color=css(mix(palette.window_bg, palette.text_secondary)),
    )


def build_meta_date_html(
    icons: Sequence[IconFamily],
    date: str,
    *,
    chrome: MetaChrome | None = None,
) -> str:
    """Return HTML for a date value, with a count link when shared by other icons."""
    cleaned = date.strip()
    if not cleaned:
        return "—"
    return _meta_value_html(icons, META_KIND_DATE, cleaned, chrome=chrome or light_meta_chrome())


def build_meta_list_html(
    icons: Sequence[IconFamily],
    kind: str,
    values: Sequence[str],
    *,
    chrome: MetaChrome | None = None,
) -> str:
    """Return HTML for category/tag lists with count links when shared."""
    cleaned = [item.strip() for item in values if item.strip()]
    if not cleaned:
        return "—"
    style = chrome or light_meta_chrome()
    return " ".join(_meta_value_html(icons, kind, item, chrome=style) for item in cleaned)


def build_variants_header_html(
    family: IconFamily,
    icons: Sequence[IconFamily],
    *,
    chrome: MetaChrome | None = None,
) -> str:
    """Return rich-text header with chip-style meta links when values are shared."""
    style = chrome or light_meta_chrome()
    lines = [
        f'<div style="font-weight:600;">{html.escape(family.title)}</div>',
        f'<div style="color:{style.id_color};font-size:11px;">{html.escape(family.id)}</div>',
    ]
    if family.date.strip():
        lines.append(
            f'<div style="margin-top:4px;">Date: {build_meta_date_html(icons, family.date, chrome=style)}</div>',
        )
    categories = [item.strip() for item in family.categories if item.strip()]
    if categories:
        lines.append(
            '<div style="margin-top:2px;">Categories: '
            f"{build_meta_list_html(icons, META_KIND_CATEGORY, categories, chrome=style)}</div>",
        )
    else:
        lines.append('<div style="margin-top:2px;">Categories: —</div>')
    tags = [item.strip() for item in family.tags if item.strip()]
    if tags:
        lines.append(
            f'<div style="margin-top:2px;">Tags: {build_meta_list_html(icons, META_KIND_TAG, tags, chrome=style)}</div>',
        )
    else:
        lines.append('<div style="margin-top:2px;">Tags: —</div>')
    return "".join(lines)


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


def _meta_value_html(icons: Sequence[IconFamily], kind: str, value: str, *, chrome: MetaChrome) -> str:
    escaped = html.escape(value)
    total = count_families_for_meta(icons, kind, value)
    if total <= 1:
        # Unique values are plain text — only shared (filterable) values get a chip.
        return f'<span style="color:{chrome.plain};margin:0 2px 2px 0;">{escaped}</span>'
    href = html.escape(meta_link_href(kind, value), quote=True)
    count = html.escape(f"({total})")
    chip = (
        f"background-color:{chrome.chip_bg};color:{chrome.chip_fg};text-decoration:none;"
        "border-radius:8px;padding:1px 6px;margin:0 2px 2px 0;"
    )
    return (
        f'<a href="{href}" style="{chip}">{escaped} '
        f'<span style="color:{chrome.chip_count};">{count}</span></a>'
    )
