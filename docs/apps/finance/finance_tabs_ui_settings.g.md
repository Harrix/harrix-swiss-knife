---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `finance_tabs_ui_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_accounts_splitter_sizes`](#-function-load_accounts_splitter_sizes)
- [🔧 Function `load_charts_splitter_sizes`](#-function-load_charts_splitter_sizes)
- [🔧 Function `load_exchange_splitter_sizes`](#-function-load_exchange_splitter_sizes)
- [🔧 Function `load_rates_splitter_sizes`](#-function-load_rates_splitter_sizes)
- [🔧 Function `load_reports_splitter_sizes`](#-function-load_reports_splitter_sizes)
- [🔧 Function `save_accounts_splitter_sizes`](#-function-save_accounts_splitter_sizes)
- [🔧 Function `save_charts_splitter_sizes`](#-function-save_charts_splitter_sizes)
- [🔧 Function `save_exchange_splitter_sizes`](#-function-save_exchange_splitter_sizes)
- [🔧 Function `save_rates_splitter_sizes`](#-function-save_rates_splitter_sizes)
- [🔧 Function `save_reports_splitter_sizes`](#-function-save_reports_splitter_sizes)

</details>

## 🔧 Function `load_accounts_splitter_sizes`

```python
def load_accounts_splitter_sizes() -> list[int]
```

Return Accounts-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def load_accounts_splitter_sizes() -> list[int]:
    return load_splitter_sizes(ACCOUNTS_SPLITTER_KEY, ACCOUNTS_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `load_charts_splitter_sizes`

```python
def load_charts_splitter_sizes() -> list[int]
```

Return Charts-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def load_charts_splitter_sizes() -> list[int]:
    return load_splitter_sizes(CHARTS_SPLITTER_KEY, CHARTS_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `load_exchange_splitter_sizes`

```python
def load_exchange_splitter_sizes() -> list[int]
```

Return Currency Exchange-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def load_exchange_splitter_sizes() -> list[int]:
    return load_splitter_sizes(EXCHANGE_SPLITTER_KEY, EXCHANGE_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `load_rates_splitter_sizes`

```python
def load_rates_splitter_sizes() -> list[int]
```

Return Exchange Rates-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def load_rates_splitter_sizes() -> list[int]:
    return load_splitter_sizes(RATES_SPLITTER_KEY, RATES_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `load_reports_splitter_sizes`

```python
def load_reports_splitter_sizes() -> list[int]
```

Return Reports-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def load_reports_splitter_sizes() -> list[int]:
    return load_splitter_sizes(REPORTS_SPLITTER_KEY, REPORTS_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `save_accounts_splitter_sizes`

```python
def save_accounts_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Accounts-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_accounts_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(ACCOUNTS_SPLITTER_KEY, sizes, ACCOUNTS_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `save_charts_splitter_sizes`

```python
def save_charts_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Charts-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_charts_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(CHARTS_SPLITTER_KEY, sizes, CHARTS_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `save_exchange_splitter_sizes`

```python
def save_exchange_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Currency Exchange-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_exchange_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(EXCHANGE_SPLITTER_KEY, sizes, EXCHANGE_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `save_rates_splitter_sizes`

```python
def save_rates_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Exchange Rates-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_rates_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(RATES_SPLITTER_KEY, sizes, RATES_SPLITTER_DEFAULT)
```

</details>

## 🔧 Function `save_reports_splitter_sizes`

```python
def save_reports_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Reports-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_reports_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(REPORTS_SPLITTER_KEY, sizes, REPORTS_SPLITTER_DEFAULT)
```

</details>
