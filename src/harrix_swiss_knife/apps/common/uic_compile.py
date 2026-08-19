"""Compile Qt `.ui` files and fix UTF-16 surrogate escapes from `pyside6-uic`.

`pyside6-uic` emits non-BMP emoji as UTF-16 surrogate-pair backslash-u escapes.
Python 3 string literals then contain lone surrogates, and
`QCoreApplication.translate` raises `UnicodeEncodeError: surrogates not allowed`.

"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication

_SURROGATE_PAIR_RE = re.compile(
    r"\\u(d[89ab][0-9a-f]{2})\\u(d[c-f][0-9a-f]{2})",
    re.IGNORECASE,
)
_APPS_ROOT = Path(__file__).resolve().parents[1]
_APP_UI_NAMES = frozenset({"finance", "fitness", "food", "habits"})
_TRANSLATE_PATCH_INSTALLED = [False]


def combine_utf16_surrogates(text: str) -> str:
    """Turn UTF-16 surrogate code points in `text` into real Unicode characters.

    Args:

    - `text` (`str`): String that may contain high+low surrogate pairs.

    Returns:

    - `str`: The same text, valid for UTF-8 (emoji combined from surrogate pairs).

    """
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return text.encode("utf-16", "surrogatepass").decode("utf-16")
    return text


def compile_app_ui(app_name: str) -> Path:
    """Run `pyside6-uic` for `apps/{app_name}/window.ui` and fix surrogate escapes.

    Args:

    - `app_name` (`str`): One of `finance`, `fitness`, `food`, `habits`.

    Returns:

    - `Path`: Path to the written `window.py`.

    """
    if app_name not in _APP_UI_NAMES:
        allowed = ", ".join(sorted(_APP_UI_NAMES))
        msg = f"Unknown app {app_name!r}. Expected one of: {allowed}."
        raise ValueError(msg)
    ui_path = _APPS_ROOT / app_name / "window.ui"
    py_path = _APPS_ROOT / app_name / "window.py"
    compile_ui(ui_path, py_path)
    return py_path


def compile_ui(ui_path: Path, py_path: Path) -> None:
    """Run `pyside6-uic` and rewrite UTF-16 surrogate escapes in `py_path`.

    Args:

    - `ui_path` (`Path`): Input `.ui` file.
    - `py_path` (`Path`): Output Python module path.

    """
    if not ui_path.is_file():
        msg = f"UI file not found: {ui_path}"
        raise FileNotFoundError(msg)
    command = [*_pyside_uic_command(), str(ui_path), "-o", str(py_path)]
    subprocess.run(command, check=True)
    rewrite_uic_py(py_path)


def install_safe_qt_translate() -> None:
    """Patch `QCoreApplication.translate` so UIC surrogate emoji does not crash.

    `pyside6-uic` can emit UTF-16 surrogate pairs in Python string literals.
    Python 3 cannot UTF-8-encode those, and `translate` then raises
    `UnicodeEncodeError`. The patch combines surrogate pairs first.

    """
    if _TRANSLATE_PATCH_INSTALLED[0]:
        return

    original = QCoreApplication.translate

    def translate(context: str, key: str, /, disambiguation: str | None = None, n: int = -1) -> str:
        return original(context, combine_utf16_surrogates(key), disambiguation, n)

    QCoreApplication.translate = translate  # ty: ignore[invalid-assignment]
    _TRANSLATE_PATCH_INSTALLED[0] = True


def rewrite_uic_py(py_path: Path) -> bool:
    """Rewrite UTF-16 surrogate-pair escapes in a generated UIC Python file.

    Args:

    - `py_path` (`Path`): Generated `window.py` (or any UIC output).

    Returns:

    - `bool`: `True` when the file changed.

    """
    text = py_path.read_text(encoding="utf-8")
    rewritten = rewrite_uic_source(text)
    if rewritten == text:
        return False
    py_path.write_text(rewritten, encoding="utf-8", newline="\n")
    return True


def rewrite_uic_source(source: str) -> str:
    """Replace UTF-16 surrogate-pair escapes in Python source with UCS-4 escapes.

    Args:

    - `source` (`str`): Generated UIC Python source.

    Returns:

    - `str`: Source with UCS-4 capital-U escapes instead of surrogate pairs.

    """
    return _SURROGATE_PAIR_RE.sub(_combined_unicode_escape, source)


def _combined_unicode_escape(match: re.Match[str]) -> str:
    """Turn one high+low UTF-16 surrogate pair into a UCS-4 escape."""
    high = int(match.group(1), 16)
    low = int(match.group(2), 16)
    codepoint = 0x10000 + ((high - 0xD800) << 10) + (low - 0xDC00)
    return f"\\U{codepoint:08x}"


def _pyside_uic_command() -> list[str]:
    """Return the `pyside6-uic` argv prefix from the active venv or PATH."""
    scripts_dir = Path(sys.executable).resolve().parent
    name = "pyside6-uic.exe" if os.name == "nt" else "pyside6-uic"
    local = scripts_dir / name
    if local.is_file():
        return [str(local)]
    found = shutil.which("pyside6-uic")
    if found:
        return [found]
    msg = "pyside6-uic not found (activate the project venv)."
    raise FileNotFoundError(msg)
