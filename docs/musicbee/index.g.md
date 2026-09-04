---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `index.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FileIndex`](#%EF%B8%8F-class-fileindex)
  - [⚙️ Method `existing_path`](#%EF%B8%8F-method-existing_path)
- [🏛️ Class `IndexedFile`](#%EF%B8%8F-class-indexedfile)
  - [⚙️ Method `basename_key (property)`](#%EF%B8%8F-method-basename_key-property)
- [🔧 Function `index_audio_files`](#-function-index_audio_files)

</details>

## 🏛️ Class `FileIndex`

```python
class FileIndex
```

Lookup tables for remapping missing playlist/library paths.

<details>
<summary>Code:</summary>

```python
class FileIndex:

    files: list[IndexedFile] = field(default_factory=list)
    by_basename: dict[str, list[IndexedFile]] = field(default_factory=dict)
    by_key: dict[str, IndexedFile] = field(default_factory=dict)

    def existing_path(self, path: str) -> Path | None:
        """Return the indexed file for `path` when it exists."""
        hit = self.by_key.get(normalize_path_key(path))
        if hit is not None:
            return hit.path
        candidate = Path(path)
        return candidate if candidate.is_file() else None
```

</details>

### ⚙️ Method `existing_path`

```python
def existing_path(self, path: str) -> Path | None
```

Return the indexed file for `path` when it exists.

<details>
<summary>Code:</summary>

```python
def existing_path(self, path: str) -> Path | None:
        hit = self.by_key.get(normalize_path_key(path))
        if hit is not None:
            return hit.path
        candidate = Path(path)
        return candidate if candidate.is_file() else None
```

</details>

## 🏛️ Class `IndexedFile`

```python
class IndexedFile
```

One audio file on disk.

<details>
<summary>Code:</summary>

```python
class IndexedFile:

    path: Path
    size: int

    @property
    def basename_key(self) -> str:
        """Casefolded file name."""
        return self.path.name.casefold()
```

</details>

### ⚙️ Method `basename_key (property)`

```python
def basename_key(self) -> str
```

Casefolded file name.

<details>
<summary>Code:</summary>

```python
def basename_key(self) -> str:
        return self.path.name.casefold()
```

</details>

## 🔧 Function `index_audio_files`

```python
def index_audio_files(root: Path, extensions: frozenset[str]) -> FileIndex
```

Walk [`root`](../apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) and collect audio files whose suffix is in `extensions`.

<details>
<summary>Code:</summary>

```python
def index_audio_files(root: Path, extensions: frozenset[str]) -> FileIndex:
    index = FileIndex()
    if not root.is_dir():
        return index
    suffixes = {item if item.startswith(".") else f".{item}" for item in extensions}
    suffixes = {item.casefold() for item in suffixes}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in suffixes:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        item = IndexedFile(path=path, size=size)
        index.files.append(item)
        index.by_basename.setdefault(item.basename_key, []).append(item)
        index.by_key[normalize_path_key(path)] = item
    return index
```

</details>
