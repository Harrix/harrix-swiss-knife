"""Markdown store for per-habit daily comments in a Notes-Habits repo."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.markdown_commit import resolve_git_repo, run_git_commit
from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.apps.common.db_git import ensure_folder_git_repo
from harrix_swiss_knife.paths import get_config_path, get_project_root

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

DEFAULT_HABIT_COMMENTS_DIR = "Notes-Habits"
_DATE_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
_UNSAFE_FOLDER_RE = re.compile(r'[<>:"/\\\\|?*]')
_WHITESPACE_RE = re.compile(r"\s+")
_DEFAULT_BEGINNING = "---\nlang: ru\n---\n"
_PREVIEW_MAX_LENGTH = 72
_NOTE_REPO_NAMES = (
    "Notes",
    "Notes-Diaries",
    "Notes-External",
    "Notes-Health",
    DEFAULT_HABIT_COMMENTS_DIR,
    "Notes-Lists",
    "Notes-Places",
    "Notes-Temp",
)


class HabitCommentsStore:
    """Read and write per-habit daily comments as Markdown notes."""

    def __init__(
        self,
        root: Path | None,
        *,
        beginning: str = "",
        paths_git: list[str] | None = None,
        commit: bool = True,
    ) -> None:
        """Create a store rooted at the Notes-Habits folder.

        Args:

        - `root` (`Path | None`): Repository folder. `None` disables storage.
        - `beginning` (`str`): YAML front matter for new files.
        - `paths_git` (`list[str] | None`): Git roots used to resolve the repo.
        - `commit` (`bool`): Commit after a successful write. Defaults to `True`.

        """
        self._root = Path(root) if root is not None else None
        self._beginning = beginning or _DEFAULT_BEGINNING
        self._paths_git = list(paths_git or [])
        self._commit = commit

    def comment(self, habit_id: int, date_str: str) -> str:
        """Return the comment for `habit_id` on `date_str`, or `""`."""
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return ""
        for item in parse_habit_comment_file(path.read_text(encoding="utf-8")):
            if item.date == date_str:
                return item.text
        return ""

    def comments_for_habit(self, habit_id: int) -> list[HabitDayComment]:
        """Return all dated comments for a habit, newest first."""
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return []
        items = parse_habit_comment_file(path.read_text(encoding="utf-8"))
        return sorted(items, key=lambda item: item.date, reverse=True)

    def dates_with_comments(self, habit_ids: Iterable[int]) -> dict[int, set[str]]:
        """Return the comment dates present for each habit ID."""
        result: dict[int, set[str]] = {}
        for habit_id in habit_ids:
            result[int(habit_id)] = {item.date for item in self.comments_for_habit(int(habit_id))}
        return result

    def ensure_repository(self) -> bool:
        """Create the Notes-Habits folder and Git repo when they are missing."""
        if self._root is None:
            return False
        try:
            self._root.mkdir(parents=True, exist_ok=True)
        except OSError:
            logger.warning("Could not create habit comments folder %s", self._root)
            return False
        ensure_folder_git_repo(self._root)
        posix = self._root.as_posix()
        if posix not in self._paths_git:
            self._paths_git.append(posix)
        return self._root.is_dir()

    def find_habit_file(self, habit_id: int) -> Path | None:
        """Return the existing Markdown file for `habit_id`, if any."""
        if self._root is None:
            return None
        prefix = f"{int(habit_id):04d}"
        if not self._root.is_dir():
            return None
        matches = sorted(path for path in self._root.glob(f"{prefix}-*") if path.is_dir())
        exact = self._root / prefix
        if exact.is_dir():
            matches = [exact, *matches]
        seen: set[Path] = set()
        for folder in matches:
            resolved = folder.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            named = folder / f"{folder.name}.md"
            if named.is_file():
                return named
            fallback = next(iter(sorted(folder.glob("*.md"))), None)
            if fallback is not None:
                return fallback
        return None

    @classmethod
    def from_config(cls, config: dict[str, Any] | None, *, commit: bool = True) -> HabitCommentsStore:
        """Build a store from application config."""
        data = config or {}
        paths_git = data.get("paths_git")
        git_roots = [str(path) for path in paths_git] if isinstance(paths_git, list) else []
        return cls(
            resolve_habit_comments_root(data),
            beginning=habit_comment_beginning(data),
            paths_git=git_roots,
            commit=commit,
        )

    def is_configured(self) -> bool:
        """Return whether a comments folder is configured."""
        return self._root is not None

    def root(self) -> Path | None:
        """Return the Notes-Habits folder, or `None` when unconfigured."""
        return self._root

    def set_comment(
        self,
        habit_id: int,
        date_str: str,
        text: str,
        *,
        habit_name: str,
    ) -> Path | None:
        """Write or delete the comment for one habit day.

        Empty `text` removes that date. Returns the Markdown path, or `None`
        when storage is not configured.

        """
        if self._root is None:
            return None
        cleaned = text.strip()
        path = self.find_habit_file(habit_id)
        if path is None and not cleaned:
            return None
        if not self.ensure_repository():
            return None

        if path is None:
            path = self._new_habit_file(habit_id, habit_name)
        existing = parse_habit_comment_file(path.read_text(encoding="utf-8")) if path.is_file() else []
        existed = any(item.date == date_str for item in existing)
        remaining = [item for item in existing if item.date != date_str]
        if cleaned:
            remaining.append(HabitDayComment(date=date_str, text=cleaned))
        previous = path.read_text(encoding="utf-8") if path.is_file() else ""
        rendered = render_habit_comment_file(
            remaining,
            habit_id=habit_id,
            habit_name=habit_name,
            beginning=self._beginning,
        )
        if rendered == previous:
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        if self._commit:
            self._commit_change(
                path,
                habit_name=habit_name,
                date_str=date_str,
                deleted=not cleaned,
                existed=existed,
            )
        return path

    def _commit_change(
        self,
        path: Path,
        *,
        habit_name: str,
        date_str: str,
        deleted: bool,
        existed: bool,
    ) -> None:
        repo = resolve_git_repo(path, self._paths_git)
        if repo is None:
            return
        if deleted:
            message = f"🗑️ Delete habit comment {habit_name} {date_str}"
        elif existed:
            message = f"🔧 Modify habit comment {habit_name} {date_str}"
        else:
            message = f"➕ Add habit comment {habit_name} {date_str}"  # noqa: RUF001
        ok, output = run_git_commit(repo, message, [path])
        if not ok:
            logger.warning("Habit comment git commit failed: %s", output)

    def _new_habit_file(self, habit_id: int, habit_name: str) -> Path:
        if self._root is None:
            msg = "Habit comments folder is not configured"
            raise RuntimeError(msg)
        folder_name = f"{int(habit_id):04d}-{habit_comment_folder_slug(habit_name)}"
        folder = self._root / folder_name
        return folder / f"{folder_name}.md"


@dataclass(frozen=True)
class HabitDayComment:
    """One dated comment for a habit."""

    date: str
    text: str


def apply_habit_comments_root_to_config(config: dict[str, Any], root: Path) -> bool:
    """Set `path_habit_comments` and append the folder to `paths_git` / `paths_notes`.

    Args:

    - `config` (`dict[str, Any]`): In-memory config to update.
    - `root` (`Path`): Notes-Habits repository folder.

    Returns:

    - `bool`: `True` when at least one field changed.

    """
    posix = Path(root).as_posix()
    changed = False
    current = str(config.get("path_habit_comments") or "").strip()
    if not current or Path(current).as_posix() != posix:
        config["path_habit_comments"] = posix
        changed = True
    for key in ("paths_git", "paths_notes"):
        raw = config.get(key)
        items = [str(item) for item in raw] if isinstance(raw, list) else []
        if not _path_in_list(posix, items):
            items.append(posix)
            config[key] = items
            changed = True
    return changed


def habit_comment_beginning(config: dict[str, Any] | None) -> str:
    """Return `beginning_of_md` YAML with `personal_data` applied.

    Uses the same front matter as new Markdown notes, then the caller adds
    `habit-id`. When `personal_data.enabled` is true, `author` and
    `author-email` are inserted.

    """
    data = config or {}
    beginning = _resolve_beginning_of_md(str(data.get("beginning_of_md") or ""))
    personal = data.get("personal_data")
    return OnNewMarkdown.apply_personal_data_to_beginning(
        beginning,
        personal if isinstance(personal, dict) else None,
    )


def habit_comment_folder_slug(name: str) -> str:
    """Return a filesystem-safe stem from a habit name."""
    cleaned = _UNSAFE_FOLDER_RE.sub("", (name or "").strip())
    cleaned = _WHITESPACE_RE.sub("-", cleaned).strip(".-")
    return cleaned or "habit"


def parse_habit_comment_file(content: str) -> list[HabitDayComment]:
    """Return dated `## YYYY-MM-DD` sections from a habit comment file."""
    matches = list(_DATE_HEADING_RE.finditer(content))
    comments: list[HabitDayComment] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        text = content[start:end].strip()
        if text:
            comments.append(HabitDayComment(date=match.group(1), text=text))
    return comments


def persist_habit_comments_root(
    root: Path,
    config: dict[str, Any] | None = None,
    *,
    config_path: Path | None = None,
) -> None:
    """Write Notes-Habits paths into `config.json` and keep `config` in sync.

    Args:

    - `root` (`Path`): Notes-Habits repository folder.
    - `config` (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
    - `config_path` (`Path | None`): Config file. Defaults to the project config.

    """
    path = Path(config_path) if config_path is not None else get_config_path()
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        data = loaded if isinstance(loaded, dict) else {}
    else:
        data = {}
    apply_habit_comments_root_to_config(data, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    if config is not None:
        apply_habit_comments_root_to_config(config, root)


def preview_habit_comment(text: str) -> str:
    """Return the first line of a comment, truncated for list rows."""
    preview = text.splitlines()[0] if text else ""
    if len(preview) > _PREVIEW_MAX_LENGTH:
        return preview[: _PREVIEW_MAX_LENGTH - 1] + "…"
    return preview


def render_habit_comment_file(
    comments: Iterable[HabitDayComment],
    *,
    habit_id: int,
    habit_name: str,
    beginning: str = "",
) -> str:
    """Render a named-folder habit comment file, newest dates first."""
    ordered = sorted(
        (HabitDayComment(date=item.date, text=item.text.strip()) for item in comments if item.text.strip()),
        key=lambda item: item.date,
        reverse=True,
    )
    front = _frontmatter_with_habit_id(beginning or _DEFAULT_BEGINNING, habit_id).rstrip()
    lines = [front, "", f"# {habit_name.strip() or 'Habit'}", ""]
    for item in ordered:
        lines.extend([f"## {item.date}", "", item.text.rstrip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def resolve_habit_comments_root(config: dict[str, Any] | None) -> Path | None:
    """Return the Notes-Habits repository path from config, if it can be inferred."""
    data = config or {}
    raw = str(data.get("path_habit_comments") or "").strip()
    if raw:
        return Path(raw)
    parent = resolve_notes_parent(data)
    if parent is not None:
        return parent / DEFAULT_HABIT_COMMENTS_DIR
    return None


def resolve_notes_parent(config: dict[str, Any] | None) -> Path | None:
    """Return the folder that holds Notes, Notes-Diaries, and sibling repos."""
    data = config or {}
    diary = str(data.get("path_diary") or "").strip()
    if diary:
        diary_path = Path(diary)
        if diary_path.name.lower() == "diary":
            return diary_path.parent.parent
        if diary_path.name == "Notes-Diaries":
            return diary_path.parent
    notes = str(data.get("path_notes") or "").strip()
    if notes:
        return _notes_parent_from_path_notes(Path(notes))
    paths_notes = data.get("paths_notes")
    if isinstance(paths_notes, list):
        for item in paths_notes:
            raw = str(item or "").strip()
            if raw:
                return _notes_parent_from_path_notes(Path(raw))
    return None


def _contains_note_repos(folder: Path) -> bool:
    """Return whether `folder` already contains a Notes / Notes-* repository."""
    try:
        return folder.is_dir() and any((folder / name).is_dir() for name in _NOTE_REPO_NAMES)
    except OSError:
        return False


def _frontmatter_with_habit_id(beginning: str, habit_id: int) -> str:
    text = (beginning or _DEFAULT_BEGINNING).replace("\r\n", "\n").strip()
    if not text.startswith("---"):
        return f"---\nlang: ru\nhabit-id: {habit_id}\n---"
    lines = text.splitlines()
    end_idx = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end_idx is None:
        return f"---\nlang: ru\nhabit-id: {habit_id}\n---"
    body = [line for line in lines[1:end_idx] if not line.lower().startswith("habit-id:")]
    body.append(f"habit-id: {habit_id}")
    return "\n".join(["---", *body, "---"])


def _notes_parent_from_path_notes(notes_path: Path) -> Path:
    """Infer the shared notes folder from `path_notes`."""
    if _contains_note_repos(notes_path):
        return notes_path
    if _contains_note_repos(notes_path.parent):
        return notes_path.parent
    if notes_path.name == "Notes" and notes_path.parent.name == "Notes":
        return notes_path.parent
    return notes_path


def _path_in_list(posix: str, items: list[str]) -> bool:
    """Return whether `posix` is already present in `items`."""
    target = Path(posix)
    return any(Path(str(item)) == target or Path(str(item)).as_posix() == target.as_posix() for item in items)


def _resolve_beginning_of_md(raw: str) -> str:
    """Return beginning-of-md text, expanding a `snippet:` path when needed."""
    text = raw.strip()
    if not text:
        return _DEFAULT_BEGINNING
    if text.startswith("snippet:"):
        snippet_path = get_project_root() / text.split("snippet:", 1)[1].strip()
        if snippet_path.is_file():
            return snippet_path.read_text(encoding="utf-8")
        return _DEFAULT_BEGINNING
    return raw
