---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `open_images.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOpenImages`](#%EF%B8%8F-class-onopenimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnOpenImages`

```python
class OnOpenImages(ActionBase)
```

Open the source images temporary folder.

This action opens the temporary directory containing original images
(`images`) in the system's file explorer, allowing quick access
to view or manage the source image files.

<details>
<summary>Code:</summary>

```python
class OnOpenImages(ActionBase):

    icon = "📂"
    title = "Open the folder images"

    @ActionBase.handle_exceptions("opening images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the source images temporary folder."""
        path = h.dev.get_project_root() / "temp/images"
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

Open the source images temporary folder.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path = h.dev.get_project_root() / "temp/images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)
```

</details>
