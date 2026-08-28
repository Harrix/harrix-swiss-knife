"""Add vector images into flat folders or note-icon repositories."""

from __future__ import annotations

import hashlib
import re
import shutil
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import harrix_pylib as h

from harrix_swiss_knife.apps.icons.add_vector_meta import NoteMeta, note_dir_for_meta
from harrix_swiss_knife.apps.icons.catalog import FLAT_ICON_EXTENSIONS, rebuild_catalog
from harrix_swiss_knife.apps.icons.family_id import family_id_from_stem

if TYPE_CHECKING:
    from collections.abc import Sequence

CollisionPolicy = Literal["rename", "replace", "skip"]


@dataclass
class AddVectorReport:
    """Aggregate report for a batch import."""

    results: list[AddVectorResult] = field(default_factory=list)
    catalog_rebuilt: bool = False

    @property
    def summary_lines(self) -> list[str]:
        """Human-readable summary lines."""
        counts: dict[str, int] = {}
        for item in self.results:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        status_order = (
            AddVectorStatus.ADDED,
            AddVectorStatus.CREATED_NOTE,
            AddVectorStatus.RENAMED,
            AddVectorStatus.REPLACED,
            AddVectorStatus.SKIPPED_SAME,
            AddVectorStatus.SKIPPED_POLICY,
            AddVectorStatus.ERROR,
        )
        lines = [f"Processed {len(self.results)} vector file(s)."]
        lines.extend(f"- {key.value}: {counts[key.value]}" for key in status_order if counts.get(key.value))
        if self.catalog_rebuilt:
            lines.append("Catalog rebuilt.")
        return lines


@dataclass
class AddVectorResult:
    """Outcome of processing one vector file."""

    source: Path
    family_id: str
    dest: Path | None
    status: AddVectorStatus
    message: str


class AddVectorStatus(StrEnum):
    """Result status for one vector file."""

    ADDED = "added"
    REPLACED = "replaced"
    RENAMED = "renamed"
    SKIPPED_SAME = "skipped_same"
    SKIPPED_POLICY = "skipped_policy"
    CREATED_NOTE = "created_note"
    ERROR = "error"


def add_variants_to_family(
    sources: list[Path],
    *,
    repo_root: Path,
    family_id: str,
    note_folder: str,
    collision_policy: CollisionPolicy = "rename",
    rebuild: bool = True,
) -> AddVectorReport:
    """Add vector files as variants into an existing note folder."""
    report = AddVectorReport()
    note_dir = Path(repo_root) / note_folder if note_folder else Path(repo_root) / "icons" / family_id
    if not note_dir.is_dir():
        report.results.append(
            AddVectorResult(
                source=Path(),
                family_id=family_id,
                dest=None,
                status=AddVectorStatus.ERROR,
                message=f"Note folder not found: {note_dir}",
            )
        )
        return report

    img_dir = note_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    md_path = note_dir / f"{family_id}.md"

    for source in collect_vector_sources(sources):
        dest_name = variant_dest_name(source, family_id=family_id)
        dest_path = img_dir / dest_name
        place = _place_vector_file(
            source,
            dest_path=dest_path,
            img_dir=img_dir,
            collision_policy=collision_policy,
            family_id=family_id,
        )
        report.results.append(place)
        if (
            place.status not in {AddVectorStatus.ERROR, AddVectorStatus.SKIPPED_SAME, AddVectorStatus.SKIPPED_POLICY}
            and place.dest is not None
        ):
            ensure_featured_from_source(note_dir, place.dest)
            if md_path.is_file():
                append_icon_to_note(md_path, place.dest.name)

    if rebuild:
        rebuild_catalog(repo_root)
        report.catalog_rebuilt = True
    return report


