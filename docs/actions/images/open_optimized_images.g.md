---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `open_optimized_images.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOpenOptimizedImages`](#%EF%B8%8F-class-onopenoptimizedimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnOpenOptimizedImages`

```python
class OnOpenOptimizedImages(ActionBase)
```

Open the optimized images temporary folder.

This action opens the temporary directory containing optimized images
(`optimized_images`) in the system's file explorer, allowing quick access
to view or use the processed image files.

<details>
<summary>Code:</summary>

```python
class OnOpenOptimizedImages(ActionBase):

    icon = "📂"
    title = "Open the folder optimized_images"

    @ActionBase.handle_exceptions("opening optimized images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the optimized images temporary folder."""
        path = h.dev.get_project_root() / "temp/optimized_images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open the optimized images temporary folder.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path = h.dev.get_project_root() / "temp/optimized_images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)
```

</details>
