"""Find Git repos under configured roots that need a commit."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

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
    """Scan `paths_git_roots` for repositories with uncommitted changes.

    For each dirty repo you can open it in GitHub Desktop or create a commit
    (`git add -A` + `git commit`) with a message you enter.

    """

    icon = "📌"
    title = "Check Git repos needing commit…"
    description = "List dirty repos under paths_git_roots; open GitHub Desktop or commit."
    cli_available = True
    cli_hint = "file check-git-repos-needing-commit"
    bold_title = True

    _ACTION_OPEN_DESKTOP = "Open in GitHub Desktop"
    _ACTION_COMMIT = "Create commit…"
    _ACTION_BACK = "Back to list"
    _COMMIT_STATUS_PREVIEW_LINES = 12

    @ActionBase.handle_exceptions("checking git repos needing commit")
    def execute(
        self,
        *_args: Any,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Scan configured roots and offer Desktop / commit actions for dirty repos."""
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
        """Show the dirty-repo list and handle Desktop / commit choices."""
        dirty = result if isinstance(result, list) else []
        roots = self._configured_roots()
        self._report_scan(roots, dirty)
        if not dirty:
            self.show_toast("All Git repos are clean")
            self.show_result()
            return

        self.show_toast(f"{len(dirty)} repo(s) need a commit")
        self._interactive_loop(list(dirty))

    def _commit_repo(self, repo: DirtyRepo) -> None:
        status = OnDiscardGitChanges.git_porcelain(repo.path).strip()
        status_lines = status.splitlines()
        preview_n = self._COMMIT_STATUS_PREVIEW_LINES
        preview = "\n".join(status_lines[:preview_n])
        if len(status_lines) > preview_n:
            preview = f"{preview}\n…"
        message = self.dialogs.get_text_textarea(
            f"Commit — {repo.path.name}",
            f"Commit message for `{repo.path}`:\n\n{preview}",
        )
        if message is None:
            self.add_line(f"⚪ {repo.path.name}: commit cancelled")
            return
        subject = " ".join(message.strip().splitlines()).strip()
        if not subject:
            self.add_line(f"❌ {repo.path.name}: empty commit message")
            return

        add_p = OnDiscardGitChanges.git_run(repo.path, "add", "-A")
        if add_p.returncode != 0:
            self.add_line(f"❌ {repo.path.name}: git add failed: {add_p.stderr.strip() or add_p.stdout}")
            return
        commit_p = OnDiscardGitChanges.git_run(repo.path, "commit", "-m", subject)
        if commit_p.returncode != 0:
            self.add_line(f"❌ {repo.path.name}: git commit failed: {commit_p.stderr.strip() or commit_p.stdout}")
            return
        self.add_line(f"✅ {repo.path.name}: committed — {subject}")
        self.show_toast(f"Committed {repo.path.name}")

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

    def _interactive_loop(self, dirty: list[DirtyRepo]) -> None:
        current = list(dirty)
        while True:
            if not current:
                self.add_line("✅ All configured Git repos are clean")
                self.show_toast("All Git repos are clean")
                self.show_result()
                return

            choices = [
                (
                    str(repo.path),
                    f"{repo.changed_count} change(s)\n" + "\n".join(repo.sample_lines),
                )
                for repo in current
            ]
            selected = self.dialogs.get_choice_from_list_with_descriptions(
                self.title,
                f"{len(current)} repository(ies) need a commit. Choose one:",
                choices,
            )
            if selected is None:
                self.add_line("Done.")
                self.show_result()
                return

            repo = next((item for item in current if str(item.path) == selected), None)
            if repo is None:
                current = self._scan_dirty_repos(self._configured_roots())
                continue

            action = self.dialogs.get_choice_from_described_cards(
                repo.path.name,
                f"`{repo.path}`",
                [
                    ("📂", self._ACTION_OPEN_DESKTOP, "Open this repository in GitHub Desktop"),
                    ("💾", self._ACTION_COMMIT, "Stage all changes and create a commit"),
                    ("↩️", self._ACTION_BACK, "Return to the dirty-repo list"),
                ],
            )
            if action is None or action == self._ACTION_BACK:
                current = self._scan_dirty_repos(self._configured_roots())
                continue
            if action == self._ACTION_OPEN_DESKTOP:
                ok, detail = self._open_github_desktop(repo.path)
                if ok:
                    self.add_line(f"📂 {repo.path.name}: opened in GitHub Desktop")
                    self.show_toast(f"Opened {repo.path.name}")
                else:
                    self.add_line(f"❌ {repo.path.name}: {detail}")
            elif action == self._ACTION_COMMIT:
                self._commit_repo(repo)

            current = self._scan_dirty_repos(self._configured_roots())
            if current != dirty:
                self._report_scan(self._configured_roots(), current)
            dirty = list(current)

    @staticmethod
    def _open_github_desktop(repo: Path) -> tuple[bool, str]:
        """Open `repo` in GitHub Desktop. Return `(ok, detail)`."""
        repo = repo.resolve()
        if not repo.is_dir():
            return False, f"Folder not found: {repo}"

        github_cli = shutil.which("github")
        if github_cli:
            proc = subprocess.run(
                [github_cli, str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                return True, github_cli
            detail = (proc.stderr or proc.stdout or "").strip()
            return False, detail or f"`github` exited with {proc.returncode}"

        if sys.platform == "win32":
            local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
            bat = Path(local) / "GitHubDesktop" / "bin" / "github.bat"
            if bat.is_file():
                proc = subprocess.run(
                    ["cmd", "/c", str(bat), str(repo)],  # noqa: S607
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc.returncode == 0:
                    return True, str(bat)
            exe = Path(local) / "GitHubDesktop" / "GitHubDesktop.exe"
            if exe.is_file():
                # Protocol open is more reliable than passing a bare path to the EXE.
                url = "x-github-client://openLocalRepo/" + quote(str(repo).replace("\\", "/"))
                os.startfile(url)  # noqa: S606
                return True, url
            return False, "GitHub Desktop not found (install it or add `github` to PATH)"

        return False, "GitHub Desktop CLI (`github`) not found on PATH"

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
