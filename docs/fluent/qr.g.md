---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qr.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `Ecc`](#%EF%B8%8F-class-ecc)
- [🔧 Function `encode_qr`](#-function-encode_qr)

</details>

## 🏛️ Class `Ecc`

```python
class Ecc(Enum)
```

Error correction level: (format bits, index into the tables).

<details>
<summary>Code:</summary>

```python
class Ecc(Enum):

    LOW = (1, 0)
    MEDIUM = (0, 1)
    QUARTILE = (3, 2)
    HIGH = (2, 3)
```

</details>

## 🔧 Function `encode_qr`

```python
def encode_qr(text: str, ecc: Ecc = Ecc.MEDIUM) -> list[list[bool]]
```

Encode `text` (UTF-8 bytes) and return the module matrix (`True` = dark).

Raises:

- `ValueError`: When the text does not fit in version 40.

<details>
<summary>Code:</summary>

```python
def encode_qr(text: str, ecc: Ecc = Ecc.MEDIUM) -> list[list[bool]]:
    data = text.encode("utf-8")
    version = _choose_version(len(data), ecc)
    bits: list[int] = []
    _append_bits(bits, _BYTE_MODE, 4)
    _append_bits(bits, len(data), 8 if version <= _SMALL_VERSION_MAX else 16)
    for byte in data:
        _append_bits(bits, byte, 8)
    capacity = _num_data_codewords(version, ecc) * 8
    _append_bits(bits, 0, min(4, capacity - len(bits)))
    _append_bits(bits, 0, (-len(bits)) % 8)
    pad_index = 0
    while len(bits) < capacity:
        _append_bits(bits, _PAD_BYTES[pad_index % 2], 8)
        pad_index += 1
    codewords = [int("".join(map(str, bits[i : i + 8])), 2) for i in range(0, len(bits), 8)]
    final = _add_ecc_and_interleave(codewords, version, ecc)
    return _build_matrix(final, version, ecc)
```

</details>
