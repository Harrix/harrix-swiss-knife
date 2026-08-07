---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `site_article_links.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `DUAL_LINK_RE`](#-constant-dual_link_re)
- [🏛️ Class `ContentArticleRef`](#%EF%B8%8F-class-contentarticleref)
  - [📎 Attribute `section`](#-attribute-section)
  - [📎 Attribute `year`](#-attribute-year)
  - [📎 Attribute `lang`](#-attribute-lang)
  - [📎 Attribute `slug`](#-attribute-slug)
  - [⚙️ Method `github_blob_url`](#%EF%B8%8F-method-github_blob_url)
  - [⚙️ Method `repo_name`](#%EF%B8%8F-method-repo_name)
  - [⚙️ Method `site_url`](#%EF%B8%8F-method-site_url)
  - [⚙️ Method `submodule_relpath`](#%EF%B8%8F-method-submodule_relpath)
- [🏛️ Class `DualLinkMatch`](#%EF%B8%8F-class-duallinkmatch)
  - [📎 Attribute `start`](#-attribute-start)
  - [📎 Attribute `end`](#-attribute-end)
  - [📎 Attribute `title`](#-attribute-title)
  - [📎 Attribute `github_url`](#-attribute-github_url)
  - [📎 Attribute `site_url`](#-attribute-site_url)
  - [📎 Attribute `user`](#-attribute-user)
  - [📎 Attribute `repo`](#-attribute-repo)
  - [📎 Attribute `slug`](#-attribute-slug-1)
- [🏛️ Class `PermalinkYamlFix`](#%EF%B8%8F-class-permalinkyamlfix)
  - [📎 Attribute `text`](#-attribute-text)
  - [📎 Attribute `changes`](#-attribute-changes)
- [🏛️ Class `RelativeSiteLinkMatch`](#%EF%B8%8F-class-relativesitelinkmatch)
  - [📎 Attribute `start`](#-attribute-start-1)
  - [📎 Attribute `end`](#-attribute-end-1)
  - [📎 Attribute `title`](#-attribute-title-1)
  - [📎 Attribute `target`](#-attribute-target)
  - [📎 Attribute `ref`](#-attribute-ref)
- [🏛️ Class `SiteLinkSettings`](#%EF%B8%8F-class-sitelinksettings)
  - [📎 Attribute `default_language`](#-attribute-default_language)
  - [📎 Attribute `site_name`](#-attribute-site_name)
  - [📎 Attribute `github_user`](#-attribute-github_user)
- [🔧 Function `build_article_title_index`](#-function-build_article_title_index)
- [🔧 Function `content_root_from_config`](#-function-content_root_from_config)
- [🔧 Function `ensure_article_permalink_yaml`](#-function-ensure_article_permalink_yaml)
- [🔧 Function `expected_site_url_from_repo`](#-function-expected_site_url_from_repo)
- [🔧 Function `extract_first_h1`](#-function-extract_first_h1)
- [🔧 Function `find_dual_links`](#-function-find_dual_links)
- [🔧 Function `find_relative_site_links`](#-function-find_relative_site_links)
- [🔧 Function `format_dual_link`](#-function-format_dual_link)
- [🔧 Function `github_https_url_for_repo`](#-function-github_https_url_for_repo)
- [🔧 Function `is_forbidden_cross_language_link`](#-function-is_forbidden_cross_language_link)
- [🔧 Function `is_single_word_link_text`](#-function-is_single_word_link_text)
- [🔧 Function `normalize_url_for_compare`](#-function-normalize_url_for_compare)
- [🔧 Function `parse_content_repo_name`](#-function-parse_content_repo_name)
- [🔧 Function `parse_github_blob_url`](#-function-parse_github_blob_url)
- [🔧 Function `parse_site_url_or_path`](#-function-parse_site_url_or_path)
- [🔧 Function `replace_dual_link_title`](#-function-replace_dual_link_title)
- [🔧 Function `replace_span`](#-function-replace_span)
- [🔧 Function `resolve_content_article_ref`](#-function-resolve_content_article_ref)
- [🔧 Function `site_link_settings_from_config`](#-function-site_link_settings_from_config)
- [🔧 Function `site_repo_from_config`](#-function-site_repo_from_config)

</details>

## 📎 Constant `DUAL_LINK_RE`

```python
DUAL_LINK_RE = re.compile('\\[(?P<title>[^\\]]*)\\]\\((?P<github>https://github\\.com/(?P<user>[^/]+)/(?P<repo>[^/]+)/blob/[^/]+/(?P<slug>[^/]+)/(?P=slug)\\.md)\\)\\s*\\|\\s*\\[↗️\\]\\((?P<site>https?://[^)\\s]+)\\)')
```

_No docstring provided._

## 🏛️ Class `ContentArticleRef`

```python
class ContentArticleRef
```

Parsed content article coordinates.

<details>
<summary>Code:</summary>

```python
class ContentArticleRef:

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
```

</details>

### 📎 Attribute `section`

```python
section: str
```

_No docstring provided._

### 📎 Attribute `year`

```python
year: str | None
```

_No docstring provided._

### 📎 Attribute `lang`

```python
lang: str
```

_No docstring provided._

### 📎 Attribute `slug`

```python
slug: str
```

_No docstring provided._

### ⚙️ Method `github_blob_url`

```python
def github_blob_url(self, settings: SiteLinkSettings) -> str
```

Return GitHub blob URL for `{slug}/{slug}.md`.

<details>
<summary>Code:</summary>

```python
def github_blob_url(self, settings: SiteLinkSettings) -> str:
        repo = self.repo_name(settings)
        return f"https://github.com/{settings.github_user}/{repo}/blob/main/{self.slug}/{self.slug}.md"
