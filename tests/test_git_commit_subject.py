"""Tests for Git commit subject cleanup."""

from __future__ import annotations

from harrix_swiss_knife.integrations.bothub.git_commit_subject import normalize_commit_subject


def test_normalize_commit_subject_keeps_single_line() -> None:
    assert normalize_commit_subject("🐞 Fix nested snippet resolution\n") == "🐞 Fix nested snippet resolution"


def test_normalize_commit_subject_strips_fences_quotes_and_period() -> None:
    raw = '```text\n"🔧 Modify path slash action to flip slashes."\n```'
    assert normalize_commit_subject(raw) == "🔧 Modify path slash action to flip slashes"
