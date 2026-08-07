---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recorder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FinalizeResult`](#%EF%B8%8F-class-finalizeresult)
- [🏛️ Class `MicrophoneRecorder`](#%EF%B8%8F-class-microphonerecorder)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `can_continue`](#%EF%B8%8F-method-can_continue)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `duration_seconds`](#%EF%B8%8F-method-duration_seconds)
  - [⚙️ Method `is_recording (property)`](#%EF%B8%8F-method-is_recording-property)
  - [⚙️ Method `list_input_devices (staticmethod)`](#%EF%B8%8F-method-list_input_devices-staticmethod)
  - [⚙️ Method `recorded_path (property)`](#%EF%B8%8F-method-recorded_path-property)
  - [⚙️ Method `recording_wav_path (property)`](#%EF%B8%8F-method-recording_wav_path-property)
  - [⚙️ Method `release`](#%EF%B8%8F-method-release)
  - [⚙️ Method `resolve_input_device (staticmethod)`](#%EF%B8%8F-method-resolve_input_device-staticmethod)
  - [⚙️ Method `save_device (staticmethod)`](#%EF%B8%8F-method-save_device-staticmethod)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)
- [🏛️ Class `StartResult`](#%EF%B8%8F-class-startresult)

</details>

## 🏛️ Class `FinalizeResult`

```python
class FinalizeResult
```

Result of stopping and writing a recording.

<details>
<summary>Code:</summary>

```python
class FinalizeResult:

    success: bool
    recorded_path: str = ""
    recording_wav_path: str = ""
    normalized_pcm: bytes = b""
    message: str = ""
    ffmpeg_warning: str = ""
