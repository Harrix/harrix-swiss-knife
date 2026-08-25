---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `snippets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSnippets`](#%EF%B8%8F-class-onsnippets)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnSnippets`

```python
class OnSnippets(ActionBase)
```

Show or hide the Quick paste overlay.

<details>
<summary>Code:</summary>

```python
class OnSnippets(ActionBase):

    icon = "📋"
    title = "Quick paste"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("opening quick paste")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Toggle the snippets overlay."""
        SnippetsDialog.toggle()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Toggle the snippets overlay.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        SnippetsDialog.toggle()
```

</details>
