"""Verify Android code quality (Spotless, Detekt, Android Lint)."""

from __future__ import annotations

import sys
from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.android_gradle import (
    resolve_android_dir,
    resolve_android_home,
    resolve_java_home,
    run_gradle,
)


class OnAndroidCheck(ActionBase):
    """Run Android quality checks (`qualityCheck`).

    Runs Spotless check, Detekt (with Compose rules), and `lintDebug`. Requires
    Windows, JDK 17, and Android SDK. Prefer `hsk android format` first to
    auto-fix formatting issues.

    """

    icon = "🔬"
    title = "Check Android code"
    cli_available = True
    cli_hint = "android check"

    @ActionBase.handle_exceptions("Android check")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Run Spotless check, Detekt, and Android Lint."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        android_dir = resolve_android_dir()
        if android_dir is None:
            self.add_line("❌ android folder or gradlew.bat not found.")
            if not noninteractive:
                self.show_result()
            return

        local_props = android_dir / "local.properties"
        if not local_props.is_file() and not resolve_android_home():
            self.add_line(
                "❌ Android SDK not configured. Run `install\\setup-android-sdk.bat` "
                "or set ANDROID_HOME and create android/local.properties."
            )
            if not noninteractive:
                self.show_result()
            return

        java_home = resolve_java_home()
        if java_home is None:
            self.add_line(
                "❌ JAVA_HOME is not set and no JDK 17 was found. "
                "Run `install\\setup-android-sdk.bat` or set JAVA_HOME, then restart the app."
            )
            if not noninteractive:
                self.show_result()
            return

        self.add_line(f"🔵 Starting qualityCheck in {android_dir}")
        self.add_line(f"$ JAVA_HOME={java_home}")
        gradlew = android_dir / "gradlew.bat"
        self.add_line(f'$ "{gradlew}" qualityCheck --no-daemon')

        process = run_gradle(android_dir, java_home, "qualityCheck")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ qualityCheck failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ qualityCheck completed (spotlessCheck, detekt, lintDebug).")

        if not noninteractive:
            self.show_result()
