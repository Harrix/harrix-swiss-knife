"""Tests for the Python installer-EXE builder helpers."""

from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from harrix_swiss_knife.actions.common.install_zip_builder import (
    DEFAULT_STEP_LABELS,
    OFFLINE_EXE_NAME,
    OFFLINE_ZIP_NAME,
    ONLINE_EXCLUDE_DIRS,
    ONLINE_EXE_NAME,
    ONLINE_ZIP_NAME,
    STEP_BINARIES,
    STEP_BUILD_EXES,
    STEP_BUILD_ZIPS,
    STEP_INSTALLERS,
    STEP_OPEN,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_WIPE,
    BuildSteps,
    _copy_deps,
    cli_argv_for_steps,
    commit_stage_dir,
    install_dir,
    redundant_media_zip_names,
    run_pipeline,
    steps_from_cli_flags,
    uv_isolated_env,
    wipe_dependencies,
)
from harrix_swiss_knife.installer.pack_exes import build_payload_zips, pack_installer_exes
from harrix_swiss_knife.installer.payload import append_overlay_zip, extract_overlay, read_overlay_bounds
from harrix_swiss_knife.installer.wizard import detect_mode_from_argv


def test_build_steps_from_labels_all_defaults() -> None:
    steps = BuildSteps.from_labels(DEFAULT_STEP_LABELS)
    assert steps.wipe_dependencies
    assert steps.binaries
    assert steps.installers
    assert steps.repos
    assert steps.uv_cache
    assert steps.build_zips
    assert steps.open_install
    assert not steps.clean_logs


def test_build_steps_exe_only() -> None:
    steps = BuildSteps.from_labels([STEP_BUILD_EXES])
    assert not steps.wipe_dependencies
    assert not steps.binaries
    assert steps.build_zips
    assert steps.any_work()


def test_build_steps_empty_is_no_work() -> None:
    steps = BuildSteps.from_labels([])
    assert not steps.any_work()
    assert not steps.open_install


def test_steps_from_cli_flags_skip() -> None:
    steps = steps_from_cli_flags(no_wipe=True, skip_uv_cache=True, no_open=True)
    assert not steps.wipe_dependencies
    assert steps.binaries
    assert not steps.uv_cache
    assert not steps.open_install
    assert steps.build_zips


def test_steps_from_cli_flags_no_exes() -> None:
    steps = steps_from_cli_flags(no_exes=True)
    assert not steps.build_zips
    steps2 = steps_from_cli_flags(no_zips=True)
    assert not steps2.build_zips


def test_cli_argv_for_steps_roundtrip() -> None:
    steps = BuildSteps(
        wipe_dependencies=False,
        binaries=True,
        installers=False,
        repos=True,
        uv_cache=False,
        build_zips=True,
        open_install=False,
        clean_logs=True,
    )
    flags = cli_argv_for_steps(steps)
    assert "--no-wipe" in flags
    assert "--skip-installers" in flags
    assert "--skip-uv-cache" in flags
    assert "--no-open" in flags
    assert "--clean-logs" in flags
    assert "--skip-binaries" not in flags


def test_cli_argv_includes_no_exes_when_skipped() -> None:
    steps = BuildSteps(build_zips=False)
    flags = cli_argv_for_steps(steps)
    assert "--no-exes" in flags


def test_uv_isolated_env_drops_live_venv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("VIRTUAL_ENV", r"C:\locked\.venv")
    monkeypatch.setenv("UV_PYTHON", "3.12")
    cache_dir = tmp_path / "cache"
    venv_dir = tmp_path / "venv"
    env = uv_isolated_env(cache_dir=cache_dir, project_environment=venv_dir)
    assert "VIRTUAL_ENV" not in env
    assert "UV_PYTHON" not in env
    assert env["UV_CACHE_DIR"] == str(cache_dir)
    assert env["UV_PROJECT_ENVIRONMENT"] == str(venv_dir)


def test_commit_stage_dir_replaces_existing(tmp_path: Path) -> None:
    final_dir = tmp_path / "repos"
    final_dir.mkdir()
    (final_dir / "old.zip").write_bytes(b"old")
    stage_dir = tmp_path / "repos.stage.abc"
    stage_dir.mkdir()
    (stage_dir / "new.zip").write_bytes(b"new")
    commit_stage_dir(stage_dir, final_dir)
    assert not stage_dir.exists()
    assert (final_dir / "new.zip").read_bytes() == b"new"
    assert not (final_dir / "old.zip").exists()


