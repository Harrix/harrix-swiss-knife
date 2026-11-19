"""Canonical list of periodic maintenance / update actions for the checklist UI.

When adding a new `On*` action that is a recurring maintenance, sync, update, or
health-check step, decide whether it belongs here (see `.cursor/rules/hsk-maintenance-checklist.mdc`).

Action classes are resolved lazily to avoid import cycles with `actions.development`.

"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import harrix_pylib as h

from harrix_swiss_knife.action_usage import load_action_usage
from harrix_swiss_knife.paths import get_config_path_str

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.common.base import ActionBase

# Optional Tools row: hidden unless the checklist footer checkbox is on.
UPDATE_HSK_STEP_CLASS = "OnUpdateHarrixSwissKnife"
_SHOW_UPDATE_HSK_KEY = "maintenance_checklist_show_update_hsk"


@dataclass(frozen=True, slots=True)
class MaintenanceStep:
    """One resolved row in the maintenance checklist."""

    action_cls: type[ActionBase]
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None

    @property
    def class_name(self) -> str:
        """Action class name used in `action_usage.json`."""
        return self.action_cls.__name__

    @property
    def title(self) -> str:
        """Display title for the checklist row."""
        if self.title_override:
            return self.title_override
        raw = getattr(self.action_cls, "title", self.class_name)
        return str(raw).replace("`", "")


@dataclass(frozen=True, slots=True)
class MaintenanceStepSpec:
    """Declarative checklist row (action imported lazily)."""

    module: str
    class_name: str
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None


def format_last_used(iso_stamp: str | None) -> str:
    """Return a short relative or absolute label for a usage timestamp."""
    parsed = _parse_last_used(iso_stamp)
    if parsed is None:
        return "Never" if not iso_stamp or not str(iso_stamp).strip() else str(iso_stamp)
    now = datetime.now(UTC).astimezone()
    local = parsed.astimezone()
    delta = now - local
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return local.strftime("%Y-%m-%d %H:%M")
    if seconds < _SECONDS_PER_MINUTE:
        return "Just now"
    if seconds < _SECONDS_PER_HOUR:
        minutes = seconds // _SECONDS_PER_MINUTE
        return f"{minutes} min ago"
    if seconds < _SECONDS_PER_DAY:
        hours = seconds // _SECONDS_PER_HOUR
        return f"{hours} h ago"
    if seconds < _SECONDS_PER_DAY * _RELATIVE_WEEK_DAYS:
        days = seconds // _SECONDS_PER_DAY
        return f"{days} d ago"
    return local.strftime("%Y-%m-%d %H:%M")


def is_last_used_within(iso_stamp: str | None, *, hours: float = 24) -> bool:
    """Return whether `iso_stamp` falls within the last `hours` (inclusive of now)."""
    parsed = _parse_last_used(iso_stamp)
    if parsed is None or hours <= 0:
        return False
    now = datetime.now(UTC).astimezone()
    seconds = (now - parsed.astimezone()).total_seconds()
    return 0 <= seconds < hours * _SECONDS_PER_HOUR


def last_used_for_class(class_name: str) -> str:
    """Return the ISO `last_used` stamp for `class_name`, or empty string."""
    entry = load_action_usage().get(class_name)
    if entry is None:
        return ""
    return entry.get("last_used") or ""


def load_show_update_hsk_step() -> bool:
    """Return whether the Update HSK checklist row is visible (default: hidden)."""
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return False
    value = loaded.get(_SHOW_UPDATE_HSK_KEY, False)
    return value if isinstance(value, bool) else False


def maintenance_groups() -> list[tuple[str, list[MaintenanceStep]]]:
    """Group resolved steps preserving order."""
    groups: list[tuple[str, list[MaintenanceStep]]] = []
    index: dict[str, list[MaintenanceStep]] = {}
    for step in maintenance_steps():
        bucket = index.get(step.group)
        if bucket is None:
            bucket = []
            index[step.group] = bucket
            groups.append((step.group, bucket))
        bucket.append(step)
    return groups


@lru_cache(maxsize=1)
def maintenance_steps() -> tuple[MaintenanceStep, ...]:
    """Resolve and cache checklist steps."""
    return tuple(_resolve_spec(spec) for spec in MAINTENANCE_STEP_SPECS)


def save_show_update_hsk_step(*, enabled: bool) -> None:
    """Persist whether the Update HSK checklist row is visible (`config-temp.json`)."""
    h.dev.config_update_value(_SHOW_UPDATE_HSK_KEY, bool(enabled), get_config_path_str(), is_temp=True)


def _parse_last_used(iso_stamp: str | None) -> datetime | None:
    if not iso_stamp or not str(iso_stamp).strip():
        return None
    try:
        parsed = datetime.fromisoformat(str(iso_stamp).strip())
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _resolve_spec(spec: MaintenanceStepSpec) -> MaintenanceStep:
    module = importlib.import_module(spec.module)
    action_cls = getattr(module, spec.class_name)
    return MaintenanceStep(
        action_cls=action_cls,
        group=spec.group,
        lucide_icon=spec.lucide_icon,
        note=spec.note,
        include_in_run_all=spec.include_in_run_all,
        title_override=spec.title_override,
    )


_SECONDS_PER_MINUTE = 60
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_DAY = 86400
_RELATIVE_WEEK_DAYS = 7


# Order is the suggested Run-all sequence within and across groups.
MAINTENANCE_STEP_SPECS: tuple[MaintenanceStepSpec, ...] = (
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.update_uv",
        "OnUpdateUv",
        "Tools",
        "download",
        note="Update the uv installer itself",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.update_node",
        "OnUpdateNode",
        "Tools",
        "file-code",
        note="Install / refresh Node.js",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.npm_manage_packages",
        "OnNpmManagePackages",
        "Tools",
        "package",
        note="Global npm packages from config",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.update_lucide_icons",
        "OnUpdateLucideIcons",
        "Tools",
        "sparkles",
        note="Refresh Lucide SVG assets",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.upgrade_uv_packages",
        "OnUpgradeUvPackages",
        "Tools",
        "boxes",
        note="Exits the app, upgrades project packages, then relaunches",
        include_in_run_all=False,
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.update_harrix_swiss_knife",
        "OnUpdateHarrixSwissKnife",
        "Tools",
        "refresh-cw",
        note="Pull and update this app from GitHub",
        include_in_run_all=False,
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.markdown.beautify_md_and_regenerate_g_md",
        "OnBeautifyMdAndRegenerateGMd",
        "Content",
        "file-text",
        note="Beautify notes and regenerate `.g.md`",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.site.generate_static_site",
        "OnGenerateStaticSite",
        "Content",
        "globe",
        note="Build the static site",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.python.check_python_projects",
        "OnCheckPythonProjects",
        "Checks",
        "flask-conical",
        note="Full PY check for configured projects",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.files.check_git_repos_needing_commit",
        "OnCheckGitReposNeedingCommit",
        "Checks",
        "git-branch",
        note="Dirty repos under `paths_git_roots`",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.files.sync_chrome_yandex_bookmarks",
        "OnSyncChromeYandexBookmarks",
        "Sync",
        "bookmark",
        note="Merge Chrome and Yandex bookmark exports",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.vscode.sync_save_commands",
        "OnSyncSaveCommands",
        "Sync",
        "command",
        note="Union Saved Commands across editors",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.vscode.backup_cursor",
        "OnBackupCursor",
        "Sync",
        "hard-drive",
        note="ZIP Cursor settings / chats / `.cursor`",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.apps.habits",
        "OnHabits",
        "Sync",
        "check-circle",
        note="Open Habits — use TickTick sync there",
        include_in_run_all=False,
        title_override="Habit tracker (TickTick sync)…",
    ),
    MaintenanceStepSpec(
        "harrix_swiss_knife.actions.development.transfer_private_data",
        "OnTransferPrivateData",
        "Sync",
        "folder-input",
        note="Export / import private ZIP",
        include_in_run_all=False,
    ),
)
