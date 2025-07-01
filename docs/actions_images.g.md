---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `actions_images.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `OnClearImages`](#class-onclearimages)
  - [Method `execute`](#method-execute)
- [Class `OnOpenImages`](#class-onopenimages)
  - [Method `execute`](#method-execute-1)
- [Class `OnOpenOptimizedImages`](#class-onopenoptimizedimages)
  - [Method `execute`](#method-execute-2)
- [Class `OnOptimize`](#class-onoptimize)
  - [Method `execute`](#method-execute-3)
  - [Method `in_thread`](#method-in_thread)
  - [Method `thread_after`](#method-thread_after)
- [Class `OnOptimizeClipboard`](#class-onoptimizeclipboard)
  - [Method `execute`](#method-execute-4)
- [Class `OnOptimizeClipboardDialog`](#class-onoptimizeclipboarddialog)
  - [Method `execute`](#method-execute-5)
- [Class `OnOptimizeDialogReplace`](#class-onoptimizedialogreplace)
  - [Method `execute`](#method-execute-6)
  - [Method `in_thread`](#method-in_thread-1)
  - [Method `thread_after`](#method-thread_after-1)
- [Class `OnOptimizeFile`](#class-onoptimizefile)
  - [Method `execute`](#method-execute-7)
- [Class `OnOptimizeQuality`](#class-onoptimizequality)
  - [Method `execute`](#method-execute-8)
  - [Method `in_thread`](#method-in_thread-2)
  - [Method `thread_after`](#method-thread_after-2)
- [Class `OnResizeOptimizePngToAvif`](#class-onresizeoptimizepngtoavif)
  - [Method `execute`](#method-execute-9)
  - [Method `in_thread`](#method-in_thread-3)
  - [Method `thread_after`](#method-thread_after-3)

</details>

## Class `OnClearImages`

```python
class OnClearImages(action_base.ActionBase)
```

Clear temporary image directories.

This action removes all files from the temporary image folders
(`images` and `optimized_images`) and recreates the empty directories,
providing a clean workspace for new image operations.

<details>
<summary>Code:</summary>

```python
class OnClearImages(action_base.ActionBase):

    icon = "🧹"
    title = "Clear folders images"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
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

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

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

## Class `OnOpenImages`

```python
class OnOpenImages(action_base.ActionBase)
```

Open the source images temporary folder.

This action opens the temporary directory containing original images
(`images`) in the system's file explorer, allowing quick access
to view or manage the source image files.

<details>
<summary>Code:</summary>

```python
class OnOpenImages(action_base.ActionBase):

    icon = "📂"
    title = "Open the folder images"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        path = h.dev.get_project_root() / "temp/images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path = h.dev.get_project_root() / "temp/images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)
```

</details>

## Class `OnOpenOptimizedImages`

```python
class OnOpenOptimizedImages(action_base.ActionBase)
```

Open the optimized images temporary folder.

This action opens the temporary directory containing optimized images
(`optimized_images`) in the system's file explorer, allowing quick access
to view or use the processed image files.

<details>
<summary>Code:</summary>

```python
class OnOpenOptimizedImages(action_base.ActionBase):

    icon = "📂"
    title = "Open the folder optimized_images"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        path = h.dev.get_project_root() / "temp/optimized_images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path = h.dev.get_project_root() / "temp/optimized_images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)
```

</details>

## Class `OnOptimize`

```python
class OnOptimize(action_base.ActionBase)
```

Run standard image optimization on all images in the temp folder.

This action executes the npm optimize script to process all images
in the temporary `images` directory using default optimization settings,
creating compressed versions in the `optimized_images` directory.

<details>
<summary>Code:</summary>

```python
class OnOptimize(action_base.ActionBase):

    icon = "🚀"
    title = "Optimize images"
    bold_title = True

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return h.dev.run_powershell_script("npm run optimize")

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return h.dev.run_powershell_script("npm run optimize")
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnOptimizeClipboard`

```python
class OnOptimizeClipboard(action_base.ActionBase)
```

Optimize an image from the clipboard with default naming.

