"""Tests for uv project/library name validation."""

from harrix_swiss_knife.actions.common.uv_name import validate_uv_project_name


def test_validate_uv_project_name_accepts_valid_names() -> None:
    assert validate_uv_project_name("python-project-07") is None
    assert validate_uv_project_name("MyLibrary") is None
    assert validate_uv_project_name("test_name") is None


def test_validate_uv_project_name_rejects_empty_name() -> None:
    assert validate_uv_project_name("") == "Name must not be empty."
    assert validate_uv_project_name("   ") == "Name must not be empty."


def test_validate_uv_project_name_rejects_invalid_names() -> None:
    assert validate_uv_project_name("bad name") == "Name must not contain spaces."
    assert validate_uv_project_name("проект") == (
        "Name must contain only English letters, digits, hyphens, and underscores."
    )
    assert validate_uv_project_name("bad/name") == (
        "Name must contain only English letters, digits, hyphens, and underscores."
    )
