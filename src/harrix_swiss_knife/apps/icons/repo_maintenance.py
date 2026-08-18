"""Check icon notes and run Beautify MD plus in-place SVG optimize."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal

import harrix_pylib as h
from PySide6.QtCore import QObject, Signal, Slot

from harrix_swiss_knife.actions.common.image_optimize import OptimizeSizeStats
from harrix_swiss_knife.actions.markdown.beautify_md import OnBeautifyMd
from harrix_swiss_knife.actions.markdown.check_md import OnCheckMd
from harrix_swiss_knife.apps.icons.catalog import (
    FLAT_ICON_EXTENSIONS,
    iter_icon_note_dirs,
    parse_note_frontmatter,
)
from harrix_swiss_knife.apps.icons.family_id import category_from_family_id

MaintenanceKind = Literal["check", "beautify_optimize"]
ProgressCallback = Callable[[int, int, str], None]

_NOTE_ASSET_DIRS = frozenset({"img", "files"})
_SKIP_DIR_NAMES = frozenset({".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv"})
_FEATURED_STEM = "featured-image"


class RepoMaintenanceWorker(QObject):
    """Run icon-repo maintenance outside the GUI thread."""

    progress = Signal(int, int, str)
    succeeded = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, repo_root: Path, kind: MaintenanceKind) -> None:
        """Store the repository path and the job kind."""
        super().__init__()
        self._repo_root = Path(repo_root)
        self._kind = kind

    @Slot()
    def run(self) -> None:
        """Execute the selected maintenance job."""
        try:
            if self._kind == "check":
                text = check_icon_repo(self._repo_root, on_progress=self._emit_progress)
            else:
                text = beautify_and_optimize_icons(self._repo_root, on_progress=self._emit_progress)
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(text)
        finally:
            self.finished.emit()

    def _emit_progress(self, done: int, total: int, message: str) -> None:
        self.progress.emit(done, total, message)


def beautify_and_optimize_icons(
    repo_root: Path,
    *,
    on_progress: ProgressCallback | None = None,
) -> str:
    """Beautify Markdown notes under `icons/` and optimize SVG files in place."""
    icons_dir = _require_icons_dir(repo_root)
    lines: list[str] = ["🔵 Beautify Markdown"]
    beautify = OnBeautifyMd()
    beautify.beautify_markdown_common(
        str(icons_dir),
        is_include_summaries_and_combine=False,
        delete_generated_g_md=True,
    )
    lines.extend(beautify.result_lines)

    svgs = _iter_icon_svgs(icons_dir)
    total = max(1, len(svgs) + 1)
    _notify(on_progress, 1, total, "Optimizing SVG files…")
    lines.append("")
    lines.append("🔵 Optimize SVG files")
    stats = OptimizeSizeStats()
    errors: list[str] = []
    optimizer = h.svg_opt.SvgOptimizer()
    for index, svg in enumerate(svgs, start=1):
        _notify(on_progress, index + 1, total, f"Optimizing {svg.name}…")
        before = svg.stat().st_size
        try:
            optimizer.optimize_file(svg)
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"❌ {svg}: {exc}")
            continue
        stats.add(before, svg.stat().st_size)
    if svgs:
        lines.append(f"✅ Optimized {stats.count} SVG file(s).")
        lines.append(stats.format_summary())
    else:
        lines.append("🔵 No SVG files found.")
    lines.extend(errors)
    return "\n".join(lines).strip() + "\n"


def check_icon_repo(
    repo_root: Path,
    *,
    on_progress: ProgressCallback | None = None,
) -> str:
    """Check note filenames, category folders, and Markdown rules."""
    icons_dir = _require_icons_dir(repo_root)
    note_dirs = iter_icon_note_dirs(icons_dir)
    structure_issues = _collect_top_level_issues(icons_dir)
    total = max(1, len(note_dirs) + 1)
    for done, note_dir in enumerate(note_dirs, start=1):
        _notify(on_progress, done, total, f"Checking {note_dir.name}…")
        structure_issues.extend(_check_note_dir(note_dir, icons_dir))

    _notify(on_progress, total, total, "Checking Markdown…")
    md_lines = _check_markdown_notes(icons_dir)
    lines = [
        "🔵 Check images",
        f"Notes: {len(note_dirs)}",
        "",
        "📁 Filenames, folders, and categories",
    ]
    if structure_issues:
        lines.extend(f"- {item}" for item in structure_issues)
        lines.append(f"🔢 Structure issues = {len(structure_issues)}")
    else:
        lines.append("✅ Filenames, folders, and categories match.")
    lines.append("")
    lines.append("🚧 Markdown check")
    lines.extend(md_lines)
    return "\n".join(lines).strip() + "\n"


def is_family_prefixed_filename(name: str, family_id: str) -> bool:
    """Return whether `name` is the family note or a `{family_id}_…` variant."""
    stem = Path(name).stem
    return stem == family_id or stem.startswith(f"{family_id}_")


def _check_markdown_notes(icons_dir: Path) -> list[str]:
    action = OnCheckMd()
    action.folder_path = icons_dir
    action.include_g_md = False
    action.selected_rule_ids = h.md_check.MdChecker().all_rules
    action.check_md_common()
    return list(action.result_lines)


def _check_note_dir(note_dir: Path, icons_dir: Path) -> list[str]:
    family_id = note_dir.name
    issues: list[str] = []
    rel = _rel(note_dir, icons_dir.parent)
    folder_category = "" if note_dir.parent == icons_dir else note_dir.parent.name
    id_category = category_from_family_id(family_id) if "__" in family_id else ""

    if folder_category and id_category and folder_category != id_category:
        issues.append(
            f"{rel}: folder category `{folder_category}` does not match family id prefix `{id_category}`",
        )
    elif not folder_category and id_category:
        issues.append(f"{rel}: note should live in `icons/{id_category}/{family_id}`")

    md_path = note_dir / f"{family_id}.md"
    if not md_path.is_file():
        issues.append(f"{rel}: missing `{family_id}.md`")
    else:
        try:
            meta = parse_note_frontmatter(md_path.read_text(encoding="utf-8"))
        except OSError as exc:
            issues.append(f"{_rel(md_path, icons_dir.parent)}: cannot read note ({exc})")
        else:
            yaml_categories = [str(item).strip() for item in (meta.get("categories") or []) if str(item).strip()]
            expected = folder_category or id_category
            if expected and not any(item.casefold() == expected.casefold() for item in yaml_categories):
                shown = ", ".join(yaml_categories) if yaml_categories else "(empty)"
                issues.append(
                    f"{_rel(md_path, icons_dir.parent)}: YAML categories [{shown}] "
                    f"do not include folder category `{expected}`",
                )

    for path in _iter_note_files(note_dir):
        if _is_allowed_note_file(path, note_dir, family_id):
            continue
        issues.append(
            f"{_rel(path, icons_dir.parent)}: filename does not start with family id `{family_id}`",
        )
    return issues


def _collect_top_level_issues(icons_dir: Path) -> list[str]:
    issues: list[str] = []
    try:
        entries = list(icons_dir.iterdir())
    except OSError as exc:
        return [f"icons/: cannot read folder ({exc})"]
    for entry in entries:
        if entry.name.startswith(".") or entry.name.casefold() in _SKIP_DIR_NAMES:
            continue
        if entry.is_file():
            issues.append(f"{_rel(entry, icons_dir.parent)}: unexpected file in `icons/`")
    return issues


def _is_allowed_note_file(path: Path, note_dir: Path, family_id: str) -> bool:
    if path.parent == note_dir:
        if path.stem.casefold() == _FEATURED_STEM and path.suffix.casefold() in FLAT_ICON_EXTENSIONS:
            return True
        return path.name == f"{family_id}.md"
    return is_family_prefixed_filename(path.name, family_id)


def _iter_icon_svgs(icons_dir: Path) -> list[Path]:
    results: list[Path] = []
    for path in icons_dir.rglob("*.svg"):
        if not path.is_file():
            continue
        if any(part.startswith(".") or part.casefold() in _SKIP_DIR_NAMES for part in path.parts):
            continue
        results.append(path)
    results.sort(key=lambda item: item.as_posix().casefold())
    return results


def _iter_note_files(note_dir: Path) -> list[Path]:
    files: list[Path] = []
    try:
        entries = list(note_dir.iterdir())
    except OSError:
        return files
    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_file():
            files.append(entry)
            continue
        if not entry.is_dir() or entry.name.casefold() not in _NOTE_ASSET_DIRS:
            continue
        try:
            files.extend(path for path in entry.iterdir() if path.is_file() and not path.name.startswith("."))
        except OSError:
            continue
    return files


def _notify(on_progress: ProgressCallback | None, done: int, total: int, message: str) -> None:
    if on_progress is not None:
        on_progress(done, total, message)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _require_icons_dir(repo_root: Path) -> Path:
    icons_dir = Path(repo_root) / "icons"
    if not icons_dir.is_dir():
        msg = f"icons/ not found in {repo_root}"
        raise FileNotFoundError(msg)
    return icons_dir
