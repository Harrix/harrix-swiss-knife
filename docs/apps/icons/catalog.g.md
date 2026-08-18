---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CatalogLoadCancelledError`](#%EF%B8%8F-class-catalogloadcancellederror)
- [🏛️ Class `IconCatalog`](#%EF%B8%8F-class-iconcatalog)
  - [⚙️ Method `categories`](#%EF%B8%8F-method-categories)
  - [⚙️ Method `filter_icons`](#%EF%B8%8F-method-filter_icons)
  - [⚙️ Method `folder_prefixes`](#%EF%B8%8F-method-folder_prefixes)
- [🏛️ Class `IconFamily`](#%EF%B8%8F-class-iconfamily)
  - [⚙️ Method `featured_path`](#%EF%B8%8F-method-featured_path)
  - [⚙️ Method `matches`](#%EF%B8%8F-method-matches)
  - [⚙️ Method `note_path`](#%EF%B8%8F-method-note_path)
  - [⚙️ Method `refresh_search_blob`](#%EF%B8%8F-method-refresh_search_blob)
- [🏛️ Class `IconVariant`](#%EF%B8%8F-class-iconvariant)
  - [⚙️ Method `absolute_path`](#%EF%B8%8F-method-absolute_path)
- [🔧 Function `delete_icon_family`](#-function-delete_icon_family)
- [🔧 Function `exclusive_sidebar_filters`](#-function-exclusive_sidebar_filters)
- [🔧 Function `family_in_folder`](#-function-family_in_folder)
- [🔧 Function `family_license_info`](#-function-family_license_info)
- [🔧 Function `folder_disk_path`](#-function-folder_disk_path)
- [🔧 Function `folder_parts`](#-function-folder_parts)
- [🔧 Function `is_note_icons_repo`](#-function-is_note_icons_repo)
- [🔧 Function `is_openable_license_url`](#-function-is_openable_license_url)
- [🔧 Function `iter_icon_note_dirs`](#-function-iter_icon_note_dirs)
- [🔧 Function `load_catalog`](#-function-load_catalog)
- [🔧 Function `open_icons_folder`](#-function-open_icons_folder)
- [🔧 Function `parse_note_frontmatter`](#-function-parse_note_frontmatter)
- [🔧 Function `preferred_sidebar_folder`](#-function-preferred_sidebar_folder)
- [🔧 Function `rebuild_catalog`](#-function-rebuild_catalog)
- [🔧 Function `remove_empty_parents`](#-function-remove_empty_parents)
- [🔧 Function `resolve_icons_root`](#-function-resolve_icons_root)
- [🔧 Function `scan_flat_folder`](#-function-scan_flat_folder)

</details>

## 🏛️ Class `CatalogLoadCancelledError`

```python
class CatalogLoadCancelledError(Exception)
```

Raised when a catalog scan is cancelled by the user.

<details>
<summary>Code:</summary>

```python
class CatalogLoadCancelledError(Exception):
```

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

    def filter_icons(
        self,
        *,
        category: str | None = None,
        folder: str | None = None,
        query: str = "",
    ) -> list[IconFamily]:
        """Filter icons by optional category, folder prefix, and search query."""
        needle = query.strip()
        result: list[IconFamily] = []
        for icon in self.icons:
            if category and category not in icon.categories:
                continue
            if folder and not family_in_folder(icon.folder, folder):
                continue
            if needle and not icon.matches(needle):
                continue
            result.append(icon)
        return result

    def folder_prefixes(self) -> list[str]:
        """Return sorted unique folder prefixes for the sidebar tree.

        Note catalogs omit the family note folder itself. Flat catalogs keep
        every parent directory of icon files.

        """
        prefixes: set[str] = set()
        for icon in self.icons:
            parts = folder_parts(icon.folder)
            if self.kind == "note" and parts:
                parts = parts[:-1]
            for index in range(len(parts)):
                prefixes.add("/".join(parts[: index + 1]))
        return sorted(prefixes, key=str.casefold)
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
def filter_icons(self, *, category: str | None = None, folder: str | None = None, query: str = '') -> list[IconFamily]
```

