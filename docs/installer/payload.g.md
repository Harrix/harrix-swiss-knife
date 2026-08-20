---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `payload.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `append_overlay_zip`](#-function-append_overlay_zip)
- [🔧 Function `create_work_dir`](#-function-create_work_dir)
- [🔧 Function `extract_overlay`](#-function-extract_overlay)
- [🔧 Function `frozen_executable`](#-function-frozen_executable)
- [🔧 Function `is_frozen`](#-function-is_frozen)
- [🔧 Function `long_path`](#-function-long_path)
- [🔧 Function `read_overlay_bounds`](#-function-read_overlay_bounds)
- [🔧 Function `read_overlay_member`](#-function-read_overlay_member)

</details>

## 🔧 Function `append_overlay_zip`

```python
def append_overlay_zip(stub_exe: Path, zip_path: Path, out_exe: Path) -> None
```

Copy stub and append zip bytes + length + magic.

<details>
<summary>Code:</summary>

```python
def append_overlay_zip(stub_exe: Path, zip_path: Path, out_exe: Path) -> None:
    zip_bytes = zip_path.read_bytes()
    out_exe.parent.mkdir(parents=True, exist_ok=True)
    with out_exe.open("wb") as out, stub_exe.open("rb") as stub:
        while True:
            chunk = stub.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
        out.write(zip_bytes)
        out.write(struct.pack("<Q", len(zip_bytes)))
        out.write(OVERLAY_MAGIC)
```

</details>

## 🔧 Function `create_work_dir`

```python
def create_work_dir() -> Path
```

Create a short-path work folder so deep payload entries stay manageable.

Deep `uv-cache` paths plus the long `%LOCALAPPDATA%\Temp` prefix overflow
`MAX_PATH` for tools that do not opt into long paths, so prefer a short root.

<details>
<summary>Code:</summary>

```python
def create_work_dir() -> Path:
    if sys.platform == "win32":
        drive = os.environ.get("SYSTEMDRIVE", "C:")
        short_root = Path(f"{drive}\\") / "hsk-setup"
        try:
            short_root.mkdir(parents=True, exist_ok=True)
            return Path(tempfile.mkdtemp(prefix="", dir=str(short_root)))
        except OSError:
            pass
    return Path(tempfile.mkdtemp(prefix="hsk-install-"))
```

</details>

## 🔧 Function `extract_overlay`

```python
def extract_overlay(exe_path: Path, dest_dir: Path, *, log: LogFn | None = None, progress: ProgressFn | None = None) -> Path
```

Extract appended zip into `dest_dir`. Return path to `dependencies/` (or dest if flat).

<details>
<summary>Code:</summary>

```python
def extract_overlay(
    exe_path: Path,
    dest_dir: Path,
    *,
    log: LogFn | None = None,
    progress: ProgressFn | None = None,
) -> Path:
    bounds = read_overlay_bounds(exe_path)
    if bounds is None:
        msg = f"No HSK payload overlay in `{exe_path}`"
        raise RuntimeError(msg)
    start, length = bounds
    _make_dirs(dest_dir)
    tmp_zip = dest_dir / "_payload.zip"
    if log:
        log(f"Extracting payload ({length // _COPY_CHUNK} MB) from this EXE…")
    with exe_path.open("rb") as src, tmp_zip.open("wb") as dst:
        src.seek(start)
        remaining = length
        done = 0
        while remaining > 0:
            chunk = src.read(min(_COPY_CHUNK, remaining))
            if not chunk:
                break
            dst.write(chunk)
            remaining -= len(chunk)
            done += len(chunk)
            if progress:
                progress(done, length)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        infos = zf.infolist()
        total = max(len(infos), 1)
        for index, info in enumerate(infos, start=1):
            _extract_member(zf, info, dest_dir)
            if progress:
                progress(index, total)
            if log and (index % _LOG_EVERY == 0 or index == total):
                log(f"    Extracted {index}/{total} files: {_display_name(info.filename)}")
    tmp_zip.unlink(missing_ok=True)
    deps = dest_dir / "dependencies"
    if deps.is_dir():
        return deps
    # Flat overlay: dependencies contents at root of zip
    return dest_dir
```

</details>

## 🔧 Function `frozen_executable`

```python
def frozen_executable() -> Path
```

Path to the running frozen EXE (or current interpreter when unpackaged).

<details>
<summary>Code:</summary>

```python
def frozen_executable() -> Path:
    return Path(sys.executable).resolve()
```

</details>

## 🔧 Function `is_frozen`

```python
def is_frozen() -> bool
```

Return whether the installer is running as a frozen executable.

<details>
<summary>Code:</summary>

```python
def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))
```

</details>

## 🔧 Function `long_path`

```python
def long_path(path: Path) -> str
```

Return a filesystem path string that is not limited by Windows `MAX_PATH`.

<details>
<summary>Code:</summary>

```python
def long_path(path: Path) -> str:
    absolute = str(Path(path).resolve())
    if sys.platform != "win32" or absolute.startswith(_LONG_PATH_PREFIX):
        return absolute
    if absolute.startswith("\\\\"):
        return _LONG_PATH_PREFIX + "UNC" + absolute[1:]
    return _LONG_PATH_PREFIX + absolute
```

</details>

## 🔧 Function `read_overlay_bounds`

```python
def read_overlay_bounds(exe_path: Path) -> tuple[int, int] | None
```

Return `(zip_start, zip_length)` or `None` if no overlay.

<details>
<summary>Code:</summary>

```python
def read_overlay_bounds(exe_path: Path) -> tuple[int, int] | None:
    size = exe_path.stat().st_size
    if size < OVERLAY_TRAILER_SIZE:
        return None
    with exe_path.open("rb") as f:
        f.seek(size - OVERLAY_TRAILER_SIZE)
        trailer = f.read(OVERLAY_TRAILER_SIZE)
    length = struct.unpack_from("<Q", trailer, 0)[0]
    magic = trailer[8:]
    if magic != OVERLAY_MAGIC:
        return None
    if length <= 0 or length + OVERLAY_TRAILER_SIZE > size:
        return None
    return size - OVERLAY_TRAILER_SIZE - length, length
```

</details>

## 🔧 Function `read_overlay_member`

```python
def read_overlay_member(exe_path: Path, member: str) -> bytes | None
```

Read one file from the appended overlay zip without extracting the payload.

<details>
<summary>Code:</summary>

```python
def read_overlay_member(exe_path: Path, member: str) -> bytes | None:
    bounds = read_overlay_bounds(exe_path)
    if bounds is None:
        return None
    start, length = bounds
    with exe_path.open("rb") as src:
        view = _OffsetView(src, start, length)
        with zipfile.ZipFile(view, "r") as zf:
            try:
                info = zf.getinfo(member)
            except KeyError:
                return None
            return zf.read(info)
```

</details>
