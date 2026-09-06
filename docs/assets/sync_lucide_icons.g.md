---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sync_lucide_icons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `lucide_dir`](#-function-lucide_dir)
- [🔧 Function `main`](#-function-main)

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

## 🔧 Function `main`

```python
def main() -> None
```

Replace `assets/lucide/*.svg` with the latest lucide-static icons.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    dest = lucide_dir()
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Fetching lucide-static metadata from {_NPM_LATEST}")
    with urllib.request.urlopen(_NPM_LATEST, timeout=60) as response:
        meta = json.load(response)
    version = str(meta["version"])
    tarball = str(meta["dist"]["tarball"])
    print(f"Downloading lucide-static {version}: {tarball}")
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
        for old in dest.glob("*.svg"):
            old.unlink()
        for svg in svgs:
            shutil.copy2(svg, dest / svg.name)
        license_path = dest / "LICENSE.txt"
        try:
            urllib.request.urlretrieve(_LICENSE_URL, license_path)
        except OSError:
            package_license = extract / "package" / "LICENSE"
            if package_license.is_file():
                shutil.copy2(package_license, license_path)
        (dest / "VERSION.txt").write_text(f"{version}\n", encoding="utf-8")
    print(f"Wrote {len(svgs)} SVGs to {dest} (lucide-static {version})")
```

</details>
