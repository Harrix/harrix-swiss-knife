---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `add_vector_meta.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `NoteMeta`](#%EF%B8%8F-class-notemeta)
- [🏛️ Class `RepoMetaDefaults`](#%EF%B8%8F-class-repometadefaults)
- [🔧 Function `consensus_value`](#-function-consensus_value)
- [🔧 Function `defaults_from_source_stem`](#-function-defaults_from_source_stem)
- [🔧 Function `extra_categories_for_family`](#-function-extra_categories_for_family)
- [🔧 Function `extract_permalink_base`](#-function-extract_permalink_base)
- [🔧 Function `extract_permalink_source_base`](#-function-extract_permalink_source_base)
- [🔧 Function `join_permalink`](#-function-join_permalink)
- [🔧 Function `note_dir_for_meta`](#-function-note_dir_for_meta)
- [🔧 Function `note_meta_from_existing`](#-function-note_meta_from_existing)
- [🔧 Function `note_meta_with_category`](#-function-note_meta_with_category)
- [🔧 Function `permalink_suffixes`](#-function-permalink_suffixes)
- [🔧 Function `scan_repo_meta_defaults`](#-function-scan_repo_meta_defaults)
- [🔧 Function `sync_family_id_category`](#-function-sync_family_id_category)
- [🔧 Function `today_iso_date`](#-function-today_iso_date)

</details>

## 🏛️ Class `NoteMeta`

```python
class NoteMeta
```

User-confirmed metadata for a new icon note.

<details>
<summary>Code:</summary>

```python
class NoteMeta:

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
```

</details>

## 🏛️ Class `RepoMetaDefaults`

```python
class RepoMetaDefaults
```

Consensus defaults extracted from existing icon notes.

<details>
<summary>Code:</summary>

```python
class RepoMetaDefaults:

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
```

</details>

## 🔧 Function `consensus_value`

```python
def consensus_value(values: list[str]) -> str
```

Return the only distinct value, otherwise empty.

<details>
<summary>Code:</summary>

```python
def consensus_value(values: list[str]) -> str:
    unique = sorted({item.strip() for item in values if item.strip()}, key=str.casefold)
    if len(unique) == 1:
        return unique[0]
    return ""
```

</details>

## 🔧 Function `defaults_from_source_stem`

```python
def defaults_from_source_stem(stem: str) -> tuple[str, str, str]
```

Return `(family_id, title, category)` derived from a source filename stem.

<details>
<summary>Code:</summary>

```python
def defaults_from_source_stem(stem: str) -> tuple[str, str, str]:
    family_id = family_id_from_stem(stem)
    title = title_from_family_id(family_id)
    category = category_from_family_id(family_id) if "__" in family_id else ""
    return family_id, title, category
```

</details>

## 🔧 Function `extra_categories_for_family`

```python
def extra_categories_for_family(categories: list[str], family_id: str) -> list[str]
```

Return YAML categories that are not the family-id folder prefix.

<details>
<summary>Code:</summary>

```python
def extra_categories_for_family(categories: list[str], family_id: str) -> list[str]:
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
```

</details>

## 🔧 Function `extract_permalink_base`

```python
def extract_permalink_base(permalink: str) -> str | None
```

Strip `/{category}/{family_id}` from a site permalink.

<details>
<summary>Code:</summary>

```python
def extract_permalink_base(permalink: str) -> str | None:
    text = permalink.strip().rstrip("/")
    if not text:
        return None
    match = _PERMALINK_SUFFIX_RE.search(text)
    if match is None:
        return None
    base = text[: match.start()] + "/"
    return base if base.startswith("http") else None
```

</details>

## 🔧 Function `extract_permalink_source_base`

```python
def extract_permalink_source_base(permalink_source: str) -> str | None
```

Strip `/{category}/{family_id}/{family_id}.md` from a GitHub permalink.

<details>
<summary>Code:</summary>

```python
def extract_permalink_source_base(permalink_source: str) -> str | None:
    text = permalink_source.strip()
    if not text:
        return None
    match = _PERMALINK_SOURCE_SUFFIX_RE.search(text)
    if match is None:
        return None
    base = text[: match.start()] + "/"
    return base if base.startswith("http") else None
