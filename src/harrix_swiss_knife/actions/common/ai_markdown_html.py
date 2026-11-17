"""Build full HTML pages for AI Markdown answers (Harrix `blank.html` + pyssg)."""

from __future__ import annotations

import html
import re
import tempfile
from pathlib import Path

import harrix_pyssg as hsg

_CONTENT_BLOCK_RE = re.compile(
    r"<!--\s*h-ssg:content-start\s*-->.*?<!--\s*h-ssg:content-end\s*-->",
    re.IGNORECASE | re.DOTALL,
)
_TITLE_RE = re.compile(r"(<title>)(.*?)(</title>)", re.IGNORECASE | re.DOTALL)
_MATH_INLINE_RE = re.compile(
    r'<span\s+class="math\s+inline">(.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)
_MATH_BLOCK_RE = re.compile(
    r'<div\s+class="math\s+block">(.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)

_CONTENT_SHELL = """<!-- h-ssg:content-start -->
<div class="section">
  <div class="container">
    <div class="columns">
      <div class="column is-10-desktop is-offset-1-desktop content">
{body}
      </div>
    </div>
  </div>
</div>
<!-- h-ssg:content-end -->"""


def adapt_math_for_harrix_katex(content_html: str) -> str:
    """Map mdit-py dollarmath markup to Harrix `.tex[data-expr]` nodes."""

    def _to_tex(match: re.Match[str], *, block: bool) -> str:
        expr = html.unescape(match.group(1)).strip()
        if not expr:
            return ""
        escaped = html.escape(expr, quote=True)
        tag = "div" if block else "span"
        return f'<{tag} class="tex" data-expr="{escaped}"></{tag}>'

    html_out = _MATH_INLINE_RE.sub(lambda m: _to_tex(m, block=False), content_html)
    return _MATH_BLOCK_RE.sub(lambda m: _to_tex(m, block=True), html_out)


def build_ai_answer_html(markdown: str, *, dist_dir: Path, title: str = "Ask AI answer") -> str:
    """Fill `blank.html` with rendered Markdown for WebView display."""
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


def markdown_to_article_html(markdown: str) -> str:
    """Render Markdown to article-body HTML via harrix-pyssg (GFM + dollarmath)."""
    text = markdown if markdown.endswith("\n") else f"{markdown}\n"
    with tempfile.TemporaryDirectory(prefix="hsk-ai-md-") as temp_dir:
        md_path = Path(temp_dir) / "answer.md"
        md_path.write_text(text, encoding="utf-8")
        return hsg.Article(md_path).get_html_code()


def resolve_html_template_dist(config: dict | None) -> Path | None:
    """Return `path_html_template_dist` when it contains a usable `blank.html`."""
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
