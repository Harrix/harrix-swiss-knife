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


COFFEE_TEMPLATE = """### {{Title:line}}: {{Score:float:10}}

{{Images:images}}

_{{Title:line}}_

- **City:** {{City:line}}
- **Place:** {{Place:line}}
- **Web:** <{{Web:line}}>
- **Date:** {{Date:date}}
- **Comments:** {{Comments:multiline}}
"""


def test_parse_block_and_fill_round_trip_coffee_template() -> None:
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    values = {
        "Title": "Flat white",
        "Score": "9",
        "Images": "img/a.jpg, img/b.jpg",
        "City": "Moscow",
        "Place": "Coffee shop",
        "Web": "https://example.com",
        "Date": "2025-06-01",
        "Comments": "Great foam\nNice taste",
    }
    block = TemplateParser.fill_template(COFFEE_TEMPLATE, values)
    parsed = TemplateParser.parse_block(COFFEE_TEMPLATE, block, fields)
    assert parsed is not None
    assert parsed["Title"] == "Flat white"
    assert parsed["Score"] == "9"
    assert parsed["Images"] == "img/a.jpg,img/b.jpg"
    assert parsed["City"] == "Moscow"
    assert parsed["Comments"] == "Great foam\nNice taste"


EVENT_TEMPLATE_IMAGES = """### {{Title:line}}: {{Score:float:10}}

{{Images:images}}

_{{Title:line}}_

- **City:** {{City:line}}
- **Place:** {{Place:line}}
- **Web:** <{{Web:line}}>
- **Date:** {{Date:date}}
- **Comments:** {{Comments:multiline}}
"""


def test_parse_block_single_image_via_images_field() -> None:
    fields, _ = TemplateParser.parse_template(EVENT_TEMPLATE_IMAGES)
    values = {
        "Title": "Concert",
        "Score": "10",
        "Images": "img/event.jpg",
        "City": "SPb",
        "Place": "Arena",
        "Web": "https://arena.ru",
        "Date": "2025-07-01",
        "Comments": "Amazing",
    }
    block = TemplateParser.fill_template(EVENT_TEMPLATE_IMAGES, values)
    parsed = TemplateParser.parse_block(EVENT_TEMPLATE_IMAGES, block, fields)
    assert parsed is not None
    assert parsed["Images"] == "img/event.jpg"


def test_split_entries_finds_blocks_by_heading_level() -> None:
    content = """## 2025

### First: 8

Body one

### Second: 9

Body two
"""
    entries = TemplateParser.split_entries(content, COFFEE_TEMPLATE)
    assert len(entries) == 2
    assert entries[0].display_title == "First: 8"
    assert entries[1].display_title == "Second: 9"
    assert "Body one" in entries[0].block_text
    assert entries[0].start < entries[1].start
