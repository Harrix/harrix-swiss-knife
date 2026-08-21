"""Tests for in-place ZIP update of Harrix stack repos."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, PropertyMock, patch

from harrix_swiss_knife.actions.development.update_harrix_swiss_knife import OnUpdateHarrixSwissKnife
from harrix_swiss_knife.paths import clear_directory_contents


def test_clear_directory_contents_keeps_named_children(tmp_path: Path) -> None:
    keep = tmp_path / ".venv"
    keep.mkdir()
    (keep / "marker.txt").write_text("ok", encoding="utf-8")
    gone = tmp_path / "src"
    gone.mkdir()
    (gone / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / "readme.md").write_text("r", encoding="utf-8")

    clear_directory_contents(tmp_path, keep_names={".venv"})

    assert keep.is_dir()
    assert (keep / "marker.txt").read_text(encoding="utf-8") == "ok"
    assert not gone.exists()
    assert not (tmp_path / "readme.md").exists()


def test_resolve_github_branch_falls_back_to_main() -> None:
    action = OnUpdateHarrixSwissKnife()
    action.add_line = MagicMock()
    action._fetch_github_default_branch = MagicMock(side_effect=OSError(2, "No such file or directory"))
    assert action._resolve_github_branch("Harrix", "harrix-pylib") == "main"
    action.add_line.assert_called()
    assert "falling back" in str(action.add_line.call_args.args[0])


def test_swiss_zip_preserves_venv_and_data(tmp_path: Path) -> None:
    dest = tmp_path / "harrix-swiss-knife"
    dest.mkdir()
    (dest / ".venv" / "Lib").mkdir(parents=True)
    (dest / ".venv" / "Lib" / "certifi-ca.pem").write_text("ca", encoding="utf-8")
    (dest / "data" / "databases").mkdir(parents=True)
    (dest / "data" / "databases" / "food.db").write_text("db", encoding="utf-8")
    (dest / "temp").mkdir()
    (dest / "old.py").write_text("old", encoding="utf-8")
    cfg = dest / "config" / "config.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('{"keep": true}\n', encoding="utf-8")

    src = tmp_path / "src_root"
    src.mkdir()
    (src / "new.py").write_text("new", encoding="utf-8")
    (src / "config").mkdir()
    (src / "config" / "config.json").write_text('{"incoming": 1}\n', encoding="utf-8")

    action = OnUpdateHarrixSwissKnife()
    action.add_line = MagicMock()
    tasks = action._worker_zip_swiss_knife(dest, src, cfg, tmp_path / "apply-tmp")

    assert (dest / ".venv" / "Lib" / "certifi-ca.pem").read_text(encoding="utf-8") == "ca"
    assert (dest / "data" / "databases" / "food.db").read_text(encoding="utf-8") == "db"
    assert (dest / "new.py").read_text(encoding="utf-8") == "new"
    assert not (dest / "old.py").exists()
    assert tasks
    assert tasks[0]["local"] == {"keep": True}
    assert tasks[0]["incoming"] == {"incoming": 1}


def test_worker_run_downloads_all_zips_before_applying(tmp_path: Path) -> None:
    order: list[str] = []
    hsk = tmp_path / "harrix-swiss-knife"
    pylib = tmp_path / "harrix-pylib"
    hsk.mkdir()
    pylib.mkdir()

    action = OnUpdateHarrixSwissKnife()
    action.add_line = MagicMock()
    action.raise_if_work_cancelled = MagicMock()

    def fake_download(dest: Path, _owner: str, work_dir: Path) -> Path:
        order.append(f"download:{dest.name}")
        extracted = work_dir / "tree"
        extracted.mkdir(parents=True)
        (extracted / "file.txt").write_text(dest.name, encoding="utf-8")
        return extracted

    def fake_apply(dest: Path, _src_root: Path, _apply_tmp: Path) -> list:
        order.append(f"apply:{dest.name}")
        return []

    steps = cast(
        "list[OnUpdateHarrixSwissKnife._UpdateStep]",
        [
            {"kind": "zip", "path": hsk, "commit_message": None, "skip_reason": None},
            {"kind": "zip", "path": pylib, "commit_message": None, "skip_reason": None},
        ],
    )
    with (
        patch.object(type(action), "config", new_callable=PropertyMock) as mock_config,
        patch.object(action, "_download_and_extract_zip", side_effect=fake_download),
        patch.object(action, "_apply_extracted_zip", side_effect=fake_apply),
    ):
        mock_config.return_value = {"github_user": "Harrix"}
        action._worker_run(steps)

    assert order == [
        "download:harrix-swiss-knife",
        "download:harrix-pylib",
        "apply:harrix-swiss-knife",
        "apply:harrix-pylib",
    ]


def test_worker_finished_does_not_offer_restart_when_nothing_updated() -> None:
    action = OnUpdateHarrixSwissKnife()
    action._updated_project_names = []
    action.add_line = MagicMock()
    action.show_toast = MagicMock()
    action.show_result = MagicMock()
    action.get_yes_no_question = MagicMock()

    action._worker_finished([])

    action.get_yes_no_question.assert_not_called()


def test_worker_finished_restarts_when_user_accepts() -> None:
    action = OnUpdateHarrixSwissKnife()
    action._updated_project_names = ["harrix-swiss-knife"]
    action.add_line = MagicMock()
    action.show_toast = MagicMock()
    action.show_result = MagicMock()
    action.get_yes_no_question = MagicMock(return_value=True)

    with patch(
        "harrix_swiss_knife.actions.development.update_harrix_swiss_knife.restart_current_application",
        return_value=True,
    ) as restart:
        action._worker_finished([])

    action.get_yes_no_question.assert_called_once()
    restart.assert_called_once()


def test_worker_finished_skips_restart_when_user_declines() -> None:
    action = OnUpdateHarrixSwissKnife()
    action._updated_project_names = ["harrix-swiss-knife"]
    action.add_line = MagicMock()
    action.show_toast = MagicMock()
    action.show_result = MagicMock()
    action.get_yes_no_question = MagicMock(return_value=False)

    with patch(
        "harrix_swiss_knife.actions.development.update_harrix_swiss_knife.restart_current_application"
    ) as restart:
        action._worker_finished([])

    action.get_yes_no_question.assert_called_once()
    restart.assert_not_called()
