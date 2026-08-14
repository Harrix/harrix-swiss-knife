"""Add optimized SVG files into Harrix-Vector-Icons note folders."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal

import harrix_pylib as h

from harrix_swiss_knife.apps.icons.catalog import rebuild_catalog
from harrix_swiss_knife.apps.icons.family_id import (
    category_from_family_id,
    family_id_from_stem,
    note_dir_for_family_id,
    tags_from_family_id,
    title_from_family_id,
)


@dataclass
class AddSvgResult:
    """Outcome of processing one SVG."""

    source: Path
    family_id: str
    dest: Path | None
    status: AddSvgStatus
    message: str


class AddSvgStatus(StrEnum):
    """Result status for one source SVG."""

    ADDED = "added"
    REPLACED = "replaced"
    RENAMED = "renamed"
    SKIPPED_SAME = "skipped_same"
    SKIPPED_POLICY = "skipped_policy"
    CREATED_NOTE = "created_note"
    ERROR = "error"


@dataclass
class AddSvgsReport:
    """Aggregate report for a batch import."""

    results: list[AddSvgResult] = field(default_factory=list)
    catalog_rebuilt: bool = False

    @property
    def summary_lines(self) -> list[str]:
        """Human-readable summary lines."""
        counts: dict[str, int] = {}
        for item in self.results:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        status_order = (
            AddSvgStatus.ADDED,
            AddSvgStatus.CREATED_NOTE,
            AddSvgStatus.RENAMED,
            AddSvgStatus.REPLACED,
            AddSvgStatus.SKIPPED_SAME,
            AddSvgStatus.SKIPPED_POLICY,
            AddSvgStatus.ERROR,
        )
        lines = [f"Processed {len(self.results)} SVG file(s)."]
        lines.extend(f"- {key.value}: {counts[key.value]}" for key in status_order if counts.get(key.value))
        if self.catalog_rebuilt:
            lines.append("Catalog rebuilt.")
        return lines


@dataclass(slots=True)
class SvgJob:
    """One source SVG mapped to a target note folder."""

    source: Path
    family_id: str
    note_dir: Path
    dest_name: str
    dest_path: Path
    source_hash: str
    collision: bool = False
    same_hash: bool = False


def add_svgs_to_repo(
    source_dir: Path,
    *,
    repo_root: Path,
    collision_policy: CollisionPolicy = "rename",
    rebuild: bool = True,
) -> AddSvgsReport:
    """Discover SVGs in `source_dir`, add them into note folders, optionally rebuild catalog."""
    report = AddSvgsReport()
    sources = discover_source_svgs(source_dir)
    if not sources:
        report.results.append(
            AddSvgResult(
                source=source_dir,
                family_id="",
                dest=None,
                status=AddSvgStatus.ERROR,
                message=f"No SVG files found in `{source_dir}`",
            )
        )
        return report

    jobs = build_jobs(sources, repo_root=repo_root)
    for job in jobs:
        report.results.extend(process_job(job, repo_root=repo_root, collision_policy=collision_policy))

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


def build_jobs(source_svgs: list[Path], *, repo_root: Path) -> list[SvgJob]:
    """Map source SVGs to destination note folders and detect collisions."""
    icons_dir = Path(repo_root) / "icons"
    jobs: list[SvgJob] = []
    for source in source_svgs:
        family_id = family_id_from_stem(source.stem)
        note_dir = resolve_note_dir(icons_dir, family_id)
        dest_name = source.name
        dest_path = note_dir / "img" / dest_name
        source_hash = file_sha256(source)
        collision = dest_path.is_file()
        same_hash = collision and file_sha256(dest_path) == source_hash
        jobs.append(
            SvgJob(
                source=source,
                family_id=family_id,
                note_dir=note_dir,
                dest_name=dest_name,
                dest_path=dest_path,
                source_hash=source_hash,
                collision=collision,
                same_hash=same_hash,
            )
        )
    return jobs


def discover_source_svgs(source_dir: Path) -> list[Path]:
    """Return sorted SVG files under `source_dir` (non-recursive for top-level packs, recursive otherwise).

    Scans recursively, but skips files already inside a target repo `icons/` tree when
    `source_dir` itself is that repo root.

    """
    root = Path(source_dir).resolve()
    if not root.is_dir():
        return []
    icons_marker = root / "icons"
    results: list[Path] = []
    for path in sorted(root.rglob("*.svg")):
        if not path.is_file():
            continue
        # Avoid re-importing from the destination icons tree when user picks the repo root.
        try:
            if icons_marker.is_dir() and path.resolve().is_relative_to(icons_marker.resolve()):
                continue
        except (OSError, ValueError):
            pass
        results.append(path)
    return results


def ensure_featured_image(note_dir: Path, svg_path: Path) -> None:
    """Copy `svg_path` to `featured-image.svg` when featured is missing."""
    featured = note_dir / "featured-image.svg"
    if featured.is_file():
        return
    featured.write_text(svg_path.read_text(encoding="utf-8"), encoding="utf-8")


def ensure_note_scaffold(note_dir: Path, family_id: str, *, repo_root: Path) -> bool:
    """Create note folder + Markdown when missing. Return whether a new note was created."""
    note_dir.mkdir(parents=True, exist_ok=True)
    (note_dir / "img").mkdir(parents=True, exist_ok=True)
    md_path = note_dir / f"{family_id}.md"
    if md_path.is_file():
        return False

    category = category_from_family_id(family_id)
    title = title_from_family_id(family_id)
    tags = tags_from_family_id(family_id)
    tags_yaml = "\n".join(f"  - {tag}" for tag in tags)
    today = datetime.now(UTC).date().isoformat()
    permalink = _permalink_for_note(note_dir, family_id, repo_root)
    body = f"""---
