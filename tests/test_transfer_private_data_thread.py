"""Tests for Transfer private data background pack/install."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from harrix_swiss_knife.actions.common.private_data import (
    CatalogUpsertStats,
    InstallPrivateDataResult,
    PackPrivateDataResult,
    PrivateDataSelection,
)
from harrix_swiss_knife.actions.development.transfer_private_data import OnTransferPrivateData


def _run_export(action: OnTransferPrivateData, tmp_path: Path, *, noninteractive: bool) -> None:
    action._run_export(
        project_root=tmp_path,
        default_zip=tmp_path / "private-data.zip",
        sqlite_fitness="",
        sqlite_finance="",
        sqlite_food="",
        noninteractive=noninteractive,
        zip_arg=tmp_path / "private-data.zip",
        include_api_keys=False,
        include_fitness=True,
        include_finance=False,
        include_food=False,
        parts_specified=True,
        api_key_files=(),
    )


def _run_import(action: OnTransferPrivateData, tmp_path: Path, *, noninteractive: bool) -> None:
    recover = tmp_path / "recover.sql"
    recover.write_text("-- test", encoding="utf-8")
    action._run_import(
        project_root=tmp_path,
        default_zip=tmp_path / "private-data.zip",
        sqlite_fitness="",
        sqlite_finance="",
        sqlite_food="",
        recover_sql=recover,
        finance_recover_sql=recover,
        food_recover_sql=recover,
        noninteractive=noninteractive,
        zip_arg=tmp_path / "private-data.zip",
        include_api_keys=False,
        include_fitness=True,
        include_finance=False,
        include_food=False,
        parts_specified=True,
        api_key_files=(),
    )


def _pack_result(tmp_path: Path) -> PackPrivateDataResult:
    zip_path = tmp_path / "private-data.zip"
    zip_path.write_bytes(b"zip")
    return PackPrivateDataResult(
        zip_path=zip_path,
        api_keys_count=0,
        fitness_img_count=2,
        exercises_count=1,
        types_count=0,
    )


def _install_result() -> InstallPrivateDataResult:
    return InstallPrivateDataResult(
        api_keys_count=0,
        fitness_img_count=2,
        catalog_stats=CatalogUpsertStats(),
        fitness_db_path=None,
        fitness_img_dir=Path("fitness_img"),
        created_database=False,
    )


def _action() -> OnTransferPrivateData:
    action = OnTransferPrivateData()
    action.start_thread = MagicMock()
    action.show_result = MagicMock()
    action.show_toast = MagicMock()
    action.add_line = MagicMock()
    return action


def test_cli_export_packs_inline(tmp_path: Path) -> None:
    packed = _pack_result(tmp_path)
    action = _action()
    with patch(
        "harrix_swiss_knife.actions.development.transfer_private_data.pack_private_data",
        return_value=packed,
    ) as pack:
        _run_export(action, tmp_path, noninteractive=True)
    pack.assert_called_once()
    action.start_thread.assert_not_called()
    action.show_toast.assert_called_once()
    action.show_result.assert_called_once()


def test_tray_export_starts_thread_with_toast(tmp_path: Path) -> None:
    packed = _pack_result(tmp_path)
    action = _action()
    with patch(
        "harrix_swiss_knife.actions.development.transfer_private_data.pack_private_data",
        return_value=packed,
    ) as pack:
        _run_export(action, tmp_path, noninteractive=False)
        pack.assert_not_called()
        action.start_thread.assert_called_once()
        assert action.start_thread.call_args.args[2] == "Exporting private data…"
        action.in_thread()
        pack.assert_called_once()
    action.thread_after(None)
    action.show_toast.assert_called_once()
    action.show_result.assert_called_once()


def test_cli_import_installs_inline(tmp_path: Path) -> None:
    action = _action()
    present = PrivateDataSelection(api_keys=False, fitness=True)
    with (
        patch(
            "harrix_swiss_knife.actions.development.transfer_private_data.inspect_private_data_zip",
            return_value=present,
        ),
        patch(
            "harrix_swiss_knife.actions.development.transfer_private_data.install_private_data",
            return_value=_install_result(),
        ) as install,
    ):
        _run_import(action, tmp_path, noninteractive=True)
    install.assert_called_once()
    action.start_thread.assert_not_called()
    action.show_toast.assert_called_once()
    action.show_result.assert_called_once()


def test_tray_import_starts_thread_with_toast(tmp_path: Path) -> None:
    action = _action()
    present = PrivateDataSelection(api_keys=False, fitness=True)
    with (
        patch(
            "harrix_swiss_knife.actions.development.transfer_private_data.inspect_private_data_zip",
            return_value=present,
        ),
        patch(
            "harrix_swiss_knife.actions.development.transfer_private_data.install_private_data",
            return_value=_install_result(),
        ) as install,
    ):
        _run_import(action, tmp_path, noninteractive=False)
        install.assert_not_called()
        action.start_thread.assert_called_once()
        assert action.start_thread.call_args.args[2] == "Importing private data…"
        action.in_thread()
    install.assert_called_once()
    action.thread_after(None)
    action.show_toast.assert_called_once()
    action.show_result.assert_called_once()
