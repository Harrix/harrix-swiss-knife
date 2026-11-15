---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sync_lucide_icons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LucideSyncResult`](#%EF%B8%8F-class-lucidesyncresult)
- [🔧 Function `lucide_dir`](#-function-lucide_dir)
- [🔧 Function `read_lucide_version`](#-function-read_lucide_version)
- [🔧 Function `sync_lucide_icons`](#-function-sync_lucide_icons)
- [🔧 Function `main`](#-function-main)

</details>

## 🏛️ Class `LucideSyncResult`

```python
class LucideSyncResult
```

Outcome of refreshing `assets/lucide` from npm `lucide-static`.

<details>
<summary>Code:</summary>

```python
class LucideSyncResult:

    dest: Path
    old_version: str
    new_version: str
    svg_count: int
```

</details>

## 🔧 Function `lucide_dir`

```python
def lucide_dir() -> Path
```

Return `assets/lucide/` next to this script.

<details>
<summary>Code:</summary>

```python
def lucide_dir() -> Path:
    return Path(__file__).resolve().parent / "lucide"
```

</details>

## 🔧 Function `read_lucide_version`

```python
def read_lucide_version(dest: Path | None = None) -> str
```

Return the pinned Lucide version from `VERSION.txt`, or empty when missing.

<details>
<summary>Code:</summary>

```python
def read_lucide_version(dest: Path | None = None) -> str:
    path = (dest or lucide_dir()) / "VERSION.txt"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()
```

</details>

## 🔧 Function `sync_lucide_icons`

```python
def sync_lucide_icons(*, progress: ProgressCallback | None = None) -> LucideSyncResult
```

Replace `assets/lucide/*.svg` with the latest lucide-static icons.

Args:

- `progress` (`ProgressCallback | None`): Optional line reporter for UI threads.

Returns:

- [`LucideSyncResult`](#%EF%B8%8F-class-lucidesyncresult): Destination folder, old/new versions, and SVG count.

Raises:

- `FileNotFoundError`: When the npm tarball has no icons.
- `OSError`: When download or extract fails.
- `urllib.error.URLError`: When npm metadata or the tarball cannot be fetched.

<details>
<summary>Code:</summary>

```python
def sync_lucide_icons(*, progress: ProgressCallback | None = None) -> LucideSyncResult:
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
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Replace `assets/lucide/*.svg` with the latest lucide-static icons.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    sync_lucide_icons()
```

</details>
