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

</details>

## 🏛️ Class `OnAndroidBuild`

```python
class OnAndroidBuild(ActionBase)
```

Build HSK Android APK (`assembleDebug` or `assembleRelease`).

Tray: asks Debug vs Release, then runs Gradle. CLI: pass `debug` or
`release`. Requires Windows, JDK 17, and Android SDK (`ANDROID_HOME` /
`android/local.properties`). Use `install/setup-android-sdk.bat` once
to install the toolchain.

<details>
<summary>Code:</summary>

```python
class OnAndroidBuild(ActionBase):

    icon = "📱"
    title = "Build Android APK…"
    cli_available = True
    cli_hint = "dev android-build <debug|release>"

    VARIANT_DEBUG: ClassVar[str] = "Debug"
    VARIANT_RELEASE: ClassVar[str] = "Release (unsigned)"
    CLI_VARIANTS: ClassVar[tuple[str, ...]] = ("debug", "release")

    _VARIANT_CONFIG: ClassVar[dict[str, tuple[str, str]]] = {
        "debug": ("assembleDebug", "app/build/outputs/apk/debug/app-debug.apk"),
        "release": ("assembleRelease", "app/build/outputs/apk/release/app-release-unsigned.apk"),
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
            self.show_result()
            return

        resolved = self._resolve_variant(variant=variant, noninteractive=noninteractive)
        if resolved is None:
            return

        gradle_task, apk_relative = resolved
        android_dir = self._android_dir()
        if android_dir is None:
            self.show_result()
            return

        self._gradle_task = gradle_task
        self._apk_relative = apk_relative

        if noninteractive:
            self.add_line(f"🔵 Starting {gradle_task} in {android_dir}")
            self._run_gradle_build(android_dir, gradle_task, apk_relative)
            return

        self._android_dir_for_thread = android_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Android APK build thread")
    def in_thread(self) -> str | None:
        """Run Gradle in a worker thread for the tray UI."""
        android_dir = getattr(self, "_android_dir_for_thread", None)
        if android_dir is None:
            return None
        self._run_gradle_build(
            android_dir,
            getattr(self, "_gradle_task", "assembleDebug"),
            getattr(self, "_apk_relative", "app/build/outputs/apk/debug/app-debug.apk"),
        )
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

    def _resolve_variant(
        self,
        *,
        variant: str | None,
        noninteractive: bool,
    ) -> tuple[str, str] | None:
        """Map CLI/tray choice to Gradle task and APK path, or cancel."""
        key: str | None = None
        if variant is not None:
            key = str(variant).strip().lower()
        elif noninteractive:
            self.add_line("❌ variant is required when noninteractive is True (debug|release).")
            return None
        else:
            choice = self.get_choice_from_list(
                self.title,
                "Choose APK build variant:",
                [self.VARIANT_DEBUG, self.VARIANT_RELEASE],
            )
            if choice is None:
                return None
            if choice == self.VARIANT_DEBUG:
                key = "debug"
            elif choice == self.VARIANT_RELEASE:
                key = "release"
            else:
                self.add_line(f"❌ Unknown choice: {choice}")
                self.show_result()
                return None

        config = self._VARIANT_CONFIG.get(key or "")
        if config is None:
            supported = ", ".join(self.CLI_VARIANTS)
            self.add_line(f"❌ Unknown variant: {variant!r}. Use: {supported}")
            self.show_result()
            return None
        return config

    def _run_gradle_build(self, android_dir: Path, gradle_task: str, apk_relative: str) -> None:
        """Invoke Gradle and report the APK path or failure."""
        gradlew = android_dir / "gradlew.bat"
        cmd = f'"{gradlew}" {gradle_task} --no-daemon'
        self.add_line(f"$ cd {android_dir}")
        self.add_line(f"$ {cmd}")
        result = h.dev.run_command(cmd, cwd=str(android_dir))
        if result:
            self.add_line(result)

        apk_path = android_dir / apk_relative
        failed = "BUILD FAILED" in (result or "") or "FAILURE:" in (result or "")
        if failed or not apk_path.is_file():
            self.add_line(f"❌ {gradle_task} failed (APK missing or build error).")
            self.add_line("Hint: run install\\setup-android-sdk.bat if the SDK is not installed.")
            return

        self.add_line(f"✅ APK: {apk_path}")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Build the Android APK (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        variant: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            self.show_result()
            return

        resolved = self._resolve_variant(variant=variant, noninteractive=noninteractive)
        if resolved is None:
            return

        gradle_task, apk_relative = resolved
        android_dir = self._android_dir()
        if android_dir is None:
            self.show_result()
            return

        self._gradle_task = gradle_task
        self._apk_relative = apk_relative

        if noninteractive:
            self.add_line(f"🔵 Starting {gradle_task} in {android_dir}")
            self._run_gradle_build(android_dir, gradle_task, apk_relative)
            return

        self._android_dir_for_thread = android_dir
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
        android_dir = getattr(self, "_android_dir_for_thread", None)
        if android_dir is None:
            return None
        self._run_gradle_build(
            android_dir,
            getattr(self, "_gradle_task", "assembleDebug"),
            getattr(self, "_apk_relative", "app/build/outputs/apk/debug/app-debug.apk"),
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
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
