---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `clear_temp_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnClearTempFolder`](#️-class-oncleartempfolder)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnClearTempFolder`

```python
class OnClearTempFolder(ActionBase)
```

Clear the project `temp/` folder.

Empties `images` and `optimized_images` in place and removes all other
files and folders under `temp/`.

<details>
<summary>Code:</summary>

```python
class OnClearTempFolder(ActionBase):

    icon = "🧹"
    title = "Clear temp folder"

    @ActionBase.handle_exceptions("clearing temp folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Clear project temp directory."""
        for line in clear_temp_folder():
            self.add_line(line)
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Clear project temp directory.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        for line in clear_temp_folder():
            self.add_line(line)
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
