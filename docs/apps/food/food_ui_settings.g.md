---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_ui_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_food_splitter_sizes`](#-function-load_food_splitter_sizes)
- [🔧 Function `save_food_splitter_sizes`](#-function-save_food_splitter_sizes)

</details>

## 🔧 Function `load_food_splitter_sizes`

```python
def load_food_splitter_sizes() -> list[int]
```

Return Food-tab splitter sizes (form, items, log).

<details>
<summary>Code:</summary>

```python
def load_food_splitter_sizes() -> list[int]:
    return load_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, FOOD_SPLITTER_SIZES_DEFAULT)
```

</details>

## 🔧 Function `save_food_splitter_sizes`

```python
def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Food-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, sizes, FOOD_SPLITTER_SIZES_DEFAULT)
```

</details>
