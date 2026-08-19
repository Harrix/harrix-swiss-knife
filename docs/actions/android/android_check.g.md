---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_check.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAndroidCheck`](#%EF%B8%8F-class-onandroidcheck)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnAndroidCheck`

```python
class OnAndroidCheck(ActionBase)
```

Run Android quality checks (`qualityCheck`) on a selected project.

Runs Spotless check, Detekt (with Compose rules), and `lintDebug`. The tray
dialog lists folders from `paths_android_projects` in `config.json` (or
browse). CLI passes the project folder. Requires Windows, JDK 17, and
Android SDK. Prefer `hsk android format` first to auto-fix formatting
issues.

<details>
<summary>Code:</summary>

```python
class OnAndroidCheck(ActionBase):

    icon = "🔬"
    title = "Check Android code in …"
    cli_available = True
    cli_hint = "android check"

    @ActionBase.handle_exceptions("android check")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Run qualityCheck (sync for CLI, background thread for tray)."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            android_dir = Path(folder_path).resolve()
        else:
            android_dir = self.dialogs.get_folder_with_choice_option(
                self.config["paths_android_projects"], self.config["path_github"]
            )
        if not android_dir:
            return

        if not is_android_project(android_dir):
            self.add_line(f"❌ {android_dir} is not an Android project (no gradlew.bat)")
            if not noninteractive:
                self.show_result()
            return

        local_props = android_dir / "local.properties"
        if not local_props.is_file() and not resolve_android_home():
            self.add_line(
                f"❌ Android SDK not configured. {ANDROID_SDK_SETUP_HINT} "
                "Or set ANDROID_HOME and create local.properties in the project."
            )
            if not noninteractive:
                self.show_result()
            return

        java_home = resolve_java_home()
        if java_home is None:
            self.add_line(
                f"❌ JAVA_HOME is not set and no JDK 17 was found. {ANDROID_SDK_SETUP_HINT} Then restart the app."
            )
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self._run_quality_check(android_dir, java_home)
            return

        self.folder_path = android_dir
        self._java_home = java_home
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("android check thread")
    def in_thread(self) -> str | None:
        """Run qualityCheck in a worker thread for the tray UI."""
        android_dir = getattr(self, "folder_path", None)
        java_home = getattr(self, "_java_home", None)
        if android_dir is None or not java_home:
            return None
        self._run_quality_check(android_dir, java_home)
        return None

    @ActionBase.handle_exceptions("android check thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray check."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _run_quality_check(self, android_dir: Path, java_home: str) -> None:
        """Invoke ``qualityCheck`` and append output lines."""
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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, folder_path: Path | None = None, noninteractive: bool = False, **_kwargs: Any) -> None
```

Run qualityCheck (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            android_dir = Path(folder_path).resolve()
        else:
            android_dir = self.dialogs.get_folder_with_choice_option(
                self.config["paths_android_projects"], self.config["path_github"]
            )
        if not android_dir:
            return

        if not is_android_project(android_dir):
            self.add_line(f"❌ {android_dir} is not an Android project (no gradlew.bat)")
            if not noninteractive:
                self.show_result()
            return

        local_props = android_dir / "local.properties"
        if not local_props.is_file() and not resolve_android_home():
            self.add_line(
                f"❌ Android SDK not configured. {ANDROID_SDK_SETUP_HINT} "
                "Or set ANDROID_HOME and create local.properties in the project."
            )
            if not noninteractive:
                self.show_result()
            return

        java_home = resolve_java_home()
        if java_home is None:
            self.add_line(
                f"❌ JAVA_HOME is not set and no JDK 17 was found. {ANDROID_SDK_SETUP_HINT} Then restart the app."
            )
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self._run_quality_check(android_dir, java_home)
            return

        self.folder_path = android_dir
        self._java_home = java_home
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Run qualityCheck in a worker thread for the tray UI.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        android_dir = getattr(self, "folder_path", None)
        java_home = getattr(self, "_java_home", None)
        if android_dir is None or not java_home:
            return None
        self._run_quality_check(android_dir, java_home)
        return None
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a tray check.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()
```

</details>
