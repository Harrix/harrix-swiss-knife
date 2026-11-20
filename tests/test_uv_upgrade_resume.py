"""Tests for post-uv-upgrade resume payload in config-temp."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.uv_upgrade_resume import (
    clear_uv_upgrade_resume,
    normalize_uv_upgrade_resume,
    pop_uv_upgrade_resume,
    save_uv_upgrade_resume,
)

if TYPE_CHECKING:
    import pytest


def test_normalize_uv_upgrade_resume_adds_upgrade_step_when_reopening() -> None:
    payload = normalize_uv_upgrade_resume(
        {
            "reopen_maintenance_checklist": True,
            "maintenance_session_done": ["OnUpdateUv"],
        }
    )
    assert payload is not None
    assert payload["reopen_maintenance_checklist"] is True
    assert payload["maintenance_session_done"] == ["OnUpdateUv", "OnUpgradeUvPackages"]


def test_normalize_uv_upgrade_resume_rejects_invalid() -> None:
    assert normalize_uv_upgrade_resume(None) is None
    assert normalize_uv_upgrade_resume("x") is None


def test_save_and_pop_uv_upgrade_resume_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    (tmp_path / "config-temp.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.uv_upgrade_resume.get_config_path_str",
        lambda: str(config),
    )
    save_uv_upgrade_resume(
        reopen_maintenance_checklist=True,
        maintenance_session_done=["OnUpdateNode"],
    )
    loaded = pop_uv_upgrade_resume()
    assert loaded is not None
    assert loaded["reopen_maintenance_checklist"] is True
    assert "OnUpgradeUvPackages" in loaded["maintenance_session_done"]
    assert "OnUpdateNode" in loaded["maintenance_session_done"]
    assert pop_uv_upgrade_resume() is None
    clear_uv_upgrade_resume()
