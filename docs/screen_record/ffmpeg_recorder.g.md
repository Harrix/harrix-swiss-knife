---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ffmpeg_recorder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecorderStartResult`](#%EF%B8%8F-class-recorderstartresult)
- [🏛️ Class `ScreenRecorder`](#%EF%B8%8F-class-screenrecorder)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `abort`](#%EF%B8%8F-method-abort)
  - [⚙️ Method `is_running (property)`](#%EF%B8%8F-method-is_running-property)
  - [⚙️ Method `last_error_text`](#%EF%B8%8F-method-last_error_text)
  - [⚙️ Method `output_path (property)`](#%EF%B8%8F-method-output_path-property)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)
- [🔧 Function `list_dshow_audio_devices`](#-function-list_dshow_audio_devices)

</details>

## 🏛️ Class `RecorderStartResult`

```python
class RecorderStartResult
```

Outcome of starting an ffmpeg capture process.

<details>
<summary>Code:</summary>

```python
class RecorderStartResult:

    ok: bool
    message: str = ""
    audio_warning: str = ""
```

</details>

## 🏛️ Class `ScreenRecorder`

```python
class ScreenRecorder
```

Wrap a long-lived `ffmpeg` gdigrab process.

<details>
<summary>Code:</summary>

```python
class ScreenRecorder:

    def __init__(self) -> None:
        """Create an idle recorder."""
        self._process: subprocess.Popen[Any] | None = None
        self._output: Path | None = None
        self._stderr_thread: threading.Thread | None = None
        self._stderr_tail: list[str] = []

    def abort(self) -> None:
        """Kill ffmpeg and delete a partial output file."""
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
        output = self._output
        self._clear_process()
        if output is not None and output.is_file():
            with contextlib.suppress(OSError):
                output.unlink()

    @property
    def is_running(self) -> bool:
        """Whether ffmpeg is still alive."""
        process = self._process
        return process is not None and process.poll() is None

    def last_error_text(self) -> str:
        """Return recent ffmpeg stderr lines (best-effort)."""
        return "\n".join(self._stderr_tail[-30:]).strip()

    @property
    def output_path(self) -> Path | None:
        """Destination MP4 path for the current/last session."""
        return self._output

    def start(
        self,
        region: GdigrabRegion,
        output: Path,
        *,
        audio: ScreenRecordAudio = "none",
        framerate: int = 30,
        on_stderr_line: Callable[[str], None] | None = None,
    ) -> RecorderStartResult:
        """Start capturing `region` into `output`."""
        if self.is_running:
            return RecorderStartResult(ok=False, message="Recording already in progress")
        root = get_project_root()
        if not is_ffmpeg_available(root):
            return RecorderStartResult(ok=False, message="ffmpeg.exe not found in project root")
        ffmpeg = ffmpeg_exe_path(root)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            output.unlink()

        audio_warning = ""
        result = self._spawn(ffmpeg, region, output, audio=audio, framerate=framerate, on_stderr_line=on_stderr_line)
        if not result.ok:
            return result
        audio_warning = result.audio_warning
        # Give ffmpeg a moment; wasapi/dshow often fails immediately.
        if not self._wait_alive(0.6):
            dead_message = self.last_error_text() or "ffmpeg exited immediately"
            self.abort()
            if audio != "none":
                retry = self._spawn(
                    ffmpeg,
                    region,
                    output,
                    audio="none",
                    framerate=framerate,
                    on_stderr_line=on_stderr_line,
                )
                if retry.ok and self._wait_alive(0.6):
                    return RecorderStartResult(
                        ok=True,
                        audio_warning=f"Audio failed ({dead_message.splitlines()[-1][:120]}); recording video only",
                    )
                self.abort()
            return RecorderStartResult(ok=False, message=dead_message)
        return RecorderStartResult(ok=True, audio_warning=audio_warning)

    def stop(self, *, timeout: float = 20.0) -> tuple[bool, str]:
        """Ask ffmpeg to finish (`q`) and wait. Return `(ok, message)`."""
        process = self._process
        output = self._output
        if process is None:
            if output is not None and output.is_file() and output.stat().st_size > 0:
                return True, str(output)
            return False, self.last_error_text() or "No active recording"
        try:
            if process.poll() is None and process.stdin is not None:
                process.stdin.write(b"q\n")
                process.stdin.flush()
                with contextlib.suppress(OSError):
                    process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=3)
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            self._clear_process()
            if output is not None and output.is_file() and output.stat().st_size > 0:
                return True, str(output)
            return False, "ffmpeg did not exit in time; process killed"
        code = process.returncode
        tail = self.last_error_text()
        self._clear_process()
        if output is not None and output.is_file() and output.stat().st_size > 0:
            return True, str(output)
        if code not in (0, None):
            return False, tail or f"ffmpeg exited with code {code}"
        return False, tail or "Recording file was not created"

    def _audio_input_args(self, audio: ScreenRecordAudio) -> _AudioArgs:
        if audio == "none":
            return _AudioArgs()
        if audio == "mic":
            device = _resolve_dshow_mic_name()
            if not device:
                return _AudioArgs(warning="Microphone not found for dshow")
            return _AudioArgs(args=["-f", "dshow", "-i", f"audio={device}"])
        if audio == "system":
            return _AudioArgs(args=["-f", "wasapi", "-loopback", "1", "-i", "default"])
        mic = _resolve_dshow_mic_name()
        if not mic:
            return _AudioArgs(
                args=["-f", "wasapi", "-loopback", "1", "-i", "default"],
                warning="Microphone not found; using system audio only",
            )
        return _AudioArgs(
            args=[
                "-f",
                "dshow",
                "-i",
                f"audio={mic}",
                "-f",
                "wasapi",
                "-loopback",
                "1",
                "-i",
                "default",
            ],
            map_args=[
                "-filter_complex",
                "[1:a][2:a]amix=inputs=2:duration=longest[aout]",
                "-map",
                "0:v",
                "-map",
                "[aout]",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
            ],
        )

    def _clear_process(self) -> None:
        self._process = None
        self._stderr_thread = None

    def _read_stderr(
        self,
        process: subprocess.Popen[Any],
        on_line: Callable[[str], None] | None,
    ) -> None:
        stream = process.stderr
        if stream is None:
            return
        for raw in iter(stream.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip()
            if not line:
                continue
            self._stderr_tail.append(line)
            if len(self._stderr_tail) > _STDERR_TAIL_LIMIT:
                self._stderr_tail = self._stderr_tail[-_STDERR_TAIL_KEEP:]
            if on_line is not None:
                on_line(line)

    def _spawn(
        self,
        ffmpeg: Path,
        region: GdigrabRegion,
        output: Path,
        *,
        audio: ScreenRecordAudio,
        framerate: int,
        on_stderr_line: Callable[[str], None] | None,
    ) -> RecorderStartResult:
        args = [
            str(ffmpeg),
            "-hide_banner",
            "-y",
            "-f",
            "gdigrab",
            "-framerate",
            str(max(1, framerate)),
            "-offset_x",
            str(region.offset_x),
            "-offset_y",
            str(region.offset_y),
            "-video_size",
            f"{region.width}x{region.height}",
            "-i",
            "desktop",
        ]
        audio_inputs = self._audio_input_args(audio)
        audio_warning = ""
        if audio != "none" and not audio_inputs.args:
            audio_warning = audio_inputs.warning or "Audio unavailable; recording video only"
        else:
            args.extend(audio_inputs.args)
            audio_warning = audio_inputs.warning

        args.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
            ]
        )
        if audio_inputs.map_args:
            args.extend(audio_inputs.map_args)
        elif audio_inputs.args:
            args.extend(["-c:a", "aac", "-b:a", "128k"])
        args.append(str(output))

        try:
            process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                **hidden_subprocess_kwargs(),
            )
        except OSError as exc:
            return RecorderStartResult(ok=False, message=f"Could not start ffmpeg: {exc}")

        self._process = process
        self._output = output
        self._stderr_tail = []
        self._stderr_thread = threading.Thread(
            target=self._read_stderr,
            args=(process, on_stderr_line),
            daemon=True,
        )
        self._stderr_thread.start()
        return RecorderStartResult(ok=True, audio_warning=audio_warning)

    def _wait_alive(self, seconds: float) -> bool:
        process = self._process
        if process is None:
            return False
        deadline = time.monotonic() + max(0.0, seconds)
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return False
            time.sleep(0.05)
        return process.poll() is None
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create an idle recorder.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        self._process: subprocess.Popen[Any] | None = None
        self._output: Path | None = None
        self._stderr_thread: threading.Thread | None = None
        self._stderr_tail: list[str] = []
