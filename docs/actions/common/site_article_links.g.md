---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `site_article_links.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ContentArticleRef`](#%EF%B8%8F-class-contentarticleref)
  - [⚙️ Method `github_blob_url`](#%EF%B8%8F-method-github_blob_url)
  - [⚙️ Method `repo_name`](#%EF%B8%8F-method-repo_name)
  - [⚙️ Method `site_url`](#%EF%B8%8F-method-site_url)
- [🏛️ Class `DualLinkMatch`](#%EF%B8%8F-class-duallinkmatch)
- [🏛️ Class `SiteLinkSettings`](#%EF%B8%8F-class-sitelinksettings)
- [🔧 Function `build_article_title_index`](#-function-build_article_title_index)
- [🔧 Function `content_root_from_config`](#-function-content_root_from_config)
- [🔧 Function `expected_site_url_from_repo`](#-function-expected_site_url_from_repo)
- [🔧 Function `extract_first_h1`](#-function-extract_first_h1)
- [🔧 Function `find_dual_links`](#-function-find_dual_links)
- [🔧 Function `normalize_url_for_compare`](#-function-normalize_url_for_compare)
- [🔧 Function `parse_content_repo_name`](#-function-parse_content_repo_name)
- [🔧 Function `parse_github_blob_url`](#-function-parse_github_blob_url)
- [🔧 Function `replace_dual_link_title`](#-function-replace_dual_link_title)

</details>

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
```

</details>

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
    body = markdown
    if body.startswith("\ufeff"):
        body = body[1:]
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

## 🔧 Function `normalize_url_for_compare`

```python
def normalize_url_for_compare(url: str) -> str
```

Normalize URL for equality checks (strip trailing slash, lowercase scheme/host).

<details>
<summary>Code:</summary>

```python
def normalize_url_for_compare(url: str) -> str:
    text = url.strip()
    if text.endswith("/"):
        text = text[:-1]
    return text
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
    if len(tokens) >= 2 and _LANG_RE.fullmatch(tokens[-1]):
        lang = tokens.pop().lower()
    if len(tokens) >= 2 and _YEAR_RE.fullmatch(tokens[-1]):
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
