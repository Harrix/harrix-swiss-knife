"""Tests for durable Speech to text pending recording store."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.actions.text.speech_to_text_pending import SpeechToTextPendingStore
from harrix_swiss_knife.integrations.bothub.speech import MIN_AUDIO_BYTES


def _write_wav(path: Path, *, size: int = MIN_AUDIO_BYTES) -> Path:
    path.write_bytes(b"RIFF" + b"x" * max(0, size - 4))
    return path


def test_pending_store_save_load_clear(tmp_path: Path) -> None:
    store = SpeechToTextPendingStore(root=tmp_path / "pending")
    source = _write_wav(tmp_path / "clip.wav", size=MIN_AUDIO_BYTES + 20)

    saved = store.save(source)
    assert saved.path.is_file()
    assert saved.mime_type == "audio/wav"
    assert saved.size_bytes >= MIN_AUDIO_BYTES

    loaded = store.load()
    assert loaded is not None
    assert loaded.path == saved.path
    assert loaded.mime_type == "audio/wav"
    assert loaded.path.read_bytes() == source.read_bytes()

    store.clear()
    assert store.load() is None
    assert not saved.path.exists()


def test_pending_store_rejects_tiny_file(tmp_path: Path) -> None:
    store = SpeechToTextPendingStore(root=tmp_path / "pending")
    source = tmp_path / "tiny.wav"
    source.write_bytes(b"tiny")
    with pytest.raises(ValueError, match="too short"):
        store.save(source)


def test_pending_store_replaces_previous_extension(tmp_path: Path) -> None:
    store = SpeechToTextPendingStore(root=tmp_path / "pending")
    wav = _write_wav(tmp_path / "a.wav", size=MIN_AUDIO_BYTES + 8)
    m4a = tmp_path / "b.m4a"
    m4a.write_bytes(b"ftyp" + b"y" * MIN_AUDIO_BYTES)

    first = store.save(wav)
    second = store.save(m4a)
    assert second.path.suffix == ".m4a"
    assert not first.path.exists()
    loaded = store.load()
    assert loaded is not None
    assert loaded.path == second.path
    assert loaded.mime_type == "audio/m4a"
