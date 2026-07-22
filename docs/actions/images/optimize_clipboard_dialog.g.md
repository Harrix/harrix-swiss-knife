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
class OnOptimizeClipboardDialog(OnOptimizeClipboard)
```

Optimize an image from the clipboard with custom naming.

This action extends OnOptimizeClipboard by prompting the user to provide
a custom filename for the optimized image, allowing for more organized
image management in the output directory.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboardDialog(OnOptimizeClipboard):

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Optimize an image from the clipboard with custom naming."""
        super().execute(*args, is_dialog=True, **kwargs)
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
def execute(self, *args: Any, **kwargs: Any) -> None:
        super().execute(*args, is_dialog=True, **kwargs)
```

</details>
