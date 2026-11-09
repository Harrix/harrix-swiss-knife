---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fitness_ui_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_sets_splitter_sizes`](#-function-load_sets_splitter_sizes)
- [🔧 Function `save_sets_splitter_sizes`](#-function-save_sets_splitter_sizes)

</details>

## 🔧 Function `load_sets_splitter_sizes`

```python
def load_sets_splitter_sizes() -> list[int]
```

Return Sets-tab splitter sizes (form, exercises, process).

<details>
<summary>Code:</summary>

```python
def load_sets_splitter_sizes() -> list[int]:
    return load_splitter_sizes(SETS_SPLITTER_SIZES_KEY, SETS_SPLITTER_SIZES_DEFAULT)
```

</details>

## 🔧 Function `save_sets_splitter_sizes`

```python
def save_sets_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Sets-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_sets_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(SETS_SPLITTER_SIZES_KEY, sizes, SETS_SPLITTER_SIZES_DEFAULT)
```

</details>
