---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_form_chrome.py`

## 🔧 Function `install_form_chrome`

```python
def install_form_chrome(app: QApplication) -> None
```

Install the shared form chrome polish filter once on `app`.

<details>
<summary>Code:</summary>

```python
def install_form_chrome(app: QApplication) -> None:
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP)
    if isinstance(existing, _FormChromeFilter):
        return
    event_filter = _FormChromeFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP, event_filter)
```

</details>
