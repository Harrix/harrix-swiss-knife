---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_build.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAndroidBuild`](#%EF%B8%8F-class-onandroidbuild)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
  - [🏛️ Class `OnAndroidBuild.InstallTarget`](#%EF%B8%8F-class-onandroidbuildinstalltarget)
    - [⚙️ Method `device_id (property)`](#%EF%B8%8F-method-device_id-property)

</details>

## 🏛️ Class `OnAndroidBuild`

```python
class OnAndroidBuild(ActionBase)
```

Build an Android APK (`assembleDebug` or `assembleRelease`).

Tray dialog lists folders from `paths_android_projects` (or browse), a
checkbox to build all listed projects sequentially, a **Release** checkbox
(initial value from `android_build_variant` in `config/config.json`, default
[`release`](../../apps/common/audio_recording/recorder.g.md#%EF%B8%8F-method-release)), and a single install target on the right: connected `adb`
devices plus installed AVDs. Selecting a stopped AVD starts the emulator
before `adb install -r`. CLI may pass a project folder and optional
`debug`/[`release`](../../apps/common/audio_recording/recorder.g.md#%EF%B8%8F-method-release) to override the variant, or `--all` to build every
configured project; CLI installs on the first authorized adb device.
Requires Windows, JDK 17, and Android SDK (`ANDROID_HOME` /
`local.properties`). Use `install/setup-android-sdk.bat` once to install
the toolchain. After a successful build, the result dialog can open the APK
folder. If the phone is still waiting for USB debugging authorization,
waits for confirmation.

<details>
<summary>Code:</summary>

```python
class OnAndroidBuild(ActionBase):

    icon = "📱"
    title = "Build Android APK in …"
    cli_available = True
    cli_hint = "android build [FOLDER] [debug|release] [--all]"

    CLI_VARIANTS: ClassVar[tuple[str, ...]] = ("debug", "release")
    DEFAULT_VARIANT: ClassVar[str] = "release"
    CONFIG_KEY: ClassVar[str] = "android_build_variant"
    ALL_PROJECTS_CHECKBOX_LABEL: ClassVar[str] = "Build and install all projects sequentially"

    _ADB_AUTH_POLL_INTERVAL_SEC: ClassVar[float] = 2.0
    _ADB_AUTH_TIMEOUT_SEC: ClassVar[float] = 120.0
    _EMULATOR_BOOT_TIMEOUT_SEC: ClassVar[float] = 180.0
    _EMULATOR_BOOT_POLL_INTERVAL_SEC: ClassVar[float] = 3.0

    _VARIANT_TASKS: ClassVar[dict[str, str]] = {
        "debug": "assembleDebug",
        "release": "assembleRelease",
    }

    @ActionBase.handle_exceptions("android apk build")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        variant: str | None = None,
        build_all: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Build the Android APK (sync for CLI, background thread for tray)."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive and folder_path is None and not build_all:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True (unless --all)"),
                self.title,
            )
            return

        install_target: OnAndroidBuild.InstallTarget | None = None
        projects: list[Path] = []
        if build_all:
            projects = self._configured_android_projects()
            if not projects:
                self.add_line("❌ No valid Android projects in paths_android_projects.")
                if not noninteractive:
                    self.show_result()
                return
        elif folder_path is not None:
            projects = [Path(folder_path).resolve()]
        else:
            loading_toast = toast_notification.ToastNotification(
                message=strip_md_inline_code_markers("Loading Android devices and AVDs…"),
                duration=60000,
            )
            loading_toast.present()
            app = QApplication.instance()
            if app is not None:
                app.processEvents()
            try:
                targets = self._collect_install_targets()
            finally:
                loading_toast.close()
                if app is not None:
                    app.processEvents()
            default_device_id = targets[0].device_id if targets else None
            release_default = self._config_variant_is_release()
            choice = self.dialogs.get_android_build_selection(
                self.config["paths_android_projects"],
                self.config["path_github"],
                build_all_checkbox_label=self.ALL_PROJECTS_CHECKBOX_LABEL,
                release_default=release_default,
                devices=[(target.label, target.device_id) for target in targets],
                default_device_id=default_device_id,
            )
            if choice is None:
                return
            if choice.build_all:
                projects = self._configured_android_projects()
                if not projects:
                    self.add_line("❌ No valid Android projects in paths_android_projects.")
                    if not noninteractive:
                        self.show_result()
                    return
            else:
                projects = [choice.folder]
            variant = "release" if choice.release else "debug"
            install_target = self._target_by_device_id(targets, choice.device_id)

        resolved = self._resolve_variant(variant=variant, source_hint="tray dialog" if not noninteractive else None)
        if resolved is None:
            if not noninteractive:
                self.show_result()
            return

        variant_key, gradle_task = resolved
        if not resolve_android_home() and not any((project / "local.properties").is_file() for project in projects):
            self.add_line(
                "❌ Android SDK not configured. Run `install\\setup-android-sdk.bat` "
                "or set ANDROID_HOME and create local.properties in the project."
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

        self._variant_key = variant_key
        self._gradle_task = gradle_task
        self._java_home = java_home
        self._android_projects = projects
        self._install_target = install_target

        if noninteractive:
            self._run_projects_build(projects, variant_key, gradle_task, java_home, install_target)
            return

        self.folder_path = projects[0]
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("android apk build thread")
    def in_thread(self) -> str | None:
        """Run Gradle in a worker thread for the tray UI."""
        projects = getattr(self, "_android_projects", None)
        java_home = getattr(self, "_java_home", None)
        if not projects or not java_home:
            return None
        self._run_projects_build(
            projects,
            getattr(self, "_variant_key", self.DEFAULT_VARIANT),
            getattr(self, "_gradle_task", "assembleRelease"),
            java_home,
            getattr(self, "_install_target", None),
        )
        return None

    @ActionBase.handle_exceptions("android apk build thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray build."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _adb_shell_getprop(self, adb: Path, serial: str, prop: str) -> str | None:
        """Return a trimmed `getprop` value from a device, or `None`."""
        process = subprocess.run(
            [str(adb), "-s", serial, "shell", "getprop", prop],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if process.returncode != 0:
            return None
        value = (process.stdout or "").strip()
        return value or None

    def _collect_install_targets(self) -> list[InstallTarget]:
        """Return connected adb devices and installed AVDs for the tray list."""
        targets: list[OnAndroidBuild.InstallTarget] = []
        seen_avds: set[str] = set()
        adb = self._resolve_adb()
        if adb is not None:
            authorized, _unauthorized = self._list_adb_device_states(adb)
            for serial in authorized:
                avd_name = self._emulator_avd_name(adb, serial)
                model = self._adb_shell_getprop(adb, serial, "ro.product.model")
                if avd_name:
                    seen_avds.add(avd_name)
                    label = f"{avd_name} ({serial}) — running"
                    if model:
                        label = f"{avd_name} / {model} ({serial}) — running"
                    targets.append(
                        OnAndroidBuild.InstallTarget(kind="adb", key=serial, label=label, serial=serial),
                    )
                else:
                    label = f"{model} ({serial}) — connected" if model else f"{serial} — connected"
                    targets.append(
                        OnAndroidBuild.InstallTarget(kind="adb", key=serial, label=label, serial=serial),
                    )

        emulator = self._resolve_emulator()
        if emulator is not None:
            for avd_name in self._list_avd_names(emulator):
                if avd_name in seen_avds:
                    continue
                targets.append(
                    OnAndroidBuild.InstallTarget(
                        kind="avd",
                        key=avd_name,
                        label=f"{avd_name} — AVD (start on install)",
                    ),
                )
        return targets

    def _config_variant_is_release(self) -> bool:
        """Return whether config `android_build_variant` resolves to release."""
        raw = self.config.get(self.CONFIG_KEY, self.DEFAULT_VARIANT)
        key = str(raw or self.DEFAULT_VARIANT).strip().lower()
        return key == "release"

    def _configured_android_projects(self) -> list[Path]:
        """Return existing Android project folders from `paths_android_projects`."""
        raw = self.config.get("paths_android_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_android_projects" must be a list.')
            return []

        projects: list[Path] = []
        for entry in raw:
            path = Path(str(entry)).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                self.add_line(f"⚠️ Could not resolve path: {entry}")
                continue
            if not resolved.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {resolved}")
                continue
            if not is_android_project(resolved):
                self.add_line(f"⚠️ Skip (not an Android project): {resolved}")
                continue
            projects.append(resolved)
        return projects

    def _emulator_avd_name(self, adb: Path, serial: str) -> str | None:
        """Return AVD name for an emulator serial, or `None` for physical devices."""
        if not serial.startswith("emulator-"):
            return None
        process = subprocess.run(
            [str(adb), "-s", serial, "emu", "avd", "name"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if process.returncode != 0:
            return None
        for line in (process.stdout or "").splitlines():
            stripped = line.strip()
            if not stripped or stripped == "OK":
                continue
            return stripped
        return None

    def _ensure_install_serial(
        self,
        adb: Path,
        target: InstallTarget | None,
    ) -> str | None:
        """Resolve an authorized adb serial for install, starting an AVD if needed."""
        if target is None:
            devices = self._wait_for_adb_device(adb)
            if not devices:
                return None
            serial = devices[0]
            if len(devices) > 1:
                self.add_line(f"🔵 Multiple adb devices ({len(devices)}); installing on first: {serial}")
            return serial

        if target.kind == "adb":
            serial = target.serial or target.key
            authorized, unauthorized = self._list_adb_device_states(adb)
            if serial in authorized:
                return serial
            if serial in unauthorized:
                waited = self._wait_for_specific_adb_device(adb, serial, unauthorized_hint=True)
                return waited
            self.add_line(f"❌ Selected adb device not connected: {serial}")
            return None

        # Offline or selected AVD by name — find running instance or start it.
        serial = self._find_running_avd_serial(adb, target.key)
        if serial is not None:
            return serial

        if not self._start_avd(target.key):
            return None
        return self._wait_for_avd_boot(adb, target.key)

    def _find_running_avd_serial(self, adb: Path, avd_name: str) -> str | None:
        """Return adb serial of a running emulator with the given AVD name."""
        authorized, _unauthorized = self._list_adb_device_states(adb)
        for serial in authorized:
            if self._emulator_avd_name(adb, serial) == avd_name:
                return serial
        return None

    def _install_apk_via_adb(
        self,
        apk_path: Path,
        target: InstallTarget | None = None,
    ) -> None:
        """Install the APK on the selected (or first) adb device."""
        adb = self._resolve_adb()
        if adb is None:
            self.add_line("🔵 adb not found - APK not installed (install platform-tools / setup-android-sdk).")
            return

        serial = self._ensure_install_serial(adb, target)
        if not serial:
            return

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

    def _list_avd_names(self, emulator: Path) -> list[str]:
        """Return installed AVD names from ``emulator -list-avds``."""
        process = subprocess.run(
            [str(emulator), "-list-avds"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if process.returncode != 0:
            return []
        return [line.strip() for line in (process.stdout or "").splitlines() if line.strip()]

    def _resolve_adb(self) -> Path | None:
        """Resolve ``adb.exe`` from Android SDK or PATH."""
        android_home = resolve_android_home()
        if android_home:
            candidate = Path(android_home) / "platform-tools" / "adb.exe"
            if candidate.is_file():
                return candidate

        which = h.dev.run_command("where adb", is_shell=True)
        for line in (which or "").splitlines():
            path = Path(line.strip().strip('"'))
            if path.is_file():
                return path
        return None

    def _resolve_emulator(self) -> Path | None:
        """Resolve ``emulator.exe`` from Android SDK or PATH."""
        android_home = resolve_android_home()
        if android_home:
            candidate = Path(android_home) / "emulator" / "emulator.exe"
            if candidate.is_file():
                return candidate

        which = h.dev.run_command("where emulator", is_shell=True)
        for line in (which or "").splitlines():
            path = Path(line.strip().strip('"'))
            if path.is_file():
                return path
        return None

    def _resolve_variant(
        self,
        *,
        variant: str | None,
        source_hint: str | None = None,
    ) -> tuple[str, str] | None:
        """Map CLI override, tray choice, or config to variant key and Gradle task."""
        if variant is not None:
            key = str(variant).strip().lower()
            source = source_hint or "CLI"
        else:
            raw = self.config.get(self.CONFIG_KEY, self.DEFAULT_VARIANT)
            key = str(raw or self.DEFAULT_VARIANT).strip().lower()
            source = f"config.json `{self.CONFIG_KEY}`"

        gradle_task = self._VARIANT_TASKS.get(key)
        if gradle_task is None:
            supported = ", ".join(self.CLI_VARIANTS)
            self.add_line(f"❌ Unknown Android build variant {key!r} from {source}. Use: {supported}")
            return None

        self.add_line(f"🔵 Build variant: {key} ({gradle_task}) — {source}")
        return key, gradle_task

    def _run_gradle_build(
        self,
        android_dir: Path,
        variant_key: str,
        gradle_task: str,
        java_home: str,
        target: InstallTarget | None,
    ) -> bool:
        """Invoke Gradle with a resolved JDK and report the APK path or failure.

        Returns:

        - `bool`: `True` when the APK was produced successfully.

        """
        if not is_android_project(android_dir):
            self.add_line(f"❌ {android_dir} is not an Android project (no gradlew.bat)")
            return False

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
            return False

        apk_path = find_built_apk(android_dir, variant_key)
        if apk_path is None:
            expected = android_dir / "app" / "build" / "outputs" / "apk" / variant_key
            self.add_line(f"❌ {gradle_task} finished but no APK found in {expected}")
            return False

        self.add_line(f"✅ APK: {apk_path}")
        self.result_folder = apk_path.parent
        self._install_apk_via_adb(apk_path, target)
        return True

    def _run_projects_build(
        self,
        projects: list[Path],
        variant_key: str,
        gradle_task: str,
        java_home: str,
        target: InstallTarget | None,
    ) -> None:
        """Build and install one or more Android projects sequentially."""
        total = len(projects)
        if total > 1:
            self.add_line(f"🔵 Building {total} Android project(s) sequentially…")

        failed: list[str] = []
        for index, project in enumerate(projects, start=1):
            if total > 1:
                self.add_line(f"\n=== [{index}/{total}] {project.name} ({project}) ===")
            if not self._run_gradle_build(project, variant_key, gradle_task, java_home, target):
                failed.append(project.name)

        if total > 1:
            passed = total - len(failed)
            if not failed:
                self.add_line(f"\n✅ All Android projects built ({passed}/{total}).")
            else:
                self.add_line(f"\n❌ Build failed in {len(failed)} project(s): {', '.join(failed)}")

    def _start_avd(self, avd_name: str) -> bool:
        """Launch an AVD in the background. Return `False` if emulator is missing."""
        emulator = self._resolve_emulator()
        if emulator is None:
            self.add_line("❌ emulator not found - cannot start AVD (install Android emulator / Android Studio).")
            return False

        cmd = [str(emulator), "-avd", avd_name]
        self.add_line(f"🔵 Starting AVD: {avd_name}")
        self.add_line(f"$ {' '.join(cmd)}")
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
        try:
            subprocess.Popen(  # noqa: S603
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
                close_fds=True,
            )
        except OSError as exc:
            self.add_line(f"❌ Failed to start emulator: {exc}")
            return False
        return True

    @staticmethod
    def _target_by_device_id(
        targets: list[InstallTarget],
        device_id: str | None,
    ) -> InstallTarget | None:
        """Map a dialog `device_id` back to an `InstallTarget`."""
        if device_id is None:
            return None
        for target in targets:
            if target.device_id == device_id:
                return target
        return None

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

    def _wait_for_avd_boot(self, adb: Path, avd_name: str) -> str | None:
        """Wait until the AVD is authorized and boot completed."""
        timeout = int(self._EMULATOR_BOOT_TIMEOUT_SEC)
        self.add_line(f"🔵 Waiting for AVD `{avd_name}` to boot (up to {timeout}s)…")
        deadline = time.monotonic() + self._EMULATOR_BOOT_TIMEOUT_SEC
        while time.monotonic() < deadline:
            serial = self._find_running_avd_serial(adb, avd_name)
            if serial is not None:
                boot = self._adb_shell_getprop(adb, serial, "sys.boot_completed")
                if boot == "1":
                    self.add_line(f"✅ AVD `{avd_name}` ready as {serial}")
                    return serial
            time.sleep(self._EMULATOR_BOOT_POLL_INTERVAL_SEC)

        self.add_line(f"❌ Timed out waiting for AVD `{avd_name}` ({timeout}s). APK not installed.")
        return None

    def _wait_for_specific_adb_device(
        self,
        adb: Path,
        serial: str,
        *,
        unauthorized_hint: bool,
    ) -> str | None:
        """Wait until a specific serial becomes authorized."""
        timeout = int(self._ADB_AUTH_TIMEOUT_SEC)
        if unauthorized_hint:
            self.add_line(
                f"🔵 adb device unauthorized ({serial}). "
                f"Confirm the USB debugging fingerprint on the phone "
                f"(waiting up to {timeout}s)…"
            )
        deadline = time.monotonic() + self._ADB_AUTH_TIMEOUT_SEC
        while time.monotonic() < deadline:
            authorized, unauthorized = self._list_adb_device_states(adb)
            if serial in authorized:
                self.add_line(f"✅ USB debugging authorized: {serial}")
                return serial
            if serial not in unauthorized and serial not in authorized:
                self.add_line(f"🔵 adb device disconnected while waiting ({serial}) - APK not installed.")
                return None
            time.sleep(self._ADB_AUTH_POLL_INTERVAL_SEC)

        self.add_line(f"❌ Timed out waiting for USB debugging authorization ({timeout}s). APK not installed.")
        return None

    @dataclass(frozen=True)
    class InstallTarget:
        """One install destination: connected adb device or installed AVD."""

        kind: Literal["adb", "avd"]
        key: str
        label: str
        serial: str | None = None

        @property
        def device_id(self) -> str:
            """Opaque ID stored in the tray device list (`adb:` / `avd:`)."""
            return f"{self.kind}:{self.key}"
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, folder_path: Path | None = None, variant: str | None = None, build_all: bool = False, noninteractive: bool = False, **_kwargs: Any) -> None
```

Build the Android APK (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        variant: str | None = None,
        build_all: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive and folder_path is None and not build_all:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True (unless --all)"),
                self.title,
            )
            return

        install_target: OnAndroidBuild.InstallTarget | None = None
        projects: list[Path] = []
        if build_all:
            projects = self._configured_android_projects()
            if not projects:
                self.add_line("❌ No valid Android projects in paths_android_projects.")
                if not noninteractive:
                    self.show_result()
                return
        elif folder_path is not None:
            projects = [Path(folder_path).resolve()]
        else:
            loading_toast = toast_notification.ToastNotification(
                message=strip_md_inline_code_markers("Loading Android devices and AVDs…"),
                duration=60000,
            )
            loading_toast.present()
            app = QApplication.instance()
            if app is not None:
                app.processEvents()
            try:
                targets = self._collect_install_targets()
            finally:
                loading_toast.close()
                if app is not None:
                    app.processEvents()
            default_device_id = targets[0].device_id if targets else None
            release_default = self._config_variant_is_release()
            choice = self.dialogs.get_android_build_selection(
                self.config["paths_android_projects"],
                self.config["path_github"],
                build_all_checkbox_label=self.ALL_PROJECTS_CHECKBOX_LABEL,
                release_default=release_default,
                devices=[(target.label, target.device_id) for target in targets],
                default_device_id=default_device_id,
            )
            if choice is None:
                return
            if choice.build_all:
                projects = self._configured_android_projects()
                if not projects:
                    self.add_line("❌ No valid Android projects in paths_android_projects.")
                    if not noninteractive:
                        self.show_result()
                    return
            else:
                projects = [choice.folder]
            variant = "release" if choice.release else "debug"
            install_target = self._target_by_device_id(targets, choice.device_id)

        resolved = self._resolve_variant(variant=variant, source_hint="tray dialog" if not noninteractive else None)
        if resolved is None:
            if not noninteractive:
                self.show_result()
            return

        variant_key, gradle_task = resolved
        if not resolve_android_home() and not any((project / "local.properties").is_file() for project in projects):
            self.add_line(
                "❌ Android SDK not configured. Run `install\\setup-android-sdk.bat` "
                "or set ANDROID_HOME and create local.properties in the project."
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

        self._variant_key = variant_key
        self._gradle_task = gradle_task
        self._java_home = java_home
        self._android_projects = projects
        self._install_target = install_target

        if noninteractive:
            self._run_projects_build(projects, variant_key, gradle_task, java_home, install_target)
            return

        self.folder_path = projects[0]
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Run Gradle in a worker thread for the tray UI.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        projects = getattr(self, "_android_projects", None)
        java_home = getattr(self, "_java_home", None)
        if not projects or not java_home:
            return None
        self._run_projects_build(
            projects,
            getattr(self, "_variant_key", self.DEFAULT_VARIANT),
            getattr(self, "_gradle_task", "assembleRelease"),
            java_home,
            getattr(self, "_install_target", None),
        )
        return None
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a tray build.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()
```

</details>

### 🏛️ Class `OnAndroidBuild.InstallTarget`

```python
class InstallTarget
```

One install destination: connected adb device or installed AVD.

<details>
<summary>Code:</summary>

```python
class InstallTarget:

        kind: Literal["adb", "avd"]
        key: str
        label: str
        serial: str | None = None

        @property
        def device_id(self) -> str:
            """Opaque ID stored in the tray device list (`adb:` / `avd:`)."""
            return f"{self.kind}:{self.key}"
```

</details>

#### ⚙️ Method `device_id (property)`

```python
def device_id(self) -> str
```

Opaque ID stored in the tray device list (`adb:` / `avd:`).

<details>
<summary>Code:</summary>

```python
def device_id(self) -> str:
            return f"{self.kind}:{self.key}"
```

</details>
