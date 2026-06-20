---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `clear_images.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnClearImages`](#️-class-onclearimages)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnClearImages`

```python
class OnClearImages(ActionBase)
```

Clear temporary image directories.

This action removes all files from the temporary image folders
(`images` and `optimized_images`) and recreates the empty directories,
providing a clean workspace for new image operations.

<details>
<summary>Code:</summary>

```python
class OnClearImages(ActionBase):

    icon = "🧹"
    title = "Clear folders images"

    @ActionBase.handle_exceptions("clearing image folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Clear temporary image directories."""
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp/optimized_images"]
        for path in paths:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True)
                result = f"Folder `{path}` is clean."
            else:
                result = f"❌ Folder `{path}` is not exist."
            self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Clear temporary image directories.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp/optimized_images"]
        for path in paths:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True)
                result = f"Folder `{path}` is clean."
            else:
                result = f"❌ Folder `{path}` is not exist."
            self.add_line(result)
        self.show_result()
```

</details>
