"""Git commit helpers for New Markdown template flows."""

from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ruff: noqa: RUF001

_DEFAULT_TEMPLATE_COMMIT_MESSAGES: dict[str, str] = {
    "📺 Movie: series": '🎬 Add series "{TitleEnglish}" (season {Season})',
    "🎬 Movie": '🎬 Add movie "{TitleEnglish}"',
    "📖 Book": '➕ Add book "{TitleEnglish}" {AuthorEnglish}',
    "☕ Coffee": '☕ Add coffee note "{Title}" in {City}',
    "✈️ Travel": '➕ Add travel "{Title}"',
    "🎭 Events": '➕ Add event "{Title}"',
}

_BUILTIN_COMMAND_COMMIT_MESSAGES: dict[str, str] = {
    "new_diary": "➕ Add diary note",
    "new_cases": "➕ Add cases",
    "new_dream": "💤 Add dreams {Date}",
    "new_quotes": '➕ Add quotes from {Author} — "{Book Title}"',
}

_COMMIT_PLACEHOLDER_RE = re.compile(r"\{([^}]+)\}")


def build_commit_message_for_command(command_key: str, **field_values: str) -> str | None:
    """Return a commit subject for a built-in New Markdown command."""
    pattern = _BUILTIN_COMMAND_COMMIT_MESSAGES.get(command_key)
    if not pattern:
        return None
    return format_commit_message(pattern, field_values)


def build_commit_message_for_template(
    template_name: str,
    template_config: dict[str, Any],
    field_values: dict[str, str],
) -> str | None:
    """Return a commit subject for a markdown_templates entry, or None if unknown."""
    pattern = template_config.get("commit_message_template") or _DEFAULT_TEMPLATE_COMMIT_MESSAGES.get(template_name)
    if not pattern:
        return None
    return format_commit_message(str(pattern), field_values)


def format_commit_message(pattern: str, field_values: dict[str, str]) -> str:
    """Substitute ``{Field}`` placeholders in a commit message pattern."""
    values = _commit_substitution_values(field_values)

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return values.get(key, "")

    message = _COMMIT_PLACEHOLDER_RE.sub(_replace, pattern)
    message = re.sub(r"  +", " ", message)
    return message.strip()


def resolve_git_repo(target_path: Path, paths_git: list[str]) -> Path | None:
    """Find a Git repository root that contains ``target_path``."""
    target = target_path.resolve()
    candidates: list[Path] = []

    for raw in paths_git:
        repo = Path(raw).resolve()
        try:
            target.relative_to(repo)
        except ValueError:
            continue
        candidates.append(repo)

    if candidates:
        candidates.sort(key=lambda path: len(str(path)), reverse=True)
        for repo in candidates:
            if _is_git_repo(repo):
                return repo

    current = target if target.is_dir() else target.parent
    while True:
        if _is_git_repo(current):
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def run_git_commit(repo: Path, message: str, paths_to_add: list[Path]) -> tuple[bool, str]:
    """Stage ``paths_to_add`` relative to ``repo`` and create a commit."""
    repo_resolved = repo.resolve()
    rel_paths: list[str] = []
    for path in paths_to_add:
        if not path.exists():
            continue
        resolved = path.resolve()
        try:
            rel_paths.append(resolved.relative_to(repo_resolved).as_posix())
        except ValueError:
            continue

    if not rel_paths:
        return False, "No files inside the git repository to commit."

    add_proc = subprocess.run(
        ["git", "add", "--", *rel_paths],  # noqa: S607
        cwd=repo_resolved,
        capture_output=True,
        text=True,
        check=False,
    )
    add_output = (add_proc.stdout + "\n" + add_proc.stderr).strip()
    if add_proc.returncode != 0:
        return False, add_output or "git add failed."

    commit_proc = subprocess.run(
        ["git", "commit", "-m", message],  # noqa: S607
        cwd=repo_resolved,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (commit_proc.stdout + "\n" + commit_proc.stderr).strip()
    if commit_proc.returncode != 0:
        return False, output or "git commit failed."
    return True, output


def _commit_substitution_values(field_values: dict[str, str]) -> dict[str, str]:
    now_local = datetime.now(UTC).astimezone()
    author_english = (field_values.get("Author's name in English") or "").strip()
    author = (field_values.get("Author") or "").strip()
    title = (field_values.get("Title") or "").strip()
    title_english = (
        (field_values.get("Original or English title") or "").strip()
        or (field_values.get("Title in English") or "").strip()
        or title
    )
    values = {key: (value or "").strip() for key, value in field_values.items()}
    values["TitleEnglish"] = title_english
    values["AuthorEnglish"] = author_english or author
    values["Date"] = values.get("Date") or now_local.strftime("%Y-%m-%d")
    return values


def _is_git_repo(path: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"
