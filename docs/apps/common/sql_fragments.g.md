---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sql_fragments.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BaseSqlFragmentValidationError`](#%EF%B8%8F-class-basesqlfragmentvalidationerror)
- [🏛️ Class `EmptyOrderByFragmentError`](#%EF%B8%8F-class-emptyorderbyfragmenterror)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `EmptySqlFragmentError`](#%EF%B8%8F-class-emptysqlfragmenterror)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
- [🏛️ Class `UnsafeOrderByFragmentError`](#%EF%B8%8F-class-unsafeorderbyfragmenterror)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `invalid_direction`](#%EF%B8%8F-method-invalid_direction)
  - [⚙️ Method `too_complex`](#%EF%B8%8F-method-too_complex)
- [🏛️ Class `UnsafeSqlFragmentError`](#%EF%B8%8F-class-unsafesqlfragmenterror)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `forbidden_characters`](#%EF%B8%8F-method-forbidden_characters)
  - [⚙️ Method `forbidden_keyword`](#%EF%B8%8F-method-forbidden_keyword)
  - [⚙️ Method `no_tokens`](#%EF%B8%8F-method-no_tokens)
  - [⚙️ Method `quoted_literals_not_allowed`](#%EF%B8%8F-method-quoted_literals_not_allowed)
- [🔧 Function `validate_order_by_fragment`](#-function-validate_order_by_fragment)
- [🔧 Function `validate_where_fragment`](#-function-validate_where_fragment)
- [🔧 Function `_ensure_no_obvious_injection`](#-function-_ensure_no_obvious_injection)

</details>

## 🏛️ Class `BaseSqlFragmentValidationError`

```python
class BaseSqlFragmentValidationError(ValueError)
```

Base error for SQL fragment validation failures.

<details>
<summary>Code:</summary>

```python
class BaseSqlFragmentValidationError(ValueError):
```

</details>

## 🏛️ Class `EmptyOrderByFragmentError`

```python
class EmptyOrderByFragmentError(BaseSqlFragmentValidationError)
```

ORDER BY fragment must not be empty.

<details>
<summary>Code:</summary>

```python
class EmptyOrderByFragmentError(BaseSqlFragmentValidationError):

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("Empty ORDER BY fragment")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create exception with standard message.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__("Empty ORDER BY fragment")
```

</details>

## 🏛️ Class `EmptySqlFragmentError`

```python
class EmptySqlFragmentError(BaseSqlFragmentValidationError)
```

SQL fragment must not be empty.

<details>
<summary>Code:</summary>

```python
class EmptySqlFragmentError(BaseSqlFragmentValidationError):

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("Empty SQL fragment")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create exception with standard message.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__("Empty SQL fragment")
```

</details>

## 🏛️ Class `UnsafeOrderByFragmentError`

```python
class UnsafeOrderByFragmentError(BaseSqlFragmentValidationError)
```

ORDER BY fragment failed validation.

<details>
<summary>Code:</summary>

```python
class UnsafeOrderByFragmentError(BaseSqlFragmentValidationError):

    def __init__(self, msg: str) -> None:
        """Create exception with validation message."""
        super().__init__(msg)

    @classmethod
    def invalid_direction(cls) -> UnsafeOrderByFragmentError:
        """Direction must be ASC or DESC."""
        return cls("Unsafe ORDER BY fragment (direction must be ASC or DESC)")

    @classmethod
    def too_complex(cls) -> UnsafeOrderByFragmentError:
        """ORDER BY fragment is too complex."""
        return cls("Unsafe ORDER BY fragment (too complex)")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, msg: str) -> None
```

Create exception with validation message.

<details>
<summary>Code:</summary>

```python
def __init__(self, msg: str) -> None:
        super().__init__(msg)
```

</details>

### ⚙️ Method `invalid_direction`

```python
def invalid_direction(cls) -> UnsafeOrderByFragmentError
```

Direction must be ASC or DESC.

<details>
<summary>Code:</summary>

```python
def invalid_direction(cls) -> UnsafeOrderByFragmentError:
        return cls("Unsafe ORDER BY fragment (direction must be ASC or DESC)")
```

</details>

### ⚙️ Method `too_complex`

```python
def too_complex(cls) -> UnsafeOrderByFragmentError
```

ORDER BY fragment is too complex.

<details>
<summary>Code:</summary>

```python
def too_complex(cls) -> UnsafeOrderByFragmentError:
        return cls("Unsafe ORDER BY fragment (too complex)")
```

</details>

## 🏛️ Class `UnsafeSqlFragmentError`

```python
class UnsafeSqlFragmentError(BaseSqlFragmentValidationError)
```

SQL fragment failed validation.

<details>
<summary>Code:</summary>

```python
class UnsafeSqlFragmentError(BaseSqlFragmentValidationError):

    def __init__(self, msg: str) -> None:
        """Create exception with validation message."""
        super().__init__(msg)

    @classmethod
    def forbidden_characters(cls) -> UnsafeSqlFragmentError:
        """Fragment contains forbidden characters."""
        return cls("Unsafe SQL fragment (contains forbidden characters)")

    @classmethod
    def forbidden_keyword(cls) -> UnsafeSqlFragmentError:
        """Fragment contains forbidden keyword."""
        return cls("Unsafe SQL fragment (contains forbidden keyword)")

    @classmethod
    def no_tokens(cls) -> UnsafeSqlFragmentError:
        """Fragment produced no tokens."""
        return cls("Unsafe SQL fragment (no tokens)")

    @classmethod
    def quoted_literals_not_allowed(cls) -> UnsafeSqlFragmentError:
        """Quoted literals are forbidden; use bound parameters."""
        return cls("Unsafe SQL fragment (quoted literals are not allowed; use bound parameters)")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, msg: str) -> None
