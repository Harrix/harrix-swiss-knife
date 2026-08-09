---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `library.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PhotosLibrary`](#%EF%B8%8F-class-photoslibrary)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `ensure_fresh`](#%EF%B8%8F-method-ensure_fresh)
  - [⚙️ Method `find_relative_path`](#%EF%B8%8F-method-find_relative_path)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `remember`](#%EF%B8%8F-method-remember)
  - [⚙️ Method `unique_hash_count (property)`](#%EF%B8%8F-method-unique_hash_count-property)
  - [⚙️ Method `warm_in_background`](#%EF%B8%8F-method-warm_in_background)

</details>

## 🏛️ Class `PhotosLibrary`

```python
class PhotosLibrary
```

Index image files under `photos_dir` (all subfolders) by SHA-256.

New sync uploads still write into the root of `photos_dir`; this catalog is
only used to detect content that already exists anywhere in the tree.

<details>
<summary>Code:</summary>

```python
class PhotosLibrary:

    def __init__(self, photos_dir: Path) -> None:
        """Create a library scanner for `photos_dir`."""
        self._photos_dir = photos_dir
        self._cache_path = photos_dir / _SYNC_META_DIR / "library-hashes.json"
        self._lock = threading.Lock()
        self._by_hash: dict[str, str] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._last_refresh_at: float | None = None
        self._load_cache()

    def ensure_fresh(self, *, max_age_sec: float = _DEFAULT_MAX_AGE_SEC) -> None:
        """Refresh only when the index is missing or older than `max_age_sec`."""
        with self._lock:
            if self._last_refresh_at is not None and (time.monotonic() - self._last_refresh_at) < max_age_sec:
                return
            self._refresh_unlocked()

    def find_relative_path(self, content_hash: str) -> str | None:
        """Return a relative path (POSIX-ish) for `content_hash`, if any."""
        key = content_hash.strip().lower()
        if not key:
            return None
        with self._lock:
            if not self._by_hash and self._last_refresh_at is None:
                self._refresh_unlocked()
            return self._by_hash.get(key)

    def refresh(self) -> None:
        """Rescan the tree and refresh hash → relative-path mappings."""
        with self._lock:
            self._refresh_unlocked()

    def remember(self, relative_path: str, content_hash: str) -> None:
        """Record a just-written file without a full rescan."""
        rel = _normalize_rel(relative_path)
        digest = content_hash.strip().lower()
        if not rel or not digest:
            return
        path = self._photos_dir / rel
        try:
            stat = path.stat()
        except OSError:
            return
        with self._lock:
            self._file_cache[rel] = {
                "size": stat.st_size,
                "mtime_ns": getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000)),
                "hash": digest,
            }
            self._by_hash[digest] = rel
            self._save_cache_unlocked()

    @property
    def unique_hash_count(self) -> int:
        """Number of distinct content hashes currently indexed."""
        with self._lock:
            return len(self._by_hash)

    def warm_in_background(self, *, on_done: Callable[[], None] | None = None) -> None:
        """Start a daemon scan so the first phone manifest is less likely to time out."""

        def run() -> None:
            try:
                self.refresh()
            except Exception:
                logger.exception("Photo library background scan failed")
            if on_done is not None:
                try:
                    on_done()
                except Exception:
                    logger.exception("Photo library warm callback failed")

        threading.Thread(target=run, name="photo-sync-library-warm", daemon=True).start()

    def _load_cache(self) -> None:
        if not self._cache_path.is_file():
            return
        try:
            raw = json.loads(self._cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        files = raw.get("files") if isinstance(raw, dict) else None
        if not isinstance(files, dict):
            return
        loaded: dict[str, dict[str, Any]] = {}
        by_hash: dict[str, str] = {}
        for rel, value in files.items():
            if not isinstance(value, dict):
                continue
            digest = str(value.get("hash", "")).strip().lower()
            if not digest:
                continue
            norm = _normalize_rel(str(rel))
            loaded[norm] = {
                "size": value.get("size"),
                "mtime_ns": value.get("mtime_ns"),
                "hash": digest,
            }
            by_hash.setdefault(digest, norm)
        self._file_cache = loaded
        self._by_hash = by_hash
        # Treat disk cache as a starting point; still refresh soon, but lookups work immediately.
        if by_hash:
            self._last_refresh_at = time.monotonic()

    def _refresh_unlocked(self) -> None:
        photos_dir = self._photos_dir
        if not photos_dir.is_dir():
            self._by_hash = {}
            self._file_cache = {}
            self._last_refresh_at = time.monotonic()
            return

        next_cache: dict[str, dict[str, Any]] = {}
        by_hash: dict[str, str] = {}
        skipped_cloud = 0
        for path in photos_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _IMAGE_SUFFIXES:
                continue
            if path.name.endswith(".partial"):
                continue
            try:
                relative = path.relative_to(photos_dir)
            except ValueError:
                continue
            if _SYNC_META_DIR in relative.parts:
                continue
            rel = relative.as_posix()
            try:
                stat = path.stat()
            except OSError:
                continue
            if _is_cloud_placeholder(stat):
                skipped_cloud += 1
                continue
            mtime_ns = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000))
            size = stat.st_size
            cached = self._file_cache.get(rel)
            if (
                cached is not None
                and cached.get("size") == size
                and cached.get("mtime_ns") == mtime_ns
                and isinstance(cached.get("hash"), str)
            ):
                digest = str(cached["hash"]).lower()
            else:
                try:
                    digest = _sha256_file(path)
                except OSError:
                    continue
            next_cache[rel] = {"size": size, "mtime_ns": mtime_ns, "hash": digest}
            # Prefer the first path when duplicates share a hash.
            by_hash.setdefault(digest, rel)

        self._file_cache = next_cache
        self._by_hash = by_hash
        self._last_refresh_at = time.monotonic()
        self._save_cache_unlocked()
        if skipped_cloud:
            logger.info("Photo library scan skipped %s cloud-only placeholder file(s)", skipped_cloud)

    def _save_cache_unlocked(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"files": dict(sorted(self._file_cache.items()))}
        tmp = self._cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self._cache_path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, photos_dir: Path) -> None
```

Create a library scanner for `photos_dir`.

<details>
<summary>Code:</summary>

```python
def __init__(self, photos_dir: Path) -> None:
        self._photos_dir = photos_dir
        self._cache_path = photos_dir / _SYNC_META_DIR / "library-hashes.json"
        self._lock = threading.Lock()
        self._by_hash: dict[str, str] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._last_refresh_at: float | None = None
        self._load_cache()
```

</details>

### ⚙️ Method `ensure_fresh`

```python
def ensure_fresh(self, *, max_age_sec: float = _DEFAULT_MAX_AGE_SEC) -> None
```

Refresh only when the index is missing or older than `max_age_sec`.

<details>
<summary>Code:</summary>

```python
def ensure_fresh(self, *, max_age_sec: float = _DEFAULT_MAX_AGE_SEC) -> None:
        with self._lock:
            if self._last_refresh_at is not None and (time.monotonic() - self._last_refresh_at) < max_age_sec:
                return
            self._refresh_unlocked()
```

</details>

### ⚙️ Method `find_relative_path`

```python
def find_relative_path(self, content_hash: str) -> str | None
```

Return a relative path (POSIX-ish) for `content_hash`, if any.

<details>
<summary>Code:</summary>

```python
def find_relative_path(self, content_hash: str) -> str | None:
        key = content_hash.strip().lower()
        if not key:
            return None
        with self._lock:
            if not self._by_hash and self._last_refresh_at is None:
                self._refresh_unlocked()
            return self._by_hash.get(key)
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self) -> None
```

Rescan the tree and refresh hash → relative-path mappings.

<details>
<summary>Code:</summary>

```python
def refresh(self) -> None:
        with self._lock:
            self._refresh_unlocked()
```

</details>

### ⚙️ Method `remember`

```python
def remember(self, relative_path: str, content_hash: str) -> None
```

Record a just-written file without a full rescan.

<details>
<summary>Code:</summary>

```python
def remember(self, relative_path: str, content_hash: str) -> None:
        rel = _normalize_rel(relative_path)
        digest = content_hash.strip().lower()
        if not rel or not digest:
            return
        path = self._photos_dir / rel
        try:
            stat = path.stat()
        except OSError:
            return
        with self._lock:
            self._file_cache[rel] = {
                "size": stat.st_size,
                "mtime_ns": getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000)),
                "hash": digest,
            }
            self._by_hash[digest] = rel
            self._save_cache_unlocked()
```

</details>

### ⚙️ Method `unique_hash_count (property)`

```python
def unique_hash_count(self) -> int
```

Number of distinct content hashes currently indexed.

<details>
<summary>Code:</summary>

```python
def unique_hash_count(self) -> int:
        with self._lock:
            return len(self._by_hash)
```

</details>

### ⚙️ Method `warm_in_background`

```python
def warm_in_background(self, *, on_done: Callable[[], None] | None = None) -> None
```

Start a daemon scan so the first phone manifest is less likely to time out.

<details>
<summary>Code:</summary>

```python
def warm_in_background(self, *, on_done: Callable[[], None] | None = None) -> None:

        def run() -> None:
            try:
                self.refresh()
            except Exception:
                logger.exception("Photo library background scan failed")
            if on_done is not None:
                try:
                    on_done()
                except Exception:
                    logger.exception("Photo library warm callback failed")

        threading.Thread(target=run, name="photo-sync-library-warm", daemon=True).start()
```

</details>
