---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_compact_spin_box.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CompactDoubleSpinBox`](#%EF%B8%8F-class-compactdoublespinbox)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `CompactSpinBox`](#%EF%B8%8F-class-compactspinbox)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)

</details>

## 🏛️ Class `CompactDoubleSpinBox`

```python
class CompactDoubleSpinBox(QDoubleSpinBox)
```

Decimal spin box with narrow up/down buttons stacked on the right.

<details>
<summary>Code:</summary>

```python
class CompactDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a compact decimal spin box."""
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a compact decimal spin box.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)
```

</details>

## 🏛️ Class `CompactSpinBox`

```python
class CompactSpinBox(QSpinBox)
```

Integer spin box with narrow up/down buttons stacked on the right.

<details>
<summary>Code:</summary>

```python
class CompactSpinBox(QSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a compact integer spin box."""
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a compact integer spin box.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)
```

</details>