Filter icons by optional category, folder prefix, and search query.

<details>
<summary>Code:</summary>

```python
def filter_icons(
        self,
        *,
        category: str | None = None,
        folder: str | None = None,
        query: str = "",
    ) -> list[IconFamily]:
        needle = query.strip()
        result: list[IconFamily] = []
        for icon in self.icons:
            if category and category not in icon.categories:
                continue
            if folder and not family_in_folder(icon.folder, folder):
                continue
            if needle and not icon.matches(needle):
                continue
            result.append(icon)
        return result
```

</details>

### ⚙️ Method `folder_prefixes`

```python
def folder_prefixes(self) -> list[str]
```

Return sorted unique folder prefixes for the sidebar tree.

Note catalogs omit the family note folder itself. Flat catalogs keep
every parent directory of icon files.

<details>
<summary>Code:</summary>

```python
def folder_prefixes(self) -> list[str]:
        prefixes: set[str] = set()
        for icon in self.icons:
            parts = folder_parts(icon.folder)
            if self.kind == "note" and parts:
                parts = parts[:-1]
            for index in range(len(parts)):
                prefixes.add("/".join(parts[: index + 1]))
        return sorted(prefixes, key=str.casefold)
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
    license: str = ""
    license_url: str = ""
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

    def refresh_search_blob(self) -> None:
        """Rebuild `search_blob` from current ID, title, categories, and tags."""
        self.search_blob = _build_search_blob(self)
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

### ⚙️ Method `refresh_search_blob`

```python
def refresh_search_blob(self) -> None
```

Rebuild `search_blob` from current ID, title, categories, and tags.

<details>
<summary>Code:</summary>

```python
def refresh_search_blob(self) -> None:
        self.search_blob = _build_search_blob(self)
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

## 🔧 Function `exclusive_sidebar_filters`

```python
def exclusive_sidebar_filters(*, source: Literal['folder', 'category'] | None, folder: str | None, category: str | None) -> tuple[str | None, str | None]
```

Return `(folder, category)` so only the last clicked sidebar is active.

<details>
<summary>Code:</summary>

```python
def exclusive_sidebar_filters(
    *,
    source: Literal["folder", "category"] | None,
    folder: str | None,
    category: str | None,
) -> tuple[str | None, str | None]:
    if source == "folder":
        return folder, None
    if source == "category":
        return None, category
    return None, None
```

</details>

## 🔧 Function `family_in_folder`

```python
def family_in_folder(family_folder: str, selected: str) -> bool
```

Return whether `family_folder` is `selected` or nested under it.

<details>
<summary>Code:</summary>

```python
def family_in_folder(family_folder: str, selected: str) -> bool:
    family = "/".join(folder_parts(family_folder))
    prefix = "/".join(folder_parts(selected))
    if not prefix:
        return True
    return family == prefix or family.startswith(f"{prefix}/")
```

</details>

## 🔧 Function `family_license_info`

```python
def family_license_info(family: IconFamily, repo_root: Path | None = None) -> tuple[str, str]
```

Return `(license, license_url)` from the catalog, falling back to the note.

<details>
<summary>Code:</summary>

```python
def family_license_info(family: IconFamily, repo_root: Path | None = None) -> tuple[str, str]:
    name = family.license.strip()
    url = family.license_url.strip()
    if name and url:
        return name, url
    if repo_root is None:
        return name, url
    note = family.note_path(repo_root)
    if note is None:
        return name, url
    try:
        meta = parse_note_frontmatter(note.read_text(encoding="utf-8"))
    except OSError:
        return name, url
    note_name = str(meta.get("license") or "").strip()
    note_url = str(meta.get("license-url") or "").strip()
    return name or note_name, url or note_url
```

</details>

## 🔧 Function `folder_disk_path`

