"""Orchestrate region select → record frame → ffmpeg capture."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QObject, QRect
from PySide6.QtWidgets import QMessageBox

from harrix_swiss_knife.apps.common.audio_compress import is_ffmpeg_available
from harrix_swiss_knife.paths import get_project_root
from harrix_swiss_knife.screen_record.ffmpeg_recorder import ScreenRecorder
from harrix_swiss_knife.screen_record.geometry import logical_rect_to_gdigrab
from harrix_swiss_knife.screen_record.preview_dialog import show_recording_preview
from harrix_swiss_knife.screen_record.record_frame import RecordFrameWindow
from harrix_swiss_knife.screenshot.capture import select_region
from harrix_swiss_knife.screenshot.dated_image_path import next_dated_image_path

if TYPE_CHECKING:
    from collections.abc import Callable

    from harrix_swiss_knife.screen_record.config import ScreenRecordAudio

_session_holder: dict[str, _RecordSession | None] = {"session": None}


class _RecordSession(QObject):
    """Owns the frame window and ffmpeg process for one recording."""

    def __init__(
        self,
        region: QRect,
        *,
        on_finished: Callable[[Path], None] | None = None,
    ) -> None:
        super().__init__()
        self._on_finished = on_finished
        self._recorder = ScreenRecorder()
        self._frame: RecordFrameWindow | None = RecordFrameWindow(region)
        self._frame.start_requested.connect(self._start)
        self._frame.stop_requested.connect(self._stop)
        self._frame.abort_requested.connect(self._abort)
        self._frame.destroyed.connect(self._on_frame_destroyed)

    @property
    def is_active(self) -> bool:
        """Whether the frame window still exists."""
        return self._frame is not None

    def show(self) -> None:
        """Show the recording frame."""
        if self._frame is None:
            return
        self._frame.show()
        self._frame.raise_()
        self._frame.activateWindow()

    def _abort(self) -> None:
        if self._frame is not None:
            self._frame.cancel_countdown()
        if self._recorder.is_running:
            self._recorder.abort()
        self._close_frame()

    def _close_frame(self) -> None:
        frame = self._frame
        self._frame = None
        if _session_holder["session"] is self:
            _session_holder["session"] = None
        if frame is not None:
            frame.close()
            frame.deleteLater()

    def _on_frame_destroyed(self) -> None:
        if _session_holder["session"] is self:
            _session_holder["session"] = None
        if self._recorder.is_running:
            self._recorder.abort()

    def _start(self, audio: object) -> None:
        if self._frame is None:
            return
        mode = cast("ScreenRecordAudio", audio) if audio in {"none", "mic", "system", "mic_and_system"} else "none"
        region = logical_rect_to_gdigrab(self._frame.region)
        if region is None:
            self._frame.set_status("Invalid region")
            self._frame.cancel_countdown()
            return
        output = next_dated_image_path(videos_folder(get_project_root()), extension=".mp4")
        result = self._recorder.start(region, output, audio=mode)
        if not result.ok:
            self._frame.set_status(result.message)
            self._frame.cancel_countdown()
            QMessageBox.warning(self._frame, "Screen record", result.message)
            return
        self._frame.set_recording(active=True)
        if result.audio_warning:
            self._frame.set_status(f"Recording (audio: {result.audio_warning})")

    def _stop(self) -> None:
        if self._frame is None:
            return
        if not self._recorder.is_running:
            self._close_frame()
            return
        ok, message = self._recorder.stop()
        self._frame.set_recording(active=False)
        if ok:
            path = Path(message)
            self._close_frame()
            show_recording_preview(path)
            if self._on_finished is not None:
                self._on_finished(path)
            return
        QMessageBox.warning(self._frame, "Screen record", message)
        self._frame.cancel_countdown()


def record_region(*, on_finished: Callable[[Path], None] | None = None) -> bool:
    """Start the ShareX-like region screen recording flow.

    Returns `False` when selection was cancelled or ffmpeg is missing.
    When recording finishes successfully, `on_finished` receives the MP4 path.

    """
    existing = _session_holder["session"]
    if existing is not None and existing.is_active:
        QMessageBox.information(None, "Screen record", "A recording session is already open.")
        return False

    root = get_project_root()
    if not is_ffmpeg_available(root):
        QMessageBox.warning(
            None,
            "Screen record",
            "ffmpeg.exe was not found in the project root.\nUse Development → Download optimize dependencies.",
        )
        return False

    rect = select_region(show_shutter_button=True)
    if rect is None or rect.isEmpty():
        return False

    session = _RecordSession(rect, on_finished=on_finished)
    _session_holder["session"] = session
    session.show()
    return True


def videos_folder(project_root: Path) -> Path:
    """Return `temp/videos` under `project_root`."""
    return project_root / "temp" / "videos"