```

</details>

### ⚙️ Method `repo_name`

```python
def repo_name(self, settings: SiteLinkSettings) -> str
```

Return content repository folder/name for this article.

<details>
<summary>Code:</summary>

```python
def repo_name(self, settings: SiteLinkSettings) -> str:
        name = f"{settings.site_name}-{self.section}"
        if self.year:
            name += f"-{self.year}"
        if self.lang and self.lang != settings.default_language:
            name += f"-{self.lang}"
        return name
```

</details>

### ⚙️ Method `site_url`

```python
def site_url(self, settings: SiteLinkSettings) -> str
```

Return published site URL for this article.

<details>
<summary>Code:</summary>

```python
def site_url(self, settings: SiteLinkSettings) -> str:
        segments = [self.lang or settings.default_language, self.section]
        if self.year:
            segments.append(self.year)
        segments.append(self.slug)
        return f"https://{settings.site_name}/{'/'.join(segments)}/"
```

</details>

### ⚙️ Method `submodule_relpath`

```python
def submodule_relpath(self, settings: SiteLinkSettings) -> str
```

Return site-repo relative path for this content repository (no slug).

Example: `content/en/articles/2021` for `harrix.dev-articles-2021-en`.

<details>
<summary>Code:</summary>

```python
def submodule_relpath(self, settings: SiteLinkSettings) -> str:
        segments = ["content", self.lang or settings.default_language, self.section]
        if self.year:
            segments.append(self.year)
        return "/".join(segments)
```

</details>

## 🏛️ Class `DualLinkMatch`

```python
class DualLinkMatch
```

One dual link occurrence inside a Markdown file.

<details>
<summary>Code:</summary>

```python
class DualLinkMatch:

    start: int
    end: int
    title: str
    github_url: str
    site_url: str
    user: str
    repo: str
    slug: str
```

</details>

### 📎 Attribute `start`

```python
start: int
```

_No docstring provided._

### 📎 Attribute `end`

```python
end: int
```

_No docstring provided._

### 📎 Attribute `title`

```python
title: str
```

_No docstring provided._

### 📎 Attribute `github_url`

```python
github_url: str
```

_No docstring provided._

### 📎 Attribute `site_url`

```python
site_url: str
```

_No docstring provided._

### 📎 Attribute `user`

```python
user: str
```

_No docstring provided._

### 📎 Attribute `repo`

```python
repo: str
```

_No docstring provided._

### 📎 Attribute `slug`

```python
slug: str
```

_No docstring provided._

## 🏛️ Class `PermalinkYamlFix`

```python
class PermalinkYamlFix
```

Result of ensuring `permalink` / `permalink-source` in article YAML.

<details>
<summary>Code:</summary>

```python
class PermalinkYamlFix:

    text: str
    changes: tuple[str, ...]
```

</details>

### 📎 Attribute `text`

```python
text: str
```

_No docstring provided._

### 📎 Attribute `changes`

```python
changes: tuple[str, ...]
```

_No docstring provided._

## 🏛️ Class `RelativeSiteLinkMatch`

```python
class RelativeSiteLinkMatch
```

One convertible site-relative or site-absolute Markdown link.

<details>
<summary>Code:</summary>

```python
class RelativeSiteLinkMatch:

    start: int
    end: int
    title: str
    target: str
    ref: ContentArticleRef
```

</details>

### 📎 Attribute `start`

```python
start: int
```

_No docstring provided._

### 📎 Attribute `end`

```python
end: int
```

_No docstring provided._

### 📎 Attribute `title`

```python
title: str
```

_No docstring provided._

### 📎 Attribute `target`

```python
target: str
```

_No docstring provided._

### 📎 Attribute `ref`

```python
ref: ContentArticleRef
```

_No docstring provided._

## 🏛️ Class `SiteLinkSettings`

```python
class SiteLinkSettings
```

Defaults used when building or parsing site article links.

<details>
<summary>Code:</summary>

```python
class SiteLinkSettings:

    default_language: str = "ru"
    site_name: str = "harrix.dev"
    github_user: str = "Harrix"
