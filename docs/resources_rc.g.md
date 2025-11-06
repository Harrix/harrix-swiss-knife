---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `resources_rc.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `qCleanupResources`](#-function-qcleanupresources)
- [🔧 Function `qInitResources`](#-function-qinitresources)

</details>

## 🔧 Function `qCleanupResources`

```python
def qCleanupResources()
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)  # ty: ignore[unresolved-attribute]
```

</details>

## 🔧 Function `qInitResources`

```python
def qInitResources()
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)  # ty: ignore[unresolved-attribute]
```

</details>
