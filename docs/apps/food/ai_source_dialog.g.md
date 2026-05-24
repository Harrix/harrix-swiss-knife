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

</details>

## 🏛️ Class `AiSourceDialog`

```python
class AiSourceDialog(_BaseAiSourceDialog)
```

Modal dialog to collect food source text and/or an image.

<details>
<summary>Code:</summary>

```python
class AiSourceDialog(_BaseAiSourceDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the food AI source dialog."""
        super().__init__(
            parent,
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the food AI source dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
        )
```

</details>
