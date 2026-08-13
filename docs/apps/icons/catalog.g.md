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
  - [⚙️ Method `note_path`](#%EF%B8%8F-method-note_path)
- [🏛️ Class `IconVariant`](#%EF%B8%8F-class-iconvariant)
  - [⚙️ Method `absolute_path`](#%EF%B8%8F-method-absolute_path)
- [🔧 Function `delete_icon_family`](#-function-delete_icon_family)
- [🔧 Function `is_note_icons_repo`](#-function-is_note_icons_repo)
- [🔧 Function `load_catalog`](#-function-load_catalog)
- [🔧 Function `open_icons_folder`](#-function-open_icons_folder)
- [🔧 Function `rebuild_catalog`](#-function-rebuild_catalog)
- [🔧 Function `resolve_icons_root`](#-function-resolve_icons_root)
- [🔧 Function `scan_flat_folder`](#-function-scan_flat_folder)

</details>

## 🏛️ Class `IconCatalog`

```python
class IconCatalog
```

In-memory icon catalog loaded from `catalog.json` or a flat folder scan.

<details>
<summary>Code:</summary>

```python
class IconCatalog:

    version: int
    generated_at: str
    icons: list[IconFamily]
    repo_root: Path
    kind: CatalogKind = "note"

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

One searchable icon family (note-folder or flat-file group).

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
    date: str = ""
    trademark: bool = False
    variants: list[IconVariant] = field(default_factory=list)
    search_blob: str = ""

    def featured_path(self, repo_root: Path) -> Path | None:
        """Return absolute path to featured icon file when present."""
        if not self.featured:
            return None
        path = _join_repo_path(repo_root, self.folder, self.featured)
        return path if path.is_file() else None

    def matches(self, query: str) -> bool:
        """Return whether the family matches query (case/layout tolerant)."""
        return text_matches_autocomplete(self.search_blob, query)

    def note_path(self, repo_root: Path) -> Path | None:
        """Return absolute path to the family Markdown note when present."""
        path = _join_repo_path(repo_root, self.folder, f"{self.id}.md")
        return path if path.is_file() else None
```

</details>

### ⚙️ Method `featured_path`

```python
def featured_path(self, repo_root: Path) -> Path | None
```

Return absolute path to featured icon file when present.

<details>
<summary>Code:</summary>

```python
def featured_path(self, repo_root: Path) -> Path | None:
        if not self.featured:
            return None
        path = _join_repo_path(repo_root, self.folder, self.featured)
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

### ⚙️ Method `note_path`

```python
def note_path(self, repo_root: Path) -> Path | None
```

Return absolute path to the family Markdown note when present.

<details>
<summary>Code:</summary>

```python
def note_path(self, repo_root: Path) -> Path | None:
        path = _join_repo_path(repo_root, self.folder, f"{self.id}.md")
        return path if path.is_file() else None
```

</details>

## 🏛️ Class `IconVariant`

```python
class IconVariant
```

One icon file belonging to an icon family.

<details>
<summary>Code:</summary>

```python
class IconVariant:

    file: str
    name: str
    hash: str

    def absolute_path(self, repo_root: Path, folder: str) -> Path:
        """Resolve the variant path under the icons repo root."""
        return _join_repo_path(repo_root, folder, self.file)
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
        return _join_repo_path(repo_root, folder, self.file)
```

</details>

## 🔧 Function `delete_icon_family`

```python
def delete_icon_family(family: IconFamily, repo_root: Path, *, kind: CatalogKind) -> None
```

Permanently delete an icon family from disk.

Note-folder repos remove the family directory under `icons/` (flat
`icons/{id}/` or nested `icons/{category}/{id}/`). Empty category folders
are removed afterwards. Flat dumps unlink the featured file and every
variant file that still exists.

<details>
<summary>Code:</summary>

```python
def delete_icon_family(family: IconFamily, repo_root: Path, *, kind: CatalogKind) -> None:
    root = repo_root.expanduser().resolve()
    if kind == "note":
        _delete_note_family(family, root)
        return
    _delete_flat_family(family, root)
```

</details>

## 🔧 Function `is_note_icons_repo`

```python
def is_note_icons_repo(root: Path) -> bool
```

Return whether `root` looks like a Harrix-Vector-Icons note-folder repo.

<details>
<summary>Code:</summary>

```python
def is_note_icons_repo(root: Path) -> bool:
    if (root / "catalog.json").is_file() and (root / "icons").is_dir():
        return True
    icons_dir = root / "icons"
    if not icons_dir.is_dir():
        return False
    return bool(_iter_icon_note_dirs(icons_dir))
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
        kind="note",
    )
```

</details>

## 🔧 Function `open_icons_folder`

```python
def open_icons_folder(path: Path) -> IconCatalog
```

Open a note-folder repo or a flat icon dump (SVG/AI/PDF/EPS).

Does not write `catalog.json` into flat dumps. For AI-style repos that keep
files under `src/`, that subdirectory is used when the chosen root is empty.

<details>
<summary>Code:</summary>

```python
def open_icons_folder(path: Path) -> IconCatalog:
    root = resolve_icons_root(path)
    if is_note_icons_repo(root):
        if not (root / "catalog.json").is_file() and (root / "icons").is_dir():
            return rebuild_catalog(root)
        return load_catalog(root)
    return scan_flat_folder(root)
```

</details>

## 🔧 Function `rebuild_catalog`

```python
def rebuild_catalog(repo_root: Path) -> IconCatalog
```

Rebuild `catalog.json` from `icons/` note-folders (flat or nested by category) and reload it.

<details>
<summary>Code:</summary>

```python
def rebuild_catalog(repo_root: Path) -> IconCatalog:
    icons_dir = repo_root / "icons"
    if not icons_dir.is_dir():
        msg = f"icons/ not found in {repo_root}"
        raise FileNotFoundError(msg)

    icons_payload: list[dict[str, Any]] = []
    for note_dir in _iter_icon_note_dirs(icons_dir):
        family_id = note_dir.name
        md_path = note_dir / f"{family_id}.md"
        text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
        meta = _parse_frontmatter(text) if text else {}
        categories = list(meta.get("categories") or []) or [_category_from_id(family_id)]
        title = resolve_note_title(text, file_stem=family_id)
        tags = list(meta.get("tags") or [])
        trademark = bool(meta.get("trademark"))
        icon_date = str(meta.get("date") or "").strip()
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
                "date": icon_date,
                "trademark": trademark,
                "categories": categories,
                "tags": tags,
                "folder": _relative_to_root(note_dir, repo_root),
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
    catalog = load_catalog(repo_root)
    catalog.kind = "note"
    return catalog
```

</details>

## 🔧 Function `resolve_icons_root`

```python
def resolve_icons_root(path: Path) -> Path
```

Normalize a user-chosen folder to the directory that actually holds icons.

<details>
<summary>Code:</summary>

```python
def resolve_icons_root(path: Path) -> Path:
    root = path.expanduser().resolve()
    if not root.is_dir():
        msg = f"Folder not found: {root}"
        raise FileNotFoundError(msg)
    if is_note_icons_repo(root):
        return root
    if _count_flat_icon_files(root) > 0:
        return root
    src = root / "src"
    if src.is_dir() and _count_flat_icon_files(src) > 0:
        return src
    return root
```

</details>

## 🔧 Function `scan_flat_folder`

```python
def scan_flat_folder(root: Path) -> IconCatalog
```

Build an in-memory catalog from loose icon files (no `catalog.json` write).

<details>
<summary>Code:</summary>

```python
def scan_flat_folder(root: Path) -> IconCatalog:
    files = _iter_flat_icon_files(root)
    if not files:
        msg = f"No SVG/AI/PDF/EPS icons found in {root}"
        raise FileNotFoundError(msg)

    groups: dict[str, list[Path]] = {}
    for path in files:
        key = _flat_family_id(path, root)
        groups.setdefault(key, []).append(path)

    icons: list[IconFamily] = []
    for family_id in sorted(groups, key=str.casefold):
        members = sorted(groups[family_id], key=lambda item: item.as_posix().casefold())
        featured_path = _pick_featured_file(members)
        rel_featured = _relative_to_root(featured_path, root)
        parent = Path(rel_featured).parent
        folder = "" if str(parent) in {"", "."} else str(parent).replace("\\", "/")
        featured_rel = Path(rel_featured).name
        variants: list[IconVariant] = []
        for member in members:
            rel = _relative_to_root(member, root)
            variant_file = str(Path(rel).relative_to(folder)).replace("\\", "/") if folder else Path(rel).name
            variants.append(
                IconVariant(
                    file=variant_file,
                    name=member.stem,
                    hash=_file_sha256(member),
                ),
            )
        stem = Path(family_id).name
        family = IconFamily(
            id=family_id,
            title=title_from_id(stem),
            categories=[_flat_category(folder, stem)],
            tags=[],
            folder=folder,
            featured=featured_rel,
            featured_hash=_file_sha256(featured_path),
            variants=variants,
        )
        family.search_blob = _build_search_blob(family)
        icons.append(family)

    return IconCatalog(
        version=1,
        generated_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        icons=icons,
        repo_root=root,
        kind="flat",
    )
```

</details>
