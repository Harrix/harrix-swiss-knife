"""Tests for Android SDK setup helpers."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from harrix_swiss_knife.actions.common.android_gradle import (
    GRADLE_PREFER_IPV4,
    SDK_LICENSE_HASH,
    SDK_PREVIEW_LICENSE_HASH,
    gradle_env,
    is_java_version_17_output,
    path_with_user_entry,
    run_gradle,
    write_android_local_properties,
    write_android_sdk_licenses,
)


def test_is_java_version_17_output() -> None:
    assert is_java_version_17_output('openjdk version "17.0.14" 2025-01-21')
    assert is_java_version_17_output('java version "17"')
    assert not is_java_version_17_output('openjdk version "21.0.1"')
    assert not is_java_version_17_output('openjdk version "11.0.2"')


def test_path_with_user_entry_appends_once() -> None:
    assert path_with_user_entry("", r"C:\tools") == r"C:\tools"
    assert path_with_user_entry(r"C:\a;C:\b", r"C:\c") == r"C:\a;C:\b;C:\c"
    assert path_with_user_entry(r"C:\a;C:\c;C:\b", r"C:\c") == r"C:\a;C:\c;C:\b"
    assert path_with_user_entry(r"C:\a;C:\c\;C:\b", r"C:\c") == r"C:\a;C:\c\;C:\b"


def test_gradle_env_forces_ipv4(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JAVA_TOOL_OPTIONS", raising=False)
    monkeypatch.delenv("GRADLE_OPTS", raising=False)
    monkeypatch.delenv("ANDROID_HOME", raising=False)
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)
    with patch(
        "harrix_swiss_knife.actions.common.android_gradle.resolve_android_home",
        return_value=None,
    ):
        env = gradle_env(r"C:\Java\jdk-17")
    assert GRADLE_PREFER_IPV4 in env["JAVA_TOOL_OPTIONS"].split()
    assert GRADLE_PREFER_IPV4 in env["GRADLE_OPTS"].split()
    assert env["JAVA_HOME"] == r"C:\Java\jdk-17"


def test_gradle_env_appends_ipv4_to_existing_opts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JAVA_TOOL_OPTIONS", "-Xmx512m")
    monkeypatch.setenv("GRADLE_OPTS", "-Dorg.gradle.daemon.idletimeout=10000")
    with patch(
        "harrix_swiss_knife.actions.common.android_gradle.resolve_android_home",
        return_value=None,
    ):
        env = gradle_env(r"C:\Java\jdk-17")
    assert env["JAVA_TOOL_OPTIONS"] == f"-Xmx512m {GRADLE_PREFER_IPV4}"
    assert env["GRADLE_OPTS"] == f"-Dorg.gradle.daemon.idletimeout=10000 {GRADLE_PREFER_IPV4}"


def test_run_gradle_does_not_pass_no_daemon(tmp_path: Path) -> None:
    android_dir = tmp_path / "android"
    android_dir.mkdir()
    (android_dir / "gradlew.bat").write_text("", encoding="utf-8")
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = ""
    completed.stderr = ""
    with (
        patch(
            "harrix_swiss_knife.actions.common.android_gradle.subprocess.run",
            return_value=completed,
        ) as mock_run,
        patch(
            "harrix_swiss_knife.actions.common.android_gradle.gradle_env",
            return_value={"JAVA_HOME": r"C:\Java\jdk-17"},
        ),
    ):
        run_gradle(android_dir, r"C:\Java\jdk-17", "assembleRelease")
    argv = mock_run.call_args.args[0]
    assert "--no-daemon" not in argv
    assert argv[-1] == "assembleRelease"


def test_write_android_local_properties(tmp_path: Path) -> None:
    sdk = tmp_path / "Sdk"
    sdk.mkdir()
    android_dir = tmp_path / "android"
    android_dir.mkdir()
    path = write_android_local_properties(android_dir, sdk)
    text = path.read_text(encoding="ascii")
    assert text.startswith("sdk.dir=")
    assert text.endswith("\n")
    assert "\\\\" in text or "/" in text


def test_write_android_sdk_licenses(tmp_path: Path) -> None:
    sdk = tmp_path / "Sdk"
    write_android_sdk_licenses(sdk)
    license_path = sdk / "licenses" / "android-sdk-license"
    preview_path = sdk / "licenses" / "android-sdk-preview-license"
    assert license_path.read_text(encoding="ascii") == SDK_LICENSE_HASH
    assert preview_path.read_text(encoding="ascii") == SDK_PREVIEW_LICENSE_HASH
