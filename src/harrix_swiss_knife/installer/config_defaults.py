"""Default `config.json` tweaks for a fresh install."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.installer.constants import HSK_REPO_NAME, REPO_NAMES

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.log import OutcomeLog

_PLACEHOLDER_RE = re.compile(r"<YOUR_[^>]*>", re.IGNORECASE)


def apply_config_defaults(hsk_path: Path, log: OutcomeLog) -> None:
    """Apply first-run defaults: stack paths, DBs, and show-main-window.

    Writes install-relative paths so Update / Python checks / Android actions find
    the three sibling repos under the install parent. Personal folders (notes,
    photos, vector icons, sites, …) stay as placeholders for the user to set.

    """
    config_path = _ensure_config_json(hsk_path, log)
    if config_path is None:
        return
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.add("skipped", f"Could not read config.json: {exc}")
        return
    if not isinstance(data, dict):
        log.add("skipped", "config.json root is not an object")
        return

    hsk = hsk_path.resolve()
    install_root = hsk.parent
    siblings = {name: (install_root / name).resolve() for name in REPO_NAMES}

    log.step("Default config (show main window on startup)")
    data["show_main_window_on_startup"] = True
    log.add("installed", "Configured show_main_window_on_startup=true")

    _apply_stack_paths(data, install_root=install_root, siblings=siblings, hsk=hsk, log=log)
    _apply_database_paths(data=data, hsk_path=hsk, log=log)

    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_unset_config_path(value: object) -> bool:
    """Return whether a config path looks empty, a `<YOUR_…>` placeholder, or missing."""
    if not isinstance(value, str) or not value.strip():
        return True
    if _PLACEHOLDER_RE.search(value):
        return True
    try:
        return not Path(value).expanduser().exists()
    except OSError:
        return True


def _apply_database_paths(*, data: dict[str, Any], hsk_path: Path, log: OutcomeLog) -> None:
    log.step("Default databases paths (fresh PC fallback)")
    db_dir = hsk_path / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    apps = (
        ("sqlite_finance", "finance.db"),
        ("sqlite_fitness", "fitness.db"),
        ("sqlite_habits", "habits.db"),
        ("sqlite_food", "food.db"),
    )
    for key, filename in apps:
        if is_unset_config_path(data.get(key)):
            new_path = (db_dir / filename).as_posix()
            data[key] = new_path
            log.add("installed", f"Set {key}={new_path}")


def _apply_stack_paths(
    data: dict[str, Any],
    *,
    install_root: Path,
    siblings: dict[str, Path],
    hsk: Path,
    log: OutcomeLog,
) -> None:
    """Point stack-related config keys at this install's sibling repos."""
    log.step("Default stack paths (install siblings)")
    root_posix = install_root.as_posix()
    hsk_posix = hsk.as_posix()
    pylib = siblings.get("harrix-pylib")
    pyssg = siblings.get("harrix-pyssg")
    pylib_posix = pylib.as_posix() if pylib is not None else ""
    pyssg_posix = pyssg.as_posix() if pyssg is not None else ""

    data["path_github"] = root_posix
    log.add("installed", f"Set path_github={root_posix}")

    project_paths = [siblings[name].as_posix() for name in REPO_NAMES if name in siblings and siblings[name].is_dir()]
    if not project_paths:
        project_paths = [hsk_posix]
    data["paths_python_projects"] = project_paths
    log.add("installed", f"Set paths_python_projects={project_paths}")

    library_paths = [p for p in (pylib_posix, pyssg_posix) if p and Path(p).is_dir()]
    data["paths_python_libraries"] = library_paths
    log.add("installed", f"Set paths_python_libraries={library_paths}")

    android = hsk / "android"
    android_paths = [android.as_posix()] if android.is_dir() else []
    data["paths_android_projects"] = android_paths
    if android_paths:
        log.add("installed", f"Set paths_android_projects={android_paths}")
    else:
        log.add("skipped", "paths_android_projects not set (android/ missing)")

    data["paths_python_project_creation"] = [root_posix]
    log.add("installed", f"Set paths_python_project_creation=[{root_posix}]")

    data["paths_combine_for_ai"] = [
        {
            "base_folder": hsk_posix,
            "files": [f"{hsk_posix}/src/**/*.py"],
            "name": HSK_REPO_NAME,
        }
    ]
    log.add("installed", f"Set paths_combine_for_ai for {HSK_REPO_NAME}")

    data["paths_git"] = project_paths
    log.add("installed", f"Set paths_git={project_paths}")


def _ensure_config_json(hsk_path: Path, log: OutcomeLog) -> Path | None:
    """Return `config/config.json`, copying from the example when missing."""
    config_dir = hsk_path / "config"
    config_path = config_dir / "config.json"
    if config_path.is_file():
        return config_path
    example_path = config_dir / "config.example.json"
    if not example_path.is_file():
        log.add("skipped", "Could not create config.json (config.example.json missing)")
        return None
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(example_path, config_path)
    except OSError as exc:
        log.add("skipped", f"Could not create config.json from example: {exc}")
        return None
    log.add("installed", "Created config.json from config.example.json")
    return config_path
