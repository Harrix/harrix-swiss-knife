"""Long-running ffmpeg screen capture via gdigrab (+ optional audio)."""

from __future__ import annotations

import contextlib
import re
import subprocess
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.actions.common.subprocess_run import hidden_subprocess_kwargs
from harrix_swiss_knife.apps.common.audio_compress import ffmpeg_exe_path, is_ffmpeg_available
from harrix_swiss_knife.apps.common.audio_recording.pcm_utils import audio_device_id, load_saved_microphone_id
from harrix_swiss_knife.apps.common.audio_recording.recorder import MicrophoneRecorder
from harrix_swiss_knife.paths import get_project_root

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from harrix_swiss_knife.screen_record.config import ScreenRecordAudio
    from harrix_swiss_knife.screen_record.geometry import GdigrabRegion

_DSHOW_AUDIO_RE = re.compile(r"\"([^\"]+)\"\s+\(audio\)", re.IGNORECASE)
_STDERR_TAIL_LIMIT = 200
_STDERR_TAIL_KEEP = 100


@dataclass(slots=True)
class RecorderStartResult:
    """Outcome of starting an ffmpeg capture process."""

    ok: bool
    message: str = ""
    audio_warning: str = ""


class ScreenRecorder:
    """Wrap a long-lived `ffmpeg` gdigrab process."""

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

        args = [
            str(ffmpeg),
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

    def stop(self, *, timeout: float = 15.0) -> tuple[bool, str]:
        """Ask ffmpeg to finish (`q`) and wait. Return `(ok, message)`."""
        process = self._process
        if process is None:
            return False, "No active recording"
        try:
            if process.poll() is None and process.stdin is not None:
                process.stdin.write(b"q")
                process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            self._clear_process()
            return False, "ffmpeg did not exit in time; process killed"
        code = process.returncode
        tail = "\n".join(self._stderr_tail[-20:])
        self._clear_process()
        output = self._output
        if code not in (0, None) and (output is None or not output.is_file() or output.stat().st_size == 0):
            return False, tail or f"ffmpeg exited with code {code}"
        if output is None or not output.is_file():
            return False, "Recording file was not created"
        return True, str(output)

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


@dataclass(slots=True)
class _AudioArgs:
    args: list[str] = field(default_factory=list)
    map_args: list[str] = field(default_factory=list)
    warning: str = ""


def list_dshow_audio_devices() -> list[str]:
    """Return DirectShow audio device names advertised by ffmpeg."""
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


def _resolve_dshow_mic_name() -> str | None:
    """Match the saved Qt mic (or first input) to a DirectShow audio device name."""
    preferred_id = load_saved_microphone_id()
    preferred_description = ""
    for device in MicrophoneRecorder.list_input_devices():
        if preferred_id and audio_device_id(device) == preferred_id:
            preferred_description = device.description()
            break
        if not preferred_description:
            preferred_description = device.description()
    dshow_names = list_dshow_audio_devices()
    if not dshow_names:
        return preferred_description or None
    if preferred_description:
        for name in dshow_names:
            if preferred_description.lower() in name.lower() or name.lower() in preferred_description.lower():
                return name
    return dshow_names[0]
