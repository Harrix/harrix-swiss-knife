"""Tests for template_parser module."""

from harrix_swiss_knife.template_parser import TemplateField, TemplateParser


def test_parse_template_extracts_fields_and_skips_duplicates() -> None:
    content = "# {{Title:line}}\n\n{{Score:int:5}}\n{{Title:line}}"
    fields, original = TemplateParser.parse_template(content)

    assert original == content
    assert len(fields) == 2
    assert fields[0].name == "Title"
    assert fields[0].field_type == "line"
    assert fields[1].name == "Score"
    assert fields[1].field_type == "int"
    assert fields[1].default_value == "5"


def test_fill_template_replaces_simple_placeholders() -> None:
    template = "Hello {{Name:line}}!"
    result = TemplateParser.fill_template(template, {"Name": "World"})
    assert result == "Hello World!"


def test_fill_template_formats_multiline_inside_list_item() -> None:
    template = "- Item: {{Notes:multiline}}"
    result = TemplateParser.fill_template(template, {"Notes": "first\nsecond"})
    assert result == "- Item: first\n\n  second"


def test_fill_template_expands_images_field() -> None:
    template = "{{Images:images}}"
    result = TemplateParser.fill_template(template, {"Images": "a.png, b.png", "Title": "Shot"})
    assert result == "![Shot](a.png)\n![Shot](b.png)"


def test_template_field_stores_combobox_options() -> None:
    field = TemplateField("Author", "combobox", "{{Author:combobox}}", options=["A", "B"])
    assert field.options == ["A", "B"]
