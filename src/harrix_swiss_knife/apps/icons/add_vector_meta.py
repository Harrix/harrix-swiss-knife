"""Scan note YAML and build defaults for Add Vector Image."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from harrix_swiss_knife.apps.icons.catalog import FLAT_ICON_EXTENSIONS, iter_icon_note_dirs, parse_note_frontmatter
from harrix_swiss_knife.apps.icons.family_id import category_from_family_id, family_id_from_stem, title_from_family_id

_PERMALINK_SOURCE_SUFFIX_RE = re.compile(
    r"/([^/]+)/([^/]+)/\2\.md$",
    re.IGNORECASE,
)
_PERMALINK_SUFFIX_RE = re.compile(
    r"/([^/]+)/([^/]+)/?$",
    re.IGNORECASE,
)


@dataclass(slots=True)
class NoteMeta:
    """User-confirmed metadata for a new icon note."""

    family_id: str
    title: str
    date: str
    category: str
    tags: list[str]
    author: str
    author_email: str
    license: str
    license_url: str
    permalink: str
    permalink_source: str
    lang: str = "en"
    featured_name: str = "featured-image.svg"


@dataclass(slots=True)
class RepoMetaDefaults:
    """Consensus defaults extracted from existing icon notes."""

    authors: list[str] = field(default_factory=list)
    author_emails: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    license_urls: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    author: str = ""
    author_email: str = ""
    license: str = ""
    license_url: str = ""
    permalink_base: str = ""
    permalink_source_base: str = ""
    existing_variant_stems: list[str] = field(default_factory=list)


def consensus_value(values: list[str]) -> str:
    """Return the only distinct value, otherwise empty."""
    unique = sorted({item.strip() for item in values if item.strip()}, key=str.casefold)
    if len(unique) == 1:
        return unique[0]
    return ""


def defaults_from_source_stem(stem: str) -> tuple[str, str, str]:
    """Return `(family_id, title, category)` derived from a source filename stem."""
    family_id = family_id_from_stem(stem)
    title = title_from_family_id(family_id)
    category = category_from_family_id(family_id) if "__" in family_id else ""
    return family_id, title, category


def extra_categories_for_family(categories: list[str], family_id: str) -> list[str]:
    """Return YAML categories that are not the family-id folder prefix."""
    prefix = category_from_family_id(family_id).casefold()
    extras: list[str] = []
    seen: set[str] = {prefix} if prefix else set()
    for item in categories:
        cleaned = item.strip()
        key = cleaned.casefold()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        extras.append(cleaned)
    return extras


def extract_permalink_base(permalink: str) -> str | None:
    """Strip `/{category}/{family_id}` from a site permalink."""
    text = permalink.strip().rstrip("/")
    if not text:
        return None
    match = _PERMALINK_SUFFIX_RE.search(text)
    if match is None:
        return None
    base = text[: match.start()] + "/"
    return base if base.startswith("http") else None


def extract_permalink_source_base(permalink_source: str) -> str | None:
    """Strip `/{category}/{family_id}/{family_id}.md` from a GitHub permalink."""
    text = permalink_source.strip()
    if not text:
        return None
    match = _PERMALINK_SOURCE_SUFFIX_RE.search(text)
    if match is None:
        return None
    base = text[: match.start()] + "/"
    return base if base.startswith("http") else None


def join_permalink(base: str, suffix: str) -> str:
    """Join permalink base and suffix without duplicating slashes."""
    left = base.strip()
    right = suffix.strip().lstrip("/")
    if not left:
        return right
    if not right:
        return left.rstrip("/") + ("/" if left.endswith("/") else "")
    return left.rstrip("/") + "/" + right


def note_dir_for_meta(repo_root: Path, *, family_id: str, category: str) -> Path:
    """Return destination note folder for dialog metadata."""
    icons_dir = Path(repo_root) / "icons"
    cleaned_category = category.strip()
    if cleaned_category:
        return icons_dir / cleaned_category / family_id
    return icons_dir / family_id


def note_meta_from_existing(
    *,
    family_id: str,
    title: str,
    categories: list[str],
    tags: list[str],
    featured_name: str,
    frontmatter: dict[str, Any],
) -> NoteMeta:
    """Build dialog metadata from an existing note family and frontmatter."""
    prefix = category_from_family_id(family_id) if "__" in family_id else ""
    category = prefix or (categories[0] if categories else "")
    permalink = str(frontmatter.get("permalink") or "").strip()
    permalink_source = str(frontmatter.get("permalink-source") or "").strip()
    featured = featured_name.strip() or "featured-image.svg"
    return NoteMeta(
        family_id=family_id,
        title=title,
        date=str(frontmatter.get("date") or "").strip(),
        category=category,
        tags=list(tags),
        author=str(frontmatter.get("author") or "").strip(),
        author_email=str(frontmatter.get("author-email") or "").strip(),
        license=str(frontmatter.get("license") or "").strip(),
        license_url=str(frontmatter.get("license-url") or "").strip(),
        permalink=permalink,
        permalink_source=permalink_source,
        lang=str(frontmatter.get("lang") or "en").strip() or "en",
        featured_name=featured,
    )


def note_meta_with_category(meta: NoteMeta, category: str) -> NoteMeta:
    """Return metadata with `category`, synced family ID, and permalink suffixes."""
    cleaned = category.strip()
    new_id = sync_family_id_category(meta.family_id, cleaned) or meta.family_id
    site, source = permalink_suffixes(cleaned, new_id)
    permalink = meta.permalink
    permalink_source = meta.permalink_source
    base = extract_permalink_base(permalink)
    source_base = extract_permalink_source_base(permalink_source)
    if base and site:
        permalink = join_permalink(base, site)
    if source_base and source:
        permalink_source = join_permalink(source_base, source)
    return NoteMeta(
        family_id=new_id,
        title=meta.title,
        date=meta.date,
        category=cleaned,
        tags=list(meta.tags),
        author=meta.author,
        author_email=meta.author_email,
        license=meta.license,
        license_url=meta.license_url,
        permalink=permalink,
        permalink_source=permalink_source,
        lang=meta.lang,
        featured_name=meta.featured_name,
    )


def permalink_suffixes(category: str, family_id: str) -> tuple[str, str]:
    """Return site and source path suffixes for `category` + `family_id`."""
    cleaned_id = family_id.strip()
    cleaned_category = category.strip()
    if not cleaned_id or not cleaned_category:
        return "", ""
    site = f"{cleaned_category}/{cleaned_id}"
    source = f"{cleaned_category}/{cleaned_id}/{cleaned_id}.md"
    return site, source


def scan_repo_meta_defaults(repo_root: Path) -> RepoMetaDefaults:
    """Scan note frontmatter and build consensus defaults for the add dialog."""
    icons_dir = Path(repo_root) / "icons"
    result = RepoMetaDefaults()
    if not icons_dir.is_dir():
        return result

    authors: list[str] = []
    emails: list[str] = []
    licenses: list[str] = []
    license_urls: list[str] = []
    categories: set[str] = set()
    permalink_bases: list[str] = []
    permalink_source_bases: list[str] = []
    stems: list[str] = []

    for note_dir in iter_icon_note_dirs(icons_dir):
        md_path = note_dir / f"{note_dir.name}.md"
        meta: dict[str, Any] = {}
        if md_path.is_file():
            try:
                text = md_path.read_text(encoding="utf-8")
            except OSError:
                text = ""
            meta = parse_note_frontmatter(text) if text else {}

        for key, bucket in (
            ("author", authors),
            ("author-email", emails),
            ("license", licenses),
            ("license-url", license_urls),
        ):
            value = str(meta.get(key) or "").strip()
            if value:
                bucket.append(value)

        for item in meta.get("categories") or []:
            category = str(item).strip()
            if category:
                categories.add(category)

        permalink = str(meta.get("permalink") or "").strip()
        base = extract_permalink_base(permalink)
        if base:
            permalink_bases.append(base)

        permalink_source = str(meta.get("permalink-source") or "").strip()
        source_base = extract_permalink_source_base(permalink_source)
        if source_base:
            permalink_source_bases.append(source_base)

        img_dir = note_dir / "img"
        if img_dir.is_dir():
            stems.extend(
                path.stem
                for path in img_dir.iterdir()
                if path.is_file() and path.suffix.casefold() in FLAT_ICON_EXTENSIONS
            )

    result.authors = _unique_sorted(authors)
    result.author_emails = _unique_sorted(emails)
    result.licenses = _unique_sorted(licenses)
    result.license_urls = _unique_sorted(license_urls)
    result.categories = sorted(categories, key=str.casefold)
    result.author = consensus_value(authors)
    result.author_email = consensus_value(emails)
    result.license = consensus_value(licenses)
    result.license_url = consensus_value(license_urls)
    result.permalink_base = consensus_value(permalink_bases)
    result.permalink_source_base = consensus_value(permalink_source_bases)
    result.existing_variant_stems = _unique_sorted(stems)
    return result


def sync_family_id_category(family_id: str, category: str) -> str:
    """Return `family_id` with its `__` prefix replaced by `category`."""
    cleaned_id = family_id.strip()
    cleaned_category = category.strip()
    if not cleaned_id or not cleaned_category:
        return cleaned_id
    slug = cleaned_id.split("__", 1)[1] if "__" in cleaned_id else cleaned_id
    if not slug:
        return cleaned_category
    return f"{cleaned_category}__{slug}"


def today_iso_date() -> str:
    """Return today's date in `YYYY-MM-DD` (local calendar via UTC date is fine for tests)."""
    return datetime.now(UTC).date().isoformat()


def _unique_sorted(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return sorted(result, key=str.casefold)
