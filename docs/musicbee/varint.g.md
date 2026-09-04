---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `varint.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `encode_varint`](#-function-encode_varint)
- [🔧 Function `read_varint`](#-function-read_varint)

</details>

## 🔧 Function `encode_varint`

```python
def encode_varint(value: int) -> bytes
```

Encode a non-negative integer as a 7-bit continuation sequence.

<details>
<summary>Code:</summary>

```python
def encode_varint(value: int) -> bytes:
    if value < 0:
        msg = "varint cannot encode a negative value"
        raise ValueError(msg)
    if value == 0:
        return b"\x00"
    encoded = bytearray()
    remaining = value
    while remaining > 0:
        byte = remaining & 0x7F
        remaining >>= 7
        if remaining > 0:
            byte |= 0x80
        encoded.append(byte)
    return bytes(encoded)
```

</details>

## 🔧 Function `read_varint`

```python
def read_varint(data: bytes, offset: int) -> tuple[int | None, int]
```

Read a varint starting at `offset`.

Returns:

- `tuple[int | None, int]`: `(value, new_offset)` or `(None, offset)` on failure.

<details>
<summary>Code:</summary>

```python
def read_varint(data: bytes, offset: int) -> tuple[int | None, int]:
    value = 0
    shift = 0
    position = offset
    while position < len(data):
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            return value, position
        shift += 7
        if shift > _MAX_SHIFT:
            return None, offset
    return None, offset
```

</details>
