---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_gradle.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_user_path_entry`](#-function-add_user_path_entry)
- [🔧 Function `android_studio_install_path`](#-function-android_studio_install_path)
- [🔧 Function `broadcast_user_environment_change`](#-function-broadcast_user_environment_change)
- [🔧 Function `default_android_sdk_root`](#-function-default_android_sdk_root)
- [🔧 Function `default_portable_jdk_home`](#-function-default_portable_jdk_home)
- [🔧 Function `find_built_apk`](#-function-find_built_apk)
- [🔧 Function `gradle_env`](#-function-gradle_env)
- [🔧 Function `is_android_project`](#-function-is_android_project)
- [🔧 Function `is_android_studio_installed`](#-function-is_android_studio_installed)
- [🔧 Function `is_java_version_17_output`](#-function-is_java_version_17_output)
- [🔧 Function `java_home_is_version_17`](#-function-java_home_is_version_17)
- [🔧 Function `path_with_user_entry`](#-function-path_with_user_entry)
- [🔧 Function `resolve_android_dir`](#-function-resolve_android_dir)
- [🔧 Function `resolve_android_home`](#-function-resolve_android_home)
- [🔧 Function `resolve_java17_home`](#-function-resolve_java17_home)
- [🔧 Function `resolve_java_home`](#-function-resolve_java_home)
- [🔧 Function `run_gradle`](#-function-run_gradle)
- [🔧 Function `set_user_environment_value`](#-function-set_user_environment_value)
- [🔧 Function `valid_java_home`](#-function-valid_java_home)
- [🔧 Function `windows_env_value`](#-function-windows_env_value)
- [🔧 Function `windows_no_window_kwargs`](#-function-windows_no_window_kwargs)
- [🔧 Function `windows_user_env_value`](#-function-windows_user_env_value)
- [🔧 Function `write_android_local_properties`](#-function-write_android_local_properties)
- [🔧 Function `write_android_sdk_licenses`](#-function-write_android_sdk_licenses)

</details>

## 🔧 Function `add_user_path_entry`

```python
def add_user_path_entry(entry: str) -> None
```

Append `entry` to the user PATH if it is not already present.

<details>
<summary>Code:</summary>

```python
def add_user_path_entry(entry: str) -> None:
    current = windows_user_env_value("Path") or ""
    updated = path_with_user_entry(current, entry)
    if updated != current:
        set_user_environment_value("Path", updated)
    process_path = os.environ.get("PATH") or ""
    os.environ["PATH"] = path_with_user_entry(process_path, entry)
```

</details>

## 🔧 Function `android_studio_install_path`

```python
def android_studio_install_path() -> Path
```

Return the typical Android Studio `studio64.exe` path on Windows.

<details>
<summary>Code:</summary>

```python
def android_studio_install_path() -> Path:
    program_files = os.environ.get("PROGRAMFILES") or r"C:\Program Files"
    return Path(program_files) / "Android" / "Android Studio" / "bin" / "studio64.exe"
```

</details>

## 🔧 Function `broadcast_user_environment_change`

```python
def broadcast_user_environment_change() -> None
```

Notify Windows that user environment variables changed.

<details>
<summary>Code:</summary>

```python
def broadcast_user_environment_change() -> None:
    if ctypes is None:
        return
    hwnd_broadcast = 0xFFFF
    wm_settingchange = 0x001A
    smto_abortifhung = 0x0002
    ctypes.windll.user32.SendMessageTimeoutW(
        hwnd_broadcast,
        wm_settingchange,
        0,
        "Environment",
        smto_abortifhung,
        5000,
        None,
    )
```

</details>

## 🔧 Function `default_android_sdk_root`

```python
def default_android_sdk_root() -> Path
```

Return `%LOCALAPPDATA%\Android\Sdk`.

<details>
<summary>Code:</summary>

```python
def default_android_sdk_root() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk"
```

</details>

## 🔧 Function `default_portable_jdk_home`

```python
def default_portable_jdk_home() -> Path
```

Return the portable Temurin 17 directory under `%LOCALAPPDATA%\Java`.

<details>
<summary>Code:</summary>

```python
def default_portable_jdk_home() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", "")) / "Java" / PORTABLE_TEMURIN_DIR_NAME
```

</details>

## 🔧 Function `find_built_apk`

```python
def find_built_apk(android_dir: Path, variant: str) -> Path | None
```

Return the newest APK under `app/build/outputs/apk/<variant>/`, if any.

Prefers files whose names do not contain `unsigned`.

<details>
<summary>Code:</summary>

```python
def find_built_apk(android_dir: Path, variant: str) -> Path | None:
    out_dir = android_dir / "app" / "build" / "outputs" / "apk" / variant
    if not out_dir.is_dir():
        return None
    apks = [path for path in out_dir.glob("*.apk") if path.is_file()]
    if not apks:
        return None
    preferred = [path for path in apks if "unsigned" not in path.name.lower()]
    candidates = preferred or apks
    return max(candidates, key=lambda path: path.stat().st_mtime)
