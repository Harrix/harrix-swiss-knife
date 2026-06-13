---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_clipboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeClipboard`](#%EF%B8%8F-class-onoptimizeclipboard)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnOptimizeClipboard`

```python
class OnOptimizeClipboard(ActionBase)
```

Optimize an image from the clipboard with default naming.

This action takes an image from the clipboard, saves it as a temporary file,
optimizes it using the npm optimize script, and then places the optimized
image path back into the clipboard for easy pasting into documents.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboard(ActionBase):

    icon = "🚀"
    title = "Optimize image from clipboard"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize an image from the clipboard with default naming."""
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.dialogs.get_text_input(
                "Image name", "Enter the name of the image (English, without spaces):", "image_01"
            )
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = h.dev.run_command(commands)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            stem = Path(filename).stem
            output_ext = ".avif" if (optimized_dir / (stem + ".avif")).exists() else ".png"
            filename = (optimized_dir / (stem + output_ext)).resolve()

            clipboard = QGuiApplication.clipboard()
            if clipboard is None:
                self.add_line("❌ Clipboard is not available")
                return

            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(str(filename))])
            clipboard.setMimeData(mime_data)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Optimize an image from the clipboard with default naming.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.dialogs.get_text_input(
                "Image name", "Enter the name of the image (English, without spaces):", "image_01"
            )
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = h.dev.run_command(commands)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            stem = Path(filename).stem
            output_ext = ".avif" if (optimized_dir / (stem + ".avif")).exists() else ".png"
            filename = (optimized_dir / (stem + output_ext)).resolve()

            clipboard = QGuiApplication.clipboard()
            if clipboard is None:
                self.add_line("❌ Clipboard is not available")
                return

            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(str(filename))])
            clipboard.setMimeData(mime_data)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>
