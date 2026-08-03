"""Fix titles in harrix.dev-style site article dual links inside Markdown notes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.site_article_links import (
    SiteLinkSettings,
    build_article_title_index,
    content_root_from_config,
    expected_site_url_from_repo,
    find_dual_links,
    normalize_url_for_compare,
    replace_dual_link_title,
)


class OnFixSiteArticleLinkTitles(ActionBase):
    """Fix titles in site article dual links in Markdown files.

    Scans notes for links of the form:

    `[title](https://github.com/.../slug/slug.md) | [↗️](https://site/...)`

    and replaces `title` with the article H1 from the content repositories folder
    (`paths_sites[0].input`). Missing articles and mismatched site URLs are reported.

    """

    icon = "🔗"
    title = "Fix site article link titles in …"
    cli_available = True
    cli_hint = "md fix-site-article-links"

    folder_path: Path | None = None

    @ActionBase.handle_exceptions("fixing site article link titles")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Fix site article dual-link titles in a notes folder."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting site article link title fix for path: {self.folder_path}")
            self._fix_titles_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("fixing site article link titles thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread."""
        self._fix_titles_common()

    @ActionBase.handle_exceptions("fixing site article link titles thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after the worker thread finishes."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

    def _fix_titles_common(self) -> None:
        """Scan Markdown files, fix dual-link titles, and log issues."""
        if self.folder_path is None:
            return

        content_root = content_root_from_config(self.config)
        if content_root is None:
            self.add_line("❌ Content repos folder not found. Set `paths_sites[0].input` in config.json.")
            return

        settings = SiteLinkSettings()
        self.add_line(f"📂 Content repos: {content_root}")
        title_index = build_article_title_index(content_root)
        self.add_line(f"📚 Indexed articles: {len(title_index)}")

        md_files = [
            path
            for path in Path(self.folder_path).rglob("*.md")
            if path.is_file() and not path.name.endswith(".g.md")
        ]

        fixed_count = 0
        missing_count = 0
        mismatch_count = 0
        checked_links = 0

        for md_path in h.file.iter_with_progress(md_files):
            try:
                original = md_path.read_text(encoding="utf-8")
            except OSError as exc:
                self.add_line(f"❌ {md_path}: cannot read ({exc})")
                continue

            matches = find_dual_links(original)
            if not matches:
                continue

            updated = original
            # Apply replacements from the end so earlier offsets stay valid.
            for match in reversed(matches):
                checked_links += 1
                key = (match.repo, match.slug)
                expected_site = expected_site_url_from_repo(match.repo, match.slug, settings)
                if expected_site is not None and normalize_url_for_compare(
                    match.site_url
                ) != normalize_url_for_compare(expected_site):
                    mismatch_count += 1
                    self.add_line(
                        f"⚠️ {md_path}: site URL mismatch for `{match.repo}/{match.slug}`\n"
                        f"  found:    {match.site_url}\n"
                        f"  expected: {expected_site}"
                    )

                title = title_index.get(key)
                if title is None:
                    missing_count += 1
                    self.add_line(
                        f"❌ {md_path}: article not found in content repos: "
                        f"`{match.repo}/{match.slug}/{match.slug}.md`"
                    )
                    continue

                if match.title == title:
                    continue

                updated = replace_dual_link_title(updated, match, title)
                fixed_count += 1
                self.add_line(f"✏️ {md_path}: `{match.title}` → `{title}`")

            if updated != original:
                md_path.write_text(updated, encoding="utf-8")

        self.add_line("")
        self.add_line(f"🔎 Dual links checked: {checked_links}")
        self.add_line(f"✏️ Titles fixed: {fixed_count}")
        self.add_line(f"❌ Missing articles: {missing_count}")
        self.add_line(f"⚠️ Site URL mismatches: {mismatch_count}")
        if missing_count == 0 and mismatch_count == 0 and fixed_count == 0:
            self.add_line(f"✅ No title changes needed in {self.folder_path}.")
