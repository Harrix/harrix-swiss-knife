"""Build Android APK (debug / release) via Gradle wrapper in ``android/``."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.android_gradle import (
    resolve_android_dir,
    resolve_android_home,
    resolve_java_home,
    run_gradle,
)


class OnAndroidBuild(ActionBase):
    """Build HSK Android APK (`assembleDebug` or `assembleRelease`).

    Tray uses `android_build_variant` from `config/config.json` (`debug` or
    `release`, default `release`). CLI may pass `debug`/`release` to override.
    Requires Windows, JDK 17, and Android SDK (`ANDROID_HOME` /
    `android/local.properties`). Use `install/setup-android-sdk.bat` once
    to install the toolchain. After a successful build, the result dialog
    can open the APK folder, and the action runs `adb install -r` when a USB
    device is connected. If the phone is still waiting for USB debugging
    authorization, waits for confirmation.

    """

    icon = "📱"
    title = "Build Android APK"
    cli_available = True
    cli_hint = "android build [debug|release]"

    CLI_VARIANTS: ClassVar[tuple[str, ...]] = ("debug", "release")
    DEFAULT_VARIANT: ClassVar[str] = "release"
    CONFIG_KEY: ClassVar[str] = "android_build_variant"

    _ADB_AUTH_POLL_INTERVAL_SEC: ClassVar[float] = 2.0
    _ADB_AUTH_TIMEOUT_SEC: ClassVar[float] = 120.0

    _VARIANT_CONFIG: ClassVar[dict[str, tuple[str, str]]] = {
        "debug": ("assembleDebug", "app/build/outputs/apk/debug/HarrixSwissKnife-debug.apk"),
        "release": (
            "assembleRelease",
            "app/build/outputs/apk/release/HarrixSwissKnife-release.apk",
        ),
    }

    @ActionBase.handle_exceptions("Android APK build")
    def execute(
        self,
        *_args: Any,
        variant: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Build the Android APK (sync for CLI, background thread for tray)."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        resolved = self._resolve_variant(variant=variant)
        if resolved is None:
            if not noninteractive:
                self.show_result()
            return

        gradle_task, apk_relative = resolved
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

        self._gradle_task = gradle_task
        self._apk_relative = apk_relative
        self._java_home = java_home

        if noninteractive:
            self._run_gradle_build(android_dir, gradle_task, apk_relative, java_home)
            return

        self._android_dir_for_thread = android_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Android APK build thread")
    def in_thread(self) -> str | None:
        """Run Gradle in a worker thread for the tray UI."""
        android_dir = getattr(self, "_android_dir_for_thread", None)
        java_home = getattr(self, "_java_home", None)
        if android_dir is None or not java_home:
            return None
        self._run_gradle_build(
            android_dir,
            getattr(self, "_gradle_task", "assembleRelease"),
            getattr(
                self,
                "_apk_relative",
                "app/build/outputs/apk/release/HarrixSwissKnife-release.apk",
            ),
            java_home,
        )
        return None

    @ActionBase.handle_exceptions("Android APK build thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray build."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _install_apk_via_adb(self, apk_path: Path) -> None:
        """Install the APK on the first connected adb device, if any."""
        adb = self._resolve_adb()
        if adb is None:
            self.add_line("🔵 adb not found - APK not installed (install platform-tools / setup-android-sdk).")
            return

        devices = self._wait_for_adb_device(adb)
        if not devices:
            return

        serial = devices[0]
        if len(devices) > 1:
            self.add_line(f"🔵 Multiple adb devices ({len(devices)}); installing on first: {serial}")

        cmd = [str(adb), "-s", serial, "install", "-r", str(apk_path)]
        self.add_line(f"$ {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ adb install failed (exit code {process.returncode}).")
            self.add_line(
                "Hint: enable USB debugging and Install via USB on the phone "
                "(see DEVELOPMENT.md → Android → phone setup)."
            )
            return

        self.add_line(f"✅ Installed on {serial}")

    def _list_adb_device_states(self, adb: Path) -> tuple[list[str], list[str]]:
        """Return ``(authorized, unauthorized)`` serials from ``adb devices``."""
        process = subprocess.run(
            [str(adb), "devices"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if process.returncode != 0:
            output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
            if output:
                self.add_line(output)
            return [], []

        authorized: list[str] = []
        unauthorized: list[str] = []
        min_device_columns = 2
        for raw_line in (process.stdout or "").splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("List of devices"):
                continue
            parts = stripped.split()
            if len(parts) < min_device_columns:
                continue
            serial, state = parts[0], parts[1]
            if state == "device":
                authorized.append(serial)
            elif state == "unauthorized":
                unauthorized.append(serial)
        return authorized, unauthorized

    def _resolve_adb(self) -> Path | None:
        """Resolve ``adb.exe`` from Android SDK or PATH."""
        android_home = resolve_android_home()
        if android_home:
            candidate = Path(android_home) / "platform-tools" / "adb.exe"
            if candidate.is_file():
                return candidate

        which = h.dev.run_command("where adb")
        for line in (which or "").splitlines():
            path = Path(line.strip().strip('"'))
            if path.is_file():
                return path
        return None

    def _resolve_variant(self, *, variant: str | None) -> tuple[str, str] | None:
        """Map CLI override or ``android_build_variant`` config to Gradle task and APK path."""
        if variant is not None:
            key = str(variant).strip().lower()
            source = "CLI"
        else:
            raw = self.config.get(self.CONFIG_KEY, self.DEFAULT_VARIANT)
            key = str(raw or self.DEFAULT_VARIANT).strip().lower()
            source = f"config.json `{self.CONFIG_KEY}`"

        config = self._VARIANT_CONFIG.get(key)
        if config is None:
            supported = ", ".join(self.CLI_VARIANTS)
            self.add_line(f"❌ Unknown Android build variant {key!r} from {source}. Use: {supported}")
            return None

        gradle_task, _apk_relative = config
        self.add_line(f"🔵 Build variant: {key} ({gradle_task}) — {source}")
        return config

    def _run_gradle_build(
        self,
        android_dir: Path,
        gradle_task: str,
        apk_relative: str,
        java_home: str,
    ) -> None:
        """Invoke Gradle with a resolved JDK and report the APK path or failure."""
        apk_path = android_dir / apk_relative
        gradlew = android_dir / "gradlew.bat"

        self.add_line(f"🔵 Starting {gradle_task} in {android_dir}")
        self.add_line(f"$ JAVA_HOME={java_home}")
        self.add_line(f'$ "{gradlew}" {gradle_task} --no-daemon')

        process = run_gradle(android_dir, java_home, gradle_task)
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ {gradle_task} failed (exit code {process.returncode}).")
            if "JAVA_HOME" in output:
                self.add_line("Hint: set JAVA_HOME or run install\\setup-android-sdk.bat, then restart the app.")
            else:
                self.add_line("Hint: run install\\setup-android-sdk.bat if the SDK is not installed.")
            return

        if not apk_path.is_file():
            self.add_line(f"❌ {gradle_task} finished but APK is missing: {apk_path}")
            return

        self.add_line(f"✅ APK: {apk_path}")
        self.result_folder = apk_path.parent
        self._install_apk_via_adb(apk_path)

    def _wait_for_adb_device(self, adb: Path) -> list[str]:
        """Return authorized adb serials, waiting if the phone needs USB auth."""
        authorized, unauthorized = self._list_adb_device_states(adb)
        if authorized:
            return authorized

        if not unauthorized:
            self.add_line("🔵 No adb device - APK not installed.")
            return []

        serials = ", ".join(unauthorized)
        timeout = int(self._ADB_AUTH_TIMEOUT_SEC)
        self.add_line(
            f"🔵 adb device unauthorized ({serials}). "
            f"Confirm the USB debugging fingerprint on the phone "
            f"(waiting up to {timeout}s)…"
        )

        deadline = time.monotonic() + self._ADB_AUTH_TIMEOUT_SEC
        while time.monotonic() < deadline:
            time.sleep(self._ADB_AUTH_POLL_INTERVAL_SEC)
            authorized, unauthorized = self._list_adb_device_states(adb)
            if authorized:
                self.add_line(f"✅ USB debugging authorized: {', '.join(authorized)}")
                return authorized
            if not unauthorized:
                self.add_line("🔵 adb device disconnected while waiting - APK not installed.")
                return []

        self.add_line(f"❌ Timed out waiting for USB debugging authorization ({timeout}s). APK not installed.")
        return []
