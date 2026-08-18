"""Catalog models and loaders for the Vector Icons browser."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from harrix_pylib.note_meta import resolve_note_title, title_from_id

from harrix_swiss_knife.keyboard_layout_search import text_matches_autocomplete

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_LIST_RE = re.compile(r"^\[\s*(.*?)\s*\]$")
_VARIANT_TOKEN_RE = re.compile(
    r"_(?:white|black|gray|grey|line-[a-z0-9]+)(?=(?:_\d+)?$)",
    re.IGNORECASE,
)

CatalogKind = Literal["note", "flat"]

FLAT_ICON_EXTENSIONS: frozenset[str] = frozenset({".svg", ".ai", ".pdf", ".eps"})
_SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv"},
)
_NOTE_ASSET_DIR_NAMES: frozenset[str] = frozenset({"img", "files"})


@dataclass(slots=True)
class IconCatalog:
    """In-memory icon catalog loaded from `catalog.json` or a flat folder scan."""

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


@dataclass(slots=True)
class IconFamily:
    """One searchable icon family (note-folder or flat-file group)."""

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

    def refresh_search_blob(self) -> None:
        """Rebuild `search_blob` from current ID, title, categories, and tags."""
        self.search_blob = _build_search_blob(self)


@dataclass(frozen=True, slots=True)
class IconVariant:
    """One icon file belonging to an icon family."""

    file: str
    name: str
    hash: str

    def absolute_path(self, repo_root: Path, folder: str) -> Path:
        """Resolve the variant path under the icons repo root."""
        return _join_repo_path(repo_root, folder, self.file)


def delete_icon_family(family: IconFamily, repo_root: Path, *, kind: CatalogKind) -> None:
    """Permanently delete an icon family from disk.

    Note-folder repos remove the family directory under `icons/` (flat
    `icons/{id}/` or nested `icons/{category}/{id}/`). Empty category folders
    are removed afterwards. Flat dumps unlink the featured file and every
    variant file that still exists.

    """
    root = repo_root.expanduser().resolve()
    if kind == "note":
        _delete_note_family(family, root)
        return
    _delete_flat_family(family, root)


def is_note_icons_repo(root: Path) -> bool:
    """Return whether `root` looks like a Harrix-Vector-Icons note-folder repo."""
    if (root / "catalog.json").is_file() and (root / "icons").is_dir():
        return True
    icons_dir = root / "icons"
    if not icons_dir.is_dir():
        return False
    return bool(_iter_icon_note_dirs(icons_dir))


def iter_icon_note_dirs(icons_dir: Path) -> list[Path]:
    """Return note folders under `icons/` (public wrapper)."""
    return _iter_icon_note_dirs(icons_dir)


def load_catalog(repo_root: Path) -> IconCatalog:
    """Load `catalog.json` from an icons repository root."""
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


def open_icons_folder(path: Path) -> IconCatalog:
    """Open a note-folder repo or a flat icon dump (SVG/AI/PDF/EPS).

    Does not write `catalog.json` into flat dumps. For AI-style repos that keep
    files under `src/`, that subdirectory is used when the chosen root is empty.

    Note repos rebuild `catalog.json` when it is missing or older than any icon
    note (so category/tag edits show up without a manual refresh).

    """
    root = resolve_icons_root(path)
    if is_note_icons_repo(root):
        catalog_path = root / "catalog.json"
        icons_dir = root / "icons"
        if icons_dir.is_dir() and (not catalog_path.is_file() or _catalog_is_stale(root, catalog_path)):
            return rebuild_catalog(root)
        return load_catalog(root)
    return scan_flat_folder(root)


def parse_note_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML-like frontmatter from a note (public wrapper)."""
    return _parse_frontmatter(text)


def rebuild_catalog(repo_root: Path) -> IconCatalog:
    """Rebuild `catalog.json` from `icons/` note-folders (flat or nested by category) and reload it."""
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


def remove_empty_parents(start: Path, stop: Path) -> None:
    """Remove empty directories from `start` up to, but not including, `stop`."""
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


