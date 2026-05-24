---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_clipboard_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeClipboardDialog`](#%EF%B8%8F-class-onoptimizeclipboarddialog)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnOptimizeClipboardDialog`

```python
class OnOptimizeClipboardDialog(ActionBase)
```

Optimize an image from the clipboard with custom naming.

This action extends OnOptimizeClipboard by prompting the user to provide
a custom filename for the optimized image, allowing for more organized
image management in the output directory.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboardDialog(ActionBase):

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize an image from the clipboard with custom naming."""
        OnOptimizeClipboard().execute(is_dialog=True)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Optimize an image from the clipboard with custom naming.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        OnOptimizeClipboard().execute(is_dialog=True)
```

</details>
