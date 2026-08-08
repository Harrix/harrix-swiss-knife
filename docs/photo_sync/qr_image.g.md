---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qr_image.py`

## 🔧 Function `make_qr_png_bytes`

```python
def make_qr_png_bytes(payload: str, *, box_size: int = 8, border: int = 2) -> bytes
```

Return PNG bytes for a QR code of `payload`.

<details>
<summary>Code:</summary>

```python
def make_qr_png_bytes(payload: str, *, box_size: int = 8, border: int = 2) -> bytes:
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception:
        return _fallback_png(payload)
```

</details>
