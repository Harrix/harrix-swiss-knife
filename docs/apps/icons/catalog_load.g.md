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

    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False) -> None:
        """Store the folder path and whether to force a catalog rebuild."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = rebuild_catalog(self._path) if self._rebuild else open_icons_folder(self._path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc))
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result")
            else:
                self.succeeded.emit(catalog)
        finally:
            self.finished.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, path: Path, *, rebuild: bool = False) -> None
```

Store the folder path and whether to force a catalog rebuild.

<details>
<summary>Code:</summary>

```python
def __init__(self, path: Path, *, rebuild: bool = False) -> None:
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
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
            self.failed.emit(str(exc))
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result")
            else:
                self.succeeded.emit(catalog)
        finally:
            self.finished.emit()
```

</details>
