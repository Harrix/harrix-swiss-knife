---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_source_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AiSourceDialog`](#%EF%B8%8F-class-aisourcedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🔧 Function `create_finance_dashboard_photo_dialog`](#-function-create_finance_dashboard_photo_dialog)
- [🔧 Function `create_finance_dashboard_text_dialog`](#-function-create_finance_dashboard_text_dialog)

</details>

## 🏛️ Class `AiSourceDialog`

```python
class AiSourceDialog(TextImageSourceDialog)
```

Modal dialog to collect purchase source text and/or receipt images.

<details>
<summary>Code:</summary>

```python
class AiSourceDialog(TextImageSourceDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        max_image_side: int | None = None,
        initial_image_path: str | None = None,
        initial_image_paths: list[str] | None = None,
    ) -> None:
        """Initialize the finance AI source dialog."""
        super().__init__(
            parent,
            title="Add Purchases with AI",
            description=_FINANCE_AI_DESCRIPTION,
            placeholder=PURCHASE_TEXT_PLACEHOLDER,
            image_mode=ImagePickerMode.MULTI,
            show_skip_manual=True,
            accept_button_text="Send to AI",
            accept_button_emoji="🤖",
            accept_button_style=SEND_TO_AI_BUTTON_STYLE,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
            initial_image_paths=initial_image_paths,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, max_image_side: int | None = None, initial_image_path: str | None = None, initial_image_paths: list[str] | None = None) -> None
```

Initialize the finance AI source dialog.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        max_image_side: int | None = None,
        initial_image_path: str | None = None,
        initial_image_paths: list[str] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Add Purchases with AI",
            description=_FINANCE_AI_DESCRIPTION,
            placeholder=PURCHASE_TEXT_PLACEHOLDER,
            image_mode=ImagePickerMode.MULTI,
            show_skip_manual=True,
            accept_button_text="Send to AI",
            accept_button_emoji="🤖",
            accept_button_style=SEND_TO_AI_BUTTON_STYLE,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
            initial_image_paths=initial_image_paths,
        )
```

</details>

## 🔧 Function `create_finance_dashboard_photo_dialog`

```python
def create_finance_dashboard_photo_dialog(parent: QWidget | None = None, *, max_image_side: int | None = None) -> TextImageSourceDialog
```

Build a photo-only, large-type dialog for the Finance dashboard.

<details>
<summary>Code:</summary>

```python
def create_finance_dashboard_photo_dialog(
    parent: QWidget | None = None,
    *,
    max_image_side: int | None = None,
) -> TextImageSourceDialog:
    return TextImageSourceDialog(
        parent,
        title="Add photo",
        description="Add a receipt or purchase photo.",
        show_text=False,
        show_images=True,
        images_required=True,
        image_mode=ImagePickerMode.MULTI,
        image_label="Photo (drag, paste Ctrl+V, or select files):",
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        max_image_side=max_image_side,
        large_ui=True,
    )
```

</details>

## 🔧 Function `create_finance_dashboard_text_dialog`

```python
def create_finance_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog
```

Build a text-only, large-type dialog for the Finance dashboard.

<details>
<summary>Code:</summary>

```python
def create_finance_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog:
    return TextImageSourceDialog(
        parent,
        title="Write text",
        description="Describe the purchase. AI will turn this into a transaction list.",
        placeholder="Coffee and a sandwich, 450 rubles…",
        show_text=True,
        text_required=True,
        show_images=False,
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        large_ui=True,
    )
```

</details>
