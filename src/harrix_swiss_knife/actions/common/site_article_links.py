"""Helpers for harrix.dev-style site article dual links."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_LANG_RE = re.compile(r"^(en|ru)$", re.IGNORECASE)
_YEAR_RE = re.compile(r"^\d{4}$")
_H1_RE = re.compile(r"^#\s+(.+)$")
_FRONTMATTER_RE = re.compile(r"\A---\r?\n[\s\S]*?\r?\n---\r?\n?", re.MULTILINE)
# Repo tail needs at least `{section}-{year|lang}` before optional suffix pops.
_MIN_REPO_TAIL_PARTS = 2

# [text](https://github.com/User/repo/blob/branch/slug/slug.md) | [↗️](https://site/...)
DUAL_LINK_RE = re.compile(
    r"\[(?P<title>[^\]]*)\]\("
    r"(?P<github>https://github\.com/(?P<user>[^/]+)/(?P<repo>[^/]+)/blob/[^/]+/"
    r"(?P<slug>[^/]+)/(?P=slug)\.md)"
    r"\)\s*\|\s*\[↗️\]\((?P<site>https?://[^)\s]+)\)"
)
# Any markdown link except images: [text](target)
_MD_LINK_RE = re.compile(r"(?<!!)\[(?P<title>[^\]]*)\]\((?P<target>[^)\s]+)\)")
_ASSET_EXT_RE = re.compile(
    r"\.(?:png|jpe?g|gif|svg|webp|avif|ico|md|pdf|zip|mp[34]|webm|mov|css|js)$",
    re.IGNORECASE,
)
_TOP_LEVEL_YAML_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


@dataclass(frozen=True, slots=True)
class ContentArticleRef:
    """Parsed content article coordinates."""

    section: str
    year: str | None
    lang: str
    slug: str

    def github_blob_url(self, settings: SiteLinkSettings) -> str:
        """Return GitHub blob URL for `{slug}/{slug}.md`."""
        repo = self.repo_name(settings)
        return f"https://github.com/{settings.github_user}/{repo}/blob/main/{self.slug}/{self.slug}.md"

    def repo_name(self, settings: SiteLinkSettings) -> str:
        """Return content repository folder/name for this article."""
        name = f"{settings.site_name}-{self.section}"
        if self.year:
            name += f"-{self.year}"
        if self.lang and self.lang != settings.default_language:
            name += f"-{self.lang}"
        return name

    def site_url(self, settings: SiteLinkSettings) -> str:
        """Return published site URL for this article."""
        segments = [self.lang or settings.default_language, self.section]
        if self.year:
            segments.append(self.year)
        segments.append(self.slug)
        return f"https://{settings.site_name}/{'/'.join(segments)}/"

    def submodule_relpath(self, settings: SiteLinkSettings) -> str:
        """Return site-repo relative path for this content repository (no slug).

        Example: `content/en/articles/2021` for `harrix.dev-articles-2021-en`.

        """
        segments = ["content", self.lang or settings.default_language, self.section]
        if self.year:
            segments.append(self.year)
        return "/".join(segments)


@dataclass(frozen=True, slots=True)
class DualLinkMatch:
    """One dual link occurrence inside a Markdown file."""

    start: int
    end: int
    title: str
    github_url: str
    site_url: str
    user: str
    repo: str
    slug: str


@dataclass(frozen=True, slots=True)
class PermalinkYamlFix:
    """Result of ensuring `permalink` / `permalink-source` in article YAML."""

    text: str
    changes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RelativeSiteLinkMatch:
    """One convertible site-relative or site-absolute Markdown link."""

    start: int
    end: int
    title: str
    target: str
    ref: ContentArticleRef


@dataclass(frozen=True, slots=True)
class SiteLinkSettings:
    """Defaults used when building or parsing site article links."""

    default_language: str = "ru"
    site_name: str = "harrix.dev"
    github_user: str = "Harrix"


def build_article_title_index(content_root: Path) -> dict[tuple[str, str], str]:
    """Index `(repo_name, slug) -> H1 title` under a content root folder."""
    index: dict[tuple[str, str], str] = {}
    if not content_root.is_dir():
        return index

    for repo_dir in sorted(content_root.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue
        for article_dir in sorted(repo_dir.iterdir()):
            if not article_dir.is_dir() or article_dir.name.startswith("."):
                continue
            md_path = article_dir / f"{article_dir.name}.md"
            if not md_path.is_file():
                continue
            try:
                text = md_path.read_text(encoding="utf-8")
            except OSError:
                continue
            title = extract_first_h1(text)
            if title:
                index[(repo_dir.name, article_dir.name)] = title
    return index


def content_root_from_config(config: dict) -> Path | None:
    """Resolve content repos root from `paths_sites[0].input`."""
    paths_sites = config.get("paths_sites")
    if not isinstance(paths_sites, list) or not paths_sites:
        return None
    first = paths_sites[0]
    if not isinstance(first, dict):
        return None
    raw = first.get("input")
    if not raw:
        return None
    path = Path(str(raw)).expanduser().resolve()
    return path if path.is_dir() else None


def ensure_article_permalink_yaml(
    markdown: str,
    ref: ContentArticleRef,
    settings: SiteLinkSettings,
) -> PermalinkYamlFix:
    """Check/fix/add `permalink-source` and `permalink` top-level YAML keys.

    Preserves the rest of the frontmatter text (no full YAML round-trip).

    """
    expected = {
        "permalink-source": ref.github_blob_url(settings),
        "permalink": ref.site_url(settings),
    }
    had_bom = markdown.startswith("\ufeff")
    body = markdown.removeprefix("\ufeff")
    fm_match = _FRONTMATTER_RE.match(body)
    if fm_match is None:
        yaml_block = "---\n" + "".join(f"{key}: {value}\n" for key, value in expected.items()) + "---\n\n"
        new_text = yaml_block + body.lstrip("\n")
        if had_bom:
            new_text = "\ufeff" + new_text
        return PermalinkYamlFix(text=new_text, changes=("permalink-source added", "permalink added"))

    fm_full = fm_match.group(0)
    newline = "\r\n" if "\r\n" in fm_full else "\n"
    inner = fm_full.strip().removeprefix("---").removesuffix("---").strip("\r\n")
    lines = inner.splitlines()
    key_line_indexes: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = _TOP_LEVEL_YAML_KEY_RE.match(line)
        if match is None:
            continue
        key_line_indexes[match.group(1)] = index

    changes: list[str] = []
    for key, value in expected.items():
        new_line = f"{key}: {value}"
        if key in key_line_indexes:
            index = key_line_indexes[key]
            current = _yaml_scalar_value(lines[index])
            if normalize_url_for_compare(current) == normalize_url_for_compare(value):
                continue
            lines[index] = new_line
            changes.append(f"{key} fixed")
        else:
            lines.append(new_line)
            changes.append(f"{key} added")

    if not changes:
        return PermalinkYamlFix(text=markdown, changes=())

    new_inner = newline.join(lines)
    new_fm = f"---{newline}{new_inner}{newline}---{newline}"
    new_text = new_fm + body[fm_match.end() :]
    if had_bom:
        new_text = "\ufeff" + new_text
    return PermalinkYamlFix(text=new_text, changes=tuple(changes))


def expected_site_url_from_repo(repo: str, slug: str, settings: SiteLinkSettings) -> str | None:
    """Build the expected site URL from a content repo name and slug."""
    parsed = parse_content_repo_name(repo, settings)
    if parsed is None:
        return None
    ref = ContentArticleRef(section=parsed.section, year=parsed.year, lang=parsed.lang, slug=slug)
    return ref.site_url(settings)


def extract_first_h1(markdown: str) -> str:
    """Return the first ATX H1 after optional YAML frontmatter."""
    body = markdown.removeprefix("\ufeff")
    fm_match = _FRONTMATTER_RE.match(body)
    if fm_match is not None:
        body = body[fm_match.end() :]

    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("<!--") and "-->" in line:
            continue
        h1_match = _H1_RE.fullmatch(line)
        if h1_match is not None and not line.startswith("##"):
            return h1_match.group(1).strip()
    return ""


def find_dual_links(text: str) -> list[DualLinkMatch]:
    """Return all dual-link matches in `text`."""
    return [
        DualLinkMatch(
            start=match.start(),
            end=match.end(),
            title=match.group("title"),
            github_url=match.group("github"),
            site_url=match.group("site"),
            user=match.group("user"),
            repo=match.group("repo"),
            slug=match.group("slug"),
        )
        for match in DUAL_LINK_RE.finditer(text)
    ]


def find_relative_site_links(text: str, settings: SiteLinkSettings) -> list[RelativeSiteLinkMatch]:
    """Return site-relative / site-absolute article links that are not already dual links.

    Matches forms like `[text](/games/dashes/)`, `[text](/ru/games/dashes/)`, and
    `[text](https://harrix.dev/ru/games/dashes/)`. Skips image links, asset paths,
    GitHub URLs, and spans already covered by dual links.

    """
    dual_spans = [(item.start, item.end) for item in find_dual_links(text)]
    results: list[RelativeSiteLinkMatch] = []
    for match in _MD_LINK_RE.finditer(text):
        start, end = match.start(), match.end()
        if any(span_start <= start < span_end for span_start, span_end in dual_spans):
            continue
        target = match.group("target").strip()
        if target.lower().startswith("https://github.com/") or target.lower().startswith("http://github.com/"):
            continue
        if _looks_like_asset_target(target):
            continue
        ref = parse_site_url_or_path(target, settings)
        if ref is None:
            continue
        results.append(
            RelativeSiteLinkMatch(
                start=start,
                end=end,
                title=match.group("title"),
                target=target,
                ref=ref,
            )
        )
    return results


def format_dual_link(title: str, ref: ContentArticleRef, settings: SiteLinkSettings) -> str:
    """Build `[title](github) | [↗️](site)` for an article ref."""
    return f"[{title}]({ref.github_blob_url(settings)}) | [↗️]({ref.site_url(settings)})"


def github_https_url_for_repo(repo_name: str, settings: SiteLinkSettings) -> str:
    """Return `https://github.com/{user}/{repo}` for a content repository name."""
    return f"https://github.com/{settings.github_user}/{repo_name}"


def is_forbidden_cross_language_link(source_lang: str, target_lang: str) -> bool:
    """Return `True` when an English article links to a Russian one.

    English content articles must not point at the Russian site section.

    """
    return source_lang == "en" and target_lang == "ru"


def is_single_word_link_text(text: str) -> bool:
    """Return `True` when link text is one non-empty token with no whitespace.

    Used to keep short placeholders like `here`, `link`, `article` instead of
    replacing them with the full article H1.

    """
    stripped = text.strip()
    if not stripped:
        return False
    return not any(char.isspace() for char in stripped)


def normalize_url_for_compare(url: str) -> str:
    """Normalize URL for equality checks (strip trailing slash, lowercase scheme/host)."""
    return url.strip().removesuffix("/")


def parse_content_repo_name(repo_name: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
    """Parse `{site}-{section}[-{year}][-{lang}]` into article coordinates (slug empty)."""
    prefix = f"{settings.site_name}-"
    if not repo_name.startswith(prefix):
        return None
    tokens = [token for token in repo_name[len(prefix) :].split("-") if token]
    if not tokens:
        return None
    lang = settings.default_language
    year: str | None = None
    if len(tokens) >= _MIN_REPO_TAIL_PARTS and _LANG_RE.fullmatch(tokens[-1]):
        lang = tokens.pop().lower()
    if len(tokens) >= _MIN_REPO_TAIL_PARTS and _YEAR_RE.fullmatch(tokens[-1]):
        year = tokens.pop()
    section = "-".join(tokens)
    if not section:
        return None
    return ContentArticleRef(section=section, year=year, lang=lang, slug="")


def parse_github_blob_url(url: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
    """Parse a GitHub blob URL for `{slug}/{slug}.md` under a content repo."""
    match = re.fullmatch(
        r"https?://github\.com/[^/]+/([^/]+)/blob/[^/]+/([^/]+)/\2\.md/?(?:[?#].*)?",
        url.strip(),
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    parsed = parse_content_repo_name(match.group(1), settings)
    if parsed is None:
        return None
    return ContentArticleRef(section=parsed.section, year=parsed.year, lang=parsed.lang, slug=match.group(2))


def parse_site_url_or_path(raw: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
    """Parse `/games/dashes/`, `/ru/articles/2017/slug/`, or full site URLs into a ref."""
    path_text = raw.strip()
    if not path_text:
        return None

    site_https = f"https://{settings.site_name}/"
    site_http = f"http://{settings.site_name}/"
    lower = path_text.lower()
    if lower.startswith(site_https.lower()):
        path_text = path_text[len(site_https) :]
    elif lower.startswith(site_http.lower()):
        path_text = path_text[len(site_http) :]
    elif path_text.startswith("/"):
        path_text = path_text.lstrip("/")
    else:
        return None

    path_text = path_text.split("?", 1)[0].split("#", 1)[0].strip("/")
    parts = [part for part in path_text.split("/") if part]
    if len(parts) < _MIN_REPO_TAIL_PARTS:
        return None

    lang = settings.default_language
    if _LANG_RE.fullmatch(parts[0]):
        lang = parts.pop(0).lower()
    if len(parts) < _MIN_REPO_TAIL_PARTS:
        return None

    slug = parts.pop()
    year: str | None = None
    if len(parts) >= _MIN_REPO_TAIL_PARTS and _YEAR_RE.fullmatch(parts[-1]):
        year = parts.pop()
    section = "-".join(parts)
    if not section or not slug or _ASSET_EXT_RE.search(slug):
        return None
    return ContentArticleRef(section=section, year=year, lang=lang, slug=slug)


def replace_dual_link_title(original: str, match: DualLinkMatch, new_title: str) -> str:
    """Return `original` with the dual-link title at `match` replaced by `new_title`."""
    replacement = f"[{new_title}]({match.github_url}) | [↗️]({match.site_url})"
    return original[: match.start] + replacement + original[match.end :]


def replace_span(original: str, start: int, end: int, replacement: str) -> str:
    """Return `original` with `[start:end]` replaced by `replacement`."""
    return original[:start] + replacement + original[end:]


def resolve_content_article_ref(md_path: Path, settings: SiteLinkSettings) -> ContentArticleRef | None:
    """Return article ref when `md_path` is `{repo}/{slug}/{slug}.md` under a content repo name."""
    path = md_path.resolve()
    if path.suffix.lower() != ".md":
        return None
    slug = path.stem
    if path.parent.name != slug:
        return None
    repo_name = path.parent.parent.name
    parsed = parse_content_repo_name(repo_name, settings)
    if parsed is None:
        return None
    return ContentArticleRef(section=parsed.section, year=parsed.year, lang=parsed.lang, slug=slug)


def site_link_settings_from_config(config: dict) -> SiteLinkSettings:
    """Build `SiteLinkSettings` from optional config keys (with defaults)."""
    defaults = SiteLinkSettings()
    site_name = config.get("site_name") or defaults.site_name
    github_user = config.get("github_user") or defaults.github_user
    default_language = config.get("site_default_language") or defaults.default_language
    return SiteLinkSettings(
        site_name=str(site_name),
        github_user=str(github_user),
        default_language=str(default_language),
    )


def site_repo_from_config(config: dict) -> Path | None:
    """Resolve main site Git repository path from `path_site_repo`."""
    raw = config.get("path_site_repo")
    if not raw:
        return None
    path = Path(str(raw)).expanduser().resolve()
    return path if path.is_dir() else None


def _looks_like_asset_target(target: str) -> bool:
    """Return `True` when `target` looks like a static asset path, not an article permalink."""
    path_only = target.split("?", 1)[0].split("#", 1)[0]
    return _ASSET_EXT_RE.search(path_only) is not None


def _yaml_scalar_value(line: str) -> str:
    """Extract a top-level YAML scalar value from a `key: value` line."""
    match = _TOP_LEVEL_YAML_KEY_RE.match(line)
    if match is None:
        return ""
    value = match.group(2).strip()
    min_quoted_len = 2
    if len(value) >= min_quoted_len and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value
