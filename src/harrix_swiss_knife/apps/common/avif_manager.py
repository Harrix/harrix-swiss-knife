"""AVIF file manager for applications.

This module provides a class for managing AVIF file loading, animation, and display
in Qt-based applications.

"""

from __future__ import annotations

import contextlib
import io
import logging
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageOps
from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QImageReader, QPixmap

from harrix_swiss_knife.apps.common.exercise_media import FITNESS_IMG_HIGH_DIR

if TYPE_CHECKING:
    from PySide6.QtCore import QSize
    from PySide6.QtWidgets import QLabel


logger = logging.getLogger(__name__)

_DEFAULT_FRAME_DURATION_MS = 100
_SPEED_MAX = 8.0
_SPEED_MIN = 0.1


class AvifLabelKey(StrEnum):
    """Known keys for AVIF label slots."""

    MAIN = "main"
    EXERCISES = "exercises"
    TYPES = "types"
    CHARTS = "charts"
    STATISTICS = "statistics"
    DIALOG_PREVIEW = "dialog_preview"
    LIST_HOVER = "list_hover"
    LIGHTBOX = "lightbox"


class AvifManager(QObject):
    """Manager for AVIF file operations including loading, animation, and display.

    This class handles:

    - Finding AVIF files for exercises
    - Loading static and animated AVIF images
    - Managing animation timers for multiple labels
    - Converting AVIF to QPixmap for Qt widgets

    Attributes:

    - `avif_dir` (`Path`): Directory containing AVIF files.
    - `avif_data` (`dict[str, dict]`): Dictionary storing animation data for each label key.

    """

    def __init__(self, avif_dir: Path | str, parent: QObject | None = None) -> None:
        """Initialize the AVIF manager.

        Args:

        - `avif_dir` (`Path | str`): Directory path containing AVIF files.
        - `parent` (`QObject | None`): Optional Qt parent. Defaults to `None`.

        """
        super().__init__(parent)
        self.avif_dir = Path(avif_dir)
        self.avif_data: dict[AvifLabelKey, dict] = {
            key: {
                "frames": [],
                "current_frame": 0,
                "timer": None,
                "exercise": None,
                "duration_ms": _DEFAULT_FRAME_DURATION_MS,
                "speed": 1.0,
            }
            for key in AvifLabelKey
        }
        self.label_widgets: dict[AvifLabelKey, QLabel | None] = dict.fromkeys(AvifLabelKey)
        self._frame_generations: dict[AvifLabelKey, int] = dict.fromkeys(AvifLabelKey, 0)
        self._frame_workers: dict[AvifLabelKey, _AvifFramesWorker | None] = dict.fromkeys(AvifLabelKey)

    def delete_exercise_avif(self, exercise_name: str) -> bool:
        """Delete the small and high-resolution AVIFs for `exercise_name`.

        Args:

        - `exercise_name` (`str`): Exercise name matching the AVIF stem.

        Returns:

        - `bool`: `True` when at least one file was removed, `False` otherwise.

        """
        removed = False
        for high in (False, True):
            avif_path = self.get_exercise_avif_path(exercise_name, high=high)
            if avif_path is None:
                continue
            try:
                avif_path.unlink()
            except OSError:
                logger.exception("Failed to delete exercise AVIF %s", avif_path)
                return False
            removed = True
        return removed

    def get_current_exercise(self, label_key: str | AvifLabelKey) -> str | None:
        """Get the current exercise name for a label key.

        Args:

        - `label_key` (`str`): Key identifying which label.

        Returns:

        - `str | None`: Current exercise name or `None`.

        """
        key = self._normalize_label_key(label_key)
        return self.avif_data.get(key, {}).get("exercise")

    def get_exercise_avif_path(self, exercise_name: str, *, high: bool = False) -> Path | None:
        """Get the path to the small or high-resolution AVIF for the exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.
        - `high` (`bool`): When `True`, look in `fitness_img/high/`. Defaults to the
          small UI file in `fitness_img/`.

        Returns:

        - `Path | None`: Path to the AVIF file if it exists, `None` otherwise.

        """
        avif_path = self._exercise_avif_file(exercise_name, high=high)
        return avif_path if avif_path is not None and avif_path.exists() else None

    def get_exercise_hover_avif_path(self, exercise_name: str) -> Path | None:
        """Return the hover preview file, preferring an animated high-resolution AVIF.

        Use high only when it is animated and the small UI file is missing or still.

        """
        small_path = self.get_exercise_avif_path(exercise_name)
        high_path = self.get_exercise_avif_path(exercise_name, high=True)
        if (
            high_path is not None
            and _avif_is_animated(high_path)
            and (small_path is None or not _avif_is_animated(small_path))
        ):
            return high_path
        return small_path if small_path is not None else high_path

    def get_exercise_lightbox_avif_path(self, exercise_name: str) -> Path | None:
        """Return the high-resolution AVIF when it exists, otherwise the small file."""
        high_path = self.get_exercise_avif_path(exercise_name, high=True)
        if high_path is not None:
            return high_path
        return self.get_exercise_avif_path(exercise_name)

    def has_any_exercise_avif(self) -> bool:
        """Return whether `fitness_img` contains at least one `.avif` file."""
        if not self.avif_dir.is_dir():
            return False
        return any(path.is_file() for path in self.avif_dir.rglob("*.avif"))

    def is_animation_active(self, label_key: str | AvifLabelKey) -> bool:
        """Return whether `label_key` is playing a multi-frame animation.

        Args:

        - `label_key` (`str | AvifLabelKey`): Slot to inspect.

        Returns:

        - `bool`: `True` when the slot has more than one frame and a running timer.

        """
        key = self._normalize_label_key(label_key)
        data = self.avif_data.get(key) or {}
        frames = data.get("frames")
        timer = data.get("timer")
        return isinstance(frames, list) and len(frames) > 1 and isinstance(timer, QTimer) and timer.isActive()

    def load_avif_pixmap(self, avif_path: Path) -> QPixmap | None:
        """Load a pixmap from an AVIF file, falling back to Pillow if needed.

        Args:

        - `avif_path` (`Path`): Path to the AVIF file.

        Returns:

        - `QPixmap | None`: Loaded pixmap or `None` if loading failed.

        """
        return load_image_pixmap(avif_path)

    def load_exercise_avif(
        self,
        exercise_name: str,
        label_widget: QLabel,
        label_key: str | AvifLabelKey = AvifLabelKey.MAIN,
    ) -> None:
        """Load and display AVIF for the given exercise.

        Lightbox loads synchronously (including animation). Other slots, including
        list hover, show the first frame immediately and decode remaining animation
        frames off the UI thread.

        Args:

        - `exercise_name` (`str`): Name of the exercise to load AVIF for.
        - `label_widget` (`QLabel`): Label widget to display the AVIF.
        - `label_key` (`str`): Key identifying which label to update
          (`main`, `charts`, `statistics`, and other `AvifLabelKey` values). Defaults to `main`.

        """
        key = self._normalize_label_key(label_key)
        if key not in self.avif_data:
            self.avif_data[key] = {
                "frames": [],
                "current_frame": 0,
                "timer": None,
                "exercise": None,
                "duration_ms": _DEFAULT_FRAME_DURATION_MS,
                "speed": 1.0,
            }
        data = self.avif_data[key]
        saved_speed = float(data.get("speed") or 1.0)

        self._cancel_frame_worker(key)

        timer = data["timer"]
        if timer is not None and isinstance(timer, QTimer):
            timer.stop()
            data["timer"] = None

        data["frames"] = []
        data["current_frame"] = 0
        data["exercise"] = exercise_name
        data["speed"] = saved_speed

        if key not in self.label_widgets:
            self.label_widgets[key] = None
        self.label_widgets[key] = label_widget

        label_widget.clear()
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not exercise_name:
            label_widget.setText("No exercise selected")
            return

        # Lightbox prefers high-resolution when present. Hover uses high only when
        # the small UI file is a still and high is animated. Other slots use small.
        if key == AvifLabelKey.LIGHTBOX:
            avif_path = self.get_exercise_lightbox_avif_path(exercise_name)
        elif key == AvifLabelKey.LIST_HOVER:
            avif_path = self.get_exercise_hover_avif_path(exercise_name)
        else:
            avif_path = self.get_exercise_avif_path(exercise_name)

        if avif_path is None:
            label_widget.setText(f"No AVIF found for:\n{exercise_name}")
            return

        if key == AvifLabelKey.LIGHTBOX:
            self._load_avif_synchronous(avif_path, label_widget, data, key, exercise_name)
            return

        self._load_avif_first_frame_then_async(avif_path, label_widget, data, key, exercise_name)

    def rename_exercise_avif(self, old_name: str, new_name: str) -> bool:
        """Rename small and high-resolution AVIFs to match a renamed exercise.

        Args:

        - `old_name` (`str`): Previous exercise name.
        - `new_name` (`str`): New exercise name.

        Returns:

        - `bool`: `True` when at least one file was renamed, `False` otherwise.

        """
        old = old_name.strip()
        new = new_name.strip()
        if not old or not new or old == new:
            return False

        renamed = False
        for high in (False, True):
            if self._rename_avif_file(old, new, high=high):
                renamed = True
        if renamed:
            self._retarget_exercise_name(old, new)
        return renamed

    def set_animation_speed(self, label_key: str | AvifLabelKey, speed: float) -> None:
        """Set playback speed for an existing animation slot.

        Args:

        - `label_key` (`str | AvifLabelKey`): Slot to update. Fitness lightbox uses
          `AvifLabelKey.LIGHTBOX` only.
        - `speed` (`float`): Playback multiplier. `1.0` is native speed.

        """
        key = self._normalize_label_key(label_key)
        data = self.avif_data.setdefault(
            key,
            {
                "frames": [],
                "current_frame": 0,
                "timer": None,
                "exercise": None,
                "duration_ms": _DEFAULT_FRAME_DURATION_MS,
                "speed": 1.0,
            },
        )
        data["speed"] = max(_SPEED_MIN, min(_SPEED_MAX, float(speed)))
        timer = data.get("timer")
        if isinstance(timer, QTimer) and timer.isActive():
            timer.setInterval(
                animation_interval_ms(
                    int(data.get("duration_ms") or _DEFAULT_FRAME_DURATION_MS),
                    data["speed"],
                )
            )

    def stop_animation(self, label_key: str | AvifLabelKey) -> None:
        """Stop the animation timer and clear frames for `label_key`.

        Args:

        - `label_key` (`str | AvifLabelKey`): Key identifying which label slot to stop.

        """
        key = self._normalize_label_key(label_key)
        self._cancel_frame_worker(key)
        data = self.avif_data.get(key)
        if data is None:
            return
        timer = data.get("timer")
        if isinstance(timer, QTimer):
            timer.stop()
        data["timer"] = None
        data["frames"] = []
        data["current_frame"] = 0
        data["exercise"] = None
        label_widget = self.label_widgets.get(key)
        if label_widget is not None:
            label_widget.clear()
        self.label_widgets[key] = None

    def _apply_decoded_frames(
        self,
        label_key: object,
        exercise_name: object,
        png_frames: list,
        duration_ms: int,
        *,
        generation: int,
    ) -> None:
        """Apply background-decoded frames when the slot still matches the request."""
        if not isinstance(label_key, AvifLabelKey) or not isinstance(exercise_name, str):
            return
        if self._frame_generations.get(label_key) != generation:
            return
        data = self.avif_data.get(label_key)
        label_widget = self.label_widgets.get(label_key)
        if data is None or label_widget is None or data.get("exercise") != exercise_name:
            return

        label_size = label_widget.size()
        frames: list[QPixmap] = []
        for png_bytes in png_frames:
            if not isinstance(png_bytes, (bytes, bytearray)):
                continue
            pixmap = QPixmap()
            if not pixmap.loadFromData(bytes(png_bytes)):
                continue
            scaled = pixmap.scaled(
                label_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            if not scaled.isNull():
                frames.append(scaled)

        if not frames:
            return

        data["frames"] = frames
        data["current_frame"] = 0
        label_widget.setPixmap(frames[0])

        if len(frames) == 1:
            return

        self._start_animation_timer(data, label_key, duration_ms)

    def _cancel_frame_worker(self, key: AvifLabelKey) -> None:
        """Bump generation so an in-flight decode is ignored; stop tracking the worker."""
        self._frame_generations[key] = self._frame_generations.get(key, 0) + 1
        worker = self._frame_workers.get(key)
        self._frame_workers[key] = None
        if worker is None:
            return
        # Do not wait here — generation guard drops late results.
        with contextlib.suppress(RuntimeError, TypeError):
            worker.frames_ready.disconnect()
        with contextlib.suppress(RuntimeError, TypeError):
            worker.decode_failed.disconnect()

    def _exercise_avif_file(self, exercise_name: str, *, high: bool = False) -> Path | None:
        """Return the expected AVIF path for `exercise_name`, even if the file is missing."""
        name = exercise_name.strip() if exercise_name else ""
        if not name:
            return None
        folder = self.avif_dir / FITNESS_IMG_HIGH_DIR if high else self.avif_dir
        return folder / f"{name}.avif"

    def _load_avif_first_frame_then_async(
        self,
        avif_path: Path,
        label_widget: QLabel,
        data: dict,
        key: AvifLabelKey,
        exercise_name: str,
    ) -> None:
        """Show the first frame now; decode the full animation in a worker thread."""
        try:
            pixmap = QPixmap(str(avif_path))
            if not pixmap.isNull():
                # Qt decoded a frame — show it; animate in the background only when needed.
                label_size = label_widget.size()
                scaled_pixmap = pixmap.scaled(
                    label_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label_widget.setPixmap(scaled_pixmap)
                if _avif_is_animated(avif_path):
                    self._start_frame_worker(avif_path, key, exercise_name)
                return
        except Exception:
            logger.exception("Qt AVIF load failed for %s", avif_path)

        try:
            import pillow_avif  # noqa: F401, PLC0415
        except ImportError as import_error:
            logger.warning("AVIF plugin import error: %s", import_error)
            label_widget.setText(f"AVIF plugin not available:\n{exercise_name}")
            return

        try:
            with Image.open(avif_path) as pil_image:
                label_size = label_widget.size()
                if getattr(pil_image, "is_animated", False):
                    pil_image.seek(0)
                    first = self._pil_frame_to_pixmap(pil_image.copy(), label_size=label_size)
                    if first is not None and not first.isNull():
                        label_widget.setPixmap(first)
                        data["frames"] = [first]
                    self._start_frame_worker(avif_path, key, exercise_name)
                    return

                scaled_pixmap = self._pil_frame_to_pixmap(pil_image, label_size=label_size)
                if scaled_pixmap is not None and not scaled_pixmap.isNull():
                    label_widget.setPixmap(scaled_pixmap)
                    return
        except Exception:
            logger.exception("Pillow error while loading first AVIF frame %s", avif_path)

        label_widget.setText(f"Cannot load AVIF:\n{exercise_name}")

    def _load_avif_synchronous(
        self,
        avif_path: Path,
        label_widget: QLabel,
        data: dict,
        key: AvifLabelKey,
        exercise_name: str,
    ) -> None:
        """Decode and animate on the UI thread (lightbox only)."""
        try:
            pixmap = QPixmap(str(avif_path))
            if not pixmap.isNull():
                label_size = label_widget.size()
                scaled_pixmap = pixmap.scaled(
                    label_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label_widget.setPixmap(scaled_pixmap)
                if not _avif_is_animated(avif_path):
                    return

            try:
                import pillow_avif  # noqa: F401, PLC0415
            except ImportError as import_error:
                logger.warning("AVIF plugin import error: %s", import_error)
                label_widget.setText(f"AVIF plugin not available:\n{exercise_name}")
                return

            with Image.open(avif_path) as pil_image:
                if getattr(pil_image, "is_animated", False):
                    frames: list[QPixmap] = []
                    label_size = label_widget.size()
                    for frame_index in range(getattr(pil_image, "n_frames", 1)):
                        pil_image.seek(frame_index)
                        frame = pil_image.copy()
                        scaled_pixmap = self._pil_frame_to_pixmap(frame, label_size=label_size)
                        if scaled_pixmap is not None and not scaled_pixmap.isNull():
                            frames.append(scaled_pixmap)

                    if frames:
                        data["frames"] = frames
                        label_widget.setPixmap(frames[0])
                        try:
                            duration = int(pil_image.info.get("duration", _DEFAULT_FRAME_DURATION_MS))
                        except Exception:
                            duration = _DEFAULT_FRAME_DURATION_MS
                        self._start_animation_timer(data, key, duration)
                        return
                else:
                    label_size = label_widget.size()
                    scaled_pixmap = self._pil_frame_to_pixmap(pil_image, label_size=label_size)
                    if scaled_pixmap is not None and not scaled_pixmap.isNull():
                        label_widget.setPixmap(scaled_pixmap)
                        return
        except Exception as e:
            logger.exception("Error loading AVIF %s", avif_path)
            label_widget.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")
            return

        label_widget.setText(f"Cannot load AVIF:\n{exercise_name}")

    def _next_avif_frame(self, label_key: str | AvifLabelKey) -> None:
        """Show next frame in AVIF animation for specific label.

        Args:

        - `label_key` (`str`): Key identifying which label to update.

        """
        key = self._normalize_label_key(label_key)
        frames = self.avif_data[key]["frames"]
        if not frames or not isinstance(frames, list):
            return

        current_frame_index = self.avif_data[key]["current_frame"]
        if not isinstance(current_frame_index, int):
            return

        current_frame = (current_frame_index + 1) % len(frames)
        self.avif_data[key]["current_frame"] = current_frame

        label_widget = self.label_widgets.get(key)
        if label_widget:
            label_widget.setPixmap(frames[current_frame])

    def _normalize_label_key(self, label_key: str | AvifLabelKey) -> AvifLabelKey:
        """Normalize external key (str) into `AvifLabelKey`."""
        if isinstance(label_key, AvifLabelKey):
            return label_key
        try:
            return AvifLabelKey(label_key)
        except ValueError as exc:
            allowed = ", ".join(k.value for k in AvifLabelKey)
            msg = f"Unknown label_key '{label_key}'. Allowed: {allowed}"
            raise KeyError(msg) from exc

    def _on_frame_worker_failed(self, label_key: object, exercise_name: object, message: str) -> None:
        """Log background decode failure when the slot is still current."""
        if not isinstance(label_key, AvifLabelKey) or not isinstance(exercise_name, str):
            return
        data = self.avif_data.get(label_key)
        if data is None or data.get("exercise") != exercise_name:
            return
        logger.warning("AVIF animation decode failed for %s (%s): %s", exercise_name, label_key, message)

    def _pil_frame_to_pixmap(self, frame: Image.Image, *, label_size: QSize) -> QPixmap | None:
        """Convert a PIL frame to a scaled QPixmap for the given label size."""
        png_bytes = _pil_frame_to_png_bytes(frame)
        if png_bytes is None:
            return None
        pixmap = QPixmap()
        pixmap.loadFromData(png_bytes)
        if pixmap.isNull():
            return None
        return pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _rename_avif_file(self, old_name: str, new_name: str, *, high: bool) -> bool:
        """Rename one AVIF (small or high). Return `True` when a file was renamed."""
        source = self.get_exercise_avif_path(old_name, high=high)
        if source is None:
            return False

        destination = self._exercise_avif_file(new_name, high=high)
        if destination is None:
            return False

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() == destination.resolve():
                if source.name != destination.name:
                    temp = source.with_name(f"{source.stem}.__rename__.avif")
                    source.rename(temp)
                    temp.rename(destination)
            else:
                if destination.exists():
                    destination.unlink()
                source.rename(destination)
        except OSError:
            logger.exception("Failed to rename exercise AVIF %s -> %s", source, destination)
            return False
        return True

    def _retarget_exercise_name(self, old_name: str, new_name: str) -> None:
        """Point loaded label slots from `old_name` to `new_name` after a file rename."""
        for data in self.avif_data.values():
            if data.get("exercise") == old_name:
                data["exercise"] = new_name

    def _start_animation_timer(self, data: dict, key: AvifLabelKey, duration_ms: int) -> None:
        """Start or replace the slot timer using stored playback speed."""
        old_timer = data.get("timer")
        if isinstance(old_timer, QTimer):
            old_timer.stop()
        data["duration_ms"] = max(1, int(duration_ms) if duration_ms else _DEFAULT_FRAME_DURATION_MS)
        speed = float(data.get("speed") or 1.0)
        new_timer = QTimer(self)
        new_timer.timeout.connect(lambda: self._next_avif_frame(key))
        data["timer"] = new_timer
        new_timer.start(animation_interval_ms(data["duration_ms"], speed))

    def _start_frame_worker(self, avif_path: Path, key: AvifLabelKey, exercise_name: str) -> None:
        """Kick off a background decode for animated frames."""
        generation = self._frame_generations.get(key, 0) + 1
        self._frame_generations[key] = generation
        previous = self._frame_workers.get(key)
        if previous is not None:
            previous.frames_ready.disconnect()
            previous.decode_failed.disconnect()

        worker = _AvifFramesWorker(
            avif_path=avif_path,
            label_key=key,
            exercise_name=exercise_name,
            generation=generation,
            parent=self,
        )
        worker.frames_ready.connect(
            lambda label_key, name, frames, duration, gen=generation: self._apply_decoded_frames(
                label_key,
                name,
                frames,
                duration,
                generation=gen,
            )
        )
        worker.decode_failed.connect(self._on_frame_worker_failed)

        def _clear_if_current() -> None:
            if self._frame_workers.get(key) is worker:
                self._frame_workers[key] = None

        worker.finished.connect(_clear_if_current)
        worker.finished.connect(worker.deleteLater)
        self._frame_workers[key] = worker
        worker.start()


class _AvifFramesWorker(QThread):
    """Decode animated AVIF frames to PNG bytes off the UI thread."""

    frames_ready = Signal(object, object, list, int)  # key, exercise, png_frames, duration_ms
    decode_failed = Signal(object, object, str)  # key, exercise, message

    def __init__(
        self,
        *,
        avif_path: Path,
        label_key: AvifLabelKey,
        exercise_name: str,
        generation: int,
        parent: QObject | None = None,
    ) -> None:
        """Store decode parameters for `run()`."""
        super().__init__(parent)
        self._avif_path = avif_path
        self._label_key = label_key
        self._exercise_name = exercise_name
        self.generation = generation

    def run(self) -> None:
        """Decode all frames; emit PNG byte lists for the UI thread."""
        try:
            import pillow_avif  # noqa: F401, PLC0415
        except ImportError as import_error:
            self.decode_failed.emit(self._label_key, self._exercise_name, str(import_error))
            return

        try:
            png_frames, duration = _decode_avif_png_frames(self._avif_path)
        except Exception as error:
            logger.exception("Background AVIF decode failed for %s", self._avif_path)
            self.decode_failed.emit(self._label_key, self._exercise_name, str(error))
            return

        if not png_frames:
            self.decode_failed.emit(self._label_key, self._exercise_name, "No frames decoded")
            return
        self.frames_ready.emit(self._label_key, self._exercise_name, png_frames, duration)


def animation_interval_ms(duration_ms: int, speed: float) -> int:
    """Return the timer interval for one animation frame at `speed`.

    Args:

    - `duration_ms` (`int`): Native frame duration in milliseconds.
    - `speed` (`float`): Playback multiplier. `1.0` is native speed.

    Returns:

    - `int`: Timer interval in milliseconds, at least `1`.

    """
    native = max(1, int(duration_ms) if duration_ms else _DEFAULT_FRAME_DURATION_MS)
    factor = float(speed) if speed else _SPEED_MIN
    factor = max(_SPEED_MIN, factor)
    return max(1, round(native / factor))


def load_image_pixmap(file_path: Path | str) -> QPixmap | None:
    """Load a pixmap from an image file, applying EXIF orientation when present.

    Uses Qt `QImageReader` with auto-transform for common formats. Falls back to
    Pillow (with `exif_transpose`) for AVIF when Qt cannot decode it.

    Args:

    - `file_path` (`Path | str`): Path to the image file.

    Returns:

    - `QPixmap | None`: Loaded pixmap or `None` if loading failed.

    """
    path = Path(file_path)
    reader = QImageReader(str(path))
    reader.setAutoTransform(True)
    image = reader.read()
    if not image.isNull():
        return QPixmap.fromImage(image)

    if path.suffix.lower() != ".avif":
        return None

    try:
        import pillow_avif  # noqa: F401, PLC0415
    except ModuleNotFoundError:
        return None

    try:
        with Image.open(path) as pil_image:
            if getattr(pil_image, "is_animated", False):
                pil_image.seek(0)
            oriented = ImageOps.exif_transpose(pil_image)
            frame = (oriented or pil_image).convert("RGBA")
            buffer = io.BytesIO()
            frame.save(buffer, format="PNG")
            buffer.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            return pixmap if not pixmap.isNull() else None
    except Exception:  # pragma: no cover - fallback path
        logger.exception("Failed to load AVIF pixmap from %s", path)
    return None


def _avif_is_animated(avif_path: Path) -> bool:
    """Return whether `avif_path` is an animated AVIF (Pillow metadata only)."""
    try:
        import pillow_avif  # noqa: F401, PLC0415
    except ImportError:
        return False
    try:
        with Image.open(avif_path) as pil_image:
            return bool(getattr(pil_image, "is_animated", False) and getattr(pil_image, "n_frames", 1) > 1)
    except Exception:
        return False


def _decode_avif_png_frames(avif_path: Path) -> tuple[list[bytes], int]:
    """Decode every AVIF frame to PNG bytes. Safe to call from a worker thread."""
    with Image.open(avif_path) as pil_image:
        try:
            duration = int(pil_image.info.get("duration", _DEFAULT_FRAME_DURATION_MS))
        except Exception:
            duration = _DEFAULT_FRAME_DURATION_MS

        frame_count = getattr(pil_image, "n_frames", 1) if getattr(pil_image, "is_animated", False) else 1
        png_frames: list[bytes] = []
        for frame_index in range(frame_count):
            if frame_count > 1:
                pil_image.seek(frame_index)
            png_bytes = _pil_frame_to_png_bytes(pil_image.copy())
            if png_bytes is not None:
                png_frames.append(png_bytes)
        return png_frames, duration


def _pil_frame_to_png_bytes(frame: Image.Image) -> bytes | None:
    """Flatten a PIL frame to RGB PNG bytes (no Qt objects)."""
    if frame.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", frame.size, (255, 255, 255))
        if frame.mode == "P":
            frame = frame.convert("RGBA")
        if frame.mode in ("RGBA", "LA"):
            background.paste(frame, mask=frame.split()[-1])
        else:
            background.paste(frame)
        frame = background
    elif frame.mode != "RGB":
        frame = frame.convert("RGB")

    buffer = io.BytesIO()
    frame.save(buffer, format="PNG")
    return buffer.getvalue()
