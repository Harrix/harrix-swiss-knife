"""Catalog models and loaders for the Vector Icons browser."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

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


@dataclass(frozen=True, slots=True)
class IconVariant:
    """One icon file belonging to an icon family."""

    file: str
    name: str
    hash: str

    def absolute_path(self, repo_root: Path, folder: str) -> Path:
        """Resolve the variant path under the icons repo root."""
        return _join_repo_path(repo_root, folder, self.file)


def is_note_icons_repo(root: Path) -> bool:
    """Return whether `root` looks like a Harrix-Vector-Icons note-folder repo."""
    if (root / "catalog.json").is_file() and (root / "icons").is_dir():
        return True
    icons_dir = root / "icons"
    if not icons_dir.is_dir():
        return False
    try:
        children = list(icons_dir.iterdir())
    except OSError:
        return False
    for child in children:
        if not child.is_dir():
            continue
        if (
            (child / "featured-image.svg").is_file()
            or (child / f"{child.name}.md").is_file()
            or (child / "img").is_dir()
        ):
            return True
    return False


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

    """
    root = resolve_icons_root(path)
    if is_note_icons_repo(root):
        if not (root / "catalog.json").is_file() and (root / "icons").is_dir():
            return rebuild_catalog(root)
        return load_catalog(root)
    return scan_flat_folder(root)


def rebuild_catalog(repo_root: Path) -> IconCatalog:
    """Rebuild `catalog.json` from `icons/` note-folders and reload it."""
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
    catalog = load_catalog(repo_root)
    catalog.kind = "note"
    return catalog


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
        key = _flat_family_id(path)
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
        family = IconFamily(
            id=family_id,
            title=_title_from_id(family_id),
            categories=[_category_from_id(family_id)],
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


def _category_from_id(family_id: str) -> str:
    return family_id.split("__", 1)[0] if "__" in family_id else family_id


def _count_flat_icon_files(root: Path) -> int:
    return len(_iter_flat_icon_files(root))


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


def _flat_family_id(path: Path) -> str:
    stem = path.stem
    if path.suffix.casefold() == ".svg":
        base = _VARIANT_TOKEN_RE.sub("", stem)
        return base or stem
    return stem


def _iter_flat_icon_files(root: Path) -> list[Path]:
    """Collect icon files in `root` and one level of subfolders."""
    result: list[Path] = []
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name.casefold())
    except OSError:
        return []
    for entry in entries:
        if entry.is_file() and entry.suffix.casefold() in FLAT_ICON_EXTENSIONS:
            result.append(entry)
            continue
        if not entry.is_dir() or entry.name.casefold() in _SKIP_DIR_NAMES:
            continue
        try:
            children = sorted(entry.iterdir(), key=lambda item: item.name.casefold())
        except OSError:
            continue
        result.extend(
            child for child in children if child.is_file() and child.suffix.casefold() in FLAT_ICON_EXTENSIONS
        )
    return result


def _join_repo_path(repo_root: Path, folder: str, relative: str) -> Path:
    if folder:
        return repo_root / folder / relative
    return repo_root / relative


def _parse_frontmatter(md_path: Path) -> dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {"categories", "tags"}:
            result[key] = _parse_yaml_list(value)
        elif key in {"title", "date"}:
            result[key] = value.strip("\"'")
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


def _title_from_id(family_id: str) -> str:
    slug = family_id.split("__", 1)[-1]
    return slug.replace("-", " ").replace("_", " ").title()