```

</details>

## 🏛️ Class `MicrophoneRecorder`

```python
class MicrophoneRecorder(QObject)
```

Capture microphone PCM, emit live envelopes, and finalize to an audio file.

<details>
<summary>Code:</summary>

```python
class MicrophoneRecorder(QObject):

    envelope_ready = Signal(float, float)
    recording_started = Signal()
    recording_stopped = Signal()
    finalized = Signal(object)
    start_failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize microphone recorder."""
        super().__init__(parent)
        self._state = _RecorderState()
        self._audio_source: QAudioSource | None = None
        self._audio_io = None

    def can_continue(self) -> bool:
        """Return whether continue-from-WAV is available."""
        return (
            bool(self._state.recording_wav_path)
            and Path(self._state.recording_wav_path).is_file()
            and bool(self._state.recorded_path)
        )

    def clear(self) -> None:
        """Clear finalized recording paths (does not stop an active capture)."""
        self._state.recorded_path = ""
        self._state.recording_wav_path = ""

    def duration_seconds(self) -> float:
        """Return duration of buffered PCM in seconds."""
        if self._state.wav_params is None:
            return 0.0
        sample_rate = self._state.wav_params[2]
        if sample_rate <= 0:
            return 0.0
        pcm_data = b"".join(self._state.pcm_chunks)
        return recording_duration_from_pcm(pcm_data, sample_rate)

    @property
    def is_recording(self) -> bool:
        """Return whether capture is active."""
        return self._state.is_recording

    @staticmethod
    def list_input_devices() -> list[QAudioDevice]:
        """Return available microphone devices."""
        return list(QMediaDevices.audioInputs())

    @property
    def recorded_path(self) -> str:
        """Return path to the last finalized recording (WAV or M4A)."""
        return self._state.recorded_path

    @property
    def recording_wav_path(self) -> str:
        """Return path to the WAV used for continue-recording."""
        return self._state.recording_wav_path

    def release(self) -> None:
        """Abort capture without finalizing and free multimedia handles."""
        if self._state.is_recording:
            if self._audio_source is not None:
                self._audio_source.stop()
            self._state.is_recording = False
            self._state.pcm_chunks = []
        self._cleanup_handles()

    @staticmethod
    def resolve_input_device(preferred_id: str = "") -> QAudioDevice | None:
        """Pick saved, preferred, or default microphone device."""
        devices = MicrophoneRecorder.list_input_devices()
        if not devices:
            return None

        saved_id = preferred_id or load_saved_microphone_id()
        if saved_id:
            for device in devices:
                if audio_device_id(device) == saved_id:
                    return device

        default_device = QMediaDevices.defaultAudioInput()
        for device in devices:
            if audio_device_id(device) == audio_device_id(default_device):
                return device
        return devices[0]

    @staticmethod
    def save_device(device: QAudioDevice) -> None:
        """Persist selected microphone ID."""
        save_microphone_id(device)

    def start(self, device: QAudioDevice, *, append: bool = False) -> StartResult:
        """Start microphone capture. Returns whether start succeeded."""
        if self._state.is_recording:
            return StartResult(success=False, message="Already recording")

        self._state.audio_format = recording_format_for_device(device)
        new_params = wav_params_from_audio_format(self._state.audio_format)

        if append:
            if not self._state.recording_wav_path:
                append = False
            else:
                recorded_path = Path(self._state.recording_wav_path)
            if append and not recorded_path.exists():
                append = False
            if append:
                try:
                    existing_params, existing_pcm = read_wav_pcm(recorded_path)
                except (OSError, wave.Error) as exc:
                    message = f"Cannot continue recording: {exc}"
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                if not wav_params_match_audio_format(existing_params, self._state.audio_format):
                    message = "Cannot continue: microphone format changed. Start over."
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                self._state.recording_path = recorded_path
                self._state.wav_params = existing_params
                self._state.pcm_chunks = [existing_pcm] if existing_pcm else []

        if not append:
            self._state.recording_path = self._new_recording_path()
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self._state.wav_params = new_params
            self._state.pcm_chunks = []

        try:
            self._audio_source = QAudioSource(device, self._state.audio_format, self)
            self._audio_io = self._audio_source.start()
            self._audio_io.readyRead.connect(self._on_audio_ready)
        except OSError as exc:
            self._cleanup_handles()
            message = f"Recording error: {exc}"
            self.start_failed.emit(message)
            return StartResult(success=False, message=message)

        self._state.is_recording = True
        self.recording_started.emit()
        return StartResult(success=True)

    def stop(self) -> None:
        """Stop capture and schedule finalize."""
        if not self._state.is_recording:
            return
        if self._audio_source is not None:
            self._audio_source.stop()
        self._cleanup_handles()
        self._state.is_recording = False
        self.recording_stopped.emit()
        QTimer.singleShot(100, self._finalize)

    def _cleanup_handles(self) -> None:
        if self._audio_io is not None:
            with suppress(RuntimeError, TypeError):
                self._audio_io.readyRead.disconnect(self._on_audio_ready)
            self._audio_io = None
        if self._audio_source is not None:
            source = self._audio_source
            self._audio_source = None
            source.stop()
            source.setParent(None)
            source.deleteLater()

    def _finalize(self) -> None:
        output = self._state.recording_path
        pcm_data = b"".join(self._state.pcm_chunks)
        self._state.pcm_chunks = []

        if not output or not pcm_data or self._state.wav_params is None:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message="Recording stopped"))
            return

        try:
            wav_params = wav_params_from_audio_format(self._state.audio_format)
            normalized_pcm = normalize_pcm_to_int16_mono(pcm_data, self._state.audio_format)
            normalized_pcm = trim_edge_silence_int16_mono(normalized_pcm, wav_params[2])
            write_wav(output, wav_params, normalized_pcm)
        except OSError as exc:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message=f"Recording error: {exc}"))
            return

        size = output.stat().st_size
        if size < MIN_AUDIO_BYTES:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(
                FinalizeResult(
                    success=False,
                    message=f"Recording too short ({format_file_size(size)}). Try again.",
                )
            )
            return

        final_path = output
        ffmpeg_warning = ""
        try:
            final_path = wav_to_m4a(output, project_root=get_project_root())
            self._state.recording_wav_path = str(output)
        except FfmpegNotFoundError:
            ffmpeg_warning = " (ffmpeg not found — saved as WAV, file is large)"
            self._state.recording_wav_path = str(output)
        except RuntimeError as exc:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message=f"Recording error: {exc}"))
            return

        self._state.recorded_path = str(final_path)
        self.finalized.emit(
            FinalizeResult(
                success=True,
                recorded_path=str(final_path),
                recording_wav_path=self._state.recording_wav_path,
                normalized_pcm=normalized_pcm,
                message="Ready for recognition:",
                ffmpeg_warning=ffmpeg_warning,
            )
        )

    @staticmethod
    def _new_recording_path() -> Path:
        temp_dir = get_project_root() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"hsk-speech-{uuid.uuid4().hex}.wav"

    def _on_audio_ready(self) -> None:
        if self._audio_io is None:
            return
        data = bytes(self._audio_io.readAll().data())
        if not data:
            return
        self._state.pcm_chunks.append(data)
        peak_neg, peak_pos = pcm_chunk_envelope(data, self._state.audio_format)
        self.envelope_ready.emit(peak_neg, peak_pos)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize microphone recorder.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = _RecorderState()
        self._audio_source: QAudioSource | None = None
        self._audio_io = None
```

</details>

### ⚙️ Method `can_continue`

```python
def can_continue(self) -> bool
```

Return whether continue-from-WAV is available.

<details>
<summary>Code:</summary>

```python
def can_continue(self) -> bool:
        return (
            bool(self._state.recording_wav_path)
            and Path(self._state.recording_wav_path).is_file()
            and bool(self._state.recorded_path)
        )
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Clear finalized recording paths (does not stop an active capture).

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._state.recorded_path = ""
        self._state.recording_wav_path = ""
```

</details>

### ⚙️ Method `duration_seconds`

```python
def duration_seconds(self) -> float
```

Return duration of buffered PCM in seconds.

<details>
<summary>Code:</summary>

```python
def duration_seconds(self) -> float:
        if self._state.wav_params is None:
            return 0.0
        sample_rate = self._state.wav_params[2]
        if sample_rate <= 0:
            return 0.0
        pcm_data = b"".join(self._state.pcm_chunks)
        return recording_duration_from_pcm(pcm_data, sample_rate)
```

</details>

### ⚙️ Method `is_recording (property)`

```python
def is_recording(self) -> bool
```

Return whether capture is active.

<details>
<summary>Code:</summary>

```python
def is_recording(self) -> bool:
        return self._state.is_recording
```

</details>

### ⚙️ Method `list_input_devices (staticmethod)`

```python
def list_input_devices() -> list[QAudioDevice]
```

Return available microphone devices.

<details>
<summary>Code:</summary>

```python
def list_input_devices() -> list[QAudioDevice]:
        return list(QMediaDevices.audioInputs())
```

</details>

### ⚙️ Method `recorded_path (property)`

```python
def recorded_path(self) -> str
```

Return path to the last finalized recording (WAV or M4A).

<details>
<summary>Code:</summary>

```python
def recorded_path(self) -> str:
        return self._state.recorded_path
```

</details>

### ⚙️ Method `recording_wav_path (property)`

```python
def recording_wav_path(self) -> str
```

Return path to the WAV used for continue-recording.

<details>
<summary>Code:</summary>

```python
def recording_wav_path(self) -> str:
        return self._state.recording_wav_path
```

</details>

### ⚙️ Method `release`

```python
def release(self) -> None
```

Abort capture without finalizing and free multimedia handles.

<details>
<summary>Code:</summary>

```python
def release(self) -> None:
        if self._state.is_recording:
            if self._audio_source is not None:
                self._audio_source.stop()
            self._state.is_recording = False
            self._state.pcm_chunks = []
        self._cleanup_handles()
```

</details>

### ⚙️ Method `resolve_input_device (staticmethod)`

```python
def resolve_input_device(preferred_id: str = "") -> QAudioDevice | None
```

Pick saved, preferred, or default microphone device.

<details>
<summary>Code:</summary>

```python
def resolve_input_device(preferred_id: str = "") -> QAudioDevice | None:
        devices = MicrophoneRecorder.list_input_devices()
        if not devices:
            return None

        saved_id = preferred_id or load_saved_microphone_id()
        if saved_id:
            for device in devices:
                if audio_device_id(device) == saved_id:
                    return device

        default_device = QMediaDevices.defaultAudioInput()
        for device in devices:
            if audio_device_id(device) == audio_device_id(default_device):
                return device
        return devices[0]
```

</details>

### ⚙️ Method `save_device (staticmethod)`

```python
def save_device(device: QAudioDevice) -> None
```

Persist selected microphone ID.

<details>
<summary>Code:</summary>

```python
def save_device(device: QAudioDevice) -> None:
        save_microphone_id(device)
```

</details>

### ⚙️ Method `start`

```python
def start(self, device: QAudioDevice, *, append: bool = False) -> StartResult
```

Start microphone capture. Returns whether start succeeded.

<details>
<summary>Code:</summary>

```python
def start(self, device: QAudioDevice, *, append: bool = False) -> StartResult:
        if self._state.is_recording:
            return StartResult(success=False, message="Already recording")

        self._state.audio_format = recording_format_for_device(device)
        new_params = wav_params_from_audio_format(self._state.audio_format)

        if append:
            if not self._state.recording_wav_path:
                append = False
            else:
                recorded_path = Path(self._state.recording_wav_path)
            if append and not recorded_path.exists():
                append = False
            if append:
                try:
                    existing_params, existing_pcm = read_wav_pcm(recorded_path)
                except (OSError, wave.Error) as exc:
                    message = f"Cannot continue recording: {exc}"
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                if not wav_params_match_audio_format(existing_params, self._state.audio_format):
                    message = "Cannot continue: microphone format changed. Start over."
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                self._state.recording_path = recorded_path
                self._state.wav_params = existing_params
                self._state.pcm_chunks = [existing_pcm] if existing_pcm else []

        if not append:
            self._state.recording_path = self._new_recording_path()
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self._state.wav_params = new_params
            self._state.pcm_chunks = []

        try:
            self._audio_source = QAudioSource(device, self._state.audio_format, self)
            self._audio_io = self._audio_source.start()
            self._audio_io.readyRead.connect(self._on_audio_ready)
        except OSError as exc:
            self._cleanup_handles()
            message = f"Recording error: {exc}"
            self.start_failed.emit(message)
            return StartResult(success=False, message=message)

        self._state.is_recording = True
        self.recording_started.emit()
        return StartResult(success=True)
```

</details>

### ⚙️ Method `stop`

```python
def stop(self) -> None
```

Stop capture and schedule finalize.

<details>
<summary>Code:</summary>

```python
def stop(self) -> None:
        if not self._state.is_recording:
            return
        if self._audio_source is not None:
            self._audio_source.stop()
        self._cleanup_handles()
        self._state.is_recording = False
        self.recording_stopped.emit()
        QTimer.singleShot(100, self._finalize)
```

</details>

## 🏛️ Class `StartResult`

```python
class StartResult
```

Result of attempting to start capture.

<details>
<summary>Code:</summary>

```python
class StartResult:

    success: bool
    message: str = ""
```

</details>
