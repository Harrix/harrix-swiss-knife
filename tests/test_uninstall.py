"""Tests for the uninstall helpers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from harrix_swiss_knife.installer.log import OutcomeLog
from harrix_swiss_knife.installer.uninstall import (
    UninstallOptions,
    default_preserve_dir,
    list_paths_to_preserve,
    preserve_user_data,
    run_uninstall,
)


def _make_fake_hsk(root: Path) -> Path:
    hsk = root / "harrix-swiss-knife"
    hsk.mkdir(parents=True)
    (hsk / "pyproject.toml").write_text('name = "harrix-swiss-knife"\n', encoding="utf-8")
    db_dir = hsk / "data" / "databases"
    db_dir.mkdir(parents=True)
    (db_dir / "finance.db").write_bytes(b"finance")
    (db_dir / "fitness.db").write_bytes(b"fitness")
    fitness_img = db_dir / "fitness_img"
    fitness_img.mkdir()
    (fitness_img / "Squat.avif").write_bytes(b"img")
    keys = hsk / "api-keys"
    keys.mkdir()
    (keys / "openai.txt").write_text("secret", encoding="utf-8")
    config_dir = hsk / "config"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "sqlite_finance": str(db_dir / "finance.db"),
                "sqlite_fitness": str(db_dir / "fitness.db"),
                "sqlite_habits": str(db_dir / "habits.db"),
                "sqlite_food": str(db_dir / "food.db"),
            }
        ),
        encoding="utf-8",
    )
    (hsk / "src").mkdir()
    return hsk


def test_list_paths_to_preserve_includes_dbs_and_keys(tmp_path: Path) -> None:
    hsk = _make_fake_hsk(tmp_path)
    paths = {p.name for p in list_paths_to_preserve(hsk)}
    assert "finance.db" in paths
    assert "fitness.db" in paths
    assert "api-keys" in paths or any(p.name == "api-keys" for p in list_paths_to_preserve(hsk))
    assert any(p.name == "fitness_img" for p in list_paths_to_preserve(hsk))


def test_preserve_user_data_moves_out_of_tree(tmp_path: Path) -> None:
    hsk = _make_fake_hsk(tmp_path)
    dest = tmp_path / "Harrix Swiss Knife Data"
    log = OutcomeLog()
    preserved = preserve_user_data(hsk, dest, log)
    assert preserved
    assert (dest / "data" / "databases" / "finance.db").is_file()
    assert (dest / "api-keys" / "openai.txt").is_file()
    assert not (hsk / "data" / "databases" / "finance.db").exists()
    assert (dest / "README.txt").is_file()


def test_run_uninstall_keeps_databases(tmp_path: Path) -> None:
    hsk = _make_fake_hsk(tmp_path)
    pylib = tmp_path / "harrix-pylib"
    pylib.mkdir()
    (pylib / "marker.txt").write_text("x", encoding="utf-8")
    log = OutcomeLog()
    with (
        patch("harrix_swiss_knife.installer.uninstall.remove_app_shortcuts", return_value=[]),
        patch("harrix_swiss_knife.installer.uninstall._uninstall_cli"),
        patch("harrix_swiss_knife.installer.uninstall._stop_running_app"),
    ):
        result = run_uninstall(
            UninstallOptions(hsk_path=hsk, remove_sibling_repos=True),
            log,
        )
    assert result.ok
    assert result.preserved_dir is not None
    assert (result.preserved_dir / "data" / "databases" / "finance.db").read_bytes() == b"finance"
    assert not hsk.exists()
    assert not pylib.exists()


def test_default_preserve_dir_uses_install_parent(tmp_path: Path) -> None:
    hsk = tmp_path / "harrix-swiss-knife"
    hsk.mkdir()
    assert default_preserve_dir(hsk) == tmp_path / "Harrix Swiss Knife Data"
