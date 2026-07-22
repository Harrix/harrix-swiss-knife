---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `open_photos_in_viewer.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOpenPhotosInViewer`](#%EF%B8%8F-class-onopenphotosinviewer)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnOpenPhotosInViewer`

```python
class OnOpenPhotosInViewer(ActionBase)
```

Open photos folder in configured image viewer.

This action opens the folder from `path_photos` in the program specified
by `path_image_viewer` in `config.json`. If the path is missing or the
executable does not exist, shows an error message.

<details>
<summary>Code:</summary>

```python
class OnOpenPhotosInViewer(ActionBase):

    icon = "📸"
    title = "Open photos in image viewer"

    @ActionBase.handle_exceptions("opening camera uploads in viewer")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open photos folder in configured image viewer."""
        path_viewer = (self.config.get("path_image_viewer") or "").strip()
        if not path_viewer:
            self.add_line(
                "❌ path_image_viewer is not set in config.json. "
                "Set it to the full path of your image viewer executable."
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

Open photos folder in configured image viewer.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        path_viewer = (self.config.get("path_image_viewer") or "").strip()
        if not path_viewer:
            self.add_line(
                "❌ path_image_viewer is not set in config.json. "
                "Set it to the full path of your image viewer executable."
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
