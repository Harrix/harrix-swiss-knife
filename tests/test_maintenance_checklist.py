"""Tests for the maintenance checklist registry and CLI listing."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from harrix_swiss_knife.actions.common.maintenance_checklist_steps import (
    MAINTENANCE_STEP_SPECS,
    format_last_used,
    is_last_used_within,
    maintenance_groups,
    maintenance_steps,
)
from harrix_swiss_knife.actions.development.run_maintenance_checklist import OnRunMaintenanceChecklist
from harrix_swiss_knife.actions.development.upgrade_uv_packages import OnUpgradeUvPackages


def test_format_last_used_never_and_relative() -> None:
    assert format_last_used("") == "Never"
    assert format_last_used(None) == "Never"
    recent = (datetime.now(UTC).astimezone() - timedelta(minutes=3)).isoformat(timespec="seconds")
    assert format_last_used(recent) == "3 min ago"


def test_is_last_used_within_last_day() -> None:
    assert is_last_used_within("") is False
    assert is_last_used_within(None) is False
    now = datetime.now(UTC).astimezone()
    assert is_last_used_within((now - timedelta(hours=1)).isoformat(timespec="seconds"))
    assert is_last_used_within((now - timedelta(hours=23)).isoformat(timespec="seconds"))
    assert not is_last_used_within((now - timedelta(hours=25)).isoformat(timespec="seconds"))
    assert not is_last_used_within((now + timedelta(hours=1)).isoformat(timespec="seconds"))


def test_maintenance_groups_preserve_order() -> None:
    groups = maintenance_groups()
    assert groups
    flat = [step.class_name for _, steps in groups for step in steps]
    assert flat == [step.class_name for step in maintenance_steps()]


def test_maintenance_steps_unique_and_nonempty() -> None:
    steps = maintenance_steps()
    assert steps
    assert len(MAINTENANCE_STEP_SPECS) == len(steps)
    names = [step.class_name for step in steps]
    assert len(names) == len(set(names))
    for step in steps:
        assert step.group
        assert step.lucide_icon
        assert step.title


def test_noninteractive_lists_steps() -> None:
    action = OnRunMaintenanceChecklist()
    action.execute(noninteractive=True)
    text = "\n".join(action.result_lines)
    assert "step" in text.lower()
    assert any("uv" in line.lower() for line in action.result_lines)


def test_upgrade_uv_packages_excluded_from_run_all() -> None:
    step = next(item for item in maintenance_steps() if item.action_cls is OnUpgradeUvPackages)
    assert step.include_in_run_all is False
