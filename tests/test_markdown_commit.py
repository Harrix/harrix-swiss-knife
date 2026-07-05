"""Tests for markdown git commit helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from harrix_swiss_knife.actions.markdown.markdown_commit import (
    build_commit_message_for_command,
    build_commit_message_for_template,
    format_commit_message,
    resolve_git_repo,
)


def test_format_commit_message_for_series_template() -> None:
    message = format_commit_message(
        '🎬 Add series "{Title}" (season {Season})',
        {"Title": "Rick and Morty", "Season": "9"},
    )
    assert message == '🎬 Add series "Rick and Morty" (season 9)'


def test_format_commit_message_for_book_uses_english_author() -> None:
    message = format_commit_message(
        '➕ Add book "{Title}" {AuthorEnglish}',
        {
            "Title": "The Chain of Chance",
            "Author": "Stanisław Lem",
            "Author's name in English": "Stanislaw Lem",
        },
    )
    assert message == '➕ Add book "The Chain of Chance" Stanislaw Lem'


def test_build_commit_message_for_template_uses_config_pattern() -> None:
    message = build_commit_message_for_template(
        "🎬 Movie",
        {"commit_message_template": '🎬 Add movie "{Title}"'},
        {"Title": "Tron: Ares"},
    )
    assert message == '🎬 Add movie "Tron: Ares"'


def test_build_commit_message_for_builtin_commands() -> None:
    assert build_commit_message_for_command("new_diary") == "➕ Add diary note"
    assert build_commit_message_for_command("new_cases") == "➕ Add cases"
    assert build_commit_message_for_command("new_dream", Date="2026-07-05") == "💤 Add dreams 2026-07-05"
    assert (
        build_commit_message_for_command("new_quotes", Author="Author", **{"Book Title": "Book"})
        == '➕ Add quotes from Author — "Book"'
    )


def test_resolve_git_repo_prefers_longest_paths_git_match(tmp_path: Path) -> None:
    notes_root = tmp_path / "Notes-Lists"
    movies_dir = notes_root / "Movies"
    movies_dir.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=notes_root, check=True, capture_output=True)  # noqa: S607

    repo = resolve_git_repo(movies_dir / "2026.md", [str(tmp_path), str(notes_root)])
    assert repo == notes_root.resolve()
