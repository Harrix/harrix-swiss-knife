"""Tests for action output path helpers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harrix_swiss_knife.paths import _sanitize_action_class_stem, new_action_output_file_path

if TYPE_CHECKING:
    from pathlib import Path


def test_sanitize_action_class_stem_simple() -> None:
    assert _sanitize_action_class_stem("MyAction") == "MyAction"


def test_sanitize_action_class_stem_replaces_special_chars() -> None:
    assert _sanitize_action_class_stem("Foo::Bar.Baz") == "Foo_Bar_Baz"


def test_sanitize_action_class_stem_empty_becomes_action() -> None:
    assert _sanitize_action_class_stem(":::___") == "Action"


def test_sanitize_action_class_stem_truncates_long_name() -> None:
    long_name = "A" * 200
    stem = _sanitize_action_class_stem(long_name)
    assert len(stem) == 80


def test_new_action_output_file_path_pattern(tmp_path: Path) -> None:
    path = new_action_output_file_path(tmp_path, "SampleAction")
    assert path.parent == tmp_path
    assert re.fullmatch(r"SampleAction_[0-9a-f]{12}\.txt", path.name)
