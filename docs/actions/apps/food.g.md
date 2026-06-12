---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food.py`

## 🏛️ Class `OnFood`

```python
class OnFood(AppLauncherAction)
```

Launch the food tracking application.

<details>
<summary>Code:</summary>

```python
class OnFood(AppLauncherAction):

    icon = "🍔"
    title = "Food tracker"
    main_window_class = food_main.MainWindow
```

</details>