```

</details>

## 🔧 Function `gradle_env`

```python
def gradle_env(java_home: str) -> dict[str, str]
```

Build process env for Gradle, including JDK and Android SDK paths.

<details>
<summary>Code:</summary>

```python
def gradle_env(java_home: str) -> dict[str, str]:
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
```

</details>

## 🔧 Function `is_android_project`

```python
def is_android_project(path: Path) -> bool
```

Return whether ``path`` looks like an Android Gradle project (``gradlew.bat``).

<details>
<summary>Code:</summary>

```python
def is_android_project(path: Path) -> bool:
    return path.is_dir() and (path / "gradlew.bat").is_file()
```

</details>

## 🔧 Function `is_android_studio_installed`

```python
def is_android_studio_installed() -> bool
```

Return whether Android Studio's Windows executable exists.

<details>
<summary>Code:</summary>

```python
def is_android_studio_installed() -> bool:
    return android_studio_install_path().is_file()
```

</details>

## 🔧 Function `is_java_version_17_output`

```python
def is_java_version_17_output(text: str) -> bool
```

Return whether `java -version` text reports Java 17.

<details>
<summary>Code:</summary>

```python
def is_java_version_17_output(text: str) -> bool:
    return bool(JAVA17_OUTPUT_RE.search(text))