def append_icon_to_note(md_path: Path, svg_name: str) -> None:
    """Append an image bullet under `## Icons` when not already listed."""
    if not md_path.is_file():
        return
    text = md_path.read_text(encoding="utf-8")
    bullet = f"- ![{Path(svg_name).stem}](img/{svg_name})"
    if f"img/{svg_name}" in text:
        return
    match = _ICONS_SECTION_RE.search(text)
    if match:
        section_body = match.group(2).rstrip()
        new_section = match.group(1) + (section_body + "\n" if section_body else "") + bullet + "\n"
        text = text[: match.start()] + new_section + text[match.end() :]
    elif "## Icons" not in text:
        text = text.rstrip() + f"\n\n## Icons\n\n{bullet}\n"
    else:
        text = text.rstrip() + f"\n{bullet}\n"
    md_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def collect_vector_sources(paths: Sequence[Path | str], *, skip_under: Path | None = None) -> list[Path]:
    """Collect SVG/AI/PDF/EPS files from paths and folders."""
    results: list[Path] = []
    seen: set[Path] = set()
    skip_root = skip_under.resolve() if skip_under is not None else None
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            candidates = discover_vector_files(path, skip_under=skip_root)
        elif path.is_file() and path.suffix.casefold() in FLAT_ICON_EXTENSIONS:
            candidates = [path]
        else:
            continue
        for candidate in candidates:
            resolved = candidate.resolve()
            if skip_root is not None and _is_relative_to(resolved, skip_root):
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            results.append(resolved)
    return results


def copy_vectors_to_flat_folder(
    sources: list[Path],
    *,
    dest_dir: Path,
    collision_policy: CollisionPolicy = "rename",
) -> AddVectorReport:
    """Copy vector files into a flat icons folder (no note scaffold)."""
    report = AddVectorReport()
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for source in collect_vector_sources(sources):
        report.results.append(_copy_one_file(source, dest_dir=dest_dir, collision_policy=collision_policy))
    return report


def create_note_from_meta(
    source: Path,
    *,
    repo_root: Path,
    meta: NoteMeta,
    collision_policy: CollisionPolicy = "rename",
    rebuild: bool = True,
) -> AddVectorReport:
    """Create or update a note-icon from dialog metadata and one source file."""
    report = AddVectorReport()
    source = Path(source)
    if not source.is_file():
        report.results.append(
            AddVectorResult(
                source=source,
                family_id=meta.family_id,
                dest=None,
                status=AddVectorStatus.ERROR,
                message=f"Source not found: {source}",
            )
        )
        return report

    note_dir = note_dir_for_meta(repo_root, family_id=meta.family_id, category=meta.category)
    md_path = note_dir / f"{meta.family_id}.md"
    created = not md_path.is_file()
    note_dir.mkdir(parents=True, exist_ok=True)
    (note_dir / "img").mkdir(parents=True, exist_ok=True)

    if created:
        write_note_markdown(md_path, meta=meta)
        report.results.append(
            AddVectorResult(
                source=source,
                family_id=meta.family_id,
                dest=md_path,
                status=AddVectorStatus.CREATED_NOTE,
                message=f"Created note `{meta.family_id}`",
            )
        )
    else:
        # Existing note: treat as variant add using dialog family id.
        pass

    dest_name = source.name
    img_dir = note_dir / "img"
    dest_path = img_dir / dest_name
    place = _place_vector_file(
        source,
        dest_path=dest_path,
        img_dir=img_dir,
        collision_policy=collision_policy,
        family_id=meta.family_id,
    )
    report.results.append(place)
    if (
        place.status not in {AddVectorStatus.ERROR, AddVectorStatus.SKIPPED_SAME, AddVectorStatus.SKIPPED_POLICY}
        and place.dest is not None
    ):
        ensure_featured_from_source(note_dir, place.dest)
        append_icon_to_note(md_path, place.dest.name)
        if created:
            _update_featured_link(md_path, note_dir)

    if rebuild:
        rebuild_catalog(repo_root)
        report.catalog_rebuilt = True
    return report


def discover_vector_files(source_dir: Path, *, skip_under: Path | None = None) -> list[Path]:
    """Return sorted vector files under `source_dir`, optionally skipping a subtree."""
    root = Path(source_dir).resolve()
    if not root.is_dir():
        return []
    skip = skip_under.resolve() if skip_under is not None else None
    results: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.casefold() not in FLAT_ICON_EXTENSIONS:
            continue
        if skip is not None and _is_relative_to(path, skip):
            continue
        results.append(path)
    return results