```

</details>

### ⚙️ Method `abort`

```python
def abort(self) -> None
```

Kill ffmpeg and delete a partial output file.

<details>
<summary>Code:</summary>

```python
def abort(self) -> None:
        process = self._process
        if process is not None and process.poll() is None:
            process.kill()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
        output = self._output
        self._clear_process()
        if output is not None and output.is_file():
            with contextlib.suppress(OSError):
                output.unlink()
```

</details>

### ⚙️ Method `is_running (property)`

```python
def is_running(self) -> bool
```

Whether ffmpeg is still alive.

<details>
<summary>Code:</summary>

```python
def is_running(self) -> bool:
        process = self._process
        return process is not None and process.poll() is None
```

</details>

### ⚙️ Method `last_error_text`

```python
def last_error_text(self) -> str
```

Return recent ffmpeg stderr lines (best-effort).

<details>
<summary>Code:</summary>

```python
def last_error_text(self) -> str:
        return "\n".join(self._stderr_tail[-30:]).strip()
```

</details>

### ⚙️ Method `output_path (property)`

```python
def output_path(self) -> Path | None
```

Destination MP4 path for the current/last session.

<details>
<summary>Code:</summary>

```python
def output_path(self) -> Path | None:
        return self._output
```

</details>

### ⚙️ Method `start`

```python
def start(self, region: GdigrabRegion, output: Path, *, audio: ScreenRecordAudio = 'none', framerate: int = 30, on_stderr_line: Callable[[str], None] | None = None) -> RecorderStartResult
```

Start capturing [`region`](record_frame.g.md#%EF%B8%8F-method-region-property) into `output`.

<details>
<summary>Code:</summary>

```python
def start(
        self,
        region: GdigrabRegion,
        output: Path,
        *,
        audio: ScreenRecordAudio = "none",
        framerate: int = 30,
        on_stderr_line: Callable[[str], None] | None = None,
    ) -> RecorderStartResult:
        if self.is_running:
            return RecorderStartResult(ok=False, message="Recording already in progress")
        root = get_project_root()
        if not is_ffmpeg_available(root):
            return RecorderStartResult(ok=False, message="ffmpeg.exe not found in project root")
        ffmpeg = ffmpeg_exe_path(root)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            output.unlink()

        audio_warning = ""
        result = self._spawn(ffmpeg, region, output, audio=audio, framerate=framerate, on_stderr_line=on_stderr_line)
        if not result.ok:
            return result
        audio_warning = result.audio_warning
        # Give ffmpeg a moment; wasapi/dshow often fails immediately.
        if not self._wait_alive(0.6):
            dead_message = self.last_error_text() or "ffmpeg exited immediately"
            self.abort()
            if audio != "none":
                retry = self._spawn(
                    ffmpeg,
                    region,
                    output,
                    audio="none",
                    framerate=framerate,
                    on_stderr_line=on_stderr_line,
                )
                if retry.ok and self._wait_alive(0.6):
                    return RecorderStartResult(
                        ok=True,
                        audio_warning=f"Audio failed ({dead_message.splitlines()[-1][:120]}); recording video only",
                    )
                self.abort()
            return RecorderStartResult(ok=False, message=dead_message)
        return RecorderStartResult(ok=True, audio_warning=audio_warning)
