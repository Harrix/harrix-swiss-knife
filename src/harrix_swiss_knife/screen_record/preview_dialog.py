"""Preview window for a finished screen recording."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon, make_emoji_push_button

if TYPE_CHECKING:
    from pathlib import Path

    from PySide6.QtGui import QCloseEvent

_ICON = 18
_MIN_W = 640
_MIN_H = 400
_preview_holder: dict[str, RecordingPreviewWindow | None] = {"window": None}


class RecordingPreviewWindow(QMainWindow):
    """Play a recorded MP4 and offer open-folder / close."""

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


def show_recording_preview(path: Path) -> RecordingPreviewWindow:
    """Show `path` in the shared recording preview window."""
    window = _preview_holder["window"]
    if window is not None and isValid(window):
        window.close()
    window = RecordingPreviewWindow(path)
    _preview_holder["window"] = window
    window.show()
    window.raise_()
    window.activateWindow()
    return window
