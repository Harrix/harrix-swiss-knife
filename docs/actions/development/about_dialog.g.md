---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `about_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAboutDialog`](#️-class-onaboutdialog)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnAboutDialog`

```python
class OnAboutDialog(ActionBase)
```

Show the about dialog with program information.

This action displays a dialog window containing information about the application,
including version, description, author, and license information.

<details>
<summary>Code:</summary>

```python
class OnAboutDialog(ActionBase):

    icon = "ℹ️"  # noqa: RUF001
    title = "About"
    show_in_compact_mode = True

    @ActionBase.handle_exceptions("about dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show the about dialog with program information."""
        version = self._get_version_from_pyproject()

        about_info = self.dialogs.show_about_dialog(
            title="About",
            app_name="Harrix Swiss Knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")

    def _get_version_from_pyproject(self) -> str:
        """Get version from pyproject.toml file.

        Returns:

        - `str`: Version string from `pyproject.toml`, or "Unknown" if not found.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Show the about dialog with program information.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        version = self._get_version_from_pyproject()

        about_info = self.dialogs.show_about_dialog(
            title="About",
            app_name="Harrix Swiss Knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")
```

</details>
