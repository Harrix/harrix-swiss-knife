"""Tests for Dropbox-tolerant file replace helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.photo_sync.durable_io import replace_file, write_text_replacing
from harrix_swiss_knife.photo_sync.index import DeviceSyncIndex

if TYPE_CHECKING:
    import pytest


def test_replace_file_retries_permission_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "a.tmp"
    dest = tmp_path / "a.json"
    src.write_text("new\n", encoding="utf-8")
    dest.write_text("old\n", encoding="utf-8")
    calls = {"n": 0}
    real_replace = Path.replace

    def flaky(self: Path, target: Path) -> Path:
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError(5, "Access is denied", str(self))
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", flaky)
    monkeypatch.setattr("harrix_swiss_knife.photo_sync.durable_io.time.sleep", lambda _s: None)
    replace_file(src, dest)
    assert dest.read_text(encoding="utf-8") == "new\n"
    assert calls["n"] == 3


def test_replace_file_falls_back_to_in_place_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "b.tmp"
    dest = tmp_path / "b.json"
    src.write_text("fallback\n", encoding="utf-8")
    dest.write_text("old\n", encoding="utf-8")

    def always_fail(self: Path, _target: Path) -> Path:
        raise PermissionError(5, "Access is denied", str(self))

    monkeypatch.setattr(Path, "replace", always_fail)
    monkeypatch.setattr("harrix_swiss_knife.photo_sync.durable_io.time.sleep", lambda _s: None)
    replace_file(src, dest)
    assert dest.read_text(encoding="utf-8") == "fallback\n"
    assert not src.exists()


def test_device_index_save_uses_durable_write(tmp_path: Path) -> None:
    index = DeviceSyncIndex(tmp_path, "phone-1")
    index.upsert("42", content_hash="a" * 64, filename="2024-01-01 12.00.00.jpg")
    path = tmp_path / ".hsk-photo-sync" / "phone-1.json"
    assert path.is_file()
    assert "2024-01-01 12.00.00.jpg" in path.read_text(encoding="utf-8")


def test_write_text_replacing(tmp_path: Path) -> None:
    path = tmp_path / "meta.json"
    write_text_replacing(path, '{"ok": true}\n')
    assert path.read_text(encoding="utf-8") == '{"ok": true}\n'