This action takes an image from the clipboard, saves it as a temporary file,
optimizes it using the npm optimize script, and then places the optimized
image path back into the clipboard for easy pasting into documents.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboard(action_base.ActionBase):

    icon = "🚀"
    title = "Optimize image from clipboard"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.get_text_input("Image name", "Enter the name of the image (English, without spaces):")
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

            clr.AddReference("System.Collections.Specialized")  # type: ignore[attr-defined]
            clr.AddReference("System.Windows.Forms")  # type: ignore[attr-defined]
            from System.Collections.Specialized import StringCollection  # type: ignore # noqa: PGH003, PLC0415
            from System.Windows.Forms import Clipboard  # type: ignore # noqa: PGH003, PLC0415

            filename = h.dev.get_project_root() / "temp/optimized_images" / filename
            filename = filename.resolve()

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

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
            image_name = self.get_text_input("Image name", "Enter the name of the image (English, without spaces):")
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

            clr.AddReference("System.Collections.Specialized")  # type: ignore[attr-defined]
            clr.AddReference("System.Windows.Forms")  # type: ignore[attr-defined]
            from System.Collections.Specialized import StringCollection  # type: ignore # noqa: PGH003, PLC0415
            from System.Windows.Forms import Clipboard  # type: ignore # noqa: PGH003, PLC0415

            filename = h.dev.get_project_root() / "temp/optimized_images" / filename
            filename = filename.resolve()

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>

## Class `OnOptimizeClipboardDialog`

```python
class OnOptimizeClipboardDialog(action_base.ActionBase)
```

Optimize an image from the clipboard with custom naming.

This action extends OnOptimizeClipboard by prompting the user to provide
a custom filename for the optimized image, allowing for more organized
image management in the output directory.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboardDialog(action_base.ActionBase):

    icon = "🚀"
    title = "Optimize image from clipboard as …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnOptimizeClipboard().execute(is_dialog=True)
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        OnOptimizeClipboard().execute(is_dialog=True)
```

</details>

## Class `OnOptimizeDialogReplace`

```python
class OnOptimizeDialogReplace(action_base.ActionBase)
```

Optimize images in a selected folder and replace the originals.

This action allows the user to select a folder containing images, processes
all images using the npm optimize script, and then replaces the original files
with their optimized versions, maintaining a clean directory structure.

<details>
<summary>Code:</summary>

```python
class OnOptimizeDialogReplace(action_base.ActionBase):

    icon = "⬆️"
    title = "Optimize images in … and replace"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return None

        result = h.dev.run_powershell_script(f'npm run optimize imagesFolder="{self.folder_path}"')

        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = self.folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(temp_folder)

        return result

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        if self.folder_path is None:
            return
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return None

        result = h.dev.run_powershell_script(f'npm run optimize imagesFolder="{self.folder_path}"')

        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = self.folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(temp_folder)

        return result
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        if self.folder_path is None:
            return
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnOptimizeFile`

```python
class OnOptimizeFile(action_base.ActionBase)
```

Optimize a single image file.

This action prompts the user to select a single image file, processes it
using the npm optimize script, and saves the optimized version to the
`optimized_images` directory for easy access.

<details>
<summary>Code:</summary>

```python
class OnOptimizeFile(action_base.ActionBase):

    icon = "🖼️"
    title = "Optimize one image"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )
        if not filename:
            return

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / Path(filename).name
            shutil.copy(filename, temp_filename)

            commands: str = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        filename = self.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )
        if not filename:
            return

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / Path(filename).name
            shutil.copy(filename, temp_filename)

            commands: str = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnOptimizeQuality`

```python
class OnOptimizeQuality(action_base.ActionBase)
```

Optimize images with higher quality settings.

This action runs the npm optimize script with the quality flag enabled,
which processes all images in the temp/images directory using settings
that prioritize visual quality over file size reduction, suitable for
images where detail preservation is important.

<details>
<summary>Code:</summary>

```python
class OnOptimizeQuality(action_base.ActionBase):

    icon = "🔝"
    title = "Optimize images (high quality)"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return h.dev.run_powershell_script("npm run optimize quality=true")

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return h.dev.run_powershell_script("npm run optimize quality=true")
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnResizeOptimizePngToAvif`

```python
class OnResizeOptimizePngToAvif(action_base.ActionBase)
```

Resize and optimize images and convert PNG files to AVIF format too.

<details>
<summary>Code:</summary>

```python
class OnResizeOptimizePngToAvif(action_base.ActionBase):

    icon = "↔️"
    title = "Resize and optimize images (with PNG to AVIF)"
    bold_title = True

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.max_size = self.get_text_input("Max size", "Input max image size in pixels")

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return h.dev.run_powershell_script(f"npm run optimize convertPngToAvif=true maxSize={self.max_size}")

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.max_size = self.get_text_input("Max size", "Input max image size in pixels")

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return h.dev.run_powershell_script(f"npm run optimize convertPngToAvif=true maxSize={self.max_size}")
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>
