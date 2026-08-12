---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IconCatalog`](#%EF%B8%8F-class-iconcatalog)
  - [⚙️ Method `categories`](#%EF%B8%8F-method-categories)
  - [⚙️ Method `filter_icons`](#%EF%B8%8F-method-filter_icons)
- [🏛️ Class `IconFamily`](#%EF%B8%8F-class-iconfamily)
  - [⚙️ Method `featured_path`](#%EF%B8%8F-method-featured_path)
  - [⚙️ Method `matches`](#%EF%B8%8F-method-matches)
- [🏛️ Class `IconVariant`](#%EF%B8%8F-class-iconvariant)
  - [⚙️ Method `absolute_path`](#%EF%B8%8F-method-absolute_path)
- [🔧 Function `load_catalog`](#-function-load_catalog)
- [🔧 Function `rebuild_catalog`](#-function-rebuild_catalog)

</details>

## 🏛️ Class `IconCatalog`

```python
class IconCatalog
```

In-memory icon catalog loaded from `catalog.json`.

<details>
<summary>Code:</summary>

```python
class IconCatalog:

    version: int
    generated_at: str
    icons: list[IconFamily]
    repo_root: Path

    def categories(self) -> list[str]:
        """Return sorted unique category names."""
        names: set[str] = set()
        for icon in self.icons:
            names.update(icon.categories)
        return sorted(names, key=str.casefold)

    def filter_icons(self, *, category: str | None = None, query: str = "") -> list[IconFamily]:
        """Filter icons by optional category and search query."""
        needle = query.strip()
        result: list[IconFamily] = []
        for icon in self.icons:
            if category and category not in icon.categories:
                continue
            if needle and not icon.matches(needle):
                continue
            result.append(icon)
        return result
```

</details>

### ⚙️ Method `categories`

```python
def categories(self) -> list[str]
```

Return sorted unique category names.

<details>
<summary>Code:</summary>

```python
def categories(self) -> list[str]:
        names: set[str] = set()
        for icon in self.icons:
            names.update(icon.categories)
        return sorted(names, key=str.casefold)
```

</details>

### ⚙️ Method `filter_icons`

```python
def filter_icons(self, *, category: str | None = None, query: str = '') -> list[IconFamily]
```

Filter icons by optional category and search query.

<details>
<summary>Code:</summary>

```python
def filter_icons(self, *, category: str | None = None, query: str = "") -> list[IconFamily]:
        needle = query.strip()
        result: list[IconFamily] = []
        for icon in self.icons:
            if category and category not in icon.categories:
                continue
            if needle and not icon.matches(needle):
                continue
            result.append(icon)
        return result
```

</details>

## 🏛️ Class `IconFamily`

```python
class IconFamily
```

One searchable icon family (note-folder).

<details>
<summary>Code:</summary>

```python
class IconFamily:

    id: str
    title: str
    categories: list[str]
    tags: list[str]
    folder: str
    featured: str
    featured_hash: str
    variants: list[IconVariant] = field(default_factory=list)
    search_blob: str = ""

    def featured_path(self, repo_root: Path) -> Path | None:
        """Return absolute path to featured SVG when present."""
        if not self.featured:
            return None
        path = repo_root / self.folder / self.featured
        return path if path.is_file() else None

    def matches(self, query: str) -> bool:
        """Return whether the family matches query (case/layout tolerant)."""
        return text_matches_autocomplete(self.search_blob, query)
```

</details>

### ⚙️ Method `featured_path`

```python
def featured_path(self, repo_root: Path) -> Path | None
```

Return absolute path to featured SVG when present.

<details>
<summary>Code:</summary>

```python
def featured_path(self, repo_root: Path) -> Path | None:
        if not self.featured:
            return None
        path = repo_root / self.folder / self.featured
        return path if path.is_file() else None
```

</details>

### ⚙️ Method `matches`

```python
def matches(self, query: str) -> bool
```

Return whether the family matches query (case/layout tolerant).

<details>
<summary>Code:</summary>

```python
def matches(self, query: str) -> bool:
        return text_matches_autocomplete(self.search_blob, query)
```

</details>

## 🏛️ Class `IconVariant`

```python
class IconVariant
```

One SVG file belonging to an icon family.

<details>
<summary>Code:</summary>

```python
class IconVariant:

    file: str
    name: str
    hash: str

    def absolute_path(self, repo_root: Path, folder: str) -> Path:
        """Resolve the variant path under the icons repo root."""
        return repo_root / folder / self.file
```

</details>

### ⚙️ Method `absolute_path`

```python
def absolute_path(self, repo_root: Path, folder: str) -> Path
```

Resolve the variant path under the icons repo root.

<details>
<summary>Code:</summary>

```python
def absolute_path(self, repo_root: Path, folder: str) -> Path:
        return repo_root / folder / self.file
```

</details>

## 🔧 Function `load_catalog`

```python
def load_catalog(repo_root: Path) -> IconCatalog
```

Load `catalog.json` from an icons repository root.

<details>
<summary>Code:</summary>

```python
def load_catalog(repo_root: Path) -> IconCatalog:
    path = repo_root / "catalog.json"
    if not path.is_file():
        msg = f"catalog.json not found in {repo_root}"
        raise FileNotFoundError(msg)
    raw = json.loads(path.read_text(encoding="utf-8"))
    icons = [_family_from_dict(item) for item in raw.get("icons") or [] if isinstance(item, dict)]
    return IconCatalog(
        version=int(raw.get("version") or 1),
        generated_at=str(raw.get("generated_at") or ""),
        icons=icons,
        repo_root=repo_root,
    )
```

</details>

## 🔧 Function `rebuild_catalog`

```python
def rebuild_catalog(repo_root: Path) -> IconCatalog
```

Rebuild `catalog.json` from `icons/` note-folders and reload it.

<details>
<summary>Code:</summary>

```python
def rebuild_catalog(repo_root: Path) -> IconCatalog:
    icons_dir = repo_root / "icons"
    if not icons_dir.is_dir():
        msg = f"icons/ not found in {repo_root}"
        raise FileNotFoundError(msg)

    icons_payload: list[dict[str, Any]] = []
    for note_dir in sorted(p for p in icons_dir.iterdir() if p.is_dir()):
        family_id = note_dir.name
        md_path = note_dir / f"{family_id}.md"
        meta = _parse_frontmatter(md_path) if md_path.is_file() else {}
        categories = list(meta.get("categories") or []) or [_category_from_id(family_id)]
        title = str(meta.get("title") or _title_from_id(family_id))
        tags = list(meta.get("tags") or [])
        featured = note_dir / "featured-image.svg"
        featured_rel = "featured-image.svg" if featured.is_file() else ""
        featured_hash = _file_sha256(featured) if featured.is_file() else ""
        variants: list[dict[str, str]] = []
        img_dir = note_dir / "img"
        if img_dir.is_dir():
            variants.extend(
                {
                    "file": f"img/{svg.name}",
                    "name": svg.stem,
                    "hash": _file_sha256(svg),
                }
                for svg in sorted(img_dir.glob("*.svg"))
            )
        icons_payload.append(
            {
                "id": family_id,
                "title": title,
                "categories": categories,
                "tags": tags,
                "folder": f"icons/{family_id}",
                "featured": featured_rel,
                "featured_hash": featured_hash,
                "variants": variants,
            },
        )

    catalog_data = {
        "version": 1,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "icons": icons_payload,
    }
    out = repo_root / "catalog.json"
    out.write_text(json.dumps(catalog_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return load_catalog(repo_root)
```

</details>
