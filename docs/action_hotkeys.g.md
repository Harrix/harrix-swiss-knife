---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_hotkeys.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionHotkeyBinding`](#%EF%B8%8F-class-actionhotkeybinding)
- [🔧 Function `load_action_hotkeys`](#-function-load_action_hotkeys)
- [🔧 Function `load_hotkeys_for_action`](#-function-load_hotkeys_for_action)

</details>

## 🏛️ Class `ActionHotkeyBinding`

```python
class ActionHotkeyBinding
```

One global hotkey bound to an action class name (e.g. `OnQuickLauncher`).

<details>
<summary>Code:</summary>

```python
class ActionHotkeyBinding:

    action: str
    hotkey: str
```

</details>

## 🔧 Function `load_action_hotkeys`

```python
def load_action_hotkeys(config: dict[str, Any] | None = None) -> list[ActionHotkeyBinding]
```

Return hotkey bindings from `config.json` (or from the given config dict).

Expected shape::

    `hotkeys`: [
      {`action`: `OnQuickLauncher`, `hotkeys`: ["Ctrl+Shift+F1"]},
      {`action`: `OnScreenshotRegion`, `hotkeys`: ["Ctrl+Shift+F2"]}
    ]

Each entry may use `"hotkeys"` (list of strings) or a single `"hotkey"` string.

<details>
<summary>Code:</summary>

```python
def load_action_hotkeys(config: dict[str, Any] | None = None) -> list[ActionHotkeyBinding]:
    data = config if config is not None else _load_main_config()
    raw = data.get(HOTKEYS_KEY)
    if not isinstance(raw, list):
        return []

    bindings: list[ActionHotkeyBinding] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action") or "").strip()
        if not action:
            continue
        bindings.extend(ActionHotkeyBinding(action=action, hotkey=hotkey) for hotkey in _hotkeys_from_entry(item))
    return bindings
```

</details>

## 🔧 Function `load_hotkeys_for_action`

```python
def load_hotkeys_for_action(action_name: str, config: dict[str, Any] | None = None) -> list[str]
```

Return hotkey strings bound to `action_name`, in config order.

<details>
<summary>Code:</summary>

```python
def load_hotkeys_for_action(action_name: str, config: dict[str, Any] | None = None) -> list[str]:
    name = action_name.strip()
    return [binding.hotkey for binding in load_action_hotkeys(config) if binding.action == name]
```

</details>
