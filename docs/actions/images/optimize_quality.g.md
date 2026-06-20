---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_quality.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeQuality`](#️-class-onoptimizequality)
  - [⚙️ Method `in_thread`](#️-method-in_thread)

</details>

## 🏛️ Class `OnOptimizeQuality`

```python
class OnOptimizeQuality(OnOptimize)
```

Optimize images with higher quality settings.

Processes all images in the temp/images directory using settings
that prioritize visual quality over file size reduction.

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
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            quality=True,
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
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            quality=True,
        )
```

</details>
