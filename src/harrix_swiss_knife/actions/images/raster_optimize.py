"""Raster image optimization using Pillow and ffmpeg."""

from __future__ import annotations

import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

RASTER_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})
_JPG_WEBP_EXTENSIONS = frozenset({".jpg", ".jpeg", ".webp"})
_PALETTE_COLORS = 256


def optimize_raster_file(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
) -> str:
    """Optimize a PNG, JPG, or WEBP file using Pillow and ffmpeg.

    Args:

    - `source` (`Path`): Source image path.
    - `output_folder` (`Path`): Destination folder.
    - `project_root` (`Path`): Folder containing ffmpeg.exe.
    - `quality` (`bool`): Use higher quality AVIF settings. Defaults to `False`.
    - `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.
    - `compare_png_avif` (`bool`): For PNG, compare optimized PNG vs AVIF. Defaults to `True`.

    Returns:

    - `str`: Status message.

    """
    output_folder.mkdir(parents=True, exist_ok=True)
    ext = source.suffix.lower()
    if ext == ".png":
        if compare_png_avif:
            return process_png_compare(source, output_folder, project_root, quality=quality, max_size=max_size)
        if convert_png_to_avif:
            return process_png_to_avif(source, output_folder, project_root, quality=quality, max_size=max_size)
        image = _load_and_resize(source, max_size)
        output_path = output_folder / f"{source.stem}.png"
        output_path.write_bytes(_encode_optimized_png(image))
        return f"✅ File {source.name} successfully optimized."
    if ext in _JPG_WEBP_EXTENSIONS:
        output_path = output_folder / f"{source.stem}.avif"
        return process_jpg_webp_to_avif(
            source,
            output_path,
            project_root,
            quality=quality,
            max_size=max_size,
        )
    msg = f"File {source.name} is not a supported raster format."
    raise ValueError(msg)


def process_jpg_webp_to_avif(
    source: Path,
    output_path: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    """Convert JPG or WEBP to AVIF using ffmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _convert_to_avif(source, output_path, project_root, quality=quality, max_size=max_size)
    return f"✅ File {source.name} successfully converted to AVIF."


def process_png_compare(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    """Optimize PNG, compare with AVIF from ffmpeg, and keep the smaller file."""
    output_folder.mkdir(parents=True, exist_ok=True)
    image = _load_and_resize(source, max_size)
    png_bytes = _encode_optimized_png(image)
    output_png = output_folder / f"{source.stem}.png"
    output_avif = output_folder / f"{source.stem}.avif"

    with tempfile.TemporaryDirectory(prefix="png_compare_") as temp_dir:
        temp_path = Path(temp_dir)
        temp_png = temp_path / "input.png"
        image.save(temp_png, format="PNG")
        temp_avif = temp_path / "output.avif"
        _convert_to_avif(temp_png, temp_avif, project_root, quality=quality, max_size=None)
        avif_size = temp_avif.stat().st_size
        avif_bytes = temp_avif.read_bytes()

    png_size = len(png_bytes)
    if png_size <= avif_size:
        output_png.write_bytes(png_bytes)
        return (
            f"✅ File {source.name} kept as PNG (smaller size): "
            f"PNG {(png_size / 1024):.2f} KB, AVIF {(avif_size / 1024):.2f} KB."
        )

    output_avif.write_bytes(avif_bytes)
    return (
        f"✅ File {source.name} converted to AVIF (smaller size): "
        f"PNG {(png_size / 1024):.2f} KB, AVIF {(avif_size / 1024):.2f} KB."
    )


def process_png_to_avif(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    """Convert PNG to AVIF using ffmpeg."""
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"{source.stem}.avif"
    image = _load_and_resize(source, max_size)
    with tempfile.TemporaryDirectory(prefix="png_to_avif_") as temp_dir:
        temp_png = Path(temp_dir) / "input.png"
        image.save(temp_png, format="PNG")
        _convert_to_avif(temp_png, output_path, project_root, quality=quality, max_size=None)
    return f"✅ File {source.name} successfully converted to AVIF."


def _convert_to_avif(
    source: Path,
    output: Path,
    project_root: Path,
    *,
    quality: bool,
    max_size: int | None,
) -> None:
    crf = 18 if quality else 28
    ffmpeg = _exe(project_root, "ffmpeg")
    args = [
        str(ffmpeg),
        "-i",
        str(source),
        "-c:v",
        "libaom-av1",
        "-crf",
        str(crf),
        "-cpu-used",
        "4",
        "-pix_fmt",
        "yuv420p",
    ]
    scale_vf = _scale_vf(max_size)
    if scale_vf:
        args.extend(["-vf", scale_vf])
    args.extend(["-frames:v", "1", "-y", str(output)])
    _run_checked(args)


def _encode_optimized_png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    if image.mode == "RGBA":
        quantized = image.quantize(colors=_PALETTE_COLORS, method=Image.Quantize.FASTOCTREE)
    elif image.mode == "P":
        image.save(buffer, format="PNG", optimize=True, compress_level=9)
        return buffer.getvalue()
    else:
        quantized = image.convert("RGB").quantize(colors=_PALETTE_COLORS, method=Image.Quantize.MEDIANCUT)
    quantized.save(buffer, format="PNG", optimize=True, compress_level=9)
    return buffer.getvalue()


def _exe(project_root: Path, name: str) -> Path:
    return project_root / f"{name}.exe"


def _load_and_resize(source: Path, max_size: int | None) -> Image.Image:
    with Image.open(source) as opened:
        image = opened.convert("RGBA") if opened.mode in {"RGBA", "LA", "P"} else opened.convert("RGB")
        if max_size is not None and max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return image.copy()


def _run_checked(args: list[str]) -> None:
    process = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if process.returncode != 0:
        details = (process.stderr or process.stdout or "").strip()
        msg = details or f"Command failed: {' '.join(args)}"
        raise RuntimeError(msg)


def _scale_vf(max_size: int | None) -> str | None:
    if max_size is None:
        return None
    return f"scale='if(gt(iw,ih),min({max_size},iw),-1)':'if(gt(iw,ih),-1,min({max_size},ih))'"
