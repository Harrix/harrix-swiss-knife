"""In-memory LRU cache for Vector Icons lightbox previews."""

from __future__ import annotations

from collections import OrderedDict
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from PySide6.QtGui import QImage

DEFAULT_MAX_ENTRIES = 48
PREVIEW_RENDER_SIZE = 2048


class LightboxImageCache:
    """Keep recent high-resolution lightbox rasters keyed by path fingerprint."""

    def __init__(self, *, max_entries: int = DEFAULT_MAX_ENTRIES) -> None:
        """Create an empty LRU store.

        Args:

        - `max_entries` (`int`): Maximum retained images. Defaults to `48`.

        """
        self._max_entries = max(1, max_entries)
        self._items: OrderedDict[str, QImage] = OrderedDict()

    def clear(self) -> None:
        """Drop all cached images."""
        self._items.clear()

    def get(self, path: Path, size: int) -> QImage | None:
        """Return a cached image when the path fingerprint still matches.

        Args:

        - `path` (`Path`): Icon file path.
        - `size` (`int`): Raster side length in pixels.

        Returns:

        - `QImage | None`: Cached image, or `None` on miss.

        """
        key = self._key(path, size)
        if key is None:
            return None
        image = self._items.get(key)
        if image is None:
            return None
        self._items.move_to_end(key)
        return image

    def put(self, path: Path, size: int, image: QImage) -> None:
        """Store `image` for `path` and `size`, evicting the oldest entries.

        Args:

        - `path` (`Path`): Icon file path.
        - `size` (`int`): Raster side length in pixels.
        - `image` (`QImage`): Rendered preview to keep.

        """
        key = self._key(path, size)
        if key is None or image.isNull():
            return
        self._items[key] = image
        self._items.move_to_end(key)
        while len(self._items) > self._max_entries:
            self._items.popitem(last=False)

    @property
    def size(self) -> int:
        """Number of cached images."""
        return len(self._items)

    def _key(self, path: Path, size: int) -> str | None:
        try:
            resolved = path.resolve()
            stat = resolved.stat()
        except OSError:
            return None
        return f"{resolved}|{stat.st_mtime_ns}|{stat.st_size}|{size}"


@lru_cache(maxsize=1)
def lightbox_image_cache() -> LightboxImageCache:
    """Return the process-wide lightbox image cache."""
    return LightboxImageCache()
