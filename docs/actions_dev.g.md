---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `actions_dev.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `OnExit`](#class-onexit)
  - [Method `__init__`](#method-__init__)
  - [Method `execute`](#method-execute)
- [Class `OnGetMenu`](#class-ongetmenu)
  - [Method `__init__`](#method-__init__-1)
  - [Method `execute`](#method-execute-1)
- [Class `OnNpmManagePackages`](#class-onnpmmanagepackages)
  - [Method `execute`](#method-execute-2)
  - [Method `in_thread`](#method-in_thread)
  - [Method `thread_after`](#method-thread_after)
- [Class `OnOpenConfigJson`](#class-onopenconfigjson)
  - [Method `execute`](#method-execute-3)
- [Class `OnUvUpdate`](#class-onuvupdate)
  - [Method `execute`](#method-execute-4)
  - [Method `in_thread`](#method-in_thread-1)
  - [Method `thread_after`](#method-thread_after-1)

</details>

## Class `OnExit`

```python
class OnExit(action_base.ActionBase)
```

Exit the application.

This action terminates the current Qt application instance,
closing all windows and ending the program execution.

<details>
<summary>Code:</summary>

```python
class OnExit(action_base.ActionBase):

    icon = "×"  # noqa: RUF001
    title = "Exit"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @action_base.ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        QApplication.quit()
```

</details>

### Method `__init__`

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

### Method `execute`

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

## Class `OnGetMenu`

```python
class OnGetMenu(action_base.ActionBase)
```

Display a list of all available menu items.

This action retrieves and displays a complete list of all menu items
from the parent menu, providing a convenient overview of all available
actions in the current context.

<details>
<summary>Code:</summary>

```python
class OnGetMenu(action_base.ActionBase):

    icon = "☰"
    title = "Get the list of items from this menu"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @action_base.ActionBase.handle_exceptions("menu retrieval")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.parent is not None:
            result = self.parent.get_menu()
            self.add_line(result)
        else:
            self.add_line("❌ No parent menu available.")
        self.show_result()
```

</details>

### Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnGetMenu action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__()
        self.parent = kwargs.get("parent")
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
        if self.parent is not None:
            result = self.parent.get_menu()
            self.add_line(result)
        else:
            self.add_line("❌ No parent menu available.")
        self.show_result()
```

</details>

## Class `OnNpmManagePackages`

```python
class OnNpmManagePackages(action_base.ActionBase)
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
class OnNpmManagePackages(action_base.ActionBase):

    icon = "📦"
    title = "Install/Update global NPM packages"

    @action_base.ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("NPM operations thread")
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

    @action_base.ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
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

### Method `thread_after`

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

## Class `OnOpenConfigJson`

```python
class OnOpenConfigJson(action_base.ActionBase)
```

Open the application's configuration file.

This action opens the `config.json` file in the configured editor,
allowing direct viewing and editing of the application's settings
and configuration parameters.

<details>
<summary>Code:</summary>

```python
class OnOpenConfigJson(action_base.ActionBase):

    icon = "⚙️"
    title = "Open config.json"

    @action_base.ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
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
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)
```

</details>

## Class `OnUvUpdate`

```python
class OnUvUpdate(action_base.ActionBase)
```

Update uv package manager to its latest version.

This action updates the uv Python package manager to its latest version
using the 'uv self update' command, ensuring the development environment
has the most current version of this package management tool.

<details>
<summary>Code:</summary>

```python
class OnUvUpdate(action_base.ActionBase):

    icon = "📥"
    title = "Update uv"

    @action_base.ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_command(commands)

    @action_base.ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
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
        commands = "uv self update"
        return h.dev.run_command(commands)
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
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

</details>