def test_commit_stage_dir_when_dest_missing(tmp_path: Path) -> None:
    final_dir = tmp_path / "repos"
    stage_dir = tmp_path / "repos.stage.abc"
    stage_dir.mkdir()
    (stage_dir / "a.zip").write_bytes(b"a")
    commit_stage_dir(stage_dir, final_dir)
    assert not stage_dir.exists()
    assert (final_dir / "a.zip").read_bytes() == b"a"


def test_wipe_dependencies(tmp_path: Path) -> None:
    deps = tmp_path / "install" / "dependencies"
    deps.mkdir(parents=True)
    (deps / "marker.txt").write_text("x", encoding="utf-8")
    lines: list[str] = []
    wipe_dependencies(tmp_path, lines.append)
    assert not deps.exists()
    assert any("Removing" in line for line in lines)


def test_redundant_media_zip_names(tmp_path: Path) -> None:
    deps = tmp_path / "dependencies"
    deps.mkdir()
    (deps / "avifenc.exe").write_bytes(b"enc")
    (deps / "avifdec.exe").write_bytes(b"dec")
    (deps / "windows-artifacts.zip").write_bytes(b"zip")
    (deps / "ffmpeg.exe").write_bytes(b"ff")
    (deps / "ffmpeg-master-latest-win64-gpl.zip").write_bytes(b"zip")
    names = redundant_media_zip_names(deps)
    assert "windows-artifacts.zip" in names
    assert "ffmpeg-master-latest-win64-gpl.zip" in names


def _prepare_install_tree(root: Path) -> Path:
    install = root / "install"
    install.mkdir()
    deps = install / "dependencies"
    deps.mkdir()
    (deps / "Git-latest-64-bit.exe").write_bytes(b"git")
    (deps / "ffmpeg.exe").write_bytes(b"ff")
    (deps / "avifenc.exe").write_bytes(b"enc")
    (deps / "avifdec.exe").write_bytes(b"dec")
    (deps / "windows-artifacts.zip").write_bytes(b"redundant")
    (deps / "note.txt").write_text("keep", encoding="utf-8")
    (deps / "download.log").write_text("log", encoding="utf-8")
    (deps / "repos").mkdir()
    (deps / "repos" / "harrix-swiss-knife.zip").write_bytes(b"repo")
    (deps / "uv-cache").mkdir()
    (deps / "uv-cache" / "c.bin").write_bytes(b"c")
    (deps / "uv-python-cache").mkdir()
    (deps / "uv-python-cache" / "p.bin").write_bytes(b"p")
    return install


def test_payload_zips_online_vs_offline_membership(tmp_path: Path) -> None:
    _prepare_install_tree(tmp_path)
    lines: list[str] = []
    omit = redundant_media_zip_names(tmp_path / "install" / "dependencies")
    online, offline = build_payload_zips(
        tmp_path,
        lines.append,
        copy_deps_fn=_copy_deps,
        online_exclude_dirs=ONLINE_EXCLUDE_DIRS,
        omit_files=omit,
    )
    assert online.name == ".payload-online.zip"
    assert offline.name == ".payload-offline.zip"

    with zipfile.ZipFile(online, "r") as zf:
        names = set(zf.namelist())
    assert "dependencies/ffmpeg.exe" in names
    assert "dependencies/note.txt" in names
    assert "dependencies/Git-latest-64-bit.exe" in names
    assert not any(n.startswith("dependencies/repos/") for n in names)
    assert not any(n.startswith("dependencies/uv-cache/") for n in names)
    assert not any(n.startswith("dependencies/uv-python-cache/") for n in names)
    assert "dependencies/windows-artifacts.zip" not in names
    assert "dependencies/download.log" not in names
    assert "install.bat" not in names
    assert "harrix-swiss-knife.ps1" not in names

    with zipfile.ZipFile(offline, "r") as zf:
        names = set(zf.namelist())
    assert "dependencies/repos/harrix-swiss-knife.zip" in names
    assert "dependencies/uv-cache/c.bin" in names
    assert "dependencies/uv-python-cache/p.bin" in names
    assert "dependencies/windows-artifacts.zip" not in names