def resolve_icons_root(path: Path) -> Path:
    """Normalize a user-chosen folder to the directory that actually holds icons."""
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


def scan_flat_folder(root: Path) -> IconCatalog:
    """Build an in-memory catalog from loose icon files (no `catalog.json` write)."""
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


def _build_search_blob(family: IconFamily) -> str:
    parts = [family.id, family.title, family.date, *family.categories, *family.tags]
    parts.extend(variant.name for variant in family.variants)
    return " ".join(part for part in parts if part)


def _catalog_is_stale(repo_root: Path, catalog_path: Path) -> bool:
    """Return whether any icon note is newer than `catalog.json`."""
    try:
        catalog_mtime = catalog_path.stat().st_mtime
    except OSError:
        return True
    icons_dir = repo_root / "icons"
    if not icons_dir.is_dir():
        return False
    for note_dir in _iter_icon_note_dirs(icons_dir):
        try:
            if note_dir.stat().st_mtime > catalog_mtime:
                return True
        except OSError:
            continue
        md_path = note_dir / f"{note_dir.name}.md"
        try:
            if md_path.is_file() and md_path.stat().st_mtime > catalog_mtime:
                return True
        except OSError:
            continue
    return False


def _category_from_id(family_id: str) -> str:
    return family_id.split("__", 1)[0] if "__" in family_id else family_id


def _count_flat_icon_files(root: Path) -> int:
    return len(_iter_flat_icon_files(root))


def _delete_flat_family(family: IconFamily, root: Path) -> None:
    paths: list[Path] = []
    featured = family.featured_path(root)
    if featured is not None:
        paths.append(featured)
    for variant in family.variants:
        path = variant.absolute_path(root, family.folder)
        if path.is_file():
            paths.append(path)
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        _ensure_path_inside_root(resolved, root)
        seen.add(resolved)
        unique.append(resolved)
    if not unique:
        msg = f"No files to delete for `{family.id}`"
        raise FileNotFoundError(msg)
    for path in unique:
        path.unlink()


def _delete_note_family(family: IconFamily, root: Path) -> None:
    folder = family.folder.strip().replace("\\", "/")
    if not folder or folder in {".", "icons"} or ".." in Path(folder).parts:
        msg = f"Refusing to delete unsafe folder `{family.folder}`"
        raise ValueError(msg)
    note_dir = (root / folder).resolve()
    icons_root = (root / "icons").resolve()
    if not note_dir.is_relative_to(icons_root) or note_dir == icons_root:
        msg = f"Icon folder is outside icons/: {note_dir}"
        raise ValueError(msg)
    if not note_dir.is_dir():
        msg = f"Icon folder not found: {note_dir}"
        raise FileNotFoundError(msg)
    if not _is_icon_note_dir(note_dir):
        msg = f"Refusing to delete non-note folder `{family.folder}`"
        raise ValueError(msg)
    shutil.rmtree(note_dir)
    remove_empty_parents(note_dir.parent, icons_root)


def _ensure_path_inside_root(path: Path, root: Path) -> None:
    if not path.is_relative_to(root) or path == root:
        msg = f"Refusing to delete path outside folder: {path}"
        raise ValueError(msg)


def _family_from_dict(data: dict[str, Any]) -> IconFamily:
    variants = [
        IconVariant(
            file=str(item.get("file", "")),
            name=str(item.get("name", "")),
            hash=str(item.get("hash", "")),
        )
        for item in data.get("variants") or []
        if isinstance(item, dict)
    ]
    family = IconFamily(
        id=str(data.get("id", "")),
        title=str(data.get("title", "")),
        categories=[str(c) for c in (data.get("categories") or [])],
        tags=[str(t) for t in (data.get("tags") or [])],
        folder=str(data.get("folder", "")),
        featured=str(data.get("featured", "")),
        featured_hash=str(data.get("featured_hash", "")),
        date=str(data.get("date") or "").strip(),
        trademark=bool(data.get("trademark", False)),
        variants=variants,
    )
    family.search_blob = _build_search_blob(family)
    return family


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_featured_image(note_dir: Path) -> Path | None:
    """Return the first existing `featured-image` among SVG/AI/PDF/EPS (SVG preferred)."""
    for suffix in (".svg", ".ai", ".pdf", ".eps"):
        candidate = note_dir / f"featured-image{suffix}"
        if candidate.is_file():
            return candidate
    return None


