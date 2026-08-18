---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog_load.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CatalogLoadWorker`](#%EF%B8%8F-class-catalogloadworker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)

</details>

## 🏛️ Class `CatalogLoadWorker`

```python
class CatalogLoadWorker(QObject)
```

Open or rebuild an icons catalog in a worker thread.

<details>
<summary>Code:</summary>

```python
class CatalogLoadWorker(QObject):

    succeeded = Signal(object, int)
    failed = Signal(str, int)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None:
        """Store the folder path, rebuild flag, and UI generation token."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
        self.generation = generation

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = rebuild_catalog(self._path) if self._rebuild else open_icons_folder(self._path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result", self.generation)
            else:
                self.succeeded.emit(catalog, self.generation)
        finally:
            self.finished.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None
```

Store the folder path, rebuild flag, and UI generation token.

<details>
<summary>Code:</summary>

```python
def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None:
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
        self.generation = generation
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Load the catalog and report the result.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        try:
            catalog = rebuild_catalog(self._path) if self._rebuild else open_icons_folder(self._path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result", self.generation)
            else:
                self.succeeded.emit(catalog, self.generation)
        finally:
            self.finished.emit()
```

</details>
