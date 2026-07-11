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
    template = "{{Images:images@Title#1024}}"
    result = TemplateParser.fill_template(template, {"Images": "a.png, b.png", "Title": "Shot"})
    assert result == "![Shot](a.png)\n![Shot](b.png)"


def test_fill_template_omits_line_when_all_fields_empty() -> None:
    template = "- **City:** {{City:line}}\n- **Address:** {{Address:line}}"
    assert TemplateParser.fill_template(template, {"City": "Moscow", "Address": ""}) == "- **City:** Moscow"
    assert TemplateParser.fill_template(template, {"City": "", "Address": ""}) == ""


def test_fill_template_omits_images_line_when_no_images() -> None:
    template = "### {{Title:line}}: {{Score:float:5}}\n\n{{Images:images@Title#1024}}"
    result = TemplateParser.fill_template(template, {"Title": "Cafe", "Score": "8", "Images": ""})
    assert "img/" not in result
    assert "### Cafe: 8" in result


def test_parse_block_round_trip_with_omitted_empty_lines() -> None:
    template = "- **City:** {{City:line}}\n- **Address:** {{Address:line}}\n- **Web:** <{{Web:line}}>"
    fields, _ = TemplateParser.parse_template(template)
    values = {"City": "Moscow", "Address": "", "Web": ""}
    block = TemplateParser.fill_template(template, values)
    assert block == "- **City:** Moscow"
    parsed = TemplateParser.parse_block(template, block, fields)
    assert parsed is not None
    assert parsed["City"] == "Moscow"
    assert parsed["Address"] == ""
    assert parsed["Web"] == ""


def test_template_field_stores_combobox_options() -> None:
    field = TemplateField("Author", "combobox", "{{Author:combobox}}", options=["A", "B"])
    assert field.options == ["A", "B"]


def test_parse_template_reads_image_filename_field_link() -> None:
    content = "{{Images:images@Title}}\n{{Featured:image@Address:img/a.png}}"
    fields, _ = TemplateParser.parse_template(content)
    by_name = {field.name: field for field in fields}
    assert by_name["Images"].field_link == "Title"
    assert by_name["Images"].image_optimize is False
    assert by_name["Featured"].field_link == "Address"
    assert by_name["Featured"].default_value == "img/a.png"


def test_parse_template_reads_image_optimize_max_size_suffix() -> None:
    fields, _ = TemplateParser.parse_template("{{Images:images@Title#1024}}")
    field = fields[0]
    assert field.field_link == "Title"
    assert field.image_optimize is True
    assert field.image_max_size == 1024


def test_parse_template_reads_image_optimize_with_default_value() -> None:
    fields, _ = TemplateParser.parse_template("{{Featured:image@Date#800:img/a.png}}")
    field = fields[0]
    assert field.field_link == "Date"
    assert field.image_optimize is True
    assert field.image_max_size == 800
    assert field.default_value == "img/a.png"


def test_parse_template_reads_subfolders_field_link() -> None:
    fields, _ = TemplateParser.parse_template("{{City:line@subfolders}}")
    assert fields[0].name == "City"
    assert fields[0].field_type == "line"
    assert fields[0].field_link == TemplateParser.FIELD_LINK_SUBFOLDERS


def test_parse_template_reads_note_name_field_link() -> None:
    fields, _ = TemplateParser.parse_template("{{Title:line@note_name}}")
    assert fields[0].field_link == TemplateParser.FIELD_LINK_NOTE_NAME


def test_parse_template_reads_date_from_images_links() -> None:
    fields, _ = TemplateParser.parse_template("{{Date:date@Images}}\n{{DateLast:date@Images!}}\n{{DatePlain:date}}")
    by_name = {field.name: field for field in fields}
    assert by_name["Date"].date_from_images == "Images"
    assert by_name["Date"].date_from_images_overwrite is False
    assert by_name["Date"].field_link is None
    assert by_name["DateLast"].date_from_images == "Images"
    assert by_name["DateLast"].date_from_images_overwrite is True
    assert by_name["DatePlain"].date_from_images is None


COFFEE_TEMPLATE = """### {{Title:line@note_name}}: {{Score:float:10}}

{{Images:images@Title#1024}}

_{{Title:line}}_

- **City:** {{City:line@subfolders}}
- **Address:** {{Address:line}}
- **Coordinates:** {{Coordinates:coordinates}}
- **Web:** <{{Web:line}}>
- **Date:** {{Date:date@Images}}
- **Last visit:** {{DateLast:date@Images!}}
- **Comments:** {{Comments:multiline}}
"""


def test_parse_block_and_fill_round_trip_coffee_template() -> None:
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    images_field = next(field for field in fields if field.name == "Images")
    assert images_field.field_link == "Title"
    values = {
        "Title": "Flat white",
        "Score": "9",
        "Images": "img/a.jpg, img/b.jpg",
        "City": "Moscow",
        "Address": "Tverskaya St, 12",
        "Coordinates": "55.7558, 37.6173",
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
    assert parsed["Address"] == "Tverskaya St, 12"
    assert parsed["Coordinates"] == "55.7558, 37.6173"
    assert parsed["Comments"] == "Great foam\nNice taste"


EVENT_TEMPLATE_IMAGES = """### {{Title:line}}: {{Score:float:10}}

{{Images:images@Title#1024}}

_{{Title:line}}_

- **City:** {{City:line@subfolders}}
- **Place:** {{Place:line}}
- **Web:** <{{Web:line}}>
- **Date:** {{Date:date@Images}}
- **Last visit:** {{DateLast:date@Images!}}
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