date: {today}
categories:
  - {category}
tags:
{tags_yaml}
author: {_AUTHOR}
author-email: {_AUTHOR_EMAIL}
license: CC BY 4.0
license-url: {_LICENSE_URL}
permalink-source: {permalink}
lang: en
---

# {title}

![Featured image](featured-image.svg)

## Icons

"""
    md_path.write_text(body, encoding="utf-8")
    return True


def file_sha256(path: Path) -> str:
    """Return hex SHA-256 of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jobs_with_content_collisions(jobs: list[SvgJob]) -> list[SvgJob]:
    """Return jobs where destination exists with a different hash."""
    return [job for job in jobs if job.collision and not job.same_hash]


def optimize_svg_to(source: Path, dest: Path) -> str:
    """Optimize `source` SVG into `dest` via `harrix_pylib` SvgOptimizer."""
    return h.svg_opt.SvgOptimizer().optimize_file(source, dest)


def process_job(
    job: SvgJob,
    *,
    repo_root: Path,
    collision_policy: CollisionPolicy,
) -> list[AddSvgResult]:
    """Process one SVG job (create note, optimize, place, update Markdown)."""
    results: list[AddSvgResult] = []
    created = ensure_note_scaffold(job.note_dir, job.family_id, repo_root=repo_root)
    if created:
        results.append(
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=job.note_dir / f"{job.family_id}.md",
                status=AddSvgStatus.CREATED_NOTE,
                message=f"Created note `{job.family_id}`",
            )
        )

    img_dir = job.note_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    dest_path = job.dest_path
    status = AddSvgStatus.ADDED

    if job.same_hash:
        return [
            *results,
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=dest_path,
                status=AddSvgStatus.SKIPPED_SAME,
                message=f"Skipped `{job.source.name}` (identical file already in note)",
            ),
        ]

    if job.collision and not job.same_hash:
        if collision_policy == "skip":
            return [
                *results,
                AddSvgResult(
                    source=job.source,
                    family_id=job.family_id,
                    dest=dest_path,
                    status=AddSvgStatus.SKIPPED_POLICY,
                    message=f"Skipped `{job.source.name}` (collision, policy=skip)",
                ),
            ]
        if collision_policy == "rename":
            new_name = unique_variant_name(img_dir, job.source.stem)
            dest_path = img_dir / new_name
            status = AddSvgStatus.RENAMED
        else:
            status = AddSvgStatus.REPLACED

    try:
        optimize_svg_to(job.source, dest_path)
        ensure_featured_image(job.note_dir, dest_path)
        append_icon_to_note(job.note_dir / f"{job.family_id}.md", dest_path.name)
    except (OSError, ValueError, RuntimeError) as exc:
        return [
            *results,
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=dest_path,
                status=AddSvgStatus.ERROR,
                message=f"Error for `{job.source.name}`: {exc}",
            ),
        ]

    verb = {
        AddSvgStatus.ADDED: "Added",
        AddSvgStatus.RENAMED: "Added as",
        AddSvgStatus.REPLACED: "Replaced",
    }.get(status, "Wrote")
    results.append(
        AddSvgResult(
            source=job.source,
            family_id=job.family_id,
            dest=dest_path,
            status=status,
            message=f"{verb} `{dest_path.name}` → `{job.family_id}`",
        )
    )
    return results


def resolve_note_dir(icons_dir: Path, family_id: str) -> Path:
    """Return existing note folder for `family_id`, or the nested target path."""
    nested = note_dir_for_family_id(icons_dir, family_id)
    if nested.is_dir():
        return nested
    flat = Path(icons_dir) / family_id
    if flat.is_dir():
        return flat
    # Search one level of category folders for a matching family folder name.
    try:
        for child in icons_dir.iterdir():
            if not child.is_dir():
                continue
            candidate = child / family_id
            if candidate.is_dir():
                return candidate
    except OSError:
        pass
    return nested


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


def _permalink_for_note(note_dir: Path, family_id: str, repo_root: Path) -> str:
    rel = (note_dir / f"{family_id}.md").resolve().relative_to(Path(repo_root).resolve()).as_posix()
    return f"{_PERMALINK_BASE}/{rel}"


CollisionPolicy = Literal["rename", "replace", "skip"]

_LICENSE_URL = "https://github.com/Harrix/Harrix-Vector-Icons/blob/main/LICENSE.md"
_PERMALINK_BASE = "https://github.com/Harrix/Harrix-Vector-Icons/blob/main"
_AUTHOR = "Anton Sergienko"
_AUTHOR_EMAIL = "anton.b.sergienko@gmail.com"
_ICONS_SECTION_RE = re.compile(r"(##\s+Icons\s*\n)(.*?)(?=\n##\s|\Z)", re.DOTALL | re.IGNORECASE)
