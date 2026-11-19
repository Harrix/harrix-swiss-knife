"""Tests for the maintenance checklist registry and CLI listing."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.actions.common.maintenance_checklist_dialog import MaintenanceChecklistDialog
from harrix_swiss_knife.actions.common.maintenance_checklist_steps import (
    CHECK_GIT_REPOS_STEP_CLASS,
    MAINTENANCE_STEP_SPECS,
    UPDATE_HSK_STEP_CLASS,
    format_last_used,
    is_last_used_within,
    load_show_update_hsk_step,
    maintenance_groups,
    maintenance_steps,
)
from harrix_swiss_knife.actions.development.run_maintenance_checklist import OnRunMaintenanceChecklist
from harrix_swiss_knife.actions.development.update_harrix_swiss_knife import OnUpdateHarrixSwissKnife
from harrix_swiss_knife.actions.development.upgrade_uv_packages import OnUpgradeUvPackages
from harrix_swiss_knife.win11_caption import OVERLAY_CAPTION_PROPERTY


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_format_last_used_never_and_relative() -> None:
    assert format_last_used("") == "Never"
    assert format_last_used(None) == "Never"
    recent = (datetime.now(UTC).astimezone() - timedelta(minutes=3)).isoformat(timespec="seconds")
    assert format_last_used(recent) == "3 min ago"


def test_git_repos_step_tint_follows_all_clean_status(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git check card is green only when the last scan reported every repo clean."""
    assert qapp is not None
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_show_update_hsk_step",
        lambda: False,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_git_repos_all_clean",
        lambda: True,
    )
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    try:
        row = dialog._rows[CHECK_GIT_REPOS_STEP_CLASS]
        assert row.card._success_tint is True
        assert "All configured repos are clean" in row.card._description_label.text()
        monkeypatch.setattr(
            "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_git_repos_all_clean",
            lambda: False,
        )
        dialog._refresh_row(CHECK_GIT_REPOS_STEP_CLASS)
        assert row.card._success_tint is False
        assert "Git: dirty repos" in row.card._description_label.text()
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


def test_is_last_used_within_last_day() -> None:
    assert is_last_used_within("") is False
    assert is_last_used_within(None) is False
    now = datetime.now(UTC).astimezone()
    assert is_last_used_within((now - timedelta(hours=1)).isoformat(timespec="seconds"))
    assert is_last_used_within((now - timedelta(hours=23)).isoformat(timespec="seconds"))
    assert not is_last_used_within((now - timedelta(hours=25)).isoformat(timespec="seconds"))
    assert not is_last_used_within((now + timedelta(hours=1)).isoformat(timespec="seconds"))


def test_maintenance_checklist_busy_keeps_focus_out_of_scroll_list(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disabling Run must not move focus into another card (that auto-scrolls the list)."""
    assert qapp is not None
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_show_update_hsk_step",
        lambda: False,
    )
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    dialog.show()
    qapp.processEvents()
    try:
        first = next(row for class_name, row in dialog._rows.items() if class_name != UPDATE_HSK_STEP_CLASS)
        first.run_button.setFocus(Qt.FocusReason.OtherFocusReason)
        qapp.processEvents()
        dialog._scroll.verticalScrollBar().setValue(0)
        dialog._set_busy(busy=True)
        qapp.processEvents()
        focused = dialog.focusWidget()
        assert focused is dialog or focused is None or not dialog._scroll.isAncestorOf(focused)
        assert dialog._scroll.verticalScrollBar().value() == 0
        dialog._set_busy(busy=False)
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


def test_maintenance_checklist_dialog_is_non_modal(qapp: QApplication) -> None:
    """Checklist must not block the rest of the app as an application-modal dialog."""
    assert qapp is not None
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    try:
        assert dialog.isModal() is False
        assert dialog.windowModality() == Qt.WindowModality.NonModal
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


def test_maintenance_checklist_run_buttons_enabled_before_show(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run stays enabled after construct; do not use QWidget.isVisible() for that."""
    assert qapp is not None
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_show_update_hsk_step",
        lambda: False,
    )
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    try:
        assert dialog.isVisible() is False
        enabled = [
            row.run_button.isEnabled()
            for class_name, row in dialog._rows.items()
            if class_name != UPDATE_HSK_STEP_CLASS
        ]
        assert enabled
        assert all(enabled)
        assert dialog._rows[UPDATE_HSK_STEP_CLASS].run_button.isEnabled() is False
        assert dialog._run_all_button.isEnabled() is True
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


def test_maintenance_checklist_uses_app_caption_chrome(qapp: QApplication) -> None:
    """Use the same Win11 caption / frameless chrome as other HSK app Windows."""
    assert qapp is not None
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    try:
        assert dialog.property(OVERLAY_CAPTION_PROPERTY) is True
        if sys.platform == "win32":
            assert dialog._win11_caption is True
            assert dialog.windowFlags() & Qt.WindowType.FramelessWindowHint
            assert dialog.findChild(QWidget, "captionBar") is not None
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


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


def test_show_update_hsk_pref_defaults_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_steps.h.dev.config_load",
        lambda *_args, **_kwargs: {},
    )
    assert load_show_update_hsk_step() is False


def test_update_hsk_step_hidden_by_default(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """Update HSK stays in the registry but is off until the footer checkbox is checked."""
    assert qapp is not None
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.load_show_update_hsk_step",
        lambda: False,
    )
    saved: list[bool] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.maintenance_checklist_dialog.save_show_update_hsk_step",
        lambda *, enabled: saved.append(enabled),
    )
    OnRunMaintenanceChecklist.clear_checklist_dialog()
    dialog = MaintenanceChecklistDialog()
    try:
        row = dialog._rows[UPDATE_HSK_STEP_CLASS]
        assert row.step.action_cls is OnUpdateHarrixSwissKnife
        assert row.card.isHidden() is True
        assert dialog._show_update_hsk.isChecked() is False
        dialog._show_update_hsk.setChecked(True)
        assert row.card.isHidden() is False
        assert saved == [True]
    finally:
        dialog.close()
        dialog.deleteLater()
        OnRunMaintenanceChecklist.clear_checklist_dialog()


def test_upgrade_uv_packages_excluded_from_run_all() -> None:
    step = next(item for item in maintenance_steps() if item.action_cls is OnUpgradeUvPackages)
    assert step.include_in_run_all is False
