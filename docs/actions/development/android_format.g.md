---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAndroidFormat`](#%EF%B8%8F-class-onandroidformat)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnAndroidFormat`

```python
class OnAndroidFormat(ActionBase)
```

Run Spotless apply on the Android project (`spotlessApply`).

Formats Kotlin and Gradle Kotlin DSL under `android/` with ktlint via
Spotless. Requires Windows, JDK 17, and Android SDK for Gradle to resolve
the project (same toolchain as APK builds).

<details>
<summary>Code:</summary>

```python
class OnAndroidFormat(ActionBase):

    icon = "✨"
    title = "Format Android code"
    cli_available = True
    cli_hint = "android format"

    @ActionBase.handle_exceptions("Android format")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Apply Spotless formatting (sync for CLI, background thread for tray)."""
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

        if noninteractive:
            self._run_spotless(android_dir, java_home)
            return

        self._android_dir_for_thread = android_dir
        self._java_home = java_home
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Android format thread")
    def in_thread(self) -> str | None:
        """Run Spotless in a worker thread for the tray UI."""
        android_dir = getattr(self, "_android_dir_for_thread", None)
        java_home = getattr(self, "_java_home", None)
        if android_dir is None or not java_home:
            return None
        self._run_spotless(android_dir, java_home)
        return None

    @ActionBase.handle_exceptions("Android format thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray format."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _run_spotless(self, android_dir: Path, java_home: str) -> None:
        """Invoke ``spotlessApply`` and append output lines."""
        self.add_line(f"🔵 Starting spotlessApply in {android_dir}")
        self.add_line(f"$ JAVA_HOME={java_home}")
        gradlew = android_dir / "gradlew.bat"
        self.add_line(f'$ "{gradlew}" spotlessApply --no-daemon')

        process = run_gradle(android_dir, java_home, "spotlessApply")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ spotlessApply failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ spotlessApply completed.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Apply Spotless formatting (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
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

        if noninteractive:
            self._run_spotless(android_dir, java_home)
            return

        self._android_dir_for_thread = android_dir
        self._java_home = java_home
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Run Spotless in a worker thread for the tray UI.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        android_dir = getattr(self, "_android_dir_for_thread", None)
        java_home = getattr(self, "_java_home", None)
        if android_dir is None or not java_home:
            return None
        self._run_spotless(android_dir, java_home)
        return None
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a tray format.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()
```

</details>
