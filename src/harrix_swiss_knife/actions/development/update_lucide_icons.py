"""Update bundled Lucide SVG icons from npm lucide-static."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.git_cmd import git_run
from harrix_swiss_knife.actions.common.git_dirty_ops import parse_porcelain_files
from harrix_swiss_knife.assets.sync_lucide_icons import LucideSyncResult, sync_lucide_icons
from harrix_swiss_knife.paths import get_project_root
from harrix_swiss_knife.qt_lucide_icon import clear_lucide_icon_caches

LUCIDE_COMMIT_MESSAGE = "⬆️ Update Lucide"
_MAX_THUMBNAILS = 800


@dataclass(frozen=True, slots=True)
class LucideGitChanges:
    """SVG icon names changed under `assets/lucide` according to Git."""

    added: tuple[str, ...] = ()
    modified: tuple[str, ...] = ()
    had_non_svg: bool = False

    @property
    def has_changes(self) -> bool:
        """Return whether Git reports any path under the Lucide folder."""
        return bool(self.added or self.modified or self.had_non_svg)

    @property
    def svg_names(self) -> tuple[str, ...]:
        """Return added then modified names without duplicates."""
        seen: set[str] = set()
        names: list[str] = []
        for name in (*self.added, *self.modified):
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
        return tuple(names)


class OnUpdateLucideIcons(ActionBase):
    """Download the latest Lucide SVG set into `assets/lucide`.

    Fetches `lucide-static` from npm, replaces local SVGs, optimizes them, and
    updates `VERSION.txt` / `LICENSE.txt`. Commits the Lucide folder as
    Update Lucide when Git reports changes, then shows thumbnails for added and
    updated SVGs. Android `LucideIcons.kt` is not changed.

    """

    icon = "⬇️"
    title = "Update Lucide icons"

    @ActionBase.handle_exceptions("update Lucide icons")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start the Lucide sync on a background thread."""
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)

    @ActionBase.handle_exceptions("update Lucide icons thread")
    def in_thread(self) -> LucideSyncResult:
        """Download and optimize Lucide SVGs."""

        def _progress(message: str) -> None:
            self.raise_if_work_cancelled()
            self.add_line(message)

        return sync_lucide_icons(progress=_progress)

    @ActionBase.handle_exceptions("update Lucide icons thread completion")
    def thread_after(self, result: Any) -> None:
        """Commit Lucide updates, show summary, and preview changed SVG thumbnails."""
        if not isinstance(result, LucideSyncResult):
            self.add_line(str(result))
            self.show_result()
            return
        clear_lucide_icon_caches()
        old = result.old_version or "(none)"
        new = result.new_version
        if old == new:
            summary = f"Lucide icons already at {new} ({result.svg_count} SVGs)."
        else:
            summary = f"Lucide icons updated: {old} → {new} ({result.svg_count} SVGs)."
        self.add_line(summary)
        self.add_line(f"Folder: {result.dest}")

        repo = get_project_root()
        changes = list_lucide_git_changes(repo, result.dest)
        if changes.has_changes:
            ok, detail = commit_lucide_updates(repo, result.dest)
            if ok:
                self.add_line(f"✅ {detail}")
            else:
                self.add_line(f"❌ {detail}")
        else:
            self.add_line("No Git changes under the Lucide folder.")

        self.show_toast(summary)
        self.show_result()
        self._show_changed_thumbnails(changes)

    def _show_changed_thumbnails(self, changes: LucideGitChanges) -> None:
        names = changes.svg_names
        if not names:
            return
        truncated = names[:_MAX_THUMBNAILS]
        sections: list[tuple[str, list[str]]] = []
        if changes.added:
            added = [name for name in truncated if name in set(changes.added)]
            if added:
                sections.append((f"Added ({len(changes.added)})", added))
        if changes.modified:
            modified = [name for name in truncated if name in set(changes.modified)]
            if modified:
                sections.append((f"Updated ({len(changes.modified)})", modified))
        if not sections:
            return
        note = ""
        if len(names) > _MAX_THUMBNAILS:
            note = f" Showing first {_MAX_THUMBNAILS} of {len(names)}."
        self.dialogs.show_lucide_icon_thumbnails(
            "Lucide changes",
            f"SVG icons added or updated according to Git.{note}",
            sections,
        )


def commit_lucide_updates(
    repo: Path,
    lucide_folder: Path,
    *,
    message: str = LUCIDE_COMMIT_MESSAGE,
) -> tuple[bool, str]:
    """Stage the Lucide folder and create a commit when the index has changes."""
    try:
        rel = lucide_folder.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return False, f"Lucide folder is outside the repository: {lucide_folder}"

    add_p = git_run(repo, "add", "--", rel)
    if add_p.returncode != 0:
        return False, (add_p.stderr or add_p.stdout or "git add failed").strip()

    dirty = git_run(repo, "diff", "--cached", "--quiet")
    if dirty.returncode == 0:
        return True, "No Lucide changes to commit"

    commit_p = git_run(repo, "-c", "commit.gpgsign=false", "commit", "-m", message)
    if commit_p.returncode != 0:
        return False, (commit_p.stderr or commit_p.stdout or "git commit failed").strip()
    return True, f"Committed `{message}`"


def list_lucide_git_changes(repo: Path, lucide_folder: Path) -> LucideGitChanges:
    """Return added and modified Lucide SVG names from `git status --porcelain`."""
    try:
        rel = lucide_folder.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return LucideGitChanges()

    proc = git_run(repo, "status", "--porcelain", "-u", "--", rel)
    if proc.returncode != 0 or not proc.stdout.strip():
        return LucideGitChanges()

    added: list[str] = []
    modified: list[str] = []
    had_non_svg = False
    for changed in parse_porcelain_files(proc.stdout):
        path = changed.path.replace("\\", "/")
        name = Path(path).name
        if not name.endswith(".svg"):
            had_non_svg = True
            continue
        stem = name[: -len(".svg")]
        kind = _change_kind(changed.status)
        if kind == "added":
            added.append(stem)
        elif kind == "modified":
            modified.append(stem)
        elif kind == "deleted":
            had_non_svg = True
    added_sorted = tuple(sorted(dict.fromkeys(added)))
    modified_sorted = tuple(sorted(dict.fromkeys(modified)))
    return LucideGitChanges(added_sorted, modified_sorted, had_non_svg=had_non_svg)


def _change_kind(status: str) -> str:
    """Classify a porcelain status as added, modified, deleted, or other."""
    if status == "??" or "A" in status:
        return "added"
    if "D" in status and "A" not in status and "M" not in status and "R" not in status:
        return "deleted"
    if any(code in status for code in ("M", "R", "C", "T", "U")):
        return "modified"
    return "other"
