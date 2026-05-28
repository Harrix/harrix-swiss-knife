---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tag_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TagDelegate`](#%EF%B8%8F-class-tagdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `tags`](#%EF%B8%8F-method-tags)
  - [⚙️ Method `tags`](#%EF%B8%8F-method-tags-1)

</details>

## 🏛️ Class `TagDelegate`

```python
class TagDelegate(ComboBoxDelegate)
```

Delegate for tag column with editable combo and clearable empty option.

<details>
<summary>Code:</summary>

```python
class TagDelegate(ComboBoxDelegate):

    def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        """Initialize the tag delegate."""
        super().__init__(
            parent,
            items=tags,
            editable=True,
            leading_empty_item=True,
            strip_values=True,
            write_empty_value=True,
        )

    @property
    def tags(self) -> list[str]:
        """Tag names shown in the combo box."""
        return self.items

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None
```

Initialize the tag delegate.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        super().__init__(
            parent,
            items=tags,
            editable=True,
            leading_empty_item=True,
            strip_values=True,
            write_empty_value=True,
        )
```

</details>

### ⚙️ Method `tags`

```python
def tags(self) -> list[str]
```

Tag names shown in the combo box.

<details>
<summary>Code:</summary>

```python
def tags(self) -> list[str]:
        return self.items
```

</details>

### ⚙️ Method `tags`

```python
def tags(self, value: list[str] | None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def tags(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>
