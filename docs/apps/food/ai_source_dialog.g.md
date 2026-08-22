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
- [🔧 Function `create_food_dashboard_photo_dialog`](#-function-create_food_dashboard_photo_dialog)
- [🔧 Function `create_food_dashboard_text_dialog`](#-function-create_food_dashboard_text_dialog)

</details>

## 🏛️ Class `AiSourceDialog`

```python
class AiSourceDialog(TextImageSourceDialog)
```

Modal dialog to collect food source text and/or images.

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
        """Initialize the food AI source dialog."""
        super().__init__(
            parent,
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
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

Initialize the food AI source dialog.

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
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
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

## 🔧 Function `create_food_dashboard_photo_dialog`

```python
def create_food_dashboard_photo_dialog(parent: QWidget | None = None, *, max_image_side: int | None = None) -> TextImageSourceDialog
```

Build a photo-only, large-type dialog for the Food dashboard.

<details>
<summary>Code:</summary>

```python
def create_food_dashboard_photo_dialog(
    parent: QWidget | None = None,
    *,
    max_image_side: int | None = None,
) -> TextImageSourceDialog:
    return TextImageSourceDialog(
        parent,
        title="Add photo",
        description="Add a meal photo or nutrition label.",
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

## 🔧 Function `create_food_dashboard_text_dialog`

```python
def create_food_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog
```

Build a text-only, large-type dialog for the Food dashboard.

<details>
<summary>Code:</summary>

```python
def create_food_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog:
    return TextImageSourceDialog(
        parent,
        title="Write text",
        description="Describe what you ate. AI will turn this into a food log.",
        placeholder="Oatmeal with banana and coffee…",
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
