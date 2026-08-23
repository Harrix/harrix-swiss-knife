"""Tests for installer ACL, ARP, progress, finish report, and VS Code VSIX helpers."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from harrix_swiss_knife.installer import acl as acl_mod
from harrix_swiss_knife.installer.acl import (
    installing_user_principal,
    installing_username,
    parse_icacls_failed_count,
    parse_icacls_success_count,
    repair_install_tree_acls,
)
from harrix_swiss_knife.installer.arp import ARP_KEY_NAME, register_uninstall, unregister_uninstall
from harrix_swiss_knife.installer.build_info import summarize_dependency_artifacts
from harrix_swiss_knife.installer.config_defaults import apply_config_defaults, is_unset_config_path
from harrix_swiss_knife.installer.deploy import DeployResult
from harrix_swiss_knife.installer.finish_report import (
    INSTALL_FINISH_REPORT_NAME,
    format_install_report,
    save_install_finish_report,
)
from harrix_swiss_knife.installer.log import OutcomeLog
from harrix_swiss_knife.installer.paths import (
    default_install_root_parent,
    is_under_program_files,
    normalize_install_root,
)
from harrix_swiss_knife.installer.payload import cleanup_work_dir
from harrix_swiss_knife.installer.prereqs import (
    DetectionStatus,
    PrerequisitePlan,
    detected_reinstall_keys,
    format_reinstall_warning,
    install_prerequisites,
)
from harrix_swiss_knife.installer.progress_ui import ProgressBarMode, progress_mode_for_log_line
from harrix_swiss_knife.installer.uninstall import UninstallOptions, run_uninstall
from harrix_swiss_knife.installer.uv_ops import ensure_runtime_imports, uv_sync_with_bundle_cache
from harrix_swiss_knife.installer.vscode_ext import (
    FALLBACK_PYTHON_EXTENSION_IDS,
    clear_obsolete_markers,
    install_order_for_vsixes,
    marketplace_vsix_url,
    read_extension_dependencies,
    verify_extensions_enabled,
)


def test_default_install_root_parent_prefers_existing(tmp_path: Path, monkeypatch) -> None:
    existing = tmp_path / "GitHub"
    existing.mkdir()
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.paths._preferred_parent_candidates",
        lambda: [existing],
    )
    assert default_install_root_parent() == existing.resolve()


def test_default_install_root_parent_creates_bundle_root(tmp_path: Path, monkeypatch) -> None:
    bundle = tmp_path / "harrix-swiss-knife"
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.paths._preferred_parent_candidates",
        lambda: [tmp_path / "nope"],
    )
    monkeypatch.setattr("harrix_swiss_knife.installer.paths._FALLBACK_CREATE_PARENT", bundle)
    result = default_install_root_parent()
    assert result == bundle.resolve()
    assert bundle.is_dir()


def test_normalize_install_root_keeps_bundle_and_github(tmp_path: Path) -> None:
    bundle = tmp_path / "harrix-swiss-knife"
    github = tmp_path / "GitHub"
    other = tmp_path / "apps"
    assert normalize_install_root(bundle) == bundle.resolve()
    assert normalize_install_root(github) == github.resolve()
    assert normalize_install_root(other) == other.resolve()
    assert not (other / "GitHub").exists()


def test_is_under_program_files() -> None:
    assert is_under_program_files(Path(r"C:\Program Files\Harrix"))
    assert not is_under_program_files(Path(r"C:\harrix-swiss-knife"))
    assert not is_under_program_files(Path(r"C:\GitHub"))


def test_progress_mode_for_log_line() -> None:
    assert (
        progress_mode_for_log_line("==> Extracting installer payload", extracting=False) is ProgressBarMode.DETERMINATE
    )
    assert progress_mode_for_log_line("==> uv tool install -e", extracting=True) is ProgressBarMode.INDETERMINATE
    assert progress_mode_for_log_line("  detail", extracting=True) is None


def test_parse_icacls_counts() -> None:
    text = "Successfully processed 1200 files; Failed processing 3 files"
    assert parse_icacls_success_count(text) == 1200
    assert parse_icacls_failed_count(text) == 3
    assert parse_icacls_failed_count("Successfully processed 5 files; Failed processing 0 files") == 0
    assert parse_icacls_failed_count("no summary") is None


def test_repair_install_tree_acls_treats_partial_icacls_as_failure(tmp_path: Path) -> None:
    target = tmp_path / "tree"
    target.mkdir()
    log = OutcomeLog()
    calls: list[list[str]] = []

    def fake_run_icacls(
        cmd: list[str],
        _log: OutcomeLog,
        *,
        label: str,
        allow_partial: bool = False,
    ) -> bool:
        del label  # signature must match _run_icacls
        calls.append(cmd)
        if "/reset" in cmd:
            return False
        if "/grant" in cmd:
            return False
        return allow_partial

    with (
        patch("harrix_swiss_knife.installer.acl.installing_user_principal", return_value="*S-1-5-21-1"),
        patch("harrix_swiss_knife.installer.acl.installing_username", return_value="Admin"),
        patch("harrix_swiss_knife.installer.acl._run_cmd", return_value=True),
        patch("harrix_swiss_knife.installer.acl._run_icacls", side_effect=fake_run_icacls),
    ):
        assert repair_install_tree_acls(target, log) is False
    assert any(c[:2] == ["icacls", str(target)] and "/reset" in c for c in calls)
    assert any("ACL repair incomplete" in m for m in log.failed)


def test_repair_install_tree_acls_resets_then_grants(tmp_path: Path) -> None:
    target = tmp_path / "tree"
    target.mkdir()
    log = OutcomeLog()
    seen: list[str] = []

    def fake_run_icacls(
        _cmd: list[str],
        _log: OutcomeLog,
        *,
        label: str,
        allow_partial: bool = False,
    ) -> bool:
        del allow_partial  # signature must match _run_icacls
        seen.append(label)
        return True

    with (
        patch("harrix_swiss_knife.installer.acl.installing_user_principal", return_value="*S-1-5-21-9"),
        patch("harrix_swiss_knife.installer.acl.installing_username", return_value="Admin"),
        patch("harrix_swiss_knife.installer.acl._run_cmd", return_value=True),
        patch("harrix_swiss_knife.installer.acl._run_icacls", side_effect=fake_run_icacls),
    ):
        assert repair_install_tree_acls(target, log) is True
    assert seen[0] == "icacls /reset"
    assert any(label.startswith("icacls /grant") for label in seen)
    assert any("Reset ACLs and granted Full Control" in m for m in log.installed)


def test_run_icacls_fails_when_failed_processing_nonzero() -> None:
    log = OutcomeLog()
    proc = MagicMock(returncode=0, stdout="Successfully processed 10 files; Failed processing 2 files", stderr="")
    with patch("harrix_swiss_knife.installer.acl.subprocess.run", return_value=proc):
        assert acl_mod._run_icacls(["icacls", "x", "/reset", "/T", "/C"], log, label="icacls /reset") is False


def test_repair_install_tree_acls_missing_path(tmp_path: Path) -> None:
    log = OutcomeLog()
    assert repair_install_tree_acls(tmp_path / "missing", log) is False


def test_installing_username(monkeypatch) -> None:
    monkeypatch.setenv("USERNAME", "Admin")
    assert installing_username() == "Admin"


def test_installing_user_principal_prefers_sid(monkeypatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.acl.installing_user_sid",
        lambda: "S-1-5-21-100",
    )
    monkeypatch.setenv("USERNAME", "Admin")
    assert installing_user_principal() == "*S-1-5-21-100"


def test_uv_sync_sets_link_mode_copy_online_and_offline(tmp_path: Path) -> None:
    repo = tmp_path / "harrix-pylib"
    repo.mkdir()
    deps_offline = tmp_path / "deps-offline"
    (deps_offline / "uv-cache").mkdir(parents=True)
    deps_online = tmp_path / "deps-online"
    deps_online.mkdir()

    def _sync(deps: Path) -> dict[str, object]:
        captured: dict[str, object] = {}

        def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
            captured["env"] = kwargs.get("env")
            captured["cmd"] = list(cmd)
            return MagicMock(returncode=0, stdout="", stderr="")

        log = OutcomeLog()
        with (
            patch("harrix_swiss_knife.installer.uv_ops.find_uv_exe", return_value=Path("uv.exe")),
            patch("harrix_swiss_knife.installer.uv_ops.subprocess.run", side_effect=fake_run),
        ):
            used = uv_sync_with_bundle_cache(repo, deps=deps, label="harrix-pylib", log=log)
        captured["used_offline"] = used
        return captured

    offline = _sync(deps_offline)
    online = _sync(deps_online)
    assert offline["used_offline"] is True
    assert online["used_offline"] is False
    for captured in (offline, online):
        env = captured["env"]
        assert isinstance(env, dict)
        assert env.get("UV_LINK_MODE") == "copy"


def test_ensure_runtime_imports_fails_on_permission_error(tmp_path: Path) -> None:
    hsk = tmp_path / "harrix-swiss-knife"
    python = hsk / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.write_bytes(b"x")
    log = OutcomeLog()
    proc = MagicMock(
        returncode=1,
        stdout="",
        stderr="PermissionError: ...\\PySide6\\__init__.py",
    )
    with (
        patch("harrix_swiss_knife.installer.uv_ops.subprocess.run", return_value=proc),
        pytest.raises(RuntimeError, match="PermissionError"),
    ):
        ensure_runtime_imports(hsk, log=log)


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
        install_root=Path(r"C:\harrix-swiss-knife"),
        hsk_path=Path(r"C:\harrix-swiss-knife\harrix-swiss-knife"),
        outcomes=log,
        elapsed_seconds=12.5,
    )
    text = format_install_report(result)
    assert "Installation finished." in text
    assert "C:\\harrix-swiss-knife" in text
    assert INSTALL_FINISH_REPORT_NAME in text
    assert "Desktop shortcut created" in text
    assert "Elapsed: 00:13" in text


def test_save_install_finish_report(tmp_path: Path) -> None:
    root = tmp_path / "harrix-swiss-knife"
    root.mkdir()
    text = "Installation finished.\n\nElapsed: 00:13"
    saved = save_install_finish_report(root, text)
    assert saved is not None
    assert saved == root / INSTALL_FINISH_REPORT_NAME
    assert saved.read_text(encoding="utf-8") == text + "\n"


def test_detected_reinstall_keys_when_user_reselects_installed_tools() -> None:
    status = DetectionStatus(git=True, uv=True, editor=True, managed_python=True)
    plan = PrerequisitePlan(git=True, uv=True, vscode=True, python=True)
    keys = detected_reinstall_keys(plan, status)
    assert keys == ("git", "uv", "vscode", "python")


def test_detected_reinstall_keys_empty_when_plan_matches_detection() -> None:
    status = DetectionStatus(git=True, uv=False, editor=False, managed_python=False)
    plan = PrerequisitePlan(git=False, uv=True, vscode=True, python=True)
    assert detected_reinstall_keys(plan, status) == ()


def test_format_reinstall_warning_lists_tools() -> None:
    text = format_reinstall_warning(("git", "vscode"))
    assert "Git" in text
    assert "VS Code" in text
    assert "Reinstall them anyway?" in text


def test_install_prerequisites_reinstalls_git_when_confirmed(tmp_path: Path) -> None:
    deps = tmp_path / "deps"
    deps.mkdir()
    log = OutcomeLog()
    captured: list[str] = []
    log.set_log(captured.append)
    plan = PrerequisitePlan(
        git=True,
        uv=False,
        vscode=False,
        python=False,
        python_extension=False,
        reinstall_confirmed=frozenset({"git"}),
    )
    with patch("harrix_swiss_knife.installer.prereqs.command_exists", return_value=True):
        install_prerequisites(
            plan,
            deps=deps,
            python_version="3.13",
            log=log,
            state={},
            allow_network=False,
        )
    assert any("Installing Git (reinstall)" in line for line in captured)


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


def test_cleanup_work_dir_removes_short_root(tmp_path: Path) -> None:
    short_root = tmp_path / "hsk-setup"
    work = short_root / "abc123"
    (work / "payload").mkdir(parents=True)
    (work / "install.log").write_text("log", encoding="utf-8")
    cleanup_work_dir(work)
    assert not work.exists()
    assert not short_root.exists()


def test_cleanup_work_dir_keeps_short_root_with_other_installs(tmp_path: Path) -> None:
    short_root = tmp_path / "hsk-setup"
    work = short_root / "abc123"
    other = short_root / "def456"
    work.mkdir(parents=True)
    other.mkdir()
    cleanup_work_dir(work)
    assert not work.exists()
    assert other.is_dir()


def test_clear_obsolete_markers(tmp_path: Path, monkeypatch) -> None:
    ext_root = tmp_path / ".vscode" / "extensions"
    ext_root.mkdir(parents=True)
    obsolete = ext_root / ".obsolete"
    obsolete.write_text(
        json.dumps({"ms-python.python-2026.1.0": True, "other.ext-1.0.0": True}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.installer.vscode_ext.editor_extension_dirs",
        lambda: [ext_root],
    )
    log = OutcomeLog()
    assert clear_obsolete_markers(["ms-python.python"], log) == 1
    assert json.loads(obsolete.read_text(encoding="utf-8")) == {"other.ext-1.0.0": True}


def test_verify_extensions_enabled_reports_missing() -> None:
    log = OutcomeLog()
    proc = MagicMock(returncode=0, stdout="ms-python.python\nms-python.debugpy\n", stderr="")
    with patch("harrix_swiss_knife.installer.vscode_ext.subprocess.run", return_value=proc):
        missing = verify_extensions_enabled(Path("code.cmd"), ["ms-python.python", "ms-python.vscode-pylance"], log)
    assert missing == ["ms-python.vscode-pylance"]
    assert any("does not list" in m for m in log.failed)


def test_is_unset_config_path() -> None:
    assert is_unset_config_path("")
    assert is_unset_config_path("<YOUR_GITHUB_FOLDER>/harrix-swiss-knife")
    assert is_unset_config_path(None)
    assert not is_unset_config_path(str(Path(__file__).resolve()))


def test_apply_config_defaults_sets_stack_paths(tmp_path: Path) -> None:
    root = tmp_path / "harrix-swiss-knife-root"
    hsk = root / "harrix-swiss-knife"
    pylib = root / "harrix-pylib"
    pyssg = root / "harrix-pyssg"
    for path in (hsk, pylib, pyssg):
        path.mkdir(parents=True)
    (hsk / "android").mkdir()
    cfg_dir = hsk / "config"
    cfg_dir.mkdir()
    (cfg_dir / "config.example.json").write_text(
        json.dumps(
            {
                "show_main_window_on_startup": False,
                "path_github": "<YOUR_GITHUB_FOLDER>",
                "paths_python_projects": ["<YOUR_GITHUB_FOLDER>/harrix-swiss-knife"],
                "paths_python_libraries": [],
                "sqlite_finance": "<YOUR_FINANCE_DB>",
                "sqlite_fitness": "<YOUR_FITNESS_DB>",
                "sqlite_habits": "<YOUR_HABITS_DB>",
                "sqlite_food": "<YOUR_FOOD_DB>",
            }
        ),
        encoding="utf-8",
    )
    log = OutcomeLog()
    apply_config_defaults(hsk, log)
    data = json.loads((cfg_dir / "config.json").read_text(encoding="utf-8"))
    assert data["show_main_window_on_startup"] is True
    assert Path(data["path_github"]) == root.resolve()
    assert [Path(p).name for p in data["paths_python_projects"]] == [
        "harrix-pylib",
        "harrix-pyssg",
        "harrix-swiss-knife",
    ]
    assert {Path(p).name for p in data["paths_python_libraries"]} == {"harrix-pylib", "harrix-pyssg"}
    assert data["paths_android_projects"] == [(hsk / "android").resolve().as_posix()]
    assert data["paths_python_project_creation"] == [root.resolve().as_posix()]
    assert data["paths_combine_for_ai"][0]["base_folder"] == hsk.resolve().as_posix()
    data_root = (root / "data-for-hsk").resolve()
    assert Path(data["data_for_hsk_root"]) == data_root
    assert "finance.db" in data["sqlite_finance"]
    assert data["sqlite_finance"].startswith(data_root.as_posix())
    assert data["path_notes"] == (data_root / "Notes" / "Notes").as_posix()
    assert "data-for-hsk/databases" in data["paths_git"][-1]
