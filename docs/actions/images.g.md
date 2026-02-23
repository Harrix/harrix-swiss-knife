---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `images.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnClearImages`](#%EF%B8%8F-class-onclearimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🏛️ Class `OnOpenImages`](#%EF%B8%8F-class-onopenimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
- [🏛️ Class `OnOpenOptimizedImages`](#%EF%B8%8F-class-onopenoptimizedimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
- [🏛️ Class `OnOpenPhotosInViewer`](#%EF%B8%8F-class-onopenphotosinviewer)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
- [🏛️ Class `OnOptimize`](#%EF%B8%8F-class-onoptimize)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `optimize_images_common`](#%EF%B8%8F-method-optimize_images_common)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnOptimizeClipboard`](#%EF%B8%8F-class-onoptimizeclipboard)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-5)
- [🏛️ Class `OnOptimizeClipboardDialog`](#%EF%B8%8F-class-onoptimizeclipboarddialog)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-6)
- [🏛️ Class `OnOptimizeDialogReplace`](#%EF%B8%8F-class-onoptimizedialogreplace)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-7)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)
- [🏛️ Class `OnOptimizeQuality`](#%EF%B8%8F-class-onoptimizequality)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-2)
- [🏛️ Class `OnOptimizeResize`](#%EF%B8%8F-class-onoptimizeresize)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-8)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-3)
- [🏛️ Class `OnOptimizeSingleImage`](#%EF%B8%8F-class-onoptimizesingleimage)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-9)

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

### ⚙️ Method `execute`

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
        """Execute the code. Main method for the action."""
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

Execute the code. Main method for the action.

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
        """Execute the code. Main method for the action."""
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

Execute the code. Main method for the action.

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

## 🏛️ Class `OnOpenPhotosInViewer`

```python
class OnOpenPhotosInViewer(ActionBase)
```

Open photos folder in configured image viewer (e.g. XnViewMP).

This action opens the folder from `path_photos` in the
program specified by `path_image_viewer` in config.json. If the viewer
is not installed or path is missing, shows a message and adds the key
to config.json.

<details>
<summary>Code:</summary>

```python
class OnOpenPhotosInViewer(ActionBase):

    icon = "📸"
    title = "Open photos in image viewer"

    @ActionBase.handle_exceptions("opening camera uploads in viewer")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        path_viewer = self.config.get("path_image_viewer") or ""
        path_viewer = path_viewer.strip()
        if not path_viewer:
            h.dev.config_update_value(
                "path_image_viewer",
                DEFAULT_PATH_IMAGE_VIEWER,
                "config/config.json",
                is_temp=False,
            )
            self.add_line(
                "❌ path_image_viewer is not set in config.json. "
                "Default path was added. Install XnViewMP (or set path to another image viewer) and run again."
            )
            self.show_result()
            return
        viewer_path = Path(path_viewer)
        if not viewer_path.exists():
            self.add_line(
                f"❌ Image viewer not found: {path_viewer}. "
                "Install XnViewMP (or another viewer) and set path_image_viewer in config.json."
            )
            self.show_result()
            return
        path_camera = (self.config.get("path_photos") or "").strip()
        if not path_camera:
            self.add_line("❌ path_photos is not set in config.json.")
            self.show_result()
            return
        folder = Path(path_camera)
        if not folder.exists():
            self.add_line(f"❌ Folder does not exist: {folder}")
            self.show_result()
            return
        subprocess.Popen([str(viewer_path), str(folder)], shell=False)
        self.add_line(f'Folder "{folder}" opened in image viewer.')
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path_viewer = self.config.get("path_image_viewer") or ""
        path_viewer = path_viewer.strip()
        if not path_viewer:
            h.dev.config_update_value(
                "path_image_viewer",
                DEFAULT_PATH_IMAGE_VIEWER,
                "config/config.json",
                is_temp=False,
            )
            self.add_line(
                "❌ path_image_viewer is not set in config.json. "
                "Default path was added. Install XnViewMP (or set path to another image viewer) and run again."
            )
            self.show_result()
            return
        viewer_path = Path(path_viewer)
        if not viewer_path.exists():
            self.add_line(
                f"❌ Image viewer not found: {path_viewer}. "
                "Install XnViewMP (or another viewer) and set path_image_viewer in config.json."
            )
            self.show_result()
            return
        path_camera = (self.config.get("path_photos") or "").strip()
        if not path_camera:
            self.add_line("❌ path_photos is not set in config.json.")
            self.show_result()
            return
        folder = Path(path_camera)
        if not folder.exists():
            self.add_line(f"❌ Folder does not exist: {folder}")
            self.show_result()
            return
        subprocess.Popen([str(viewer_path), str(folder)], shell=False)
        self.add_line(f'Folder "{folder}" opened in image viewer.')
```

</details>

## 🏛️ Class `OnOptimize`

```python
class OnOptimize(ActionBase)
```

Run standard image optimization on all images in the temp folder.

This action executes the npm optimize script to process all images
in the temporary `images` directory using default optimization settings,
creating compressed versions in the `optimized_images` directory.

<details>
<summary>Code:</summary>

```python
class OnOptimize(ActionBase):

    icon = "🚀"
    title = "Optimize images"
    bold_title = True

    @ActionBase.handle_exceptions("image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize convertPngToAvif=compare", h.dev.get_project_root() / "temp/optimized_images"
        )

    def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None:
        """Perform common image optimization operations.

        Args:

        - `command` (`str`): The npm command to execute for optimization.
        - `output_folder` (`str | Path | None`): Optional output folder to open after optimization.

        Returns:

        - `str | None`: The result of the command execution

        """
        result = h.dev.run_command(command)

        if output_folder:
            h.file.open_file_or_folder(output_folder)

        return result

    @ActionBase.handle_exceptions("optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

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
            "npm run optimize convertPngToAvif=compare", h.dev.get_project_root() / "temp/optimized_images"
        )
```

</details>

### ⚙️ Method `optimize_images_common`

```python
def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None
```

Perform common image optimization operations.

Args:

- `command` (`str`): The npm command to execute for optimization.
- `output_folder` (`str | Path | None`): Optional output folder to open after optimization.

Returns:

- `str | None`: The result of the command execution

<details>
<summary>Code:</summary>

```python
def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None:
        result = h.dev.run_command(command)

        if output_folder:
            h.file.open_file_or_folder(output_folder)

        return result
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

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
        """Execute the code. Main method for the action."""
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.get_text_input(
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

            clr.AddReference("System.Collections.Specialized")
            clr.AddReference("System.Windows.Forms")
            from System.Collections.Specialized import StringCollection  # type: ignore # noqa: PGH003, PLC0415
            from System.Windows.Forms import Clipboard  # type: ignore # noqa: PGH003, PLC0415

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>

### ⚙️ Method `execute`

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
            image_name = self.get_text_input(
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

            clr.AddReference("System.Collections.Specialized")
            clr.AddReference("System.Windows.Forms")
            from System.Collections.Specialized import StringCollection  # type: ignore # noqa: PGH003, PLC0415
            from System.Windows.Forms import Clipboard  # type: ignore # noqa: PGH003, PLC0415

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
```

</details>

## 🏛️ Class `OnOptimizeClipboardDialog`

```python
class OnOptimizeClipboardDialog(ActionBase)
```

Optimize an image from the clipboard with custom naming.

This action extends OnOptimizeClipboard by prompting the user to provide
a custom filename for the optimized image, allowing for more organized
image management in the output directory.

<details>
<summary>Code:</summary>

```python
class OnOptimizeClipboardDialog(ActionBase):

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnOptimizeClipboard().execute(is_dialog=True)
```

</details>

### ⚙️ Method `execute`

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

## 🏛️ Class `OnOptimizeDialogReplace`

```python
class OnOptimizeDialogReplace(OnOptimize)
```

Optimize images in a selected folder and replace the originals.

This action allows the user to select a folder containing images, processes
all images using the npm optimize script, and then replaces the original files
with their optimized versions, maintaining a clean directory structure.

<details>
<summary>Code:</summary>

```python
class OnOptimizeDialogReplace(OnOptimize):

    icon = "⬆️"
    title = "Optimize images in … and replace"
    bold_title = False

    @ActionBase.handle_exceptions("folder image optimization with replacement")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("folder optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return None

        result = self.optimize_images_common(
            f'npm run optimize imagesFolder="{self.folder_path}" convertPngToAvif=compare'
        )

        # Replace original files with optimized versions
        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = self.folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(temp_folder)

        return result

    @ActionBase.handle_exceptions("folder optimization thread completion")
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

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
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
        if self.folder_path is None:
            return None

        result = self.optimize_images_common(
            f'npm run optimize imagesFolder="{self.folder_path}" convertPngToAvif=compare'
        )

        # Replace original files with optimized versions
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

### ⚙️ Method `thread_after`

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

## 🏛️ Class `OnOptimizeResize`

```python
class OnOptimizeResize(OnOptimize)
```

Resize and optimize images (asks for max size in pixels).

<details>
<summary>Code:</summary>

```python
class OnOptimizeResize(OnOptimize):

    icon = "↔️"
    title = "Resize and optimize images"

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.max_size = self.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.max_size = self.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
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
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>

## 🏛️ Class `OnOptimizeSingleImage`

```python
class OnOptimizeSingleImage(OnOptimize)
```

Optimize a single image file and replace the original in place.

This action prompts the user to select a single image file, processes it
using the npm optimize script, and replaces the original file with the
optimized version in the same folder.

<details>
<summary>Code:</summary>

```python
class OnOptimizeSingleImage(OnOptimize):

    icon = "🖼️"
    title = "Optimize one image"
    bold_title = False

    @ActionBase.handle_exceptions("single file optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        filename = Path(filename)
        target_dir = filename.parent
        stem = filename.stem

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename.name
            shutil.copy(filename, temp_filename)

            # E501 fix: split long line for readability and line length
            npm_command = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = self.optimize_images_common(
                npm_command,
                None,
            )

            if result is not None:
                self.add_line(result)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            for ext in (".avif", ".png", ".svg"):
                output_file = optimized_dir / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    h.file.open_file_or_folder(target_dir)
                    break

        self.show_result()
```

</details>

### ⚙️ Method `execute`

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
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        filename = Path(filename)
        target_dir = filename.parent
        stem = filename.stem

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename.name
            shutil.copy(filename, temp_filename)

            # E501 fix: split long line for readability and line length
            npm_command = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = self.optimize_images_common(
                npm_command,
                None,
            )

            if result is not None:
                self.add_line(result)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            for ext in (".avif", ".png", ".svg"):
                output_file = optimized_dir / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    h.file.open_file_or_folder(target_dir)
                    break

        self.show_result()
```

</details>
