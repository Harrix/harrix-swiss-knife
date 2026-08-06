---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_modality.py`

## 🔧 Function `set_owner_window_modal`

```python
def set_owner_window_modal(widget: QWidget) -> None
```

Make `widget` modal only to its parent window hierarchy.

Must be called before `show()` / `exec()`; changing modality on an
already-visible window is ignored by Qt.

<details>
<summary>Code:</summary>

```python
def set_owner_window_modal(widget: QWidget) -> None:
    widget.setWindowModality(Qt.WindowModality.WindowModal)
```

</details>
