---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habits.py`

## 🏛️ Class `OnHabits`

```python
class OnHabits(AppLauncherAction)
```

Launch the habits tracking application.

<details>
<summary>Code:</summary>

```python
class OnHabits(AppLauncherAction):

    icon = "✅"
    title = "Habit tracker"
    main_window_module = "harrix_swiss_knife.apps.habits.main"
```

</details>
