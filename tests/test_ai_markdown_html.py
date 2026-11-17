"""Tests for AI Markdown → Harrix `blank.html` assembly."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.common.ai_markdown_html import (
    adapt_math_for_harrix_katex,
    build_ai_answer_html,
    markdown_to_article_html,
    resolve_html_template_dist,
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


def test_markdown_to_article_html_renders_fence() -> None:
    html = markdown_to_article_html("Hello\n\n```python\nprint(1)\n```\n")
    assert 'class="language-python"' in html
    assert "print(1)" in html


def test_resolve_html_template_dist_requires_blank(tmp_path: Path) -> None:
    assert resolve_html_template_dist({}) is None
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) is None
    (tmp_path / "blank.html").write_text("<html></html>", encoding="utf-8")
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) is None
    (tmp_path / "css").mkdir()
    (tmp_path / "css" / "app.css").write_text("body{}", encoding="utf-8")
    assert resolve_html_template_dist({"path_html_template_dist": str(tmp_path)}) == tmp_path.resolve()
