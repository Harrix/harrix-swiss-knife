"""Tests for template image optimize settings resolution."""

from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.template_parser import TemplateField, TemplateParser


def test_resolve_image_optimize_settings_from_template_hash_suffix() -> None:
    fields, _ = TemplateParser.parse_template("{{Images:images@Title#1024}}")
    optimize, max_size = OnNewMarkdown._resolve_image_optimize_settings(fields, {})
    assert optimize is True
    assert max_size == 1024


def test_resolve_image_optimize_settings_falls_back_to_config() -> None:
    fields = [TemplateField("Images", "images", "{{Images:images}}")]
    config = {"image_optimize": True, "image_max_size": 512}
    optimize, max_size = OnNewMarkdown._resolve_image_optimize_settings(fields, config)
    assert optimize is True
    assert max_size == 512


def test_resolve_image_optimize_settings_disabled_without_template_or_config() -> None:
    fields = [TemplateField("Images", "images", "{{Images:images@Title}}", field_link="Title")]
    optimize, max_size = OnNewMarkdown._resolve_image_optimize_settings(fields, {})
    assert optimize is False
    assert max_size is None
