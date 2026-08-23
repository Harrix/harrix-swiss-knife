---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `constants.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `installer_window_title`](#-function-installer_window_title)
- [🔧 Function `offline_install_welcome_kind`](#-function-offline_install_welcome_kind)

</details>

## 🔧 Function `installer_window_title`

```python
def installer_window_title(mode: str) -> str
```

Return the installer window title for online or offline mode.

<details>
<summary>Code:</summary>

```python
def installer_window_title(mode: str) -> str:
    if mode == "offline":
        return "Harrix Swiss Knife — Offline Installer (for personal use)"
    return "Harrix Swiss Knife — Online Installer"
```

</details>

## 🔧 Function `offline_install_welcome_kind`

```python
def offline_install_welcome_kind() -> str
```

Return the install-source phrase shown on the offline welcome page.

<details>
<summary>Code:</summary>

```python
def offline_install_welcome_kind() -> str:
    return "offline bundle, for personal use"
```

</details>
