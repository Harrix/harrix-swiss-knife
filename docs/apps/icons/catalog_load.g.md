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
  - [⚙️ Method `request_cancel`](#%EF%B8%8F-method-request_cancel)
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
    cancelled = Signal(int)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None:
        """Store the folder path, rebuild flag, and UI generation token."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
        self.generation = generation
        self._cancel = threading.Event()

    def request_cancel(self) -> None:
        """Ask the running scan to stop at the next checkpoint."""
        self._cancel.set()

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = (
                rebuild_catalog(self._path, should_cancel=self._cancel.is_set)
                if self._rebuild
                else open_icons_folder(self._path, should_cancel=self._cancel.is_set)
            )
        except CatalogLoadCancelledError:
            self.cancelled.emit(self.generation)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if self._cancel.is_set():
                self.cancelled.emit(self.generation)
            elif not isinstance(catalog, IconCatalog):
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
        self._cancel = threading.Event()
```

</details>

### ⚙️ Method `request_cancel`

```python
def request_cancel(self) -> None
```

Ask the running scan to stop at the next checkpoint.

<details>
<summary>Code:</summary>

```python
def request_cancel(self) -> None:
        self._cancel.set()
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
            catalog = (
                rebuild_catalog(self._path, should_cancel=self._cancel.is_set)
                if self._rebuild
                else open_icons_folder(self._path, should_cancel=self._cancel.is_set)
            )
        except CatalogLoadCancelledError:
            self.cancelled.emit(self.generation)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if self._cancel.is_set():
                self.cancelled.emit(self.generation)
            elif not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result", self.generation)
            else:
                self.succeeded.emit(catalog, self.generation)
        finally:
            self.finished.emit()
```

</details>
