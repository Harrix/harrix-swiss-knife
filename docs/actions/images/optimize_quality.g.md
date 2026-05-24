---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_quality.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeQuality`](#%EF%B8%8F-class-onoptimizequality)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)

</details>

## 🏛️ Class `OnOptimizeQuality`

```python
class OnOptimizeQuality(OnOptimize)
```

Optimize images with higher quality settings.

This action runs the npm optimize script with the quality flag enabled,
which processes all images in the temp/images directory using settings
that prioritize visual quality over file size reduction, suitable for
images where detail preservation is important.

<details>
<summary>Code:</summary>

```python
class OnOptimizeQuality(OnOptimize):

    icon = "🔝"
    title = "Optimize images (high quality)"
    bold_title = False

    @ActionBase.handle_exceptions("high quality optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize quality=true convertPngToAvif=compare",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return self.optimize_images_common(
            "npm run optimize quality=true convertPngToAvif=compare",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>
