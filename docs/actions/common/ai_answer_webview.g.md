---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_answer_webview.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `create_ai_answer_webview`](#-function-create_ai_answer_webview)
- [🔧 Function `load_ai_answer_html`](#-function-load_ai_answer_html)
- [🔧 Function `webengine_available`](#-function-webengine_available)

</details>

## 🔧 Function `create_ai_answer_webview`

```python
def create_ai_answer_webview(parent: QWidget | None = None) -> QWidget
```

Create a `QWebEngineView` configured for local Harrix template assets.

<details>
<summary>Code:</summary>

```python
def create_ai_answer_webview(parent: QWidget | None = None) -> QWidget:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: PLC0415

    view = QWebEngineView(parent)
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    view.setMinimumHeight(280)
    return view
```

</details>

## 🔧 Function `load_ai_answer_html`

```python
def load_ai_answer_html(view: QWidget, html: str, *, dist_dir: Path) -> None
```

Load assembled HTML with `dist_dir` as the document base URL.

<details>
<summary>Code:</summary>

```python
def load_ai_answer_html(view: QWidget, html: str, *, dist_dir: Path) -> None:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: PLC0415

    if not isinstance(view, QWebEngineView):
        msg = f"Expected QWebEngineView, got {type(view)!r}"
        raise TypeError(msg)
    base = QUrl.fromLocalFile(str(dist_dir.resolve().as_posix()) + "/")
    view.setHtml(html, base)
```

</details>

## 🔧 Function `webengine_available`

```python
def webengine_available() -> bool
```

Return whether `QWebEngineView` can be imported in this environment.

<details>
<summary>Code:</summary>

```python
def webengine_available() -> bool:
    global _webengine_available  # noqa: PLW0603
    if _webengine_available is not None:
        return _webengine_available
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401, PLC0415
    except Exception:
        _webengine_available = False
    else:
        _webengine_available = True
    return _webengine_available
```

</details>