def test_append_overlay_magic_trailer(tmp_path: Path) -> None:
    stub = tmp_path / "stub.exe"
    stub.write_bytes(b"STUBDATA")
    zip_path = tmp_path / "payload.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("dependencies/marker.txt", "hello")
    out = tmp_path / "online.exe"
    append_overlay_zip(stub, zip_path, out)
    bounds = read_overlay_bounds(out)
    assert bounds is not None
    _start, length = bounds
    assert length == zip_path.stat().st_size
    assert out.read_bytes()[:8] == b"STUBDATA"
    dest = tmp_path / "extracted"
    deps = extract_overlay(out, dest)
    assert (deps / "marker.txt").read_text(encoding="utf-8") == "hello"


def test_run_pipeline_exes_only(tmp_path: Path) -> None:
    _prepare_install_tree(tmp_path)
    stub = tmp_path / "fake-stub.exe"
    stub.write_bytes(b"FAKESTUB")

    def _fake_stub(project_root: Path, log: object, *, force: bool = False) -> Path:  # noqa: ARG001
        return stub

    steps = BuildSteps(
        wipe_dependencies=False,
        binaries=False,
        installers=False,
        repos=False,
        uv_cache=False,
        build_zips=True,
        open_install=False,
        clean_logs=False,
    )
    with patch("harrix_swiss_knife.installer.pack_exes.ensure_installer_stub", _fake_stub):
        result = run_pipeline(tmp_path, steps)
    assert result.ok
    assert result.online_zip is not None
    assert result.offline_zip is not None
    assert result.online_zip.name == ONLINE_EXE_NAME
    assert result.offline_zip.name == OFFLINE_EXE_NAME
    assert result.online_zip.is_file()
    assert read_overlay_bounds(result.online_zip) is not None
    assert read_overlay_bounds(result.offline_zip) is not None


def test_pack_installer_exes_names(tmp_path: Path) -> None:
    install = tmp_path / "install"
    install.mkdir()
    stub = install / "stub.exe"
    stub.write_bytes(b"STUB")
    online_zip = install / "o.zip"
    offline_zip = install / "f.zip"
    with zipfile.ZipFile(online_zip, "w") as zf:
        zf.writestr("dependencies/a.txt", "a")
    with zipfile.ZipFile(offline_zip, "w") as zf:
        zf.writestr("dependencies/b.txt", "b")
    lines: list[str] = []
    with patch(
        "harrix_swiss_knife.installer.pack_exes.ensure_installer_stub",
        lambda *_a, **_k: stub,
    ):
        online, offline = pack_installer_exes(tmp_path, online_zip, offline_zip, lines.append)
    assert online.name == ONLINE_EXE_NAME
    assert offline.name == OFFLINE_EXE_NAME
    assert ONLINE_ZIP_NAME == ONLINE_EXE_NAME
    assert OFFLINE_ZIP_NAME == OFFLINE_EXE_NAME


def test_run_pipeline_no_steps(tmp_path: Path) -> None:
    result = run_pipeline(tmp_path, BuildSteps.from_labels([]))
    assert not result.ok
    assert any("No steps" in line for line in result.lines)


def test_install_dir_helper() -> None:
    assert install_dir(Path("D:/x")) == Path("D:/x/install")


def test_default_labels_include_core_steps() -> None:
    assert STEP_WIPE in DEFAULT_STEP_LABELS
    assert STEP_BINARIES in DEFAULT_STEP_LABELS
    assert STEP_INSTALLERS in DEFAULT_STEP_LABELS
    assert STEP_REPOS in DEFAULT_STEP_LABELS
    assert STEP_UV_CACHE in DEFAULT_STEP_LABELS
    assert STEP_BUILD_ZIPS in DEFAULT_STEP_LABELS
    assert STEP_BUILD_EXES in DEFAULT_STEP_LABELS
    assert STEP_OPEN in DEFAULT_STEP_LABELS


@pytest.mark.parametrize(
    ("label", "attr"),
    [
        (STEP_WIPE, "wipe_dependencies"),
        (STEP_BINARIES, "binaries"),
        (STEP_BUILD_ZIPS, "build_zips"),
        (STEP_BUILD_EXES, "build_zips"),
    ],
)
def test_single_label_maps_attribute(label: str, attr: str) -> None:
    steps = BuildSteps.from_labels([label])
    assert getattr(steps, attr) is True


def test_detect_mode_from_argv() -> None:
    assert detect_mode_from_argv(["--offline"]) == "offline"
    assert detect_mode_from_argv(["--online"]) == "online"
