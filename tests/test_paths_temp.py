"""Tests for temp folder path helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.paths import clear_directory_contents, clear_temp_folder

if TYPE_CHECKING:
    from pathlib import Path


def test_clear_directory_contents_removes_children_keeps_directory(tmp_path: Path) -> None:
    root = tmp_path / "keep_me"
    root.mkdir()
    (root / "file.txt").write_text("x", encoding="utf-8")
    nested = root / "nested"
    nested.mkdir()
    (nested / "inner.txt").write_text("y", encoding="utf-8")

    clear_directory_contents(root)

    assert root.is_dir()
    assert list(root.iterdir()) == []


def test_clear_directory_contents_no_op_when_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    clear_directory_contents(missing)
    assert not missing.exists()


def test_clear_temp_folder_removes_other_entries_and_empties_reserved(tmp_path: Path) -> None:
    temp = tmp_path / "temp"
    images = temp / "images"
    optimized = temp / "optimized_images"
    action_output = temp / "action_output"
    icons = temp / "icons"
    images.mkdir(parents=True)
    optimized.mkdir(parents=True)
    action_output.mkdir(parents=True)
    icons.mkdir(parents=True)
    (images / "photo.png").write_bytes(b"img")
    (optimized / "photo.avif").write_bytes(b"avif")
    (action_output / "log.txt").write_text("log", encoding="utf-8")
    (icons / "emoji.png").write_bytes(b"png")
    (temp / "hsk-speech.wav").write_bytes(b"wav")

    lines = clear_temp_folder(temp)

    assert images.is_dir()
    assert optimized.is_dir()
    assert list(images.iterdir()) == []
    assert list(optimized.iterdir()) == []
    assert not action_output.exists()
    assert not icons.exists()
    assert not (temp / "hsk-speech.wav").exists()
    assert any("images" in line for line in lines)
    assert any("optimized_images" in line for line in lines)
    assert any("action_output" in line for line in lines)


def test_clear_temp_folder_creates_reserved_directories_when_missing(tmp_path: Path) -> None:
    temp = tmp_path / "temp"
    temp.mkdir()
    (temp / "scratch.txt").write_text("x", encoding="utf-8")

    clear_temp_folder(temp)

    assert (temp / "images").is_dir()
    assert (temp / "optimized_images").is_dir()
    assert list((temp / "images").iterdir()) == []
    assert list((temp / "optimized_images").iterdir()) == []
    assert not (temp / "scratch.txt").exists()


def test_clear_temp_folder_on_empty_creates_reserved_directories(tmp_path: Path) -> None:
    temp = tmp_path / "temp"
    temp.mkdir()

    lines = clear_temp_folder(temp)

    assert (temp / "images").is_dir()
    assert (temp / "optimized_images").is_dir()
    assert any("Created folder" in line for line in lines)
