"""Pull latest main in every Git submodule of the site repository."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.site_article_links import site_repo_from_config

_PULL_COMMAND = ["git", "submodule", "foreach", "git", "pull", "origin", "main"]


class OnPullSiteSubmodules(ActionBase):
    """Run `git submodule foreach git pull origin main` in the site repository.

    Uses `path_site_repo` from config (or an explicit folder from CLI).

    """

    icon = "⬇️"
    title = "Pull site submodules"
    description = "git submodule foreach git pull origin main in the site repo"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site pull-submodules"

    site_repo: Path | None = None

    @ActionBase.handle_exceptions("pulling site submodules")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Pull `origin main` in each submodule of the site Git repository."""
        if folder_path is not None:
            site_repo = Path(folder_path).resolve()
            if not site_repo.is_dir():
                self.add_line(f"❌ Not a folder: {site_repo}")
                if not noninteractive:
                    self.show_result()
                return
        else:
            site_repo = site_repo_from_config(self.config)
            if site_repo is None:
                self.add_line("❌ Site repository not found. Set `path_site_repo` in config.json.")
                if not noninteractive:
                    self.show_result()
                return

        self.site_repo = site_repo

        if noninteractive:
            self._pull_submodules()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("pulling site submodules thread")
    def in_thread(self) -> str | None:
        """Pull submodules in a worker thread."""
        self._pull_submodules()
        return f"{self.title} completed"

    @ActionBase.handle_exceptions("pulling site submodules thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after the worker finishes."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _pull_submodules(self) -> None:
        """Run `git submodule foreach git pull origin main` in `site_repo`."""
        if self.site_repo is None:
            return

        self.add_line(f"📂 Site repo: {self.site_repo}")
        self.add_line("▶️ Command: git submodule foreach git pull origin main")

        output = h.dev.run_command(_PULL_COMMAND, cwd=str(self.site_repo))
        self.add_line(output or "✅ Done (no output).")