def _flat_category(folder: str, stem: str) -> str:
    if folder:
        return folder.split("/", 1)[0]
    return _category_from_id(stem)


def _flat_family_id(path: Path, root: Path) -> str:
    stem = path.stem
    if path.suffix.casefold() == ".svg":
        stem = _VARIANT_TOKEN_RE.sub("", stem) or path.stem
    rel_parent = str(Path(_relative_to_root(path, root)).parent).replace("\\", "/")
    if rel_parent in {"", "."}:
        return stem
    return f"{rel_parent}/{stem}"


def _is_icon_note_dir(path: Path) -> bool:
    """Return whether `path` is an icon family note-folder."""
    if not path.is_dir():
        return False
    if (path / f"{path.name}.md").is_file() or (path / "img").is_dir():
        return True
    return _find_featured_image(path) is not None


def _iter_flat_icon_files(root: Path) -> list[Path]:
    """Collect supported icon files in `root` and all nested subfolders."""
    result: list[Path] = []
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name.casefold() not in _SKIP_DIR_NAMES:
                    stack.append(entry)
            elif entry.is_file() and entry.suffix.casefold() in FLAT_ICON_EXTENSIONS:
                result.append(entry)
    result.sort(key=lambda item: item.as_posix().casefold())
    return result


def _iter_icon_note_dirs(icons_dir: Path) -> list[Path]:
    """Collect icon note-folders under `icons/`, including category subfolders."""
    result: list[Path] = []
    stack = [icons_dir]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if not entry.is_dir():
                continue
            name = entry.name.casefold()
            if name in _SKIP_DIR_NAMES or name in _NOTE_ASSET_DIR_NAMES:
                continue
            if _is_icon_note_dir(entry):
                result.append(entry)
            else:
                stack.append(entry)
    result.sort(key=lambda item: item.as_posix().casefold())
    return result


def _iter_vector_files(directory: Path) -> list[Path]:
    """Return vector files directly under `directory`."""
    try:
        return [
            path for path in directory.iterdir() if path.is_file() and path.suffix.casefold() in FLAT_ICON_EXTENSIONS
        ]
    except OSError:
        return []


def _join_repo_path(repo_root: Path, folder: str, relative: str) -> Path:
    if folder:
        return repo_root / folder / relative
    return repo_root / relative


def _parse_frontmatter(text: str) -> dict[str, Any]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if current_list_key is not None and stripped.startswith("- "):
            item = stripped[2:].strip().strip("\"'")
            if item:
                result.setdefault(current_list_key, []).append(item)
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {"categories", "tags"}:
            if value:
                result[key] = _parse_yaml_list(value)
            else:
                result[key] = []
                current_list_key = key
        elif key == "date":
            result[key] = value.strip("\"'")
        elif key == "trademark":
            result[key] = value.lower() == "true"
        else:
            result[key] = value
    return result


def _parse_yaml_list(raw: str) -> list[str]:
    match = _LIST_RE.match(raw.strip())
    if not match:
        return [raw.strip().strip("\"'")] if raw.strip() else []
    inner = match.group(1).strip()
    if not inner:
        return []
    items: list[str] = []
    for part in inner.split(","):
        item = part.strip().strip("\"'")
        if item:
            items.append(item)
    return items


def _pick_featured_file(files: list[Path]) -> Path:
    def rank(path: Path) -> tuple[int, str]:
        suffix = path.suffix.casefold()
        stem = path.stem.casefold()
        is_variant = bool(_VARIANT_TOKEN_RE.search(stem))
        if suffix == ".svg" and not is_variant:
            kind = 0
        elif suffix == ".svg":
            kind = 1
        elif suffix == ".ai":
            kind = 2
        elif suffix == ".pdf":
            kind = 3
        else:
            kind = 4
        return kind, path.as_posix().casefold()

    return min(files, key=rank)


def _relative_to_root(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
