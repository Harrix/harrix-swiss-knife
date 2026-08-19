---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_setup_sdk.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAndroidSetupSdk`](#%EF%B8%8F-class-onandroidsetupsdk)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnAndroidSetupSdk`

```python
class OnAndroidSetupSdk(ActionBase)
```

Install JDK 17 and Android SDK packages for building the Android module.

Idempotent. Uses portable Temurin 17 under `%LOCALAPPDATA%\Java` when no
JDK 17 is found (usually no UAC). SDK goes to `%LOCALAPPDATA%\Android\Sdk`.
Optional Android Studio via winget. Windows only.

<details>
<summary>Code:</summary>

```python
class OnAndroidSetupSdk(ActionBase):

    icon = "📥"
    title = "Install JDK and Android SDK"
    cli_available = True
    cli_hint = "android setup [--android-studio]"

    STUDIO_CHOICE: str = "Install Android Studio"
    SDK_PACKAGES: tuple[str, ...] = (
        "platform-tools",
        "platforms;android-35",
        "build-tools;35.0.0",
    )
    TEMURIN_URL = (
        "https://github.com/adoptium/temurin17-binaries/releases/download/"
        "jdk-17.0.14%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.14_7.zip"
    )
    CMDTOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    _DOWNLOAD_TIMEOUT = 600
    _SDKMANAGER_TIMEOUT = 1800.0
    _WINGET_TIMEOUT = 1800.0

    @ActionBase.handle_exceptions("android sdk setup")
    def execute(
        self,
        *_args: Any,
        install_android_studio: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Install the Android toolchain (sync for CLI, background thread for tray)."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        android_dir = h.dev.get_project_root() / "android"
        if not android_dir.is_dir():
            self.add_line(f"❌ android\\ folder not found at {android_dir}")
            if not noninteractive:
                self.show_result()
            return

        want_studio = install_android_studio
        if not noninteractive:
            disabled = [self.STUDIO_CHOICE] if is_android_studio_installed() else []
            selected = self.get_checkbox_selection(
                self.title,
                "JDK 17 and the Android SDK are always installed. Android Studio is optional.",
                [self.STUDIO_CHOICE],
                default_selected=[],
                disabled_choices=disabled,
            )
            if selected is None:
                return
            want_studio = self.STUDIO_CHOICE in selected

        self._android_dir = android_dir
        self._install_android_studio = want_studio
        if noninteractive:
            self.in_thread()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)

    @ActionBase.handle_exceptions("android sdk setup thread")
    def in_thread(self) -> str:
        """Download and configure JDK 17, SDK packages, env vars, and local.properties."""
        android_dir = getattr(self, "_android_dir", None)
        if android_dir is None:
            self.add_line("❌ android\\ folder is not set.")
            return "Done."
        try:
            self._run_setup(android_dir, install_android_studio=bool(getattr(self, "_install_android_studio", False)))
        except DownloadCancelledError:
            self.add_line("❌ Request cancelled by user.")
        except Exception as exc:
            self.add_line(f"❌ Android SDK setup failed: {exc}")
        return "Done."

    @ActionBase.handle_exceptions("android sdk setup thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray setup."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _apply_user_environment(self, java_home: str, sdk_root: Path) -> None:
        """Set user JAVA_HOME / ANDROID_HOME / Path and refresh the process env."""
        self.add_line("🔵 4/6 User environment variables")
        sdk = str(sdk_root)
        set_user_environment_value("JAVA_HOME", java_home)
        set_user_environment_value("ANDROID_HOME", sdk)
        set_user_environment_value("ANDROID_SDK_ROOT", sdk)
        add_user_path_entry(str(Path(java_home) / "bin"))
        add_user_path_entry(str(sdk_root / "platform-tools"))
        add_user_path_entry(str(sdk_root / "emulator"))
        add_user_path_entry(str(sdk_root / "cmdline-tools" / "latest" / "bin"))
        broadcast_user_environment_change()
        self.add_line(f"  JAVA_HOME={java_home}")
        self.add_line(f"  ANDROID_HOME={sdk}")

    def _download(self, url: str, dest: Path) -> None:
        """Download `url` to `dest` with optional GitHub token headers."""
        download_https_to_path(
            url,
            dest,
            headers=github_download_headers(url, config=self.config),
            timeout=self._DOWNLOAD_TIMEOUT,
            should_cancel=self.is_work_cancelled,
        )

    def _ensure_cmdline_tools(self, sdk_root: Path) -> None:
        """Install Android `cmdline-tools/latest` under `sdk_root` when missing."""
        self.add_line("🔵 2/6 Android cmdline-tools")
        sdk_root.mkdir(parents=True, exist_ok=True)
        latest_dir = sdk_root / "cmdline-tools" / "latest"
        sdkmanager = latest_dir / "bin" / "sdkmanager.bat"
        if sdkmanager.is_file():
            self.add_line(f"  Already present: {sdkmanager}")
            return
        self.add_line("  Downloading Android cmdline-tools...")
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_path = tmp_path / "commandlinetools-win.zip"
            self._download(self.CMDTOOLS_URL, zip_path)
            extract_dir = tmp_path / "extract"
            extract_dir.mkdir()
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(extract_dir)
            source = extract_dir / "cmdline-tools"
            if not source.is_dir():
                nested = next(extract_dir.glob("**/sdkmanager.bat"), None)
                if nested is None:
                    msg = "cmdline-tools zip did not contain sdkmanager.bat"
                    raise RuntimeError(msg)
                source = nested.parent.parent
            latest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, latest_dir, dirs_exist_ok=True)
        if not sdkmanager.is_file():
            msg = f"sdkmanager.bat missing at {sdkmanager}"
            raise RuntimeError(msg)
        self.add_line(f"  sdkmanager: {sdkmanager}")

    def _ensure_jdk17(self) -> str:
        """Return a JDK 17 home, downloading portable Temurin when needed."""
        self.add_line("🔵 1/6 JDK 17")
        existing = resolve_java17_home()
        if existing:
            self.add_line(f"  JAVA_HOME: {existing}")
            return existing
        portable = default_portable_jdk_home()
        java_exe = portable / "bin" / "java.exe"
        if not java_exe.is_file():
            self.add_line("  Downloading portable Temurin JDK 17...")
            portable.parent.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory() as tmp:
                zip_path = Path(tmp) / "temurin17.zip"
                self._download(self.TEMURIN_URL, zip_path)
                with zipfile.ZipFile(zip_path) as archive:
                    archive.extractall(portable.parent)
        java_home = str(portable)
        if not java_home_is_version_17(java_home):
            found = next(portable.parent.glob("jdk-17*/bin/java.exe"), None)
            if found is not None:
                java_home = str(found.parent.parent)
        if not java_home_is_version_17(java_home):
            msg = "JDK 17 not available after Temurin install."
            raise RuntimeError(msg)
        self.add_line(f"  JAVA_HOME: {java_home}")
        return java_home

    def _install_android_studio(self) -> None:
        """Install Android Studio with winget when requested and not already present."""
        self.add_line("🔵 6/6 Android Studio (optional)")
        if is_android_studio_installed():
            self.add_line("  Android Studio already installed.")
            return
        winget = shutil.which("winget")
        if winget is None:
            self.add_line("  winget not found; skip Android Studio. Install it later from Microsoft Store.")
            return
        self.add_line("  Installing Android Studio via winget...")
        process = subprocess.run(  # noqa: S603
            [
                winget,
                "install",
                "--id",
                "Google.AndroidStudio",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=self._WINGET_TIMEOUT,
            **windows_no_window_kwargs(),
        )
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)
        if process.returncode != 0 and not is_android_studio_installed():
            self.add_line(f"  Android Studio install failed (winget exit {process.returncode}).")
            return
        self.add_line("  Android Studio installed (or already satisfied).")

    def _install_sdk_packages(self, sdk_root: Path, java_home: str) -> None:
        """Accept licenses and install platform-tools, android-35, and build-tools 35.0.0."""
        self.add_line("🔵 3/6 SDK packages (platform-tools, android-35, build-tools 35.0.0)")
        write_android_sdk_licenses(sdk_root)
        sdkmanager = sdk_root / "cmdline-tools" / "latest" / "bin" / "sdkmanager.bat"
        env = gradle_env(java_home)
        env["ANDROID_HOME"] = str(sdk_root)
        env["ANDROID_SDK_ROOT"] = str(sdk_root)
        process = subprocess.run(  # noqa: S603
            [str(sdkmanager), f"--sdk_root={sdk_root}", *self.SDK_PACKAGES],
            cwd=str(sdk_root),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=self._SDKMANAGER_TIMEOUT,
            **windows_no_window_kwargs(),
        )
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)
        if process.returncode != 0:
            msg = f"sdkmanager failed with exit code {process.returncode}"
            raise RuntimeError(msg)
        self.add_line("  SDK packages OK.")

    def _run_setup(self, android_dir: Path, *, install_android_studio: bool) -> None:
        """Run the full JDK / SDK / env / local.properties setup sequence."""
        java_home = self._ensure_jdk17()
        self.raise_if_work_cancelled()
        sdk_root = default_android_sdk_root()
        self._ensure_cmdline_tools(sdk_root)
        self.raise_if_work_cancelled()
        self._install_sdk_packages(sdk_root, java_home)
        self.raise_if_work_cancelled()
        self._apply_user_environment(java_home, sdk_root)
        self.add_line("🔵 5/6 android/local.properties")
        local_props = write_android_local_properties(android_dir, sdk_root)
        self.add_line(f"  Wrote {local_props}")
        if install_android_studio:
            self._install_android_studio()
        self.add_line("✅ Android toolchain is ready.")
        self.add_line("Restart the app (and terminals) so JAVA_HOME / ANDROID_HOME apply.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, install_android_studio: bool = False, noninteractive: bool = False, **_kwargs: Any) -> None
```

