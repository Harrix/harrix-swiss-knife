---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lightbox_cache.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LightboxImageCache`](#%EF%B8%8F-class-lightboximagecache)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `get`](#%EF%B8%8F-method-get)
  - [⚙️ Method `put`](#%EF%B8%8F-method-put)
  - [⚙️ Method `size (property)`](#%EF%B8%8F-method-size-property)
- [🔧 Function `lightbox_image_cache`](#-function-lightbox_image_cache)

</details>

## 🏛️ Class `LightboxImageCache`

```python
class LightboxImageCache
```

Keep recent high-resolution lightbox rasters keyed by path fingerprint.

<details>
<summary>Code:</summary>

```python
class LightboxImageCache:

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, max_entries: int = DEFAULT_MAX_ENTRIES) -> None
```

Create an empty LRU store.

Args:

- `max_entries` (`int`): Maximum retained images. Defaults to `48`.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, max_entries: int = DEFAULT_MAX_ENTRIES) -> None:
        self._max_entries = max(1, max_entries)
        self._items: OrderedDict[str, QImage] = OrderedDict()
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Drop all cached images.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._items.clear()
```

</details>

### ⚙️ Method `get`

```python
def get(self, path: Path, size: int) -> QImage | None
```

Return a cached image when the path fingerprint still matches.

Args:

- `path` (`Path`): Icon file path.
- [`size`](#%EF%B8%8F-method-size-property) (`int`): Raster side length in pixels.

Returns:

- `QImage | None`: Cached image, or `None` on miss.

<details>
<summary>Code:</summary>

```python
def get(self, path: Path, size: int) -> QImage | None:
        key = self._key(path, size)
        if key is None:
            return None
        image = self._items.get(key)
        if image is None:
            return None
        self._items.move_to_end(key)
        return image
```

</details>

### ⚙️ Method `put`

```python
def put(self, path: Path, size: int, image: QImage) -> None
```

Store `image` for `path` and [`size`](#%EF%B8%8F-method-size-property), evicting the oldest entries.

Args:

- `path` (`Path`): Icon file path.
- [`size`](#%EF%B8%8F-method-size-property) (`int`): Raster side length in pixels.
- `image` (`QImage`): Rendered preview to keep.

<details>
<summary>Code:</summary>

```python
def put(self, path: Path, size: int, image: QImage) -> None:
        key = self._key(path, size)
        if key is None or image.isNull():
            return
        self._items[key] = image
        self._items.move_to_end(key)
        while len(self._items) > self._max_entries:
            self._items.popitem(last=False)
```

</details>

### ⚙️ Method `size (property)`

```python
def size(self) -> int
```

Number of cached images.

<details>
<summary>Code:</summary>

```python
def size(self) -> int:
        return len(self._items)
```

</details>

## 🔧 Function `lightbox_image_cache`

```python
def lightbox_image_cache() -> LightboxImageCache
```

Return the process-wide lightbox image cache.

<details>
<summary>Code:</summary>

```python
def lightbox_image_cache() -> LightboxImageCache:
    return LightboxImageCache()
```

</details>
