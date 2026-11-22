"""Tests for AI Markdown → Harrix `blank.html` assembly."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.common.ai_markdown_html import (
    adapt_math_for_harrix_katex,
    build_ai_answer_html,
    markdown_to_article_html,
    normalize_ai_latex_delimiters,
    resolve_html_template_dist,
    strip_local_font_preloads,
)


def test_adapt_math_for_harrix_katex_maps_dollarmath_nodes() -> None:
    html = '<p>Inline <span class="math inline">E=mc^2</span></p><div class="math block">x^2</div>'
    out = adapt_math_for_harrix_katex(html)
    assert 'class="tex" data-expr="E=mc^2"' in out
    assert 'class="tex" data-expr="x^2"' in out
    assert "math inline" not in out
    assert "math block" not in out


def test_build_ai_answer_html_injects_content(tmp_path: Path) -> None:
    blank = """<!doctype html>
<html><head><title>Old</title>
<link href="css/app.css" rel="stylesheet" />
</head><body><main><article>
<!-- h-ssg:content-start -->
<p>demo</p>
<!-- h-ssg:content-end -->
</article></main>
<script src="js/app.js"></script>
</body></html>
"""
    (tmp_path / "blank.html").write_text(blank, encoding="utf-8")
    (tmp_path / "css").mkdir()
    (tmp_path / "css" / "app.css").write_text("body{}", encoding="utf-8")
    page = build_ai_answer_html("# Hello\n\nValue $x=1$\n", dist_dir=tmp_path, title="Ask AI answer")
    assert "<title>Ask AI answer</title>" in page
    assert "h-ssg:content-start" in page
    assert "demo" not in page
    assert 'data-expr="x=1"' in page
    assert "Hello" in page


def test_build_ai_answer_html_strips_font_preloads(tmp_path: Path) -> None:
    blank = """<!doctype html>
<html><head><title>Old</title>
<link rel="preload" href="fonts/Roboto.woff2" as="font" type="font/woff2" crossorigin />
<link href="css/app.css" rel="stylesheet" />
</head><body><main><article>
<!-- h-ssg:content-start -->
<p>demo</p>
<!-- h-ssg:content-end -->
</article></main></body></html>
"""
    (tmp_path / "blank.html").write_text(blank, encoding="utf-8")
    (tmp_path / "css").mkdir()
    (tmp_path / "css" / "app.css").write_text("body{}", encoding="utf-8")
    page = build_ai_answer_html("Hi\n", dist_dir=tmp_path, title="Ask AI answer")
    assert "Roboto" not in page
    assert 'href="css/app.css"' in page
    assert "<title>Ask AI answer</title>" in page


def test_markdown_to_article_html_renders_fence() -> None:
    html = markdown_to_article_html("Hello\n\n```python\nprint(1)\n```\n")
    assert 'class="language-python"' in html
    assert "print(1)" in html


def test_markdown_to_article_html_renders_latex_delimiters() -> None:
    html = markdown_to_article_html(r"Value \(x=1\) and \[ y=2 \].")
    assert 'class="math inline"' in html
    assert 'class="math block"' in html
    assert "(x=1)" not in html
    adapted = adapt_math_for_harrix_katex(html)
    assert 'data-expr="x=1"' in adapted
    assert 'data-expr="y=2"' in adapted


def test_normalize_ai_latex_delimiters_converts_paren_and_bracket() -> None:
    md = r"Digits \(x\) and \[ a+b=c \]."
    out = normalize_ai_latex_delimiters(md)
    assert "$x$" in out
    assert "$$\na+b=c\n$$" in out
    assert r"\(" not in out
    assert r"\[" not in out


def test_normalize_ai_latex_delimiters_skips_fenced_code() -> None:
    md = "See \\(x\\)\n\n```tex\n\\(keep\\)\n```\n"
    out = normalize_ai_latex_delimiters(md)
    assert "$x$" in out
    assert "\\(keep\\)" in out


def test_resolve_html_template_dist_requires_blank(tmp_path: Path) -> None:
    assert resolve_html_template_dist({}) is None
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) is None
    (tmp_path / "blank.html").write_text("<html></html>", encoding="utf-8")
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) is None
    (tmp_path / "css").mkdir()
    (tmp_path / "css" / "app.css").write_text("body{}", encoding="utf-8")
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) == tmp_path.resolve()


def test_strip_local_font_preloads_keeps_other_links() -> None:
    page = """<head>
    <link rel="preload" href="fonts/Roboto.woff2" as="font" type="font/woff2" crossorigin />
    <link as="font" rel="preload" href="fonts/JetBrainsMono-Regular.woff2" crossorigin="anonymous">
    <link href="css/app.css" rel="stylesheet" />
    <link rel="preload" href="js/early.js" as="script" />
</head>
"""
    out = strip_local_font_preloads(page)
    assert "woff2" not in out
    assert "crossorigin" not in out
    assert 'href="css/app.css"' in out
    assert 'as="script"' in out
