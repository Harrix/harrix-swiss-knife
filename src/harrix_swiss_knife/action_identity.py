"""Build a clipboard snippet for an action class: name, class, relative path."""

from __future__ import annotations

import inspect
from pathlib import Path

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.paths import get_project_root

_PACKAGE_ROOT_NAME = "harrix_swiss_knife"
_SRC_DIR_NAME = "src"


def action_identity_name(class_action: type) -> str:
    """Return the action display name from the class docstring, else `title`."""
    for line in inspect.cleandoc(class_action.__doc__ or "").splitlines():
        text = line.strip().rstrip(".")
        if text:
            return text
    title = strip_md_inline_code_markers(str(getattr(class_action, "title", "") or ""))
    return title.strip() or class_action.__name__


def action_relative_source_path(class_action: type) -> str:
    """Return the action module path relative to the project root, using POSIX slashes."""
    try:
        source = Path(inspect.getfile(class_action)).resolve()
    except (OSError, TypeError):
        return ""
    if source.suffix == ".pyc":
        source = source.with_suffix(".py")

    try:
        return source.relative_to(get_project_root().resolve()).as_posix()
    except ValueError:
        pass

    parts = source.parts
    if _PACKAGE_ROOT_NAME in parts:
        index = parts.index(_PACKAGE_ROOT_NAME)
        if index > 0 and parts[index - 1] == _SRC_DIR_NAME:
            index -= 1
        return Path(*parts[index:]).as_posix()
    return source.as_posix()


def format_action_identity_text(class_action: type) -> str:
    """Return three lines: action name, class name, and relative source path."""
    return "\n".join(
        (
            action_identity_name(class_action),
            class_action.__name__,
            action_relative_source_path(class_action),
        )
    )
