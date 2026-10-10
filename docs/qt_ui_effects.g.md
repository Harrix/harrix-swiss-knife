---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_ui_effects.py`

## 🔧 Function `install_ui_effects`

```python
def install_ui_effects(app: QApplication) -> None
```

Disable combo popup slide animation and install shared form chrome.

On the `windows11` style the animated popup is painted once, then grabbed
and scrolled open, which reads as a blink every time a combo opens.

Also paints Lucide checkbox / radio indicators and white dialog surfaces.

Args:

- `app` (`QApplication`): Running application.

<details>
<summary>Code:</summary>

```python
def install_ui_effects(app: QApplication) -> None:
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, enable=False)
    install_date_calendar_popups(app)
    install_form_chrome(app)
```

</details>
