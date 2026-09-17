---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `eaten_fraction.py`

## 🔧 Function `scale_food_log_eaten_weight`

```python
def scale_food_log_eaten_weight(*, weight: float | None, fraction: float) -> float | None
```

Return weight after eating `fraction` of the row (kcal/100g unchanged).

Args:

- `weight` (`float | None`): Logged mass in grams.
- `fraction` (`float`): Share actually eaten, in `(0, 1]`.

Returns:

- `float | None`: New weight.

<details>
<summary>Code:</summary>

```python
def scale_food_log_eaten_weight(*, weight: float | None, fraction: float) -> float | None:
    return _scale_amount(weight, fraction)
```

</details>
