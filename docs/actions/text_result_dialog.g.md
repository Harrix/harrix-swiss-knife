---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_result_dialog.py`

## 🔧 Function `append_result_action_buttons`

```python
def append_result_action_buttons(dialog: QDialog, button_layout: QHBoxLayout) -> None
```

Add optional rerun/rewrite buttons that close the dialog with custom result codes.

<details>
<summary>Code:</summary>

```python
def append_result_action_buttons(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    rerun_button: bool = False,
    rewrite_button: bool = False,
) -> None:
    if rerun_button:
        rerun_btn = QPushButton(RERUN_BUTTON_LABEL)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = QPushButton(REWRITE_BUTTON_LABEL)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)
```

</details>
