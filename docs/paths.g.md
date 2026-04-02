---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_config_path`](#-function-get_config_path)
- [🔧 Function `get_config_path_str`](#-function-get_config_path_str)
- [🔧 Function `get_project_root`](#-function-get_project_root)
- [🔧 Function `get_temp_config_path`](#-function-get_temp_config_path)
- [🔧 Function `get_temp_config_path_str`](#-function-get_temp_config_path_str)

</details>

## 🔧 Function `get_config_path`

```python
def get_config_path() -> Path
```

Return absolute path to main config file.

<details>
<summary>Code:</summary>

```python
def get_config_path() -> Path:

    return get_project_root() / "config" / "config.json"
```

</details>

## 🔧 Function `get_config_path_str`

```python
def get_config_path_str() -> str
```

Return config path as a string (for APIs expecting str).

<details>
<summary>Code:</summary>

```python
def get_config_path_str() -> str:

    return str(get_config_path())
```

</details>

## 🔧 Function `get_project_root`

```python
def get_project_root() -> Path
```

Return project root directory as detected by harrix_pylib.

<details>
<summary>Code:</summary>

```python
def get_project_root() -> Path:

    return h.dev.get_project_root()
```

</details>

## 🔧 Function `get_temp_config_path`

```python
def get_temp_config_path() -> Path
```

Return absolute path to temp config file.

<details>
<summary>Code:</summary>

```python
def get_temp_config_path() -> Path:

    return get_project_root() / "config" / "config-temp.json"
```

</details>

## 🔧 Function `get_temp_config_path_str`

```python
def get_temp_config_path_str() -> str
```

Return temp config path as a string (for APIs expecting str).

<details>
<summary>Code:</summary>

```python
def get_temp_config_path_str() -> str:

    return str(get_temp_config_path())
```

</details>