```

</details>

## 🔧 Function `join_permalink`

```python
def join_permalink(base: str, suffix: str) -> str
```

Join permalink base and suffix without duplicating slashes.

<details>
<summary>Code:</summary>

```python
def join_permalink(base: str, suffix: str) -> str:
    left = base.strip()
    right = suffix.strip().lstrip("/")
    if not left:
        return right
    if not right:
        return left.rstrip("/") + ("/" if left.endswith("/") else "")
    return left.rstrip("/") + "/" + right
```

</details>

## 🔧 Function `note_dir_for_meta`

```python
def note_dir_for_meta(repo_root: Path, *, family_id: str, category: str) -> Path
```

Return destination note folder for dialog metadata.

<details>
<summary>Code:</summary>

```python
def note_dir_for_meta(repo_root: Path, *, family_id: str, category: str) -> Path:
    icons_dir = Path(repo_root) / "icons"
    cleaned_category = category.strip()
    if cleaned_category:
        return icons_dir / cleaned_category / family_id
    return icons_dir / family_id
```

</details>

## 🔧 Function `note_meta_from_existing`

```python
def note_meta_from_existing(*, family_id: str, title: str, categories: list[str], tags: list[str], featured_name: str, frontmatter: dict[str, Any]) -> NoteMeta
```

Build dialog metadata from an existing note family and frontmatter.

<details>
<summary>Code:</summary>

```python
def note_meta_from_existing(
    *,
    family_id: str,
    title: str,
    categories: list[str],
    tags: list[str],
    featured_name: str,
    frontmatter: dict[str, Any],
) -> NoteMeta:
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
```

</details>

## 🔧 Function `note_meta_with_category`

```python
def note_meta_with_category(meta: NoteMeta, category: str) -> NoteMeta
```

Return metadata with `category`, synced family ID, and permalink suffixes.

<details>
<summary>Code:</summary>

```python
def note_meta_with_category(meta: NoteMeta, category: str) -> NoteMeta:
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
```

</details>

## 🔧 Function `permalink_suffixes`

```python
def permalink_suffixes(category: str, family_id: str) -> tuple[str, str]
```

Return site and source path suffixes for `category` + `family_id`.

<details>
<summary>Code:</summary>

```python
def permalink_suffixes(category: str, family_id: str) -> tuple[str, str]:
    cleaned_id = family_id.strip()
    cleaned_category = category.strip()
    if not cleaned_id or not cleaned_category:
        return "", ""
    site = f"{cleaned_category}/{cleaned_id}"
    source = f"{cleaned_category}/{cleaned_id}/{cleaned_id}.md"
    return site, source
```

</details>

## 🔧 Function `scan_repo_meta_defaults`

```python
def scan_repo_meta_defaults(repo_root: Path) -> RepoMetaDefaults
```

Scan note frontmatter and build consensus defaults for the add dialog.

<details>
<summary>Code:</summary>

```python
def scan_repo_meta_defaults(repo_root: Path) -> RepoMetaDefaults:
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
```

</details>

## 🔧 Function `sync_family_id_category`

```python
def sync_family_id_category(family_id: str, category: str) -> str
```

Return `family_id` with its `__` prefix replaced by `category`.

<details>
<summary>Code:</summary>

```python
def sync_family_id_category(family_id: str, category: str) -> str:
    cleaned_id = family_id.strip()
    cleaned_category = category.strip()
    if not cleaned_id or not cleaned_category:
        return cleaned_id
    slug = cleaned_id.split("__", 1)[1] if "__" in cleaned_id else cleaned_id
    if not slug:
        return cleaned_category
    return f"{cleaned_category}__{slug}"
```

</details>

## 🔧 Function `today_iso_date`

```python
def today_iso_date() -> str
```

Return today's date in `YYYY-MM-DD` (local calendar via UTC date is fine for tests).

<details>
<summary>Code:</summary>

```python
def today_iso_date() -> str:
    return datetime.now(UTC).date().isoformat()
```

</details>
