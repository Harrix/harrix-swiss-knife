"""QR image generation for pairing URIs."""

from __future__ import annotations

from io import BytesIO

import qrcode
from PIL import Image, ImageDraw, ImageFont


def make_qr_png_bytes(payload: str, *, box_size: int = 8, border: int = 2) -> bytes:
    """Return PNG bytes for a QR code of `payload`."""
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


def _fallback_png(payload: str) -> bytes:
    """Readable placeholder if QR encoding fails."""
    width, height = 420, 420
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, width - 9, height - 9), outline="black", width=3)
    font = ImageFont.load_default()
    lines = ["QR unavailable", "Enter manually:", payload[:48], payload[48:96], payload[96:144]]
    y = 40
    for line in lines:
        draw.text((24, y), line, fill="black", font=font)
        y += 28
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