```

Create exception with validation message.

<details>
<summary>Code:</summary>

```python
def __init__(self, msg: str) -> None:
        super().__init__(msg)
```

</details>

### ⚙️ Method `forbidden_characters`

```python
def forbidden_characters(cls) -> UnsafeSqlFragmentError
```

Fragment contains forbidden characters.

<details>
<summary>Code:</summary>

```python
def forbidden_characters(cls) -> UnsafeSqlFragmentError:
        return cls("Unsafe SQL fragment (contains forbidden characters)")
```

</details>

### ⚙️ Method `forbidden_keyword`

```python
def forbidden_keyword(cls) -> UnsafeSqlFragmentError
```

Fragment contains forbidden keyword.

<details>
<summary>Code:</summary>

```python
def forbidden_keyword(cls) -> UnsafeSqlFragmentError:
        return cls("Unsafe SQL fragment (contains forbidden keyword)")
```

</details>

### ⚙️ Method `no_tokens`

```python
def no_tokens(cls) -> UnsafeSqlFragmentError
```

Fragment produced no tokens.

<details>
<summary>Code:</summary>

```python
def no_tokens(cls) -> UnsafeSqlFragmentError:
        return cls("Unsafe SQL fragment (no tokens)")
```

</details>

### ⚙️ Method `quoted_literals_not_allowed`

```python
def quoted_literals_not_allowed(cls) -> UnsafeSqlFragmentError
```

Quoted literals are forbidden; use bound parameters.

<details>
<summary>Code:</summary>

```python
def quoted_literals_not_allowed(cls) -> UnsafeSqlFragmentError:
        return cls("Unsafe SQL fragment (quoted literals are not allowed; use bound parameters)")
```

</details>

## 🔧 Function `validate_order_by_fragment`

```python
def validate_order_by_fragment(fragment: str) -> str
```

Validate an ORDER BY fragment.

Accepts a comma-separated list of identifiers with optional ASC/DESC.
Example: `date DESC, _id ASC`

<details>
<summary>Code:</summary>

```python
def validate_order_by_fragment(fragment: str) -> str:
    frag = _ensure_no_obvious_injection(fragment)

    parts = [p.strip() for p in frag.split(",") if p.strip()]
    if not parts:
        raise EmptyOrderByFragmentError

    validated_parts: list[str] = []
    for part in parts:
        items = part.split()
        if len(items) == 1:
            column = _safe_identifier(items[0])
            validated_parts.append(column)
            continue
        if len(items) == _ORDER_BY_PARTS_WITH_DIRECTION:
            column = _safe_identifier(items[0])
            direction = items[1].upper()
            if direction not in {"ASC", "DESC"}:
                raise UnsafeOrderByFragmentError.invalid_direction()
            validated_parts.append(f"{column} {direction}")
            continue
        raise UnsafeOrderByFragmentError.too_complex()

    return ", ".join(validated_parts)
```

</details>

## 🔧 Function `validate_where_fragment`

```python
def validate_where_fragment(fragment: str) -> str
```

Validate a WHERE/AND fragment that must remain expression-only.

Policy:

- Forbids statement separators / comments.
- Forbids high-risk SQL keywords.
- Forbids quoted literals; values should be bound parameters (e.g. :name) or numeric.

<details>
<summary>Code:</summary>

```python
def validate_where_fragment(fragment: str) -> str:
    frag = _ensure_no_obvious_injection(fragment)

    if "'" in frag or '"' in frag:
        raise UnsafeSqlFragmentError.quoted_literals_not_allowed()

    # Characters whitelist.
    if not re.fullmatch(r"[A-Za-z0-9_:\s<>=!().,%+-]+", frag):
        raise UnsafeSqlFragmentError.forbidden_characters()

    # Token whitelist.
    tokens = re.findall(
        r":[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|<=|>=|!=|=|<|>|\(|\)|,|\+|-|%|\.", frag
    )
    if not tokens:
        raise UnsafeSqlFragmentError.no_tokens()

    allowed_keywords = {"AND", "OR", "NOT", "IN", "IS", "NULL", "LIKE"}
    for token in tokens:
        if token.startswith(":"):
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            continue
        if token in {"<=", ">=", "!=", "=", "<", ">", "(", ")", ",", "+", "-", "%", "."}:
            continue
        upper = token.upper()
        if upper in _BANNED_KEYWORDS:
            raise UnsafeSqlFragmentError.forbidden_keyword()
        if upper in allowed_keywords:
            continue
        _safe_identifier(token)

    return frag
```

</details>

## 🔧 Function `_ensure_no_obvious_injection`

```python
def _ensure_no_obvious_injection(fragment: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ensure_no_obvious_injection(fragment: str) -> str:
    frag = fragment.strip()
    if not frag:
        raise EmptySqlFragmentError
    lowered = frag.lower()
    for needle in _BANNED_SUBSTRINGS:
        if needle in frag:
            msg = f"Unsafe SQL fragment (contains {needle!r})"
            raise UnsafeSqlFragmentError(msg)
    # Fast keyword screening; token-level checks run below too.
    if any(f" {kw.lower()} " in f" {lowered} " for kw in (k.lower() for k in _BANNED_KEYWORDS)):
        raise UnsafeSqlFragmentError.forbidden_keyword()
    return frag
```

</details>
