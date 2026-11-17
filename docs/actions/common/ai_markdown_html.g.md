---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_markdown_html.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `adapt_math_for_harrix_katex`](#-function-adapt_math_for_harrix_katex)
- [🔧 Function `build_ai_answer_html`](#-function-build_ai_answer_html)
- [🔧 Function `markdown_to_article_html`](#-function-markdown_to_article_html)
- [🔧 Function `normalize_ai_latex_delimiters`](#-function-normalize_ai_latex_delimiters)
- [🔧 Function `resolve_html_template_dist`](#-function-resolve_html_template_dist)

</details>

## 🔧 Function `adapt_math_for_harrix_katex`

```python
def adapt_math_for_harrix_katex(content_html: str) -> str
```

Map mdit-py dollarmath markup to Harrix `.tex[data-expr]` nodes.

<details>
<summary>Code:</summary>

```python
def adapt_math_for_harrix_katex(content_html: str) -> str:

    def _to_tex(match: re.Match[str], *, block: bool) -> str:
        expr = html.unescape(match.group(1)).strip()
        if not expr:
            return ""
        escaped = html.escape(expr, quote=True)
        tag = "div" if block else "span"
        return f'<{tag} class="tex" data-expr="{escaped}"></{tag}>'

    html_out = _MATH_INLINE_RE.sub(lambda m: _to_tex(m, block=False), content_html)
    return _MATH_BLOCK_RE.sub(lambda m: _to_tex(m, block=True), html_out)
```

</details>

## 🔧 Function `build_ai_answer_html`

```python
def build_ai_answer_html(markdown: str, *, dist_dir: Path, title: str = 'Ask AI answer') -> str
```

Fill `blank.html` with rendered Markdown for WebView display.

<details>
<summary>Code:</summary>

```python
def build_ai_answer_html(markdown: str, *, dist_dir: Path, title: str = "Ask AI answer") -> str:
    blank = (dist_dir / "blank.html").read_text(encoding="utf-8")
    body = adapt_math_for_harrix_katex(markdown_to_article_html(markdown))
    indented = "\n".join(f"        {line}" if line else "" for line in body.splitlines())
    content_block = _CONTENT_SHELL.format(body=indented)
    if not _CONTENT_BLOCK_RE.search(blank):
        msg = f"blank.html missing h-ssg content markers: {dist_dir / 'blank.html'}"
        raise ValueError(msg)
    # Replacement must be a callable: body HTML may contain LaTeX backslashes.
    page = _CONTENT_BLOCK_RE.sub(lambda _match: content_block, blank, count=1)
    safe_title = html.escape(title, quote=False)
    return _TITLE_RE.sub(rf"\1{safe_title}\3", page, count=1)
```

</details>

## 🔧 Function `markdown_to_article_html`

```python
def markdown_to_article_html(markdown: str) -> str
```

Render Markdown to article-body HTML via harrix-pyssg (GFM + dollarmath).

<details>
<summary>Code:</summary>

```python
def markdown_to_article_html(markdown: str) -> str:
    text = normalize_ai_latex_delimiters(markdown)
    if not text.endswith("\n"):
        text = f"{text}\n"
    with tempfile.TemporaryDirectory(prefix="hsk-ai-md-") as temp_dir:
        md_path = Path(temp_dir) / "answer.md"
        md_path.write_text(text, encoding="utf-8")
        return hsg.Article(md_path).get_html_code()
```

</details>

## 🔧 Function `normalize_ai_latex_delimiters`

```python
def normalize_ai_latex_delimiters(markdown: str) -> str
```

Convert `\(...\)` / `\[...\]` to `$...$` / `$$...$$` outside code fences.

BotHub answers usually use LaTeX delimiters. `mdit-py-plugins.dollarmath` only
parses dollar math, and markdown-it otherwise strips the leading backslash
(`\(x\)` → `(x)`), so formulas never reach KaTeX.

<details>
<summary>Code:</summary>

```python
def normalize_ai_latex_delimiters(markdown: str) -> str:

    def _convert_segment(segment: str) -> str:
        # Blank lines around $$ so dollarmath treats them as display blocks,
        # not as nested $…$ inside a paragraph (which breaks adjacent formulas).
        segment = _LATEX_BLOCK_RE.sub(
            lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n",
            segment,
        )
        return _LATEX_INLINE_RE.sub(lambda m: f"${m.group(1).strip()}$", segment)

    parts: list[str] = []
    last = 0
    for match in _FENCED_CODE_RE.finditer(markdown):
        parts.append(_convert_segment(markdown[last : match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(_convert_segment(markdown[last:]))
    return "".join(parts)
```

</details>

## 🔧 Function `resolve_html_template_dist`

```python
def resolve_html_template_dist(config: dict | None) -> Path | None
```

Return `path_html_template_dist` when it contains a usable `blank.html`.

<details>
<summary>Code:</summary>

```python
def resolve_html_template_dist(config: dict | None) -> Path | None:
    if not isinstance(config, dict):
        return None
    raw = config.get("path_html_template_dist")
    if raw is None or not str(raw).strip():
        return None
    dist = Path(str(raw)).expanduser()
    try:
        dist = dist.resolve()
    except OSError:
        return None
    if not (dist / "blank.html").is_file():
        return None
    if not (dist / "css" / "app.css").is_file():
        return None
    return dist
```

</details>
