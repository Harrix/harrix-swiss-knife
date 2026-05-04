"""Tests for action output path helpers."""

from __future__ import annotations

import os
import re
import sys
from typing import TYPE_CHECKING

import pytest

import harrix_swiss_knife.paths as paths
from harrix_swiss_knife.paths import (
    _sanitize_action_class_stem,
    get_action_output_dir,
    list_recent_action_output_files,
    new_action_output_file_path,
)

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


def test_list_recent_action_output_files_empty_when_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "not_action_output"
    assert list_recent_action_output_files(missing) == []


def test_list_recent_action_output_files_excludes_pending(tmp_path: Path) -> None:
    (tmp_path / "pending.txt").write_text("placeholder", encoding="utf8")
    real = tmp_path / "SampleAction_abcdef012345.txt"
    real.write_text("log", encoding="utf8")
    result = list_recent_action_output_files(tmp_path, limit=10)
    assert result == [real]


def test_list_recent_action_output_files_sort_newest_first_and_limit(tmp_path: Path) -> None:
    old = tmp_path / "Old_aaaaaaaaaaaa.txt"
    mid = tmp_path / "Mid_bbbbbbbbbbbb.txt"
    new = tmp_path / "New_cccccccccccc.txt"
    old.write_text("1", encoding="utf8")
    mid.write_text("2", encoding="utf8")
    new.write_text("3", encoding="utf8")
    old.touch()
    mid.touch()
    new.touch()
    # Ensure deterministic mtimes (touch order can tie on some FS).
    os.utime(old, (1_700_000_000, 1_000))
    os.utime(mid, (1_700_000_000, 2_000))
    os.utime(new, (1_700_000_000, 3_000))

    result = list_recent_action_output_files(tmp_path, limit=2)
    assert [p.name for p in result] == [new.name, mid.name]


def test_get_action_output_dir_respects_hsk_env_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out = tmp_path / "custom_out"
    monkeypatch.setenv("HSK_ACTION_OUTPUT_DIR", str(out))
    assert get_action_output_dir() == out.resolve()


def test_get_action_output_dir_falls_back_when_project_temp_unusable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("HSK_ACTION_OUTPUT_DIR", raising=False)
    fake_root = tmp_path / "repo"
    monkeypatch.setattr(paths, "get_project_root", lambda: fake_root)
    monkeypatch.setattr(paths, "_can_use_project_temp_dir", lambda _p: False)
    user_base = tmp_path / "localappdata"
    monkeypatch.setenv("LOCALAPPDATA", str(user_base))
    monkeypatch.setattr(sys, "platform", "win32")
    expected = user_base / "HarrixSwissKnife" / "action_output"
    assert get_action_output_dir() == expected


def test_list_recent_action_output_files_non_empty_only_skips_zero_byte(tmp_path: Path) -> None:
    empty = tmp_path / "Empty_aaaaaaaaaaaa.txt"
    filled = tmp_path / "Filled_bbbbbbbbbbbb.txt"
    empty.write_text("", encoding="utf8")
    filled.write_text("x", encoding="utf8")
    os.utime(empty, (1_700_000_000, 3_000))
    os.utime(filled, (1_700_000_000, 1_000))

    assert list_recent_action_output_files(tmp_path, limit=10, non_empty_only=True) == [filled]
    assert list_recent_action_output_files(tmp_path, limit=10, non_empty_only=False) == [empty, filled]
