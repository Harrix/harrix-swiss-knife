---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `export.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExportRequest`](#%EF%B8%8F-class-exportrequest)
- [🏛️ Class `ExportResult`](#%EF%B8%8F-class-exportresult)
- [🔧 Function `export_recording`](#-function-export_recording)

</details>

## 🏛️ Class `ExportRequest`

```python
class ExportRequest
```

Parameters for exporting a trimmed recording.

<details>
<summary>Code:</summary>

```python
class ExportRequest:

    source: Path
    destination: Path
    format: ExportFormat
    start_ms: int
    end_ms: int
    remove_audio: bool = False
```

</details>

## 🏛️ Class `ExportResult`

```python
class ExportResult
```

Outcome of an export run.

<details>
<summary>Code:</summary>

```python
class ExportResult:

    ok: bool
    message: str = ""
    path: Path | None = None
```

</details>

## 🔧 Function `export_recording`

```python
def export_recording(request: ExportRequest) -> ExportResult
```

Trim and re-encode `request.source` to `request.destination`.

<details>
<summary>Code:</summary>

```python
def export_recording(request: ExportRequest) -> ExportResult:
    root = get_project_root()
    if not is_ffmpeg_available(root):
        return ExportResult(ok=False, message="ffmpeg.exe not found in project root")
    source = request.source.resolve()
    if not source.is_file():
        return ExportResult(ok=False, message=f"Source not found:\n{source}")

    start_ms = max(0, request.start_ms)
    end_ms = max(start_ms + 1, request.end_ms)
    start_s = start_ms / 1000.0
    duration_s = (end_ms - start_ms) / 1000.0
    destination = request.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if request.format == "avif_optimized":
        return _export_avif_optimized(
            source=source,
            destination=destination,
            start_s=start_s,
            duration_s=duration_s,
            root=root,
        )

    ffmpeg = ffmpeg_exe_path(root)
    args = [
        str(ffmpeg),
        "-hide_banner",
        "-y",
        "-ss",
        f"{start_s:.3f}",
        "-t",
        f"{duration_s:.3f}",
        "-i",
        str(source),
    ]
    if request.format == "mp4":
        args.extend(_mp4_args(remove_audio=request.remove_audio))
    elif request.format == "gif":
        args.extend(_gif_args())
    else:
        args.extend(_avif_args())
    args.append(str(destination))

    return _run_ffmpeg(args, destination)
```

</details>