```

</details>

### 📎 Attribute `default_language`

```python
default_language: str = 'ru'
```

_No docstring provided._

### 📎 Attribute `site_name`

```python
site_name: str = 'harrix.dev'
```

_No docstring provided._

### 📎 Attribute `github_user`

```python
github_user: str = 'Harrix'
```

_No docstring provided._

## 🔧 Function `build_article_title_index`

```python
def build_article_title_index(content_root: Path) -> dict[tuple[str, str], str]
```

Index `(repo_name, slug) -> H1 title` under a content root folder.

<details>
<summary>Code:</summary>

```python
def build_article_title_index(content_root: Path) -> dict[tuple[str, str], str]:
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
```

</details>

## 🔧 Function `content_root_from_config`

```python
def content_root_from_config(config: dict) -> Path | None
```

Resolve content repos root from `paths_sites[0].input`.

<details>
<summary>Code:</summary>

```python
def content_root_from_config(config: dict) -> Path | None:
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
```

</details>

## 🔧 Function `ensure_article_permalink_yaml`

```python
def ensure_article_permalink_yaml(markdown: str, ref: ContentArticleRef, settings: SiteLinkSettings) -> PermalinkYamlFix
```

Check/fix/add `permalink-source` and `permalink` top-level YAML keys.

Preserves the rest of the frontmatter text (no full YAML round-trip).

<details>
<summary>Code:</summary>

```python
def ensure_article_permalink_yaml(
    markdown: str,
    ref: ContentArticleRef,
    settings: SiteLinkSettings,
) -> PermalinkYamlFix:
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
```

</details>

## 🔧 Function `expected_site_url_from_repo`

```python
def expected_site_url_from_repo(repo: str, slug: str, settings: SiteLinkSettings) -> str | None
```

Build the expected site URL from a content repo name and slug.

<details>
<summary>Code:</summary>

```python
def expected_site_url_from_repo(repo: str, slug: str, settings: SiteLinkSettings) -> str | None:
    parsed = parse_content_repo_name(repo, settings)
    if parsed is None:
        return None
    ref = ContentArticleRef(section=parsed.section, year=parsed.year, lang=parsed.lang, slug=slug)
    return ref.site_url(settings)
