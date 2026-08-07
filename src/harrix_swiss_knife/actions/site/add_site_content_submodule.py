"""Add a content repository as a Git submodule of the main site repo."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.site_article_links import (
    content_root_from_config,
    github_https_url_for_repo,
    parse_content_repo_name,
    site_link_settings_from_config,
    site_repo_from_config,
)


class OnAddSiteContentSubmodule(ActionBase):
    """Add a content folder as a Git submodule under the site repository.

    Picks a local content repo folder (e.g. `…/harrix.dev-articles-2021-en`),
    derives `git submodule add https://github.com/{user}/{repo} content/{lang}/{section}/{year}`,
    and runs it in `path_site_repo` from config.

    """

    icon = "📦"
    title = "Add site content submodule…"
    description = "Add content repo as git submodule in the main site repository"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site add-submodule"

    @ActionBase.handle_exceptions("adding site content submodule")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Select a content repo folder and add it as a submodule of the site repo."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        site_repo = site_repo_from_config(self.config)
        if site_repo is None:
            self.add_line("❌ Site repository not found. Set `path_site_repo` in config.json.")
            if not noninteractive:
                self.show_result()
            return

        content_root = content_root_from_config(self.config)
        if folder_path is not None:
            content_folder = Path(folder_path).resolve()
        else:
            folder_choices = self._content_repo_choices(content_root)
            default_path = str(content_root) if content_root is not None else str(site_repo)
            content_folder = self.dialogs.get_folder_with_choice_option(folder_choices, default_path)
        if not content_folder:
            return
        content_folder = Path(content_folder).resolve()
        if not content_folder.is_dir():
            self.add_line(f"❌ Not a folder: {content_folder}")
            if not noninteractive:
                self.show_result()
            return

        settings = site_link_settings_from_config(self.config)
        parsed = parse_content_repo_name(content_folder.name, settings)
        if parsed is None:
            self.add_line(
                f"❌ Cannot parse content repo name `{content_folder.name}` "
                f"(expected `{settings.site_name}-{{section}}[-{{year}}][-{{lang}}]`)."
            )
            if not noninteractive:
                self.show_result()
            return

        repo_url = github_https_url_for_repo(content_folder.name, settings)
        relpath = parsed.submodule_relpath(settings)
        command = ["git", "submodule", "add", repo_url, relpath]

        self.add_line(f"📂 Site repo: {site_repo}")
        self.add_line(f"📁 Content folder: {content_folder}")
        self.add_line(f"🔗 URL: {repo_url}")
        self.add_line(f"📌 Path: {relpath}")
        self.add_line(f"▶️ Command: git submodule add {repo_url} {relpath}")

        if not noninteractive:
            confirmed = self.dialogs.get_yes_no_question(
                self.title,
                (f"Run in `{site_repo}`?\n\ngit submodule add {repo_url} {relpath}"),
                default_yes=True,
            )
            if not confirmed:
                self.add_line("ℹ️ Cancelled.")  # noqa: RUF001
                self.show_result()
                return

        output = h.dev.run_command(command, cwd=str(site_repo))
        self.add_line(output or "✅ Done (no output).")
        if not noninteractive:
            self.show_result()

    @staticmethod
    def _content_repo_choices(content_root: Path | None) -> list[str]:
        """List immediate child directories under the content root for the picker."""
        if content_root is None or not content_root.is_dir():
            return []
        return sorted(str(path) for path in content_root.iterdir() if path.is_dir() and not path.name.startswith("."))
