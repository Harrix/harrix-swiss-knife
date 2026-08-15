---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `errors.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AiApiError`](#%EF%B8%8F-class-aiapierror)
- [🏛️ Class `RequestCancelledError`](#%EF%B8%8F-class-requestcancellederror)

</details>

## 🏛️ Class `AiApiError`

```python
class AiApiError(RuntimeError)
```

Raised when an AI provider returns an error or the response cannot be parsed.

<details>
<summary>Code:</summary>

```python
class AiApiError(RuntimeError):
```

</details>

## 🏛️ Class `RequestCancelledError`

```python
class RequestCancelledError(AiApiError)
```

Raised when an in-flight AI request is cancelled by the user.

<details>
<summary>Code:</summary>

```python
class RequestCancelledError(AiApiError):
```

</details>