```python
def folder_disk_path(repo_root: Path, prefix: str) -> Path
```

Return the on-disk folder for a sidebar prefix (`""` is the repo root).

<details>
<summary>Code:</summary>

```python
def folder_disk_path(repo_root: Path, prefix: str) -> Path:
    parts = folder_parts(prefix)
    if not parts:
        return repo_root
    return repo_root.joinpath(*parts)
```

</details>

## 🔧 Function `folder_parts`

```python
def folder_parts(folder: str) -> list[str]
```

Split a repo-relative folder into non-empty path parts.

<details>
<summary>Code:</summary>

```python
def folder_parts(folder: str) -> list[str]:
    return [part for part in folder.replace("\\", "/").split("/") if part and part != "."]
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

## 🔧 Function `is_openable_license_url`

```python
def is_openable_license_url(url: str) -> bool
```

Return whether `url` can be opened as an http(s) license page.

<details>
<summary>Code:</summary>

```python
def is_openable_license_url(url: str) -> bool:
    cleaned = url.strip()
    lower = cleaned.casefold()
    return lower.startswith(("http://", "https://"))
```

</details>

## 🔧 Function `iter_icon_note_dirs`

```python
def iter_icon_note_dirs(icons_dir: Path) -> list[Path]
```

Return note folders under `icons/` (public wrapper).

<details>
<summary>Code:</summary>

```python
def iter_icon_note_dirs(icons_dir: Path) -> list[Path]:
    return _iter_icon_note_dirs(icons_dir)
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
def open_icons_folder(path: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog
```

Open a note-folder repo or a flat icon dump (SVG/AI/PDF/EPS).

Does not write `catalog.json` into flat dumps. For AI-style repos that keep
files under `src/`, that subdirectory is used when the chosen root is empty.

Note repos rebuild `catalog.json` when it is missing or older than any icon
note (so category/tag edits show up without a manual refresh).

<details>
<summary>Code:</summary>

```python
def open_icons_folder(path: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog:
    root = resolve_icons_root(path, should_cancel=should_cancel)
    _raise_if_cancelled(should_cancel)
    if is_note_icons_repo(root):
        catalog_path = root / "catalog.json"
        icons_dir = root / "icons"
        if icons_dir.is_dir() and (not catalog_path.is_file() or _catalog_is_stale(root, catalog_path)):
            return rebuild_catalog(root, should_cancel=should_cancel)
        return load_catalog(root)
    return scan_flat_folder(root, should_cancel=should_cancel)
```

</details>

## 🔧 Function `parse_note_frontmatter`

```python
def parse_note_frontmatter(text: str) -> dict[str, Any]
```

Parse YAML-like frontmatter from a note (public wrapper).

<details>
<summary>Code:</summary>

```python
def parse_note_frontmatter(text: str) -> dict[str, Any]:
    return _parse_frontmatter(text)
```

</details>

## 🔧 Function `preferred_sidebar_folder`

```python
def preferred_sidebar_folder(catalog: IconCatalog, family_id: str | None) -> str
```

Return a Folders-tree prefix that contains `family_id`, or `""`.

<details>
<summary>Code:</summary>

```python
def preferred_sidebar_folder(catalog: IconCatalog, family_id: str | None) -> str:
    if not family_id:
        return ""
    family = next((item for item in catalog.icons if item.id == family_id), None)
    if family is None:
        return ""
    prefixes = set(catalog.folder_prefixes())
    parts = folder_parts(family.folder)
    for index in range(len(parts), 0, -1):
        candidate = "/".join(parts[:index])
        if candidate in prefixes:
            return candidate
    return ""
```

</details>

## 🔧 Function `rebuild_catalog`

```python
def rebuild_catalog(repo_root: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog
```

Rebuild `catalog.json` from `icons/` note-folders (flat or nested by category) and reload it.

<details>
<summary>Code:</summary>

```python
def rebuild_catalog(repo_root: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog:
    icons_dir = repo_root / "icons"
    if not icons_dir.is_dir():
        msg = f"icons/ not found in {repo_root}"
        raise FileNotFoundError(msg)

    icons_payload: list[dict[str, Any]] = []
    for note_dir in _iter_icon_note_dirs(icons_dir):
        _raise_if_cancelled(should_cancel)
        family_id = note_dir.name
        md_path = note_dir / f"{family_id}.md"
        text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
        meta = _parse_frontmatter(text) if text else {}
        categories = list(meta.get("categories") or []) or [_category_from_id(family_id)]
        title = resolve_note_title(text, file_stem=family_id)
        tags = list(meta.get("tags") or [])
        trademark = bool(meta.get("trademark"))
        icon_date = str(meta.get("date") or "").strip()
        license_name = str(meta.get("license") or "").strip()
        license_url = str(meta.get("license-url") or "").strip()
        featured_path = _find_featured_image(note_dir)
        featured_rel = featured_path.name if featured_path is not None else ""
        featured_hash = _file_sha256(featured_path) if featured_path is not None else ""
        variants: list[dict[str, str]] = []
        img_dir = note_dir / "img"
        if img_dir.is_dir():
            variants.extend(
                {
                    "file": f"img/{path.name}",
                    "name": path.stem,
                    "hash": _file_sha256(path),
                }
                for path in sorted(_iter_vector_files(img_dir), key=lambda item: item.name.casefold())
            )
        icons_payload.append(
            {
                "id": family_id,
                "title": title,
                "date": icon_date,
                "license": license_name,
                "license-url": license_url,
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

## 🔧 Function `remove_empty_parents`

```python
def remove_empty_parents(start: Path, stop: Path) -> None
```

Remove empty directories from `start` up to, but not including, `stop`.

<details>
<summary>Code:</summary>

```python
def remove_empty_parents(start: Path, stop: Path) -> None:
    current = start.resolve()
    limit = stop.resolve()
    while current.is_dir() and current != limit and limit in current.parents:
        try:
            if any(current.iterdir()):
                return
            parent = current.parent
            current.rmdir()
            current = parent
        except OSError:
            return
```

</details>

## 🔧 Function `resolve_icons_root`

```python
def resolve_icons_root(path: Path, *, should_cancel: CancelCheck | None = None) -> Path
```

Normalize a user-chosen folder to the directory that actually holds icons.

<details>
<summary>Code:</summary>

```python
def resolve_icons_root(path: Path, *, should_cancel: CancelCheck | None = None) -> Path:
    root = path.expanduser().resolve()
    if not root.is_dir():
        msg = f"Folder not found: {root}"
        raise FileNotFoundError(msg)
    if is_note_icons_repo(root):
        return root
    if _has_flat_icon_file(root, should_cancel=should_cancel):
        return root
    src = root / "src"
    if src.is_dir() and _has_flat_icon_file(src, should_cancel=should_cancel):
        return src
    return root
```

</details>

## 🔧 Function `scan_flat_folder`

```python
def scan_flat_folder(root: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog
```

Build an in-memory catalog from loose icon files (no `catalog.json` write).

<details>
<summary>Code:</summary>

```python
def scan_flat_folder(root: Path, *, should_cancel: CancelCheck | None = None) -> IconCatalog:
    files = _iter_flat_icon_files(root, should_cancel=should_cancel)
    if not files:
        msg = f"No SVG/AI/PDF/EPS icons found in {root}"
        raise FileNotFoundError(msg)

    groups: dict[str, list[Path]] = {}
    for path in files:
        _raise_if_cancelled(should_cancel)
        key = _flat_family_id(path, root)
        groups.setdefault(key, []).append(path)

    icons: list[IconFamily] = []
    for family_id in sorted(groups, key=str.casefold):
        _raise_if_cancelled(should_cancel)
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
                    hash=_file_fingerprint(member),
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
            featured_hash=_file_fingerprint(featured_path),
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
