"""Tests for detached uv upgrade .cmd generation."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.uv_upgrade_bat import (
    PROJECT_NAMES,
    build_relaunch_command,
    build_uv_upgrade_cmd,
    quote_cmd_arg,
    resolve_upgrade_projects,
    write_uv_upgrade_cmd,
)


def test_resolve_upgrade_projects_orders_and_skips_missing(tmp_path: Path) -> None:
    knife = tmp_path / "harrix-swiss-knife"
    pylib = tmp_path / "harrix-pylib"
    other = tmp_path / "other-project"
    knife.mkdir()
    pylib.mkdir()
    other.mkdir()
    resolved = resolve_upgrade_projects([str(other), str(pylib), str(knife), str(knife)])
    assert [path.name for path in resolved] == ["harrix-swiss-knife", "harrix-pylib"]
    assert PROJECT_NAMES[0] == "harrix-swiss-knife"


def test_quote_cmd_arg_quotes_spaces_and_specials() -> None:
    assert quote_cmd_arg("uv.exe") == "uv.exe"
    assert quote_cmd_arg(r"C:\Program Files\uv\uv.exe") == r'"C:\Program Files\uv\uv.exe"'
    assert quote_cmd_arg('say "hi"') == '"say ""hi"""'


def test_build_relaunch_command_joins_quoted_argv() -> None:
    cmd = build_relaunch_command([r"C:\venv\Scripts\python.exe", r"D:\GitHub\app\main.py", "--flag"])
    assert cmd == r"C:\venv\Scripts\python.exe D:\GitHub\app\main.py --flag"
    spaced = build_relaunch_command([r"C:\Program Files\python.exe", "main.py"])
    assert spaced.startswith(r'"C:\Program Files\python.exe"')
    assert spaced.endswith("main.py")


def test_build_uv_upgrade_cmd_contains_wait_uv_and_projects(tmp_path: Path) -> None:
    uv = tmp_path / "uv.exe"
    uv.write_text("", encoding="utf-8")
    knife = tmp_path / "harrix-swiss-knife"
    pylib = tmp_path / "harrix-pylib"
    pyssg = tmp_path / "harrix-pyssg"
    for folder in (knife, pylib, pyssg):
        folder.mkdir()
    log = tmp_path / "upgrade.log"
    text = build_uv_upgrade_cmd(
        wait_pid=4242,
        uv_exe=uv,
        project_dirs=[knife, pylib, pyssg],
        relaunch_argv=[r"C:\venv\Scripts\pythonw.exe", r"D:\GitHub\harrix-swiss-knife\src\harrix_swiss_knife\main.py"],
        log_path=log,
        wait_timeout_seconds=90,
    )
    assert "set WAIT_PID=4242" in text
    assert "set WAIT_MAX=90" in text
    assert 'tasklist /FI "PID eq %WAIT_PID%"' in text
    assert f'set "UV={uv}"' in text
    assert "self update" in text
    assert "python upgrade" in text
    assert "sync --upgrade" in text
    assert str(knife) in text
    assert str(pylib) in text
    assert str(pyssg) in text
    assert "pythonw.exe" in text
    assert "harrix_swiss_knife" in text
    assert "pause" in text
    assert 'start ""' in text
    assert str(log) in text


def test_write_uv_upgrade_cmd_creates_file(tmp_path: Path) -> None:
    uv = tmp_path / "uv.exe"
    uv.write_bytes(b"")
    project = tmp_path / "harrix-swiss-knife"
    project.mkdir()
    out = tmp_path / "run.cmd"
    write_uv_upgrade_cmd(
        out,
        wait_pid=7,
        uv_exe=uv,
        project_dirs=[project],
        relaunch_argv=["python.exe", "main.py"],
        log_path=tmp_path / "log.txt",
    )
    content = out.read_bytes()
    assert content.startswith(b"@echo off")
    assert b"\r\n" in content
    assert b"set WAIT_PID=7" in content