def ensure_featured_from_source(note_dir: Path, source: Path) -> Path | None:
    """Copy/optimize `source` to `featured-image{ext}` when featured is missing."""
    for suffix in (".svg", ".ai", ".pdf", ".eps"):
        if (note_dir / f"featured-image{suffix}").is_file():
            return None
    featured = note_dir / f"featured-image{source.suffix.casefold()}"
    _write_vector_file(source, featured)
    return featured


def file_sha256(path: Path) -> str:
    """Return hex SHA-256 of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def note_exists_for_family(repo_root: Path, *, family_id: str, category: str) -> Path | None:
    """Return existing note dir for family/category, if present."""
    candidate = note_dir_for_meta(repo_root, family_id=family_id, category=category)
    if candidate.is_dir() and (candidate / f"{family_id}.md").is_file():
        return candidate
    icons_dir = Path(repo_root) / "icons"
    flat = icons_dir / family_id
    if flat.is_dir() and (flat / f"{family_id}.md").is_file():
        return flat
    if icons_dir.is_dir():
        try:
            for child in icons_dir.iterdir():
                if not child.is_dir():
                    continue
                nested = child / family_id
                if nested.is_dir() and (nested / f"{family_id}.md").is_file():
                    return nested
        except OSError:
            pass
    return None


def optimize_svg_to(source: Path, dest: Path) -> str:
    """Optimize `source` SVG into `dest` via `harrix_pylib` SvgOptimizer."""
    return h.svg_opt.SvgOptimizer().optimize_file(source, dest)


def unique_variant_name(img_dir: Path, stem: str, suffix: str = ".svg") -> str:
    """Return a free filename in `img_dir`, preferring `{stem}_new`, then `_new2`, and so on."""
    candidate = f"{stem}_new{suffix}"
    if not (img_dir / candidate).exists():
        return candidate
    index = 2
    while True:
        candidate = f"{stem}_new{index}{suffix}"
        if not (img_dir / candidate).exists():
            return candidate
        index += 1


def variant_dest_name(source: Path, *, family_id: str) -> str:
    """Return destination filename for a variant under `family_id`."""
    stem = source.stem
    suffix = source.suffix
    if stem == family_id or stem.startswith(f"{family_id}_"):
        return f"{stem}{suffix}"
    return f"{family_id}_{stem}{suffix}"


def write_note_markdown(md_path: Path, *, meta: NoteMeta) -> None:
    """Write a note Markdown file from `meta`."""
    categories_yaml = f"  - {meta.category}" if meta.category.strip() else ""
    tags_yaml = "\n".join(f"  - {tag}" for tag in meta.tags) if meta.tags else ""
    featured = meta.featured_name or "featured-image.svg"
    lines = [
        "---",
        f"date: {meta.date}",
        "categories:",
    ]
    if categories_yaml:
        lines.append(categories_yaml)
    lines.append("tags:")
    if tags_yaml:
        lines.append(tags_yaml)
    lines.extend(
        [
            f"author: {meta.author}",
            f"author-email: {meta.author_email}",
            f"license: {meta.license}",
            f"license-url: {meta.license_url}",
            f"permalink: {meta.permalink}",
            f"permalink-source: {meta.permalink_source}",
            f"lang: {meta.lang}",
            "---",
            "",
            f"# {meta.title}",
            "",
            f"![Featured image]({featured})",
            "",
            "## Icons",
            "",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_one_file(
    source: Path,
    *,
    dest_dir: Path,
    collision_policy: CollisionPolicy,
) -> AddVectorResult:
    dest_path = dest_dir / source.name
    source_hash = file_sha256(source)
    if dest_path.is_file() and file_sha256(dest_path) == source_hash:
        return AddVectorResult(
            source=source,
            family_id=family_id_from_stem(source.stem),
            dest=dest_path,
            status=AddVectorStatus.SKIPPED_SAME,
            message=f"Skipped `{source.name}` (identical file already present)",
        )
    status = AddVectorStatus.ADDED
    if dest_path.is_file():
        if collision_policy == "skip":
            return AddVectorResult(
                source=source,
                family_id=family_id_from_stem(source.stem),
                dest=dest_path,
                status=AddVectorStatus.SKIPPED_POLICY,
                message=f"Skipped `{source.name}` (collision, policy=skip)",
            )
        if collision_policy == "rename":
            new_name = unique_variant_name(dest_dir, source.stem, suffix=source.suffix.casefold())
            dest_path = dest_dir / new_name
            status = AddVectorStatus.RENAMED
        else:
            status = AddVectorStatus.REPLACED
    try:
        shutil.copy2(source, dest_path)
    except OSError as exc:
        return AddVectorResult(
            source=source,
            family_id=family_id_from_stem(source.stem),
            dest=dest_path,
            status=AddVectorStatus.ERROR,
            message=f"Error for `{source.name}`: {exc}",
        )
    verb = {
        AddVectorStatus.ADDED: "Copied",
        AddVectorStatus.RENAMED: "Copied as",
        AddVectorStatus.REPLACED: "Replaced",
    }.get(status, "Wrote")
    return AddVectorResult(
        source=source,
        family_id=family_id_from_stem(source.stem),
        dest=dest_path,
        status=status,
        message=f"{verb} `{dest_path.name}`",
    )


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except (OSError, ValueError):
        return False
    return True


def _place_vector_file(
    source: Path,
    *,
    dest_path: Path,
    img_dir: Path,
    collision_policy: CollisionPolicy,
    family_id: str,
) -> AddVectorResult:
    source_hash = file_sha256(source)
    if dest_path.is_file() and file_sha256(dest_path) == source_hash:
        return AddVectorResult(
            source=source,
            family_id=family_id,
            dest=dest_path,
            status=AddVectorStatus.SKIPPED_SAME,
            message=f"Skipped `{source.name}` (identical file already in note)",
        )
    status = AddVectorStatus.ADDED
    if dest_path.is_file():
        if collision_policy == "skip":
            return AddVectorResult(
                source=source,
                family_id=family_id,
                dest=dest_path,
                status=AddVectorStatus.SKIPPED_POLICY,
                message=f"Skipped `{source.name}` (collision, policy=skip)",
            )
        if collision_policy == "rename":
            new_name = unique_variant_name(img_dir, Path(dest_path).stem, suffix=source.suffix.casefold())
            dest_path = img_dir / new_name
            status = AddVectorStatus.RENAMED
        else:
            status = AddVectorStatus.REPLACED
    try:
        _write_vector_file(source, dest_path)
    except (OSError, ValueError, RuntimeError) as exc:
        return AddVectorResult(
            source=source,
            family_id=family_id,
            dest=dest_path,
            status=AddVectorStatus.ERROR,
            message=f"Error for `{source.name}`: {exc}",
        )
    verb = {
        AddVectorStatus.ADDED: "Added",
        AddVectorStatus.RENAMED: "Added as",
        AddVectorStatus.REPLACED: "Replaced",
    }.get(status, "Wrote")
    return AddVectorResult(
        source=source,
        family_id=family_id,
        dest=dest_path,
        status=status,
        message=f"{verb} `{dest_path.name}` → `{family_id}`",
    )


def _update_featured_link(md_path: Path, note_dir: Path) -> None:
    for suffix in (".svg", ".ai", ".pdf", ".eps"):
        featured = note_dir / f"featured-image{suffix}"
        if featured.is_file():
            text = md_path.read_text(encoding="utf-8")
            updated = text.replace("![Featured image](featured-image.svg)", f"![Featured image]({featured.name})")
            if updated != text:
                md_path.write_text(updated, encoding="utf-8")
            return


def _write_vector_file(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.casefold() == ".svg":
        optimize_svg_to(source, dest)
    else:
        shutil.copy2(source, dest)


_ICONS_SECTION_RE = re.compile(r"(##\s+Icons\s*\n)(.*?)(?=\n##\s|\Z)", re.DOTALL | re.IGNORECASE)