```

</details>

## 🔧 Function `extract_first_h1`

```python
def extract_first_h1(markdown: str) -> str
```

Return the first ATX H1 after optional YAML frontmatter.

<details>
<summary>Code:</summary>

````python
def extract_first_h1(markdown: str) -> str:
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
````

</details>

## 🔧 Function `find_dual_links`

```python
def find_dual_links(text: str) -> list[DualLinkMatch]
```

Return all dual-link matches in `text`.

<details>
<summary>Code:</summary>

```python
def find_dual_links(text: str) -> list[DualLinkMatch]:
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
```

</details>

## 🔧 Function `find_relative_site_links`

```python
def find_relative_site_links(text: str, settings: SiteLinkSettings) -> list[RelativeSiteLinkMatch]
```

Return site-relative / site-absolute article links that are not already dual links.

Matches forms like `[text](/games/dashes/)`, `[text](/ru/games/dashes/)`, and
`[text](https://harrix.dev/ru/games/dashes/)`. Skips image links, asset paths,
GitHub URLs, and spans already covered by dual links.

<details>
<summary>Code:</summary>

```python
def find_relative_site_links(text: str, settings: SiteLinkSettings) -> list[RelativeSiteLinkMatch]:
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
```

</details>

## 🔧 Function `format_dual_link`

```python
def format_dual_link(title: str, ref: ContentArticleRef, settings: SiteLinkSettings) -> str
```

Build `[title](github) | [↗️](site)` for an article ref.

<details>
<summary>Code:</summary>

```python
def format_dual_link(title: str, ref: ContentArticleRef, settings: SiteLinkSettings) -> str:
    return f"[{title}]({ref.github_blob_url(settings)}) | [↗️]({ref.site_url(settings)})"
```

</details>

## 🔧 Function `github_https_url_for_repo`

```python
def github_https_url_for_repo(repo_name: str, settings: SiteLinkSettings) -> str
```

Return `https://github.com/{user}/{repo}` for a content repository name.

<details>
<summary>Code:</summary>

```python
def github_https_url_for_repo(repo_name: str, settings: SiteLinkSettings) -> str:
    return f"https://github.com/{settings.github_user}/{repo_name}"
```

</details>

## 🔧 Function `is_forbidden_cross_language_link`

```python
def is_forbidden_cross_language_link(source_lang: str, target_lang: str) -> bool
```

Return `True` when an English article links to a Russian one.

English content articles must not point at the Russian site section.

<details>
<summary>Code:</summary>

```python
def is_forbidden_cross_language_link(source_lang: str, target_lang: str) -> bool:
    return source_lang == "en" and target_lang == "ru"
```

</details>

## 🔧 Function `is_single_word_link_text`

```python
def is_single_word_link_text(text: str) -> bool
```

Return `True` when link text is one non-empty token with no whitespace.

Used to keep short placeholders like `here`, `link`, `article` instead of
replacing them with the full article H1.

<details>
<summary>Code:</summary>

```python
def is_single_word_link_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    return not any(char.isspace() for char in stripped)
```

</details>

## 🔧 Function `normalize_url_for_compare`

```python
def normalize_url_for_compare(url: str) -> str
```

Normalize URL for equality checks (strip trailing slash, lowercase scheme/host).

<details>
<summary>Code:</summary>

```python
def normalize_url_for_compare(url: str) -> str:
    return url.strip().removesuffix("/")
```

</details>

## 🔧 Function `parse_content_repo_name`

```python
def parse_content_repo_name(repo_name: str, settings: SiteLinkSettings) -> ContentArticleRef | None
```

Parse `{site}-{section}[-{year}][-{lang}]` into article coordinates (slug empty).

<details>
<summary>Code:</summary>

```python
def parse_content_repo_name(repo_name: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
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
```

</details>

## 🔧 Function `parse_github_blob_url`

```python
def parse_github_blob_url(url: str, settings: SiteLinkSettings) -> ContentArticleRef | None
```

Parse a GitHub blob URL for `{slug}/{slug}.md` under a content repo.

<details>
<summary>Code:</summary>

```python
def parse_github_blob_url(url: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
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
```

</details>

## 🔧 Function `parse_site_url_or_path`

```python
def parse_site_url_or_path(raw: str, settings: SiteLinkSettings) -> ContentArticleRef | None
```

Parse `/games/dashes/`, `/ru/articles/2017/slug/`, or full site URLs into a ref.

<details>
<summary>Code:</summary>

```python
def parse_site_url_or_path(raw: str, settings: SiteLinkSettings) -> ContentArticleRef | None:
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
```

</details>

## 🔧 Function `replace_dual_link_title`

```python
def replace_dual_link_title(original: str, match: DualLinkMatch, new_title: str) -> str
```

Return `original` with the dual-link title at `match` replaced by `new_title`.

<details>
<summary>Code:</summary>

```python
def replace_dual_link_title(original: str, match: DualLinkMatch, new_title: str) -> str:
    replacement = f"[{new_title}]({match.github_url}) | [↗️]({match.site_url})"
    return original[: match.start] + replacement + original[match.end :]
```

</details>

## 🔧 Function `replace_span`

```python
def replace_span(original: str, start: int, end: int, replacement: str) -> str
```

Return `original` with `[start:end]` replaced by `replacement`.

<details>
<summary>Code:</summary>

```python
def replace_span(original: str, start: int, end: int, replacement: str) -> str:
    return original[:start] + replacement + original[end:]
```

</details>

## 🔧 Function `resolve_content_article_ref`

```python
def resolve_content_article_ref(md_path: Path, settings: SiteLinkSettings) -> ContentArticleRef | None
```

Return article ref when `md_path` is `{repo}/{slug}/{slug}.md` under a content repo name.

<details>
<summary>Code:</summary>

```python
def resolve_content_article_ref(md_path: Path, settings: SiteLinkSettings) -> ContentArticleRef | None:
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
```

</details>

## 🔧 Function `site_link_settings_from_config`

```python
def site_link_settings_from_config(config: dict) -> SiteLinkSettings
```

Build `SiteLinkSettings` from optional config keys (with defaults).

<details>
<summary>Code:</summary>

```python
def site_link_settings_from_config(config: dict) -> SiteLinkSettings:
    defaults = SiteLinkSettings()
    site_name = config.get("site_name") or defaults.site_name
    github_user = config.get("github_user") or defaults.github_user
    default_language = config.get("site_default_language") or defaults.default_language
    return SiteLinkSettings(
        site_name=str(site_name),
        github_user=str(github_user),
        default_language=str(default_language),
    )
```

</details>

## 🔧 Function `site_repo_from_config`

```python
def site_repo_from_config(config: dict) -> Path | None
```

Resolve main site Git repository path from `path_site_repo`.

<details>
<summary>Code:</summary>

```python
def site_repo_from_config(config: dict) -> Path | None:
    raw = config.get("path_site_repo")
    if not raw:
        return None
    path = Path(str(raw)).expanduser().resolve()
    return path if path.is_dir() else None
```

</details>
