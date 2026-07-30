"""Shared helpers for Android Gradle actions (build / format / check)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import harrix_pylib as h

if sys.platform == "win32":
    import winreg
else:  # pragma: no cover - Windows-only helpers
    winreg = None  # type: ignore[assignment]


def gradle_env(java_home: str) -> dict[str, str]:
    """Build process env for Gradle, including JDK and Android SDK paths."""
    env = os.environ.copy()
    env["JAVA_HOME"] = java_home
    java_bin = str(Path(java_home) / "bin")
    path_parts = [java_bin, *[p for p in env.get("PATH", "").split(os.pathsep) if p]]
    env["PATH"] = os.pathsep.join(path_parts)

    android_home = resolve_android_home()
    if android_home:
        env["ANDROID_HOME"] = android_home
        env["ANDROID_SDK_ROOT"] = android_home
    return env


def resolve_android_dir() -> Path | None:
    """Return ``android/`` under the project root if the Gradle wrapper exists."""
    android_dir = h.dev.get_project_root() / "android"
    if not android_dir.is_dir():
        return None
    if not (android_dir / "gradlew.bat").is_file():
        return None
    return android_dir


def resolve_android_home() -> str | None:
    """Resolve Android SDK root from env or the default user Sdk folder."""
    for value in (
        os.environ.get("ANDROID_HOME"),
        os.environ.get("ANDROID_SDK_ROOT"),
        windows_env_value("ANDROID_HOME"),
        windows_env_value("ANDROID_SDK_ROOT"),
    ):
        if value and Path(value).is_dir():
            return value

    default_sdk = Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk"
    if default_sdk.is_dir():
        return str(default_sdk)
    return None


def resolve_java_home() -> str | None:
    """Resolve JDK home from process/user/machine env or known install paths."""
    candidates: list[str] = [
        value
        for value in (
            os.environ.get("JAVA_HOME"),
            windows_env_value("JAVA_HOME"),
        )
        if value
    ]

    local_java = Path(os.environ.get("LOCALAPPDATA", "")) / "Java"
    if local_java.is_dir():
        candidates.extend(str(path) for path in sorted(local_java.glob("jdk-17*"), reverse=True))

    microsoft = Path(r"C:\Program Files\Microsoft")
    if microsoft.is_dir():
        candidates.extend(str(path) for path in sorted(microsoft.glob("jdk-17*"), reverse=True))

    candidates.append(r"C:\Program Files\Android\Android Studio\jbr")

    for candidate in candidates:
        java_home = valid_java_home(candidate)
        if java_home is not None:
            return java_home
    return None


def run_gradle(
    android_dir: Path,
    java_home: str,
    *tasks: str,
) -> subprocess.CompletedProcess[str]:
    """Run one or more Gradle tasks via ``gradlew.bat --no-daemon``."""
    gradlew = android_dir / "gradlew.bat"
    return subprocess.run(
        [str(gradlew), *tasks, "--no-daemon"],
        cwd=str(android_dir),
        env=gradle_env(java_home),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def valid_java_home(path: str) -> str | None:
    """Return path if it looks like a usable JDK/JBR home."""
    root = Path(path.strip().strip('"'))
    if (root / "bin" / "java.exe").is_file():
        return str(root)
    return None


def windows_env_value(name: str) -> str | None:
    """Read a persistent Windows environment variable (User, then Machine)."""
    if winreg is None:
        return None
    for root, subkey in (
        (winreg.HKEY_CURRENT_USER, r"Environment"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    ):
        try:
            with winreg.OpenKey(root, subkey) as key:
                value, _ = winreg.QueryValueEx(key, name)
        except OSError:
            continue
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
