"""Tests for commit subject ranking and history parsing."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.git_commit_suggestions import (
    CommitHistoryEntry,
    parse_commit_history_log,
    rank_commit_subjects,
)


def test_parse_commit_history_log() -> None:
    raw = "\x1e⬆️ Update packages\nuv.lock\npyproject.toml\n\x1e📚 Docs. Update\nREADME.md\n"
    entries = parse_commit_history_log(raw)
    assert len(entries) == 2
    assert entries[0].subject == "⬆️ Update packages"
    assert entries[0].paths == frozenset({"uv.lock", "pyproject.toml"})
    assert entries[1].subject == "📚 Docs. Update"
    assert entries[1].paths == frozenset({"README.md"})


def test_rank_checkbox_set_changes_exact_match() -> None:
    history = [
        CommitHistoryEntry("only uv", frozenset({"uv.lock"})),
        CommitHistoryEntry("only prompts", frozenset({"prompts.md"})),
        CommitHistoryEntry("both", frozenset({"uv.lock", "prompts.md"})),
    ]
    only_uv = rank_commit_subjects({"uv.lock"}, history, [])
    assert only_uv[0] == "only uv"
    both = rank_commit_subjects({"uv.lock", "prompts.md"}, history, [])
    assert both[0] == "both"


def test_rank_same_files_before_frequency_before_quick_paste() -> None:
    history = [
        CommitHistoryEntry("exact new", frozenset({"a.md"})),
        CommitHistoryEntry("other", frozenset({"b.md"})),
        CommitHistoryEntry("freq", frozenset({"c.md"})),
        CommitHistoryEntry("freq", frozenset({"d.md"})),
        CommitHistoryEntry("exact old", frozenset({"a.md"})),
        CommitHistoryEntry("related", frozenset({"a.md", "extra.md"})),
    ]
    ranked = rank_commit_subjects({"a.md"}, history, ["quick paste phrase", "freq"])
    assert ranked[0] == "exact new"
    assert ranked[1] == "exact old"
    assert "related" in ranked[:4]
    assert ranked.index("freq") < ranked.index("quick paste phrase")
    assert ranked[-1] == "quick paste phrase" or "quick paste phrase" in ranked
