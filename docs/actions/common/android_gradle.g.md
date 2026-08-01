---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `android_gradle.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `find_built_apk`](#-function-find_built_apk)
- [🔧 Function `gradle_env`](#-function-gradle_env)
- [🔧 Function `is_android_project`](#-function-is_android_project)
- [🔧 Function `resolve_android_dir`](#-function-resolve_android_dir)
- [🔧 Function `resolve_android_home`](#-function-resolve_android_home)
- [🔧 Function `resolve_java_home`](#-function-resolve_java_home)
- [🔧 Function `run_gradle`](#-function-run_gradle)
- [🔧 Function `valid_java_home`](#-function-valid_java_home)
- [🔧 Function `windows_env_value`](#-function-windows_env_value)

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

    default_sdk = Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk"
    if default_sdk.is_dir():
        return str(default_sdk)
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
```

</details>

## 🔧 Function `run_gradle`

```python
def run_gradle(android_dir: Path, java_home: str, *tasks: str) -> subprocess.CompletedProcess[str]
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
    )
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
