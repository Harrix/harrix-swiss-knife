"""Tests for the Python install-zip builder helpers."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.install_zip_builder import (
    DEFAULT_STEP_LABELS,
    OFFLINE_ZIP_NAME,
    ONLINE_ZIP_NAME,
    STEP_BINARIES,
    STEP_BUILD_ZIPS,
    STEP_INSTALLERS,
    STEP_OPEN,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_WIPE,
    BuildSteps,
    build_install_zips,
    cli_argv_for_steps,
    install_dir,
    redundant_media_zip_names,
    run_pipeline,
    steps_from_cli_flags,
    wipe_dependencies,
)


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


def test_build_steps_zip_only() -> None:
    steps = BuildSteps.from_labels([STEP_BUILD_ZIPS])
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
    for name in ("install.bat", "install-with-log.ps1", "harrix-swiss-knife.ps1"):
        (install / name).write_text(f"#{name}\n", encoding="utf-8")
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


def test_build_install_zips_online_vs_offline_membership(tmp_path: Path) -> None:
    _prepare_install_tree(tmp_path)
    lines: list[str] = []
    online, offline = build_install_zips(tmp_path, lines.append)
    assert online.name == ONLINE_ZIP_NAME
    assert offline.name == OFFLINE_ZIP_NAME

    with zipfile.ZipFile(online, "r") as zf:
        names = set(zf.namelist())
    assert "install.bat" in names
    assert "harrix-swiss-knife.ps1" in names
    assert "dependencies/ffmpeg.exe" in names
    assert "dependencies/note.txt" in names
    assert "dependencies/Git-latest-64-bit.exe" in names
    assert not any(n.startswith("dependencies/repos/") for n in names)
    assert not any(n.startswith("dependencies/uv-cache/") for n in names)
    assert not any(n.startswith("dependencies/uv-python-cache/") for n in names)
    assert "dependencies/windows-artifacts.zip" not in names
    assert "dependencies/download.log" not in names

    with zipfile.ZipFile(offline, "r") as zf:
        names = set(zf.namelist())
    assert "dependencies/repos/harrix-swiss-knife.zip" in names
    assert "dependencies/uv-cache/c.bin" in names
    assert "dependencies/uv-python-cache/p.bin" in names
    assert "dependencies/windows-artifacts.zip" not in names


def test_run_pipeline_zip_only(tmp_path: Path) -> None:
    _prepare_install_tree(tmp_path)
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
    result = run_pipeline(tmp_path, steps, interactive=False)
    assert result.ok
    assert result.online_zip is not None
    assert result.offline_zip is not None
    assert result.online_zip.is_file()


def test_run_pipeline_no_steps(tmp_path: Path) -> None:
    result = run_pipeline(tmp_path, BuildSteps.from_labels([]), interactive=False)
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
    assert STEP_OPEN in DEFAULT_STEP_LABELS


@pytest.mark.parametrize(
    ("label", "attr"),
    [
        (STEP_WIPE, "wipe_dependencies"),
        (STEP_BINARIES, "binaries"),
        (STEP_BUILD_ZIPS, "build_zips"),
    ],
)
def test_single_label_maps_attribute(label: str, attr: str) -> None:
    steps = BuildSteps.from_labels([label])
    assert getattr(steps, attr) is True
