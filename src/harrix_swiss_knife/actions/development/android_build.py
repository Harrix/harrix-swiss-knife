"""Build Android APK (debug / release) via Gradle wrapper in ``android/``."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase

if TYPE_CHECKING:
    from pathlib import Path


class AndroidBuildActionBase(ActionBase):
    """Shared Gradle APK build for the `android/` module.

    Runs `gradlew.bat assembleDebug` or `assembleRelease` from the repo
    `android` folder. Requires Windows, JDK 17, and Android SDK
    (`ANDROID_HOME` / `android/local.properties`). Use
    `install/setup-android-sdk.bat` once to install the toolchain.

    """

    gradle_task: ClassVar[str] = "assembleDebug"
    apk_relative: ClassVar[str] = "app/build/outputs/apk/debug/app-debug.apk"
    cli_available = True

    @ActionBase.handle_exceptions("Android APK build")
    def execute(
        self,
        *_args: Any,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Build the Android APK (sync for CLI, background thread for tray)."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            self.show_result()
            return

        android_dir = self._android_dir()
        if android_dir is None:
            self.show_result()
            return

        if noninteractive:
            self.add_line(f"🔵 Starting {self.gradle_task} in {android_dir}")
            self._run_gradle_build(android_dir)
            return

        self._android_dir_for_thread = android_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Android APK build thread")
    def in_thread(self) -> str | None:
        """Run Gradle in a worker thread for the tray UI."""
        android_dir = getattr(self, "_android_dir_for_thread", None)
        if android_dir is None:
            return None
        self._run_gradle_build(android_dir)
        return None

    @ActionBase.handle_exceptions("Android APK build thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray build."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _android_dir(self) -> Path | None:
        """Resolve ``android/`` under the project root, or report errors."""
        project_root = h.dev.get_project_root()
        android_dir = project_root / "android"
        if not android_dir.is_dir():
            self.add_line(f"❌ android folder not found: {android_dir}")
            return None

        gradlew = android_dir / "gradlew.bat"
        if not gradlew.is_file():
            self.add_line(f"❌ gradlew.bat not found: {gradlew}")
            return None

        local_props = android_dir / "local.properties"
        android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        if not local_props.is_file() and not android_home:
            self.add_line(
                "❌ Android SDK not configured. Run `install\\setup-android-sdk.bat` "
                "or set ANDROID_HOME and create android/local.properties."
            )
            return None

        return android_dir

    def _run_gradle_build(self, android_dir: Path) -> None:
        """Invoke Gradle and report the APK path or failure."""
        gradlew = android_dir / "gradlew.bat"
        cmd = f'"{gradlew}" {self.gradle_task} --no-daemon'
        self.add_line(f"$ cd {android_dir}")
        self.add_line(f"$ {cmd}")
        result = h.dev.run_command(cmd, cwd=str(android_dir))
        if result:
            self.add_line(result)

        apk_path = android_dir / self.apk_relative
        failed = "BUILD FAILED" in (result or "") or "FAILURE:" in (result or "")
        if failed or not apk_path.is_file():
            self.add_line(f"❌ {self.gradle_task} failed (APK missing or build error).")
            self.add_line("Hint: run install\\setup-android-sdk.bat if the SDK is not installed.")
            return

        self.add_line(f"✅ APK: {apk_path}")


class OnAndroidBuildDebug(AndroidBuildActionBase):
    """Build the debug APK for HSK Android (`assembleDebug`)."""

    icon = "🤖"
    title = "Build Android APK (debug)"
    cli_hint = "dev android-build-debug"
    gradle_task = "assembleDebug"
    apk_relative = "app/build/outputs/apk/debug/app-debug.apk"


class OnAndroidBuildRelease(AndroidBuildActionBase):
    """Build the release APK for HSK Android (`assembleRelease`, unsigned)."""

    icon = "🤖"
    title = "Build Android APK (release)"
    cli_hint = "dev android-build-release"
    gradle_task = "assembleRelease"
    apk_relative = "app/build/outputs/apk/release/app-release-unsigned.apk"
