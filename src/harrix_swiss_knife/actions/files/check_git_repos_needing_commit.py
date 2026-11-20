"""Find Git repos under configured roots that need a commit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.maintenance_checklist_steps import save_git_repos_all_clean
from harrix_swiss_knife.actions.files.discard_git_changes import OnDiscardGitChanges


@dataclass(frozen=True, slots=True)
class DirtyRepo:
    """One repository with a non-empty working tree."""

    path: Path
    changed_count: int
    sample_lines: tuple[str, ...]


class OnCheckGitReposNeedingCommit(ActionBase):
    """Git: scan `paths_git_roots` for repositories with uncommitted changes.

    Opens a Fluent window to review diffs, pick files, and commit with subject
    suggestions (history + Quick Paste). GitHub Desktop opens without blocking.

    """

    icon = "📌"
    title = "Git repos needing commit…"
    description = "Git: list dirty repos under paths_git_roots; open GitHub Desktop or commit."
    cli_available = True
    cli_hint = "file check-git-repos-needing-commit"
    bold_title = True

    @ActionBase.handle_exceptions("checking git repos needing commit")
    def execute(
        self,
        *_args: Any,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Scan configured roots and open the commit window when dirty repos exist."""
        roots = self._configured_roots()
        if not roots:
            self.add_line("❌ `paths_git_roots` is missing or empty in config.json.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            dirty = self._scan_dirty_repos(roots)
            self._report_scan(roots, dirty)
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking git repos needing commit thread")
    def in_thread(self) -> list[DirtyRepo]:
        """Scan roots on a worker thread."""
        return self._scan_dirty_repos(self._configured_roots())

    @ActionBase.handle_exceptions("checking git repos needing commit thread completion")
    def thread_after(self, result: Any) -> None:
        """Open the Fluent commit window, or show a clean result."""
        dirty = result if isinstance(result, list) else []
        roots = self._configured_roots()
        self._report_scan(roots, dirty)
        if not dirty:
            self.show_toast("All Git repos are clean")
            self.show_result()
            return

        self.show_toast(f"{len(dirty)} repo(s) need a commit")
        # Lazy import: window pulls snippets DB helpers; avoid cycle via actions.files.
        from harrix_swiss_knife.apps.git_commit.window import (  # noqa: PLC0415
            show_dirty_repos_commit_window,
        )

        quick_paste_db = self.config.get("sqlite_snippets")
        show_dirty_repos_commit_window(
            [repo.path for repo in dirty],
            quick_paste_db=str(quick_paste_db) if quick_paste_db else None,
            on_line=self.add_line,
        )

    def _configured_roots(self) -> list[Path]:
        raw = self.config.get("paths_git_roots")
        if not isinstance(raw, list):
            return []
        roots: list[Path] = []
        seen: set[Path] = set()
        for item in raw:
            text = str(item or "").strip()
            if not text:
                continue
            path = Path(text).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                resolved = path
            if resolved in seen:
                continue
            seen.add(resolved)
            roots.append(resolved)
        return roots

    def _report_scan(self, roots: list[Path], dirty: list[DirtyRepo]) -> None:
        save_git_repos_all_clean(all_clean=not dirty)
        self.add_line(f"🔵 Scanned {len(roots)} root(s) from `paths_git_roots`")
        for root in roots:
            self.add_line(f"  • {root}")
        if not dirty:
            self.add_line("✅ No repositories need a commit")
            return
        self.add_line(f"🔶 {len(dirty)} repository(ies) need a commit:")
        for repo in dirty:
            self.add_line(f"  • {repo.path} ({repo.changed_count} change(s))")

    def _scan_dirty_repos(self, roots: list[Path]) -> list[DirtyRepo]:
        repos: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            if not root.is_dir():
                self.add_line(f"⚪ Skip missing root: {root}")
                continue
            for repo in OnDiscardGitChanges.find_git_repos(root):
                resolved = repo.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                repos.append(resolved)

        dirty: list[DirtyRepo] = []
        for repo in sorted(repos, key=lambda path: str(path).casefold()):
            porcelain = OnDiscardGitChanges.git_porcelain(repo).strip()
            if not porcelain:
                continue
            lines = tuple(porcelain.splitlines())
            dirty.append(
                DirtyRepo(
                    path=repo,
                    changed_count=len(lines),
                    sample_lines=lines[:5],
                )
            )
        return dirty