Install the Android toolchain (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        install_android_studio: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        android_dir = h.dev.get_project_root() / "android"
        if not android_dir.is_dir():
            self.add_line(f"❌ android\\ folder not found at {android_dir}")
            if not noninteractive:
                self.show_result()
            return

        want_studio = install_android_studio
        if not noninteractive:
            disabled = [self.STUDIO_CHOICE] if is_android_studio_installed() else []
            selected = self.get_checkbox_selection(
                self.title,
                "JDK 17 and the Android SDK are always installed. Android Studio is optional.",
                [self.STUDIO_CHOICE],
                default_selected=[],
                disabled_choices=disabled,
            )
            if selected is None:
                return
            want_studio = self.STUDIO_CHOICE in selected

        self._android_dir = android_dir
        self._install_android_studio = want_studio
        if noninteractive:
            self.in_thread()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str
```

Download and configure JDK 17, SDK packages, env vars, and local.properties.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str:
        android_dir = getattr(self, "_android_dir", None)
        if android_dir is None:
            self.add_line("❌ android\\ folder is not set.")
            return "Done."
        try:
            self._run_setup(android_dir, install_android_studio=bool(getattr(self, "_install_android_studio", False)))
        except DownloadCancelledError:
            self.add_line("❌ Request cancelled by user.")
        except Exception as exc:
            self.add_line(f"❌ Android SDK setup failed: {exc}")
        return "Done."
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a tray setup.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()
```

</details>
