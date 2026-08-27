"""Background worker that converts exercise media to AVIF."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from harrix_swiss_knife.apps.common.exercise_media import save_exercise_avif

if TYPE_CHECKING:
    from PySide6.QtCore import QObject


class ExerciseMediaSaveWorker(QThread):
    """Optimize and store exercise media off the UI thread."""

    save_completed = Signal(str, str)  # exercise_name, target_path
    save_failed = Signal(str, str)  # exercise_name, error_message

    def __init__(
        self,
        source_path: str,
        exercise_name: str,
        avif_dir: Path | str,
        *,
        max_size: int | None = None,
        high_max_size: int | None = None,
        min_max_size: int | None = None,
        project_root: Path | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Store conversion parameters for `run()`."""
        super().__init__(parent)
        self._source_path = source_path
        self._exercise_name = exercise_name
        self._avif_dir = Path(avif_dir)
        self._max_size = max_size
        self._high_max_size = high_max_size
        self._min_max_size = min_max_size
        self._project_root = project_root

    def run(self) -> None:
        """Convert media and emit success or failure."""
        try:
            target = save_exercise_avif(
                self._source_path,
                self._exercise_name,
                self._avif_dir,
                project_root=self._project_root,
                max_size=self._max_size,
                high_max_size=self._high_max_size,
                min_max_size=self._min_max_size,
            )
        except Exception as error:
            self.save_failed.emit(self._exercise_name, str(error))
            return
        self.save_completed.emit(self._exercise_name, str(target))
