"""Fix titles in site article dual links inside Markdown notes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.site_article_links import (
    build_article_title_index,
    content_root_from_config,
    ensure_article_permalink_yaml,
    expected_site_url_from_repo,
    find_dual_links,
    find_relative_site_links,
    format_dual_link,
    is_forbidden_cross_language_link,
    is_single_word_link_text,
    normalize_url_for_compare,
    parse_content_repo_name,
    replace_dual_link_title,
    replace_span,
    resolve_content_article_ref,
    site_link_settings_from_config,
)


class OnFixSiteArticleLinkTitles(ActionBase):
    """Fix titles in site article dual links in Markdown files.

    Scans notes for:

    1. Dual links `[title](github…) | [↗️](site…)` — updates `title` from article H1
       (skips non-empty single-word titles without spaces, e.g. `here`, `link`)
    2. Site-relative / site-absolute links like `[text](/games/dashes/)` — converts them
       to dual form with the article H1
    3. Content articles `{repo}/{slug}/{slug}.md` — checks/fixes/adds YAML
       `permalink-source` and `permalink`
    4. English content articles — reports links to Russian articles (does not rewrite them;
       skips converting relative `/ru/…` links to dual form)

    Content repositories come from `paths_sites[0].input`. Missing articles and
    mismatched site URLs are reported.

    """

    icon = "🔗"
    title = "Fix site article link titles in …"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site fix-article-links"

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
        """Scan Markdown files, convert relative site links, fix dual-link titles and YAML."""
        if self.folder_path is None:
            return

        content_root = content_root_from_config(self.config)
        if content_root is None:
            self.add_line("❌ Content repos folder not found. Set `paths_sites[0].input` in config.json.")
            return

        settings = site_link_settings_from_config(self.config)
        self.add_line(f"📂 Content repos: {content_root}")
        title_index = build_article_title_index(content_root)
        self.add_line(f"📚 Indexed articles: {len(title_index)}")

        md_files = [
            path for path in Path(self.folder_path).rglob("*.md") if path.is_file() and not path.name.endswith(".g.md")
        ]

        fixed_count = 0
        converted_count = 0
        permalink_yaml_count = 0
        missing_count = 0
        mismatch_count = 0
        cross_lang_count = 0
        checked_dual = 0
        checked_relative = 0
        checked_permalink_yaml = 0

        for md_path in h.file.iter_with_progress(md_files):
            try:
                original = md_path.read_text(encoding="utf-8")
            except OSError as exc:
                self.add_line(f"❌ {md_path}: cannot read ({exc})")
                continue

            updated = original

            article_ref = resolve_content_article_ref(md_path, settings)
            source_lang = article_ref.lang if article_ref is not None else None
            if article_ref is not None:
                checked_permalink_yaml += 1
                yaml_fix = ensure_article_permalink_yaml(updated, article_ref, settings)
                if yaml_fix.changes:
                    updated = yaml_fix.text
                    permalink_yaml_count += 1
                    changes = ", ".join(yaml_fix.changes)
                    self.add_line(f"📎 {md_path}: YAML permalinks ({changes})")

            relative_matches = find_relative_site_links(updated, settings)
            for match in reversed(relative_matches):
                checked_relative += 1
                loc = _location(md_path, updated, match.start)
                repo = match.ref.repo_name(settings)
                if source_lang is not None and is_forbidden_cross_language_link(source_lang, match.ref.lang):
                    cross_lang_count += 1
                    self.add_line(
                        f"⚠️ {loc}: English article must not link to Russian article "
                        f"`{repo}/{match.ref.slug}`\n"
                        f"  site: {match.target}"
                    )
                    continue

                key = (repo, match.ref.slug)
                title = title_index.get(key)
                if title is None:
                    missing_count += 1
                    self.add_line(
                        f"❌ {loc}: article not found for relative link `{match.target}` → "
                        f"`{repo}/{match.ref.slug}/{match.ref.slug}.md`"
                    )
                    continue

                dual = format_dual_link(title, match.ref, settings)
                updated = replace_span(updated, match.start, match.end, dual)
                converted_count += 1
                self.add_line(f"🔗 {loc}: `{match.target}` → dual link (`{title}`)")

            dual_matches = find_dual_links(updated)
            for match in reversed(dual_matches):
                checked_dual += 1
                loc = _location(md_path, updated, match.start)
                key = (match.repo, match.slug)
                target_parsed = parse_content_repo_name(match.repo, settings)
                if (
                    source_lang is not None
                    and target_parsed is not None
                    and is_forbidden_cross_language_link(source_lang, target_parsed.lang)
                ):
                    cross_lang_count += 1
                    self.add_line(
                        f"⚠️ {loc}: English article must not link to Russian article "
                        f"`{match.repo}/{match.slug}`\n"
                        f"  site: {match.site_url}"
                    )

                expected_site = expected_site_url_from_repo(match.repo, match.slug, settings)
                if expected_site is not None and normalize_url_for_compare(match.site_url) != normalize_url_for_compare(
                    expected_site
                ):
                    mismatch_count += 1
                    self.add_line(
                        f"⚠️ {loc}: site URL mismatch for `{match.repo}/{match.slug}`\n"
                        f"  found:    {match.site_url}\n"
                        f"  expected: {expected_site}"
                    )

                title = title_index.get(key)
                if title is None:
                    missing_count += 1
                    self.add_line(
                        f"❌ {loc}: article not found in content repos: `{match.repo}/{match.slug}/{match.slug}.md`"
                    )
                    continue

                if match.title == title:
                    continue

                if is_single_word_link_text(match.title):
                    continue

                updated = replace_dual_link_title(updated, match, title)
                fixed_count += 1
                self.add_line(f"✏️ {loc}: `{match.title}` → `{title}`")

            if updated != original:
                md_path.write_text(updated, encoding="utf-8")

        self.add_line("")
        self.add_line(f"🔎 Relative site links checked: {checked_relative}")
        self.add_line(f"🔗 Converted to dual links: {converted_count}")
        self.add_line(f"🔎 Dual links checked: {checked_dual}")
        self.add_line(f"✏️ Titles fixed: {fixed_count}")
        self.add_line(f"🔎 Content article YAML checked: {checked_permalink_yaml}")
        self.add_line(f"📎 Permalinks YAML fixed/added: {permalink_yaml_count}")
        self.add_line(f"❌ Missing articles: {missing_count}")
        self.add_line(f"⚠️ Site URL mismatches: {mismatch_count}")
        self.add_line(f"⚠️ EN→RU cross-language links: {cross_lang_count}")
        if (
            missing_count == 0
            and mismatch_count == 0
            and cross_lang_count == 0
            and fixed_count == 0
            and converted_count == 0
            and permalink_yaml_count == 0
        ):
            self.add_line(f"✅ No link changes needed in {self.folder_path}.")


def _line_col_at(text: str, offset: int) -> tuple[int, int]:
    """Return 1-based line and column for a character offset in `text`."""
    clamped = max(0, min(offset, len(text)))
    line = text.count("\n", 0, clamped) + 1
    last_newline = text.rfind("\n", 0, clamped)
    col = clamped - last_newline
    return line, col


def _location(path: Path, text: str, offset: int) -> str:
    """Format `path:line:col` for checker-style clickable locations."""
    line, col = _line_col_at(text, offset)
    return f"{path}:{line}:{col}"