```

</details>

## 🔧 Function `java_home_is_version_17`

```python
def java_home_is_version_17(java_home: str) -> bool
```

Return whether `java_home` contains a Java 17 `java.exe`.

<details>
<summary>Code:</summary>

```python
def java_home_is_version_17(java_home: str) -> bool:
    java_exe = Path(java_home) / "bin" / "java.exe"
    if not java_exe.is_file():
        return False
    try:
        process = subprocess.run(
            [str(java_exe), "-version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=15,
            **windows_no_window_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return is_java_version_17_output(f"{process.stdout}\n{process.stderr}")
```

</details>

## 🔧 Function `path_with_user_entry`

```python
def path_with_user_entry(user_path: str, entry: str) -> str
```

Return `user_path` with `entry` appended when it is not already listed.

<details>
<summary>Code:</summary>

```python
def path_with_user_entry(user_path: str, entry: str) -> str:
    parts = [part for part in user_path.split(";") if part]
    entry_key = entry.rstrip("\\").casefold()
    for part in parts:
        if part.rstrip("\\").casefold() == entry_key:
            return user_path
    if not user_path.strip():
        return entry
    return user_path.rstrip(";") + ";" + entry
```

</details>

## 🔧 Function `resolve_android_dir`

```python
def resolve_android_dir() -> Path | None
```

Return `android/` under the project root if the Gradle wrapper exists.

Deprecated for tray/CLI actions; prefer an explicit folder from
`paths_android_projects` or a CLI argument. Kept for scripts that still
target the HSK tree layout.

<details>
<summary>Code:</summary>

```python
def resolve_android_dir() -> Path | None:
    android_dir = h.dev.get_project_root() / "android"
    if not is_android_project(android_dir):
        return None
    return android_dir
```

</details>

## 🔧 Function `resolve_android_home`

```python
def resolve_android_home() -> str | None
```

Resolve Android SDK root from env or the default user Sdk folder.

<details>
<summary>Code:</summary>

```python
def resolve_android_home() -> str | None:
    for value in (
        os.environ.get("ANDROID_HOME"),
        os.environ.get("ANDROID_SDK_ROOT"),
        windows_env_value("ANDROID_HOME"),
        windows_env_value("ANDROID_SDK_ROOT"),
    ):
        if value and Path(value).is_dir():
            return value

    default_sdk = default_android_sdk_root()
    if default_sdk.is_dir():
        return str(default_sdk)
    return None
```

</details>

## 🔧 Function `resolve_java17_home`

```python
def resolve_java17_home() -> str | None
```

Resolve a JDK 17 home from env or known install paths.

<details>
<summary>Code:</summary>

```python
def resolve_java17_home() -> str | None:
    for candidate in _java_home_candidates():
        java_home = valid_java_home(candidate)
        if java_home is not None and java_home_is_version_17(java_home):
            return java_home
    return None
```

</details>

## 🔧 Function `resolve_java_home`

```python
def resolve_java_home() -> str | None
```

Resolve JDK home from process/user/machine env or known install paths.

<details>
<summary>Code:</summary>

```python
def resolve_java_home() -> str | None:
    for candidate in _java_home_candidates():
        java_home = valid_java_home(candidate)
        if java_home is not None:
            return java_home
    return None
```

</details>

## 🔧 Function `run_gradle`

```python
def run_gradle(android_dir: Path, java_home: str, *tasks: str, timeout: float | None = 1800.0) -> subprocess.CompletedProcess[str]
```

Run one or more Gradle tasks via ``gradlew.bat --no-daemon``.

<details>
<summary>Code:</summary>

```python
def run_gradle(
    android_dir: Path,
    java_home: str,
    *tasks: str,
    timeout: float | None = 1800.0,
) -> subprocess.CompletedProcess[str]:
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
        timeout=timeout,
        **windows_no_window_kwargs(),
    )
```

</details>

## 🔧 Function `set_user_environment_value`

```python
def set_user_environment_value(name: str, value: str) -> None
```

Set a user-level environment variable and the current process env.

<details>
<summary>Code:</summary>

```python
def set_user_environment_value(name: str, value: str) -> None:
    if winreg is None:
        msg = "User environment variables can be set only on Windows."
        raise RuntimeError(msg)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    os.environ[name] = value
```

</details>

## 🔧 Function `valid_java_home`

```python
def valid_java_home(path: str) -> str | None
```

Return path if it looks like a usable JDK/JBR home.

<details>
<summary>Code:</summary>

```python
def valid_java_home(path: str) -> str | None:
    root = Path(path.strip().strip('"'))
    if (root / "bin" / "java.exe").is_file():
        return str(root)
    return None
```

</details>

## 🔧 Function `windows_env_value`

```python
def windows_env_value(name: str) -> str | None
```

Read a persistent Windows environment variable (User, then Machine).

<details>
<summary>Code:</summary>

```python
def windows_env_value(name: str) -> str | None:
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
```

</details>

## 🔧 Function `windows_no_window_kwargs`

```python
def windows_no_window_kwargs() -> dict[str, Any]
```

Return subprocess kwargs that hide a console window on Windows.

<details>
<summary>Code:</summary>

```python
def windows_no_window_kwargs() -> dict[str, Any]:
    if sys.platform != "win32":
        return {}
    return {"creationflags": subprocess.CREATE_NO_WINDOW}
```

</details>

## 🔧 Function `windows_user_env_value`

```python
def windows_user_env_value(name: str) -> str | None
```

Read a persistent user environment variable (`HKCU\Environment`).

<details>
<summary>Code:</summary>

```python
def windows_user_env_value(name: str) -> str | None:
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
    except OSError:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
```

</details>

## 🔧 Function `write_android_local_properties`

```python
def write_android_local_properties(android_dir: Path, sdk_root: Path) -> Path
```

Write `sdk.dir=...` into `android_dir/local.properties` (Gradle format).

<details>
<summary>Code:</summary>

```python
def write_android_local_properties(android_dir: Path, sdk_root: Path) -> Path:
    sdk_dir = str(sdk_root.resolve()).replace("\\", "\\\\")
    path = android_dir / "local.properties"
    path.write_text(f"sdk.dir={sdk_dir}\n", encoding="ascii", newline="\n")
    return path
```

</details>

## 🔧 Function `write_android_sdk_licenses`

```python
def write_android_sdk_licenses(sdk_root: Path) -> None
```

Write standard Android SDK license hashes under `sdk_root/licenses`.

<details>
<summary>Code:</summary>

```python
def write_android_sdk_licenses(sdk_root: Path) -> None:
    licenses_dir = sdk_root / "licenses"
    licenses_dir.mkdir(parents=True, exist_ok=True)
    (licenses_dir / "android-sdk-license").write_text(SDK_LICENSE_HASH, encoding="ascii", newline="")
    (licenses_dir / "android-sdk-preview-license").write_text(SDK_PREVIEW_LICENSE_HASH, encoding="ascii", newline="")
```

</details>
