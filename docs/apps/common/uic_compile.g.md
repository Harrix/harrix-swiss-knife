---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uic_compile.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `combine_utf16_surrogates`](#-function-combine_utf16_surrogates)
- [🔧 Function `compile_app_ui`](#-function-compile_app_ui)
- [🔧 Function `compile_ui`](#-function-compile_ui)
- [🔧 Function `install_safe_qt_translate`](#-function-install_safe_qt_translate)
- [🔧 Function `rewrite_uic_py`](#-function-rewrite_uic_py)
- [🔧 Function `rewrite_uic_source`](#-function-rewrite_uic_source)

</details>

## 🔧 Function `combine_utf16_surrogates`

```python
def combine_utf16_surrogates(text: str) -> str
```

Turn UTF-16 surrogate code points in `text` into real Unicode characters.

Args:

- `text` (`str`): String that may contain high+low surrogate pairs.

Returns:

- `str`: The same text, valid for UTF-8 (emoji combined from surrogate pairs).

<details>
<summary>Code:</summary>

```python
def combine_utf16_surrogates(text: str) -> str:
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return text.encode("utf-16", "surrogatepass").decode("utf-16")
    return text
```

</details>

## 🔧 Function `compile_app_ui`

```python
def compile_app_ui(app_name: str) -> Path
```

Run `pyside6-uic` for `apps/{app_name}/window.ui` and fix surrogate escapes.

Args:

- `app_name` (`str`): One of `finance`, `fitness`, `food`, `habits`.

Returns:

- `Path`: Path to the written `window.py`.

<details>
<summary>Code:</summary>

```python
def compile_app_ui(app_name: str) -> Path:
    if app_name not in _APP_UI_NAMES:
        allowed = ", ".join(sorted(_APP_UI_NAMES))
        msg = f"Unknown app {app_name!r}. Expected one of: {allowed}."
        raise ValueError(msg)
    ui_path = _APPS_ROOT / app_name / "window.ui"
    py_path = _APPS_ROOT / app_name / "window.py"
    compile_ui(ui_path, py_path)
    return py_path
```

</details>

## 🔧 Function `compile_ui`

```python
def compile_ui(ui_path: Path, py_path: Path) -> None
```

Run `pyside6-uic` and rewrite UTF-16 surrogate escapes in `py_path`.

Args:

- `ui_path` (`Path`): Input `.ui` file.
- `py_path` (`Path`): Output Python module path.

<details>
<summary>Code:</summary>

```python
def compile_ui(ui_path: Path, py_path: Path) -> None:
    if not ui_path.is_file():
        msg = f"UI file not found: {ui_path}"
        raise FileNotFoundError(msg)
    command = [*_pyside_uic_command(), str(ui_path), "-o", str(py_path)]
    subprocess.run(command, check=True)
    rewrite_uic_py(py_path)
```

</details>

## 🔧 Function `install_safe_qt_translate`

```python
def install_safe_qt_translate() -> None
```

Patch `QCoreApplication.translate` so UIC surrogate emoji does not crash.

`pyside6-uic` can emit UTF-16 surrogate pairs in Python string literals.
Python 3 cannot UTF-8-encode those, and `translate` then raises
`UnicodeEncodeError`. The patch combines surrogate pairs first.

<details>
<summary>Code:</summary>

```python
def install_safe_qt_translate() -> None:
    if _TRANSLATE_PATCH_INSTALLED[0]:
        return

    original = QCoreApplication.translate

    def translate(context: str, key: str, /, disambiguation: str | None = None, n: int = -1) -> str:
        return original(context, combine_utf16_surrogates(key), disambiguation, n)

    QCoreApplication.translate = translate  # ty: ignore[invalid-assignment]
    _TRANSLATE_PATCH_INSTALLED[0] = True
```

</details>

## 🔧 Function `rewrite_uic_py`

```python
def rewrite_uic_py(py_path: Path) -> bool
```

Rewrite UTF-16 surrogate-pair escapes in a generated UIC Python file.

Args:

- `py_path` (`Path`): Generated `window.py` (or any UIC output).

Returns:

- `bool`: `True` when the file changed.

<details>
<summary>Code:</summary>

```python
def rewrite_uic_py(py_path: Path) -> bool:
    text = py_path.read_text(encoding="utf-8")
    rewritten = rewrite_uic_source(text)
    if rewritten == text:
        return False
    py_path.write_text(rewritten, encoding="utf-8", newline="\n")
    return True
```

</details>

## 🔧 Function `rewrite_uic_source`

```python
def rewrite_uic_source(source: str) -> str
```

Replace UTF-16 surrogate-pair escapes in Python source with UCS-4 escapes.

Args:

- `source` (`str`): Generated UIC Python source.

Returns:

- `str`: Source with UCS-4 capital-U escapes instead of surrogate pairs.

<details>
<summary>Code:</summary>

```python
def rewrite_uic_source(source: str) -> str:
    return _SURROGATE_PAIR_RE.sub(_combined_unicode_escape, source)
```

</details>
