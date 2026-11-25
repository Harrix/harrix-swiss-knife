---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `beat_saber.py`

## 🏛️ Class `OnBeatSaber`

```python
class OnBeatSaber(AppLauncherAction)
```

Launch the Beat Saber progress tracker.

<details>
<summary>Code:</summary>

```python
class OnBeatSaber(AppLauncherAction):

    icon = "🎮"
    title = "Beat Saber tracker"
    description = "Official song progress, PC vs Quest compare, sync and save backups."
    main_window_module = "harrix_swiss_knife.apps.beat_saber.main"
```

</details>
