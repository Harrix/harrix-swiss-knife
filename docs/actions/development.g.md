---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `development.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAboutDialog`](#%EF%B8%8F-class-onaboutdialog)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_get_version_from_pyproject`](#%EF%B8%8F-method-_get_version_from_pyproject)
- [🏛️ Class `OnDownloadOptimizeDependencies`](#%EF%B8%8F-class-ondownloadoptimizedependencies)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
  - [⚙️ Method `_download_to_path`](#%EF%B8%8F-method-_download_to_path)
  - [⚙️ Method `_extract_exe_from_zip`](#%EF%B8%8F-method-_extract_exe_from_zip)
  - [⚙️ Method `_fetch_release_latest`](#%EF%B8%8F-method-_fetch_release_latest)
  - [⚙️ Method `_get_asset_download_url`](#%EF%B8%8F-method-_get_asset_download_url)
  - [⚙️ Method `_github_api_headers`](#%EF%B8%8F-method-_github_api_headers)
  - [⚙️ Method `_in_thread`](#%EF%B8%8F-method-_in_thread)
  - [⚙️ Method `_thread_after`](#%EF%B8%8F-method-_thread_after)
  - [⚙️ Method `_validate_https_url`](#%EF%B8%8F-method-_validate_https_url)
- [🏛️ Class `OnExit`](#%EF%B8%8F-class-onexit)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
- [🏛️ Class `OnNodeUpdate`](#%EF%B8%8F-class-onnodeupdate)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnNpmManagePackages`](#%EF%B8%8F-class-onnpmmanagepackages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)
- [🏛️ Class `OnOpenConfigJson`](#%EF%B8%8F-class-onopenconfigjson)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-5)
- [🏛️ Class `OnUvUpdate`](#%EF%B8%8F-class-onuvupdate)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-6)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-2)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-2)

</details>

## 🏛️ Class `OnAboutDialog`

```python
class OnAboutDialog(ActionBase)
```

Show the about dialog with program information.

This action displays a dialog window containing information about the application,
including version, description, author, and license information.

<details>
<summary>Code:</summary>

```python
class OnAboutDialog(ActionBase):

    icon = "ℹ️"  # noqa: RUF001
    title = "About"
    show_in_compact_mode = True

    @ActionBase.handle_exceptions("about dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        version = self._get_version_from_pyproject()

        about_info = self.show_about_dialog(
            title="About",
            app_name="Harrix Swiss Knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")

    def _get_version_from_pyproject(self) -> str:
        """Get version from pyproject.toml file.

        Returns:

        - `str`: Version string from `pyproject.toml`, or "Unknown" if not found.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        version = self._get_version_from_pyproject()

        about_info = self.show_about_dialog(
            title="About",
            app_name="Harrix Swiss Knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")
```

</details>

### ⚙️ Method `_get_version_from_pyproject`

```python
def _get_version_from_pyproject(self) -> str
```

Get version from pyproject.toml file.

Returns:

- `str`: Version string from `pyproject.toml`, or "Unknown" if not found.

<details>
<summary>Code:</summary>

```python
def _get_version_from_pyproject(self) -> str:
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"
```

</details>

## 🏛️ Class `OnDownloadOptimizeDependencies`

```python
class OnDownloadOptimizeDependencies(ActionBase)
```

Download ffmpeg.exe, avifenc.exe, avifdec.exe from official GitHub releases.

Fetches the latest Windows builds from AOMediaCodec/libavif and BtbN/FFmpeg-Builds,
extracts the executables to the project root for use by Optimize (optimize.js).
Requires Windows. Uses only standard library; optional GITHUB_TOKEN for API rate limits.

<details>
<summary>Code:</summary>

```python
class OnDownloadOptimizeDependencies(ActionBase):

    icon = "⬇️"
    title = "Download ffmpeg, avifenc, avifdec"

    # User-Agent for GitHub API (required)
    _GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; urllib)"
    # Chunk size for streaming download
    _DOWNLOAD_CHUNK = 256 * 1024
    _HTTP_FORBIDDEN = 403
    _ALLOWED_URL_SCHEMES = ("https",)

    @ActionBase.handle_exceptions("download Optimize dependencies")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return
        self.start_thread(self._in_thread, self._thread_after, self.title)

    def _download_to_path(self, url: str, dest: Path) -> None:
        """Download URL to dest path, following redirects. Raises on error."""
        self._validate_https_url(url)
        req = Request(url, headers={"User-Agent": self._GITHUB_UA})  # noqa: S310
        with urlopen(req, timeout=120) as resp, dest.open("wb") as f:  # noqa: S310
            while True:
                chunk = resp.read(self._DOWNLOAD_CHUNK)
                if not chunk:
                    break
                f.write(chunk)

    def _extract_exe_from_zip(
        self, zip_path: Path, dest_dir: Path, exe_name: str, archive_inner_path: str | None = None
    ) -> Path | None:
        """Extract a single exe from zip. If archive_inner_path given, use it; else find by exe name in namelist().

        Returns dest file path or None.
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            if archive_inner_path and archive_inner_path in zf.namelist():
                zf.extract(archive_inner_path, dest_dir)
                extracted = dest_dir / archive_inner_path
                if extracted != dest_dir / exe_name:
                    shutil.move(str(extracted), str(dest_dir / exe_name))
                return dest_dir / exe_name
            for name in zf.namelist():
                if name.replace("\\", "/").rstrip("/").endswith(exe_name):
                    zf.extract(name, dest_dir)
                    extracted = dest_dir / name
                    target = dest_dir / exe_name
                    if extracted.resolve() != target.resolve():
                        shutil.move(str(extracted), str(target))
                    # Remove empty parent dirs if any
                    for part in Path(name).parents:
                        if part != Path():
                            d = dest_dir / part
                            if d.exists() and d.is_dir() and not any(d.iterdir()):
                                d.rmdir()
                    return target
        return None

    def _fetch_release_latest(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch latest release info from GitHub API. Raises on error."""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        self._validate_https_url(url)
        req = Request(url, headers=self._github_api_headers())  # noqa: S310
        with urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode())

    def _get_asset_download_url(
        self, release: dict[str, Any], asset_name: str | None = None, name_contains: tuple[str, ...] = ()
    ) -> str:
        """Get browser_download_url for an asset by exact name or by substrings. Raises if not found."""
        assets = release.get("assets") or []
        if asset_name:
            for a in assets:
                if a.get("name") == asset_name:
                    return a["browser_download_url"]
            msg = f"Asset '{asset_name}' not found in release"
            raise ValueError(msg)
        for a in assets:
            name = a.get("name") or ""
            if all(s in name for s in name_contains) and "shared" not in name.lower() and name.endswith(".zip"):
                return a["browser_download_url"]
        msg = f"No asset matching {name_contains} found in release"
        raise ValueError(msg)

    def _github_api_headers(self) -> dict[str, str]:
        """Build headers for GitHub API requests, optionally with token."""
        headers = {"Accept": "application/vnd.github+json", "User-Agent": self._GITHUB_UA}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @ActionBase.handle_exceptions("download dependencies thread")
    def _in_thread(self) -> str:
        """Run download and extract in a separate thread."""
        dest_dir = h.dev.get_project_root()
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            try:
                # --- libavif: avifenc.exe, avifdec.exe ---
                self.add_line("Fetching libavif latest release...")
                release = self._fetch_release_latest("AOMediaCodec", "libavif")
                url = self._get_asset_download_url(release, asset_name="windows-artifacts.zip")
                self.add_line("Downloading windows-artifacts.zip...")
                zip_path = tmp_path / "libavif.zip"
                self._download_to_path(url, zip_path)
                for exe_name in ("avifenc.exe", "avifdec.exe"):
                    exe_path = self._extract_exe_from_zip(zip_path, dest_dir, exe_name)
                    if exe_path:
                        self.add_line(f"  Extracted {exe_name} -> {exe_path}")
                    else:
                        self.add_line(f"  Warning: {exe_name} not found in archive")
                # --- FFmpeg: ffmpeg.exe ---
                self.add_line("Fetching FFmpeg-Builds latest release...")
                release = self._fetch_release_latest("BtbN", "FFmpeg-Builds")
                try:
                    url = self._get_asset_download_url(release, asset_name="ffmpeg-master-latest-win64-gpl.zip")
                except ValueError:
                    url = self._get_asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
                self.add_line("Downloading FFmpeg zip...")
                zip_path = tmp_path / "ffmpeg.zip"
                self._download_to_path(url, zip_path)
                exe_path = self._extract_exe_from_zip(zip_path, dest_dir, "ffmpeg.exe")
                if exe_path:
                    self.add_line(f"  Extracted ffmpeg.exe -> {exe_path}")
                else:
                    self.add_line("  Warning: ffmpeg.exe not found in archive")
            except HTTPError as e:
                self.add_line(f"HTTP error: {e.code} {e.reason}")
                if e.code == self._HTTP_FORBIDDEN:
                    self.add_line("If rate limited, set GITHUB_TOKEN environment variable.")
            except URLError as e:
                self.add_line(f"Network error: {e.reason}")
            except ValueError as e:
                self.add_line(f"Error: {e}")
            except OSError as e:
                self.add_line(f"IO/OS error: {e}")

        return "Done."

    @ActionBase.handle_exceptions("download dependencies thread completion")
    def _thread_after(self, result: Any) -> None:
        """Show result in main thread."""
        self.show_toast("Download Optimize dependencies completed")
        self.add_line(result)
        self.show_result()

    def _validate_https_url(self, url: str) -> None:
        """Raise ValueError if URL scheme is not in allowed list (https only)."""
        scheme = urlparse(url).scheme
        if scheme not in self._ALLOWED_URL_SCHEMES:
            msg = f"URL scheme must be one of {self._ALLOWED_URL_SCHEMES}"
            raise ValueError(msg)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return
        self.start_thread(self._in_thread, self._thread_after, self.title)
```

</details>

### ⚙️ Method `_download_to_path`

```python
def _download_to_path(self, url: str, dest: Path) -> None
```

Download URL to dest path, following redirects. Raises on error.

<details>
<summary>Code:</summary>

```python
def _download_to_path(self, url: str, dest: Path) -> None:
        self._validate_https_url(url)
        req = Request(url, headers={"User-Agent": self._GITHUB_UA})  # noqa: S310
        with urlopen(req, timeout=120) as resp, dest.open("wb") as f:  # noqa: S310
            while True:
                chunk = resp.read(self._DOWNLOAD_CHUNK)
                if not chunk:
                    break
                f.write(chunk)
```

</details>

### ⚙️ Method `_extract_exe_from_zip`

```python
def _extract_exe_from_zip(self, zip_path: Path, dest_dir: Path, exe_name: str, archive_inner_path: str | None = None) -> Path | None
```

Extract a single exe from zip. If archive_inner_path given, use it; else find by exe name in namelist().

Returns dest file path or None.

<details>
<summary>Code:</summary>

```python
def _extract_exe_from_zip(
        self, zip_path: Path, dest_dir: Path, exe_name: str, archive_inner_path: str | None = None
    ) -> Path | None:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if archive_inner_path and archive_inner_path in zf.namelist():
                zf.extract(archive_inner_path, dest_dir)
                extracted = dest_dir / archive_inner_path
                if extracted != dest_dir / exe_name:
                    shutil.move(str(extracted), str(dest_dir / exe_name))
                return dest_dir / exe_name
            for name in zf.namelist():
                if name.replace("\\", "/").rstrip("/").endswith(exe_name):
                    zf.extract(name, dest_dir)
                    extracted = dest_dir / name
                    target = dest_dir / exe_name
                    if extracted.resolve() != target.resolve():
                        shutil.move(str(extracted), str(target))
                    # Remove empty parent dirs if any
                    for part in Path(name).parents:
                        if part != Path():
                            d = dest_dir / part
                            if d.exists() and d.is_dir() and not any(d.iterdir()):
                                d.rmdir()
                    return target
        return None
```

</details>

### ⚙️ Method `_fetch_release_latest`

```python
def _fetch_release_latest(self, owner: str, repo: str) -> dict[str, Any]
```

Fetch latest release info from GitHub API. Raises on error.

<details>
<summary>Code:</summary>

```python
def _fetch_release_latest(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        self._validate_https_url(url)
        req = Request(url, headers=self._github_api_headers())  # noqa: S310
        with urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
```

</details>

### ⚙️ Method `_get_asset_download_url`

```python
def _get_asset_download_url(self, release: dict[str, Any], asset_name: str | None = None, name_contains: tuple[str, ...] = ()) -> str
```

Get browser_download_url for an asset by exact name or by substrings. Raises if not found.

<details>
<summary>Code:</summary>

```python
def _get_asset_download_url(
        self, release: dict[str, Any], asset_name: str | None = None, name_contains: tuple[str, ...] = ()
    ) -> str:
        assets = release.get("assets") or []
        if asset_name:
            for a in assets:
                if a.get("name") == asset_name:
                    return a["browser_download_url"]
            msg = f"Asset '{asset_name}' not found in release"
            raise ValueError(msg)
        for a in assets:
            name = a.get("name") or ""
            if all(s in name for s in name_contains) and "shared" not in name.lower() and name.endswith(".zip"):
                return a["browser_download_url"]
        msg = f"No asset matching {name_contains} found in release"
        raise ValueError(msg)
```

</details>

### ⚙️ Method `_github_api_headers`

```python
def _github_api_headers(self) -> dict[str, str]
```

Build headers for GitHub API requests, optionally with token.

<details>
<summary>Code:</summary>

```python
def _github_api_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": self._GITHUB_UA}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
```

</details>

### ⚙️ Method `_in_thread`

```python
def _in_thread(self) -> str
```

Run download and extract in a separate thread.

<details>
<summary>Code:</summary>

```python
def _in_thread(self) -> str:
        dest_dir = h.dev.get_project_root()
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            try:
                # --- libavif: avifenc.exe, avifdec.exe ---
                self.add_line("Fetching libavif latest release...")
                release = self._fetch_release_latest("AOMediaCodec", "libavif")
                url = self._get_asset_download_url(release, asset_name="windows-artifacts.zip")
                self.add_line("Downloading windows-artifacts.zip...")
                zip_path = tmp_path / "libavif.zip"
                self._download_to_path(url, zip_path)
                for exe_name in ("avifenc.exe", "avifdec.exe"):
                    exe_path = self._extract_exe_from_zip(zip_path, dest_dir, exe_name)
                    if exe_path:
                        self.add_line(f"  Extracted {exe_name} -> {exe_path}")
                    else:
                        self.add_line(f"  Warning: {exe_name} not found in archive")
                # --- FFmpeg: ffmpeg.exe ---
                self.add_line("Fetching FFmpeg-Builds latest release...")
                release = self._fetch_release_latest("BtbN", "FFmpeg-Builds")
                try:
                    url = self._get_asset_download_url(release, asset_name="ffmpeg-master-latest-win64-gpl.zip")
                except ValueError:
                    url = self._get_asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
                self.add_line("Downloading FFmpeg zip...")
                zip_path = tmp_path / "ffmpeg.zip"
                self._download_to_path(url, zip_path)
                exe_path = self._extract_exe_from_zip(zip_path, dest_dir, "ffmpeg.exe")
                if exe_path:
                    self.add_line(f"  Extracted ffmpeg.exe -> {exe_path}")
                else:
                    self.add_line("  Warning: ffmpeg.exe not found in archive")
            except HTTPError as e:
                self.add_line(f"HTTP error: {e.code} {e.reason}")
                if e.code == self._HTTP_FORBIDDEN:
                    self.add_line("If rate limited, set GITHUB_TOKEN environment variable.")
            except URLError as e:
                self.add_line(f"Network error: {e.reason}")
            except ValueError as e:
                self.add_line(f"Error: {e}")
            except OSError as e:
                self.add_line(f"IO/OS error: {e}")

        return "Done."
```

</details>

### ⚙️ Method `_thread_after`

```python
def _thread_after(self, result: Any) -> None
```

Show result in main thread.

<details>
<summary>Code:</summary>

```python
def _thread_after(self, result: Any) -> None:
        self.show_toast("Download Optimize dependencies completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `_validate_https_url`

```python
def _validate_https_url(self, url: str) -> None
```

Raise ValueError if URL scheme is not in allowed list (https only).

<details>
<summary>Code:</summary>

```python
def _validate_https_url(self, url: str) -> None:
        scheme = urlparse(url).scheme
        if scheme not in self._ALLOWED_URL_SCHEMES:
            msg = f"URL scheme must be one of {self._ALLOWED_URL_SCHEMES}"
            raise ValueError(msg)
```

</details>

## 🏛️ Class `OnExit`

```python
class OnExit(ActionBase)
```

Exit the application.

This action terminates the current Qt application instance,
closing all windows and ending the program execution.

<details>
<summary>Code:</summary>

```python
class OnExit(ActionBase):

    icon = "×"  # noqa: RUF001
    title = "Exit"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        QApplication.quit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnExit action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__()
        self.parent = kwargs.get("parent")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        QApplication.quit()
```

</details>

## 🏛️ Class `OnNodeUpdate`

```python
class OnNodeUpdate(ActionBase)
```

Update Node.js to the latest version via winget.

This action upgrades OpenJS.NodeJS using the Windows Package Manager (winget)
command 'winget upgrade OpenJS.NodeJS'. Available only on Windows.

<details>
<summary>Code:</summary>

```python
class OnNodeUpdate(ActionBase):

    icon = "📥"
    title = "Update Node.js"

    @ActionBase.handle_exceptions("Node.js update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Node.js update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return h.dev.run_command("winget upgrade OpenJS.NodeJS")

    @ActionBase.handle_exceptions("Node.js update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return h.dev.run_command("winget upgrade OpenJS.NodeJS")
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnNpmManagePackages`

```python
class OnNpmManagePackages(ActionBase)
```

Install or update configured NPM packages globally.

This action manages NPM packages specified in the `config["npm_packages"]` list:

1. Updates NPM itself to the latest version
2. Installs/updates all configured packages (npm install will update if already exists)
3. Runs global update to ensure all packages are at latest versions

This ensures all configured packages are present and up-to-date in the system.

<details>
<summary>Code:</summary>

```python
class OnNpmManagePackages(ActionBase):

    icon = "📦"
    title = "Update/Install global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnOpenConfigJson`

```python
class OnOpenConfigJson(ActionBase)
```

Open the application's configuration file.

This action opens the `config.json` file in the configured editor,
allowing direct viewing and editing of the application's settings
and configuration parameters.

<details>
<summary>Code:</summary>

```python
class OnOpenConfigJson(ActionBase):

    icon = "⚙️"
    title = "Open config.json"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)
```

</details>

## 🏛️ Class `OnUvUpdate`

```python
class OnUvUpdate(ActionBase)
```

Update uv package manager to its latest version.

This action updates the uv Python package manager to its latest version
using the 'uv self update' command, ensuring the development environment
has the most current version of this package management tool.

<details>
<summary>Code:</summary>

```python
class OnUvUpdate(ActionBase):

    icon = "📥"
    title = "Update uv"

    @ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_command(commands)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        commands = "uv self update"
        return h.dev.run_command(commands)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

</details>
