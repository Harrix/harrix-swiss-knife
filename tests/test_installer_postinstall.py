"""Tests for installer ACL, ARP, progress, finish report, and VS Code VSIX helpers."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from harrix_swiss_knife.installer.acl import installing_username, repair_install_tree_acls
from harrix_swiss_knife.installer.arp import ARP_KEY_NAME, register_uninstall, unregister_uninstall
from harrix_swiss_knife.installer.build_info import summarize_dependency_artifacts
from harrix_swiss_knife.installer.deploy import DeployResult
from harrix_swiss_knife.installer.finish_report import format_install_report
from harrix_swiss_knife.installer.log import OutcomeLog
from harrix_swiss_knife.installer.paths import default_install_root_parent, is_under_program_files
from harrix_swiss_knife.installer.progress_ui import ProgressBarMode, progress_mode_for_log_line
from harrix_swiss_knife.installer.uninstall import UninstallOptions, run_uninstall
from harrix_swiss_knife.installer.vscode_ext import (
    FALLBACK_PYTHON_EXTENSION_IDS,
    install_order_for_vsixes,
    marketplace_vsix_url,
    read_extension_dependencies,
)


def test_default_install_root_parent_prefers_existing(tmp_path: Path, monkeypatch) -> None:
    existing = tmp_path / "GitHub"
    existing.mkdir()
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.paths._github_parent_candidates",
        lambda: [existing],
    )
    assert default_install_root_parent() == existing.resolve()


def test_default_install_root_parent_creates_c_github(tmp_path: Path, monkeypatch) -> None:
    c_github = tmp_path / "C_GitHub"
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.paths._github_parent_candidates",
        lambda: [tmp_path / "nope"],
    )
    monkeypatch.setattr("harrix_swiss_knife.installer.paths._FALLBACK_CREATE_PARENT", c_github)
    result = default_install_root_parent()
    assert result == c_github.resolve()
    assert c_github.is_dir()


def test_is_under_program_files() -> None:
    assert is_under_program_files(Path(r"C:\Program Files\Harrix"))
    assert not is_under_program_files(Path(r"C:\GitHub"))


def test_progress_mode_for_log_line() -> None:
    assert (
        progress_mode_for_log_line("==> Extracting installer payload", extracting=False) is ProgressBarMode.DETERMINATE
    )
    assert progress_mode_for_log_line("==> uv tool install -e", extracting=True) is ProgressBarMode.INDETERMINATE
    assert progress_mode_for_log_line("  detail", extracting=True) is None


def test_repair_install_tree_acls_without_icacls(tmp_path: Path) -> None:
    target = tmp_path / "tree"
    target.mkdir()
    log = OutcomeLog()
    with patch("harrix_swiss_knife.installer.acl._run_cmd", return_value=False):
        assert repair_install_tree_acls(target, log) is False
    assert any("ACL repair incomplete" in m for m in log.failed)


def test_repair_install_tree_acls_missing_path(tmp_path: Path) -> None:
    log = OutcomeLog()
    assert repair_install_tree_acls(tmp_path / "missing", log) is False


def test_installing_username(monkeypatch) -> None:
    monkeypatch.setenv("USERNAME", "Admin")
    assert installing_username() == "Admin"


def test_register_and_unregister_arp(tmp_path: Path) -> None:
    hsk = tmp_path / "harrix-swiss-knife"
    (hsk / ".venv" / "Scripts").mkdir(parents=True)
    (hsk / ".venv" / "Scripts" / "pythonw.exe").write_bytes(b"x")
    (hsk / "launch_uninstall.py").write_text("#", encoding="utf-8")
    log = OutcomeLog()

    fake_key = MagicMock()
    with patch("harrix_swiss_knife.installer.arp.winreg") as wr:
        wr.HKEY_LOCAL_MACHINE = object()
        wr.KEY_SET_VALUE = 2
        wr.REG_SZ = 1
        wr.REG_DWORD = 4
        wr.CreateKeyEx.return_value.__enter__.return_value = fake_key
        assert register_uninstall(install_root=tmp_path, hsk_path=hsk, version="1.2.3", log=log) is True
        wr.DeleteKey.side_effect = FileNotFoundError
        assert unregister_uninstall(log) is True
    assert ARP_KEY_NAME == "HarrixSwissKnife"
    assert any("Apps & Features" in m for m in log.installed)


def test_marketplace_vsix_url() -> None:
    url = marketplace_vsix_url("ms-python.python")
    assert "ms-python" in url
    assert "python" in url
    assert url.startswith("https://")


def test_read_extension_dependencies(tmp_path: Path) -> None:
    vsix = tmp_path / "ms-python.python.vsix"
    pkg = {
        "name": "python",
        "publisher": "ms-python",
        "extensionDependencies": ["ms-python.vscode-pylance", "ms-python.debugpy"],
    }
    with zipfile.ZipFile(vsix, "w") as zf:
        zf.writestr("extension/package.json", json.dumps(pkg))
    deps = read_extension_dependencies(vsix)
    assert deps == ["ms-python.vscode-pylance", "ms-python.debugpy"]


def test_install_order_dependencies_before_python(tmp_path: Path) -> None:
    folder = tmp_path / "vscode-extensions"
    folder.mkdir()
    main = folder / "ms-python.python.vsix"
    dep = folder / "ms-python.vscode-pylance.vsix"
    pkg = {"extensionDependencies": ["ms-python.vscode-pylance"]}
    with zipfile.ZipFile(main, "w") as zf:
        zf.writestr("extension/package.json", json.dumps(pkg))
    dep.write_bytes(b"PK\x03\x04dummy")
    ordered = install_order_for_vsixes(tmp_path)
    assert ordered[-1].name == "ms-python.python.vsix"
    assert ordered[0].name == "ms-python.vscode-pylance.vsix"
    assert FALLBACK_PYTHON_EXTENSION_IDS[-1] == "ms-python.python"


def test_summarize_dependency_artifacts(tmp_path: Path) -> None:
    deps = tmp_path / "dependencies"
    deps.mkdir()
    (deps / "ffmpeg.exe").write_bytes(b"x" * 2048)
    ext = deps / "vscode-extensions"
    ext.mkdir()
    (ext / "ms-python.python.vsix").write_bytes(b"y" * 100)
    (deps / "uv-cache").mkdir()
    (deps / "uv-cache" / "marker").write_text("1", encoding="utf-8")
    text = summarize_dependency_artifacts(deps)
    assert "ffmpeg.exe=" in text
    assert "vscode-extensions/ms-python.python.vsix=" in text
    assert "uv-cache/=present" in text


def test_format_install_report() -> None:
    log = OutcomeLog()
    log.add("installed", "Desktop shortcut created")
    result = DeployResult(
        ok=True,
        install_root=Path(r"C:\GitHub"),
        hsk_path=Path(r"C:\GitHub\harrix-swiss-knife"),
        outcomes=log,
        elapsed_seconds=12.5,
    )
    text = format_install_report(result)
    assert "Installation finished." in text
    assert "C:\\GitHub" in text
    assert "Desktop shortcut created" in text


def test_run_uninstall_unregisters_arp(tmp_path: Path) -> None:
    hsk = tmp_path / "harrix-swiss-knife"
    hsk.mkdir()
    (hsk / "pyproject.toml").write_text('name = "harrix-swiss-knife"\n', encoding="utf-8")
    log = OutcomeLog()
    with (
        patch("harrix_swiss_knife.installer.uninstall.remove_app_shortcuts", return_value=[]),
        patch("harrix_swiss_knife.installer.uninstall._uninstall_cli"),
        patch("harrix_swiss_knife.installer.uninstall._stop_running_app"),
        patch("harrix_swiss_knife.installer.uninstall.unregister_uninstall") as unreg,
    ):
        result = run_uninstall(UninstallOptions(hsk_path=hsk, remove_sibling_repos=False), log)
    assert result.ok
    unreg.assert_called_once()
