"""Tests for Android SDK setup helpers."""

from pathlib import Path

from harrix_swiss_knife.actions.common.android_gradle import (
    SDK_LICENSE_HASH,
    SDK_PREVIEW_LICENSE_HASH,
    is_java_version_17_output,
    path_with_user_entry,
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
