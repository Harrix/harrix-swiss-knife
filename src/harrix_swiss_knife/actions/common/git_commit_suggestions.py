"""Rank commit subject suggestions from history and Quick Paste phrases."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from harrix_swiss_knife.actions.common.git_cmd import git_run

_DEFAULT_HISTORY_LIMIT = 100


@dataclass(frozen=True, slots=True)
class CommitHistoryEntry:
    """One recent commit with its changed paths."""

    subject: str
    paths: frozenset[str]


def load_commit_history(repo: Path, *, limit: int = _DEFAULT_HISTORY_LIMIT) -> list[CommitHistoryEntry]:
    """Return recent commits with path sets (newest first)."""
    repo = repo.resolve()
    if limit <= 0:
        return []
    # Record separator RS (0x1e) between commits keeps subjects free of ambiguity.
    proc = git_run(
        repo,
        "log",
        f"-n{limit}",
        "--name-only",
        "--pretty=format:%x1e%s",
    )
    if proc.returncode != 0 or not proc.stdout:
        return []
    return parse_commit_history_log(proc.stdout)


def load_quick_paste_phrases(db_path: str | Path | None) -> list[str]:
    """Return Quick Paste phrase values, or `[]` when the DB is missing."""
    if db_path is None:
        return []
    path = Path(str(db_path)).expanduser()
    if not path.is_file():
        return []
    try:
        from harrix_swiss_knife.apps.snippets.database_manager import (  # noqa: PLC0415
            DatabaseManager,
        )

        manager = DatabaseManager(str(path))
        try:
            return [item.value for item in manager.list_items("phrase") if item.value.strip()]
        finally:
            manager.close()
    except Exception:
        return []


def parse_commit_history_log(stdout: str) -> list[CommitHistoryEntry]:
    """Parse `git log --name-only --pretty=format:%x1e%s` output."""
    text = stdout.replace("\r\n", "\n")
    entries: list[CommitHistoryEntry] = []
    for raw_block in text.split("\x1e"):
        cleaned = raw_block.strip("\n")
        if not cleaned.strip():
            continue
        lines = cleaned.splitlines()
        subject = lines[0].strip()
        if not subject:
            continue
        paths = frozenset(
            line.strip().replace("\\", "/") for line in lines[1:] if line.strip() and not line.startswith(" ")
        )
        entries.append(CommitHistoryEntry(subject=subject, paths=paths))
    return entries


def rank_commit_subjects(
    selected_paths: set[str] | frozenset[str],
    history: list[CommitHistoryEntry],
    quick_paste: list[str],
) -> list[str]:
    """Order subjects: same-files history, frequency, then Quick Paste.

    Dedupes by exact subject; preserves first-seen order within each tier.

    """
    selected = frozenset(path.replace("\\", "/") for path in selected_paths if path.strip())
    seen: set[str] = set()
    result: list[str] = []

    def add(subject: str) -> None:
        text = subject.strip()
        if not text or text in seen:
            return
        seen.add(text)
        result.append(text)

    if selected:
        for entry in history:
            if entry.paths == selected:
                add(entry.subject)
        for entry in history:
            if not entry.paths:
                continue
            if entry.paths == selected:
                continue
            if selected <= entry.paths or entry.paths <= selected:
                add(entry.subject)

    remaining_subjects = [entry.subject.strip() for entry in history if entry.subject.strip()]
    counts = Counter(remaining_subjects)
    first_index: dict[str, int] = {}
    for index, subject in enumerate(remaining_subjects):
        first_index.setdefault(subject, index)
    frequent = sorted(
        (subject for subject in first_index if subject not in seen),
        key=lambda subject: (-counts[subject], first_index[subject]),
    )
    for subject in frequent:
        add(subject)

    for phrase in quick_paste:
        add(phrase)

    return result
