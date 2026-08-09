---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `durable_io.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `replace_file`](#-function-replace_file)
- [🔧 Function `write_bytes_replacing`](#-function-write_bytes_replacing)
- [🔧 Function `write_text_replacing`](#-function-write_text_replacing)

</details>

## 🔧 Function `replace_file`

```python
def replace_file(src: Path, dest: Path) -> None
```

Move `src` onto `dest`, retrying when cloud sync locks the target.

Dropbox on Windows often raises `PermissionError: [WinError 5]` for
replace even though an in-place overwrite of `dest` still works.

<details>
<summary>Code:</summary>

```python
def replace_file(src: Path, dest: Path) -> None:
    last_error: OSError | None = None
    for delay in (0.0, *_RETRY_DELAYS_SEC):
        if delay:
            time.sleep(delay)
        try:
            src.replace(dest)
        except PermissionError as exc:
            last_error = exc
        except OSError as exc:
            winerror = getattr(exc, "winerror", None)
            if winerror not in {5, 32} and exc.errno not in {13, 16}:
                raise
            last_error = exc
        else:
            return

    # Fallback: overwrite destination contents, then drop the temp file.
    try:
        dest.write_bytes(src.read_bytes())
        src.unlink(missing_ok=True)
    except OSError as exc:
        if last_error is not None:
            raise last_error from exc
        raise
    else:
        logger.warning("Used in-place write after replace failed for %s", dest)
```

</details>

## 🔧 Function `write_bytes_replacing`

```python
def write_bytes_replacing(path: Path, data: bytes, *, tmp_suffix: str = '.tmp') -> None
```

Write `data` via a unique sibling temp file, then replace `path`.

<details>
<summary>Code:</summary>

```python
def write_bytes_replacing(path: Path, data: bytes, *, tmp_suffix: str = ".tmp") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex[:8]}{tmp_suffix}")
    try:
        tmp.write_bytes(data)
        replace_file(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
```

</details>

## 🔧 Function `write_text_replacing`

```python
def write_text_replacing(path: Path, text: str, *, encoding: str = 'utf-8') -> None
```

Write text via a unique sibling temp file, then replace `path`.

<details>
<summary>Code:</summary>

```python
def write_text_replacing(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    write_bytes_replacing(path, text.encode(encoding), tmp_suffix=".tmp")
```

</details>
