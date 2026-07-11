---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_source_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AiSourceDialog`](#️-class-aisourcedialog)
  - [⚙️ Method `__init__`](#️-method-__init__)

</details>

## 🏛️ Class `AiSourceDialog`

```python
class AiSourceDialog(_BaseAiSourceDialog)
```

Modal dialog to collect purchase source text and/or a receipt image.

<details>
<summary>Code:</summary>

```python
class AiSourceDialog(_BaseAiSourceDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        max_image_side: int | None = None,
        initial_image_path: str | None = None,
    ) -> None:
        """Initialize the finance AI source dialog."""
        super().__init__(
            parent,
            title="Add Purchases with AI",
            description=_FINANCE_AI_DESCRIPTION,
            placeholder=PURCHASE_TEXT_PLACEHOLDER,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
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
    ) -> None:
        super().__init__(
            parent,
            title="Add Purchases with AI",
            description=_FINANCE_AI_DESCRIPTION,
            placeholder=PURCHASE_TEXT_PLACEHOLDER,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
        )
```

</details>
