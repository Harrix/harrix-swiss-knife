"""Download the Lucide SVG set into `assets/lucide/`.

Run from the repo (venv optional):

```text
python src/harrix_swiss_knife/assets/sync_lucide_icons.py
```

Uses the `lucide-static` npm tarball so UI code can load icons by Lucide ID
(`save`, `trash`, …) without copying files one by one.

"""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import harrix_pylib as h

_NPM_LATEST = "https://registry.npmjs.org/lucide-static/latest"
_LICENSE_URL = "https://raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE"

ProgressCallback = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class LucideSyncResult:
    """Outcome of refreshing `assets/lucide` from npm `lucide-static`."""

    dest: Path
    old_version: str
    new_version: str
    svg_count: int


def lucide_dir() -> Path:
    """Return `assets/lucide/` next to this script."""
    return Path(__file__).resolve().parent / "lucide"


def read_lucide_version(dest: Path | None = None) -> str:
    """Return the pinned Lucide version from `VERSION.txt`, or empty when missing."""
    path = (dest or lucide_dir()) / "VERSION.txt"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def sync_lucide_icons(*, progress: ProgressCallback | None = None) -> LucideSyncResult:
    """Replace `assets/lucide/*.svg` with the latest lucide-static icons.

    Args:

    - `progress` (`ProgressCallback | None`): Optional line reporter for UI threads.

    Returns:

    - `LucideSyncResult`: Destination folder, old/new versions, and SVG count.

    Raises:

    - `FileNotFoundError`: When the npm tarball has no icons.
    - `OSError`: When download or extract fails.
    - `urllib.error.URLError`: When npm metadata or the tarball cannot be fetched.

    """
    dest = lucide_dir()
    dest.mkdir(parents=True, exist_ok=True)
    old_version = read_lucide_version(dest)

    def _log(message: str) -> None:
        if progress is not None:
            progress(message)
        else:
            print(message)

    _log(f"Fetching lucide-static metadata from {_NPM_LATEST}")
    with urllib.request.urlopen(_NPM_LATEST, timeout=60) as response:
        meta = json.load(response)
    version = str(meta["version"])
    tarball = str(meta["dist"]["tarball"])
    _log(f"Downloading lucide-static {version}: {tarball}")
    with tempfile.TemporaryDirectory(prefix="lucide-static-") as raw_tmp:
        tmp = Path(raw_tmp)
        archive = tmp / "lucide-static.tgz"
        urllib.request.urlretrieve(tarball, archive)  # noqa: S310
        extract = tmp / "extract"
        extract.mkdir()
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(extract, filter="data")
        icons_src = extract / "package" / "icons"
        if not icons_src.is_dir():
            msg = f"lucide-static tarball has no icons/ folder ({extract})"
            raise FileNotFoundError(msg)
        svgs = sorted(icons_src.glob("*.svg"))
        if not svgs:
            msg = f"No SVG icons in {icons_src}"
            raise FileNotFoundError(msg)
        _log(f"Replacing {len(list(dest.glob('*.svg')))} local SVGs with {len(svgs)} from npm…")
        for old in dest.glob("*.svg"):
            old.unlink()
        for svg in svgs:
            shutil.copy2(svg, dest / svg.name)
        _log("Optimizing SVGs…")
        optimizer = h.svg_opt.SvgOptimizer()
        for svg in dest.glob("*.svg"):
            optimizer.optimize_file(svg)
        license_path = dest / "LICENSE.txt"
        try:
            urllib.request.urlretrieve(_LICENSE_URL, license_path)
        except OSError:
            package_license = extract / "package" / "LICENSE"
            if package_license.is_file():
                shutil.copy2(package_license, license_path)
        (dest / "VERSION.txt").write_text(f"{version}\n", encoding="utf-8")
    svg_count = len(svgs)
    _log(f"Wrote and optimized {svg_count} SVGs to {dest} (lucide-static {version})")
    return LucideSyncResult(
        dest=dest,
        old_version=old_version,
        new_version=version,
        svg_count=svg_count,
    )


def main() -> None:
    """Replace `assets/lucide/*.svg` with the latest lucide-static icons."""
    sync_lucide_icons()


if __name__ == "__main__":
    main()
