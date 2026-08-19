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
- [🔧 Function `extract_overlay`](#-function-extract_overlay)
- [🔧 Function `frozen_executable`](#-function-frozen_executable)
- [🔧 Function `is_frozen`](#-function-is_frozen)
- [🔧 Function `read_overlay_bounds`](#-function-read_overlay_bounds)

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
    dest_dir.mkdir(parents=True, exist_ok=True)
    tmp_zip = dest_dir / "_payload.zip"
    if log:
        log(f"Extracting payload ({length // (1024 * 1024)} MB)…")
    with exe_path.open("rb") as src, tmp_zip.open("wb") as dst:
        src.seek(start)
        remaining = length
        done = 0
        chunk_size = 1024 * 1024
        while remaining > 0:
            chunk = src.read(min(chunk_size, remaining))
            if not chunk:
                break
            dst.write(chunk)
            remaining -= len(chunk)
            done += len(chunk)
            if progress:
                progress(done, length)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        members = zf.namelist()
        total = max(len(members), 1)
        for index, name in enumerate(members, start=1):
            zf.extract(name, dest_dir)
            if progress:
                progress(index, total)
            if log and index % 50 == 0:
                log(f"  Extracted {index}/{total} entries…")
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
