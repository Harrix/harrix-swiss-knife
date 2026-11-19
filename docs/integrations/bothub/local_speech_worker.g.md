---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `local_speech_worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LocalSpeechWorker`](#%EF%B8%8F-class-localspeechworker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)

</details>

## 🏛️ Class `LocalSpeechWorker`

```python
class LocalSpeechWorker(QThread)
```

Run faster-whisper transcription off the UI thread.

<details>
<summary>Code:</summary>

```python
class LocalSpeechWorker(QThread):

    finished_success = Signal(str)
    finished_error = Signal(str)

    def __init__(
        self,
        audio: tuple[bytes, str],
        *,
        model_size: str = "small",
        parent: QObject | None = None,
    ) -> None:
        """Store audio bytes and the Whisper model size for `run`."""
        super().__init__(parent)
        self._audio = audio
        self._model_size = model_size

    def run(self) -> None:
        """Transcribe on this thread and emit success or error."""
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        try:
            text = transcribe_audio_local(self._audio, model_size=self._model_size)
        except (OSError, RuntimeError, ValueError) as exc:
            self.finished_error.emit(str(exc))
            return
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        self.finished_success.emit(text)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, audio: tuple[bytes, str], *, model_size: str = 'small', parent: QObject | None = None) -> None
```

Store audio bytes and the Whisper model size for [`run`](#%EF%B8%8F-method-run).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        audio: tuple[bytes, str],
        *,
        model_size: str = "small",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._audio = audio
        self._model_size = model_size
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Transcribe on this thread and emit success or error.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        try:
            text = transcribe_audio_local(self._audio, model_size=self._model_size)
        except (OSError, RuntimeError, ValueError) as exc:
            self.finished_error.emit(str(exc))
            return
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        self.finished_success.emit(text)
```

</details>
