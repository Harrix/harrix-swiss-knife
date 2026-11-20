"""Plain-text Git diffs for a single path (Fluent dirty-repos commit window)."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.common.git_cmd import git_run

_STATUS_XY_LEN = 2


def git_diff_text_for_path(repo: Path, relative_path: str, *, status: str = " M") -> str:
    """Return a unified diff (or untracked content) for one path under `repo`.

    Args:

    - `repo` (`Path`): Repository root.
    - `relative_path` (`str`): Path relative to the repo (forward or back slashes).
    - `status` (`str`): Two-character porcelain status; used to pick untracked vs diff.

    Returns:

    - `str`: Diff text, untracked file body, or a short note when empty.

    """
    repo = repo.resolve()
    path = relative_path.replace("\\", "/").strip()
    if not path:
        return ""

    index_status = status[0] if len(status) >= 1 else " "
    work_status = status[1] if len(status) >= _STATUS_XY_LEN else " "

    if index_status == "?" or work_status == "?":
        return _untracked_preview(repo, path)

    chunks: list[str] = []
    staged = git_run(repo, "diff", "--cached", "--", path)
    if staged.returncode == 0 and staged.stdout.strip():
        chunks.append(staged.stdout.rstrip())
    unstaged = git_run(repo, "diff", "--", path)
    if unstaged.returncode == 0 and unstaged.stdout.strip():
        chunks.append(unstaged.stdout.rstrip())
    if chunks:
        return "\n\n".join(chunks) + "\n"

    # Deleted / renamed edge cases with empty diff output.
    show = git_run(repo, "diff", "HEAD", "--", path)
    if show.returncode == 0 and show.stdout.strip():
        return show.stdout
    return f"(No textual diff for `{path}`.)\n"


def _untracked_preview(repo: Path, relative_path: str, *, max_bytes: int = 200_000) -> str:
    file_path = repo / Path(relative_path)
    if not file_path.is_file():
        return f"(Untracked path `{relative_path}` is not a regular file.)\n"
    try:
        raw = file_path.read_bytes()[:max_bytes]
    except OSError as exc:
        return f"(Could not read `{relative_path}`: {exc})\n"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return f"(Binary or non-UTF-8 untracked file `{relative_path}`, {len(raw)} bytes shown max.)\n"
    header = f"+++ untracked: {relative_path}\n"
    return header + text + ("" if text.endswith("\n") else "\n")
