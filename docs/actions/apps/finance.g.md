---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `finance.py`

## 🏛️ Class `OnFinance`

```python
class OnFinance(AppLauncherAction)
```

Launch the finance tracking application.

<details>
<summary>Code:</summary>

```python
class OnFinance(AppLauncherAction):

    icon = "💰"
    title = "Finance tracker"
    main_window_class = finance_main.MainWindow
```

</details>
