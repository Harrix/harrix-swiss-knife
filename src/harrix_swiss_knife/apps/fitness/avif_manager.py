"""AVIF file manager for fitness app.

This module provides a class for managing AVIF file loading, animation, and display
in the fitness tracking application.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

if TYPE_CHECKING:
    from PySide6.QtWidgets import QLabel


class AvifManager:
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

    def __init__(self, avif_dir: Path | str) -> None:
        """Initialize the AVIF manager.

        Args:
            - `avif_dir` (`Path | str`): Directory path containing AVIF files.

        """
        self.avif_dir = Path(avif_dir)
        self.avif_data: dict[str, dict] = {
            "main": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "exercises": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "types": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "charts": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "statistics": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
        }
        self.label_widgets: dict[str, QLabel | None] = {
            "main": None,
            "exercises": None,
            "types": None,
            "charts": None,
            "statistics": None,
        }

    def get_exercise_avif_path(self, exercise_name: str) -> Path | None:
        """Get the path to the AVIF file for the given exercise.

        Args:
            - `exercise_name` (`str`): Name of the exercise.

        Returns:
            - `Path | None`: Path to the AVIF file if it exists, None otherwise.

        """
        if not exercise_name:
            return None

        avif_path = self.avif_dir / f"{exercise_name}.avif"
        return avif_path if avif_path.exists() else None

    def load_avif_pixmap(self, avif_path: Path) -> QPixmap | None:
        """Load a pixmap from an AVIF file, falling back to Pillow if needed.

        Args:
            - `avif_path` (`Path`): Path to the AVIF file.

        Returns:
            - `QPixmap | None`: Loaded pixmap or None if loading failed.

        """
        pixmap = QPixmap(str(avif_path))
        if not pixmap.isNull():
            return pixmap

        try:
            import pillow_avif  # noqa: F401, PLC0415
        except ModuleNotFoundError:
            return None

        try:
            with Image.open(avif_path) as pil_image:
                if getattr(pil_image, "is_animated", False):
                    pil_image.seek(0)
                frame = pil_image.convert("RGBA")
                buffer = io.BytesIO()
                frame.save(buffer, format="PNG")
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                return pixmap if not pixmap.isNull() else None
        except Exception as exc:  # pragma: no cover - fallback path
            print(f"Failed to load AVIF pixmap from {avif_path}: {exc}")
        return None

    def load_exercise_avif(
        self,
        exercise_name: str,
        label_widget: QLabel,
        label_key: str = "main",
    ) -> None:
        """Load and display AVIF animation for the given exercise using Pillow with AVIF support.

        Args:
            - `exercise_name` (`str`): Name of the exercise to load AVIF for.
            - `label_widget` (`QLabel`): Label widget to display the AVIF.
            - `label_key` (`str`): Key identifying which label to update
              ('main', 'exercises', 'types', 'charts', 'statistics'). Defaults to `"main"`.

        """
        # Get reference to data dict for this label
        data = self.avif_data[label_key]

        # Stop current animation if exists
        timer = data["timer"]
        if timer is not None and isinstance(timer, QTimer):
            timer.stop()
            data["timer"] = None

        data["frames"] = []
        data["current_frame"] = 0
        data["exercise"] = exercise_name

        # Clear label and reset alignment
        # Store label widget for this key
        self.label_widgets[label_key] = label_widget

        label_widget.clear()
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not exercise_name:
            label_widget.setText("No exercise selected")
            return

        # Get path to AVIF
        avif_path = self.get_exercise_avif_path(exercise_name)

        if avif_path is None:
            label_widget.setText(f"No AVIF found for:\n{exercise_name}")
            return

        try:
            # Try Qt native first
            pixmap = QPixmap(str(avif_path))

            if not pixmap.isNull():
                label_size = label_widget.size()
                scaled_pixmap = pixmap.scaled(
                    label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                label_widget.setPixmap(scaled_pixmap)
                return

            # Fallback to Pillow with AVIF plugin for animation
            try:
                import pillow_avif  # noqa: F401, PLC0415

                # Open with Pillow
                pil_image = Image.open(avif_path)

                # Handle animated AVIF
                if getattr(pil_image, "is_animated", False):
                    # Extract all frames
                    frames: list[QPixmap] = []
                    label_size = label_widget.size()

                    for frame_index in range(getattr(pil_image, "n_frames", 1)):
                        pil_image.seek(frame_index)

                        # Create a copy of the frame
                        frame = pil_image.copy()

                        # Convert to RGB if needed
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

                        # Convert PIL image to QPixmap
                        buffer = io.BytesIO()
                        frame.save(buffer, format="PNG")
                        buffer.seek(0)

                        pixmap = QPixmap()
                        pixmap.loadFromData(buffer.getvalue())

                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation,
                            )
                            frames.append(scaled_pixmap)

                    if frames:
                        # Store frames in data dict
                        data["frames"] = frames

                        # Show first frame
                        label_widget.setPixmap(frames[0])

                        # Start animation timer
                        new_timer = QTimer()
                        new_timer.timeout.connect(lambda: self._next_avif_frame(label_key))
                        data["timer"] = new_timer

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        new_timer.start(duration)
                        return
                else:
                    # Static image
                    frame = pil_image

                    # Convert to RGB if needed
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

                    # Convert PIL image to QPixmap
                    buffer = io.BytesIO()
                    frame.save(buffer, format="PNG")
                    buffer.seek(0)

                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())

                    if not pixmap.isNull():
                        label_size = label_widget.size()
                        scaled_pixmap = pixmap.scaled(
                            label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                        )
                        label_widget.setPixmap(scaled_pixmap)
                        return

            except ImportError as import_error:
                print(f"Import error: {import_error}")
                label_widget.setText(f"AVIF plugin not available:\n{exercise_name}")
                return
            except Exception as pil_error:
                print(f"Pillow error: {pil_error}")

            label_widget.setText(f"Cannot load AVIF:\n{exercise_name}")

        except Exception as e:
            print(f"General error: {e}")
            label_widget.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")

    def _next_avif_frame(self, label_key: str) -> None:
        """Show next frame in AVIF animation for specific label.

        Args:
            - `label_key` (`str`): Key identifying which label to update.

        """
        frames = self.avif_data[label_key]["frames"]
        if not frames or not isinstance(frames, list):
            return

        current_frame_index = self.avif_data[label_key]["current_frame"]
        if not isinstance(current_frame_index, int):
            return

        current_frame = (current_frame_index + 1) % len(frames)
        self.avif_data[label_key]["current_frame"] = current_frame

        label_widget = self.label_widgets.get(label_key)
        if label_widget:
            label_widget.setPixmap(frames[current_frame])

    def get_current_exercise(self, label_key: str) -> str | None:
        """Get the current exercise name for a label key.

        Args:
            - `label_key` (`str`): Key identifying which label.

        Returns:
            - `str | None`: Current exercise name or None.

        """
        return self.avif_data.get(label_key, {}).get("exercise")