```

</details>

### ⚙️ Method `stop`

```python
def stop(self, *, timeout: float = 20.0) -> tuple[bool, str]
```

Ask ffmpeg to finish (`q`) and wait. Return `(ok, message)`.

<details>
<summary>Code:</summary>

```python
def stop(self, *, timeout: float = 20.0) -> tuple[bool, str]:
        process = self._process
        output = self._output
        if process is None:
            if output is not None and output.is_file() and output.stat().st_size > 0:
                return True, str(output)
            return False, self.last_error_text() or "No active recording"
        try:
            if process.poll() is None and process.stdin is not None:
                process.stdin.write(b"q\n")
                process.stdin.flush()
                with contextlib.suppress(OSError):
                    process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=3)
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            self._clear_process()
            if output is not None and output.is_file() and output.stat().st_size > 0:
                return True, str(output)
            return False, "ffmpeg did not exit in time; process killed"
        code = process.returncode
        tail = self.last_error_text()
        self._clear_process()
        if output is not None and output.is_file() and output.stat().st_size > 0:
            return True, str(output)
        if code not in (0, None):
            return False, tail or f"ffmpeg exited with code {code}"
        return False, tail or "Recording file was not created"
```

</details>

## 🔧 Function `list_dshow_audio_devices`

```python
def list_dshow_audio_devices() -> list[str]
```

Return DirectShow audio device names advertised by ffmpeg.

<details>
<summary>Code:</summary>

```python
def list_dshow_audio_devices() -> list[str]:
    root = get_project_root()
    if not is_ffmpeg_available(root):
        return []
    ffmpeg = ffmpeg_exe_path(root)
    try:
        completed = subprocess.run(
            [str(ffmpeg), "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            **hidden_subprocess_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    text = f"{completed.stderr}\n{completed.stdout}"
    return [match.group(1) for match in _DSHOW_AUDIO_RE.finditer(text)]
```

</details>
