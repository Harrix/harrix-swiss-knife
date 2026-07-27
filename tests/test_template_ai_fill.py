"""Tests for New Markdown template AI fill helpers."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.template_ai_fill import (
    collect_ai_fill_candidates_from_fields,
    format_fields_for_prompt,
    is_ai_fill_candidate,
    parse_template_fields_response,
)
from harrix_swiss_knife.template_parser import TemplateField


def _field(name: str, field_type: str, default: str | None = None) -> TemplateField:
    return TemplateField(name, field_type, f"{{{{{name}:{field_type}}}}}", default)


def test_is_ai_fill_candidate_excludes_review_and_media_and_bool() -> None:
    assert not is_ai_fill_candidate(_field("Review", "multiline"), "")
    assert not is_ai_fill_candidate(_field("Images", "images"), "")
    assert not is_ai_fill_candidate(_field("Photo", "image"), "")
    assert not is_ai_fill_candidate(_field("Doc", "file"), "")
    assert not is_ai_fill_candidate(_field("Docs", "files"), "")
    assert not is_ai_fill_candidate(_field("Published", "bool"), "false")
    assert not is_ai_fill_candidate(_field("Date", "date"), "")
    assert not is_ai_fill_candidate(_field("Date watching", "date"), "2019-10-28")


def test_is_ai_fill_candidate_empty_and_zero() -> None:
    assert is_ai_fill_candidate(_field("Title", "line"), "")
    assert is_ai_fill_candidate(_field("Title", "line"), "   ")
    assert is_ai_fill_candidate(_field("Season", "int"), "0")
    assert is_ai_fill_candidate(_field("Score", "float"), "0")
    assert is_ai_fill_candidate(_field("Score", "float"), "0.0")
    assert not is_ai_fill_candidate(_field("Title", "line"), "Filled")
    assert not is_ai_fill_candidate(_field("Season", "int"), "2")


def test_is_ai_fill_candidate_numeric_default() -> None:
    assert is_ai_fill_candidate(_field("Score", "float", "10"), "10")
    assert is_ai_fill_candidate(_field("Score", "float", "10"), "10.0")
    assert not is_ai_fill_candidate(_field("Score", "float", "10"), "8.5")
    assert is_ai_fill_candidate(_field("Season", "int", "1"), "1")
    assert not is_ai_fill_candidate(_field("Season", "int", "1"), "3")


def test_collect_ai_fill_candidates_from_fields() -> None:
    fields = [
        _field("Title", "line"),
        _field("Score", "float", "10"),
        _field("Date", "date"),
        _field("Review", "multiline"),
        _field("Poster", "image"),
    ]
    names = [field.name for field in collect_ai_fill_candidates_from_fields(fields)]
    assert names == ["Title", "Score"]
    assert "Date" not in names


def test_format_fields_for_prompt() -> None:
    text = format_fields_for_prompt([_field("Title", "line"), _field("Score", "float")])
    assert text == "- Title (line)\n- Score (float)"


def test_parse_template_fields_response_json() -> None:
    parsed = parse_template_fields_response('{"Title": "Song of the Sea", "Score": 8.5, "Date watching": "2019-10-28"}')
    assert parsed == {
        "Title": "Song of the Sea",
        "Score": "8.5",
        "Date watching": "2019-10-28",
    }


def test_parse_template_fields_response_strips_fences_and_ignores_review() -> None:
    raw = """```json
{"Title": "Red Turtle", "Review": "Nice", "Score": "9"}
```"""
    parsed = parse_template_fields_response(raw)
    assert parsed == {"Title": "Red Turtle", "Score": "9"}
    assert "Review" not in parsed


def test_parse_template_fields_response_partial_and_null() -> None:
    parsed = parse_template_fields_response('{"Title": "A", "URL": null}')
    assert parsed == {"Title": "A"}


def test_parse_template_fields_response_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_template_fields_response("not json")
    with pytest.raises(TypeError, match="JSON object"):
        parse_template_fields_response("[]")
    with pytest.raises(ValueError, match="Empty"):
        parse_template_fields_response("   ")
