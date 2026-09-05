---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecordingPreviewWindow`](#%EF%B8%8F-class-recordingpreviewwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
- [🔧 Function `show_recording_preview`](#-function-show_recording_preview)

</details>

## 🏛️ Class `RecordingPreviewWindow`

```python
class RecordingPreviewWindow(QMainWindow)
```

Play a recorded MP4 and offer open-folder / close.

<details>
<summary>Code:</summary>

```python
class RecordingPreviewWindow(QMainWindow):

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        """Create a preview for `path`."""
        super().__init__(parent)
        self.setWindowTitle(f"Recording — {path.name}")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self._path = path.resolve()

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._video = QVideoWidget(central)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self._video, stretch=1)

        self._path_label = QLabel(str(self._path), central)
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._path_label.setWordWrap(True)
        root.addWidget(self._path_label)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_emoji_icon("▶️", _ICON))
        self._play_btn.setToolTip("Play / Pause")
        self._play_btn.setText("Play")
        self._play_btn.clicked.connect(self._toggle_play)
        buttons.addWidget(self._play_btn)

        folder_btn = make_emoji_push_button("Open folder", "📂")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        buttons.addWidget(folder_btn)

        close_btn = make_emoji_push_button("Close", "❌")
        close_btn.setToolTip("Close preview")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video)
        self._player.setSource(QUrl.fromLocalFile(str(self._path)))
        self._player.playbackStateChanged.connect(self._on_state_changed)
        QTimer.singleShot(0, self._player.play)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop playback and clear the shared preview reference."""
        self._player.stop()
        if _preview_holder["window"] is self:
            _preview_holder["window"] = None
        super().closeEvent(event)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._play_btn.setText("Pause" if playing else "Play")
        self._play_btn.setIcon(create_emoji_icon("⏸️" if playing else "▶️", _ICON))

    def _open_folder(self) -> None:
        folder = self._path.parent
        if not folder.is_dir():
            QMessageBox.warning(self, "Recording", f"Folder not found:\n{folder}")
            return
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _toggle_play(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, path: Path, parent: QWidget | None = None) -> None
```

Create a preview for `path`.

<details>
<summary>Code:</summary>

```python
def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Recording — {path.name}")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self._path = path.resolve()

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._video = QVideoWidget(central)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self._video, stretch=1)

        self._path_label = QLabel(str(self._path), central)
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._path_label.setWordWrap(True)
        root.addWidget(self._path_label)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_emoji_icon("▶️", _ICON))
        self._play_btn.setToolTip("Play / Pause")
        self._play_btn.setText("Play")
        self._play_btn.clicked.connect(self._toggle_play)
        buttons.addWidget(self._play_btn)

        folder_btn = make_emoji_push_button("Open folder", "📂")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        buttons.addWidget(folder_btn)

        close_btn = make_emoji_push_button("Close", "❌")
        close_btn.setToolTip("Close preview")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video)
        self._player.setSource(QUrl.fromLocalFile(str(self._path)))
        self._player.playbackStateChanged.connect(self._on_state_changed)
        QTimer.singleShot(0, self._player.play)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Stop playback and clear the shared preview reference.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._player.stop()
        if _preview_holder["window"] is self:
            _preview_holder["window"] = None
        super().closeEvent(event)
```

</details>

## 🔧 Function `show_recording_preview`

```python
def show_recording_preview(path: Path) -> RecordingPreviewWindow
```

Show `path` in the shared recording preview window.

<details>
<summary>Code:</summary>

```python
def show_recording_preview(path: Path) -> RecordingPreviewWindow:
    previous = _preview_holder["window"]
    if previous is not None and isValid(previous):
        previous.close()
    if not path.is_file() or path.stat().st_size <= 0:
        msg = f"Recording file is missing or empty:\n{path}"
        raise FileNotFoundError(msg)
    window = RecordingPreviewWindow(path)
    _preview_holder["window"] = window
    window.show()
    window.raise_()
    window.activateWindow()
    return window
```

</details>
