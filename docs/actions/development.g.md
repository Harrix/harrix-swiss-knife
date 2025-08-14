---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `development.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAboutDialog`](#%EF%B8%8F-class-onaboutdialog)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_get_version_from_pyproject`](#%EF%B8%8F-method-_get_version_from_pyproject)
- [🏛️ Class `OnExit`](#%EF%B8%8F-class-onexit)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
- [🏛️ Class `OnNpmManagePackages`](#%EF%B8%8F-class-onnpmmanagepackages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnOpenConfigJson`](#%EF%B8%8F-class-onopenconfigjson)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
- [🏛️ Class `OnUvUpdate`](#%EF%B8%8F-class-onuvupdate)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)

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
        """Execute the code. Main method for the action."""
        version = self._get_version_from_pyproject()

        about_info = self.show_about_dialog(
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
            str: Version string from pyproject.toml, or "Unknown" if not found.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with Path.open(pyproject_path, "rb") as f:
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

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        version = self._get_version_from_pyproject()

        about_info = self.show_about_dialog(
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

### ⚙️ Method `_get_version_from_pyproject`

```python
def _get_version_from_pyproject(self) -> str
```

Get version from pyproject.toml file.

Returns:
str: Version string from pyproject.toml, or "Unknown" if not found.

<details>
<summary>Code:</summary>

```python
def _get_version_from_pyproject(self) -> str:
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with Path.open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"
```

</details>

## 🏛️ Class `OnExit`

```python
class OnExit(ActionBase)
```

Exit the application.

This action terminates the current Qt application instance,
closing all windows and ending the program execution.

<details>
<summary>Code:</summary>

```python
class OnExit(ActionBase):

    icon = "×"  # noqa: RUF001
    title = "Exit"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        QApplication.quit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnExit action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__()
        self.parent = kwargs.get("parent")
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
        QApplication.quit()
```

</details>

## 🏛️ Class `OnNpmManagePackages`

```python
class OnNpmManagePackages(ActionBase)
```

Install or update configured NPM packages globally.

This action manages NPM packages specified in the `config["npm_packages"]` list:

1. Updates NPM itself to the latest version
2. Installs/updates all configured packages (npm install will update if already exists)
3. Runs global update to ensure all packages are at latest versions

This ensures all configured packages are present and up-to-date in the system.

<details>
<summary>Code:</summary>

```python
class OnNpmManagePackages(ActionBase):

    icon = "📦"
    title = "Install/Update global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
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
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"
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
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnOpenConfigJson`

```python
class OnOpenConfigJson(ActionBase)
```

Open the application's configuration file.

This action opens the `config.json` file in the configured editor,
allowing direct viewing and editing of the application's settings
and configuration parameters.

<details>
<summary>Code:</summary>

```python
class OnOpenConfigJson(ActionBase):

    icon = "⚙️"
    title = "Open config.json"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
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
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)
```

</details>

## 🏛️ Class `OnUvUpdate`

```python
class OnUvUpdate(ActionBase)
```

Update uv package manager to its latest version.

This action updates the uv Python package manager to its latest version
using the 'uv self update' command, ensuring the development environment
has the most current version of this package management tool.

<details>
<summary>Code:</summary>

```python
class OnUvUpdate(ActionBase):

    icon = "📥"
    title = "Update uv"

    @ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_command(commands)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
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
        commands = "uv self update"
        return h.dev.run_command(commands)
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
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

</details>
