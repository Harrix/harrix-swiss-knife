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
- [Class `OnNpmInstallPackages`](#class-onnpminstallpackages)
  - [Method `execute`](#method-execute-2)
  - [Method `in_thread`](#method-in_thread)
  - [Method `thread_after`](#method-thread_after)
- [Class `OnNpmUpdatePackages`](#class-onnpmupdatepackages)
  - [Method `execute`](#method-execute-3)
  - [Method `in_thread`](#method-in_thread-1)
  - [Method `thread_after`](#method-thread_after-1)
- [Class `OnOpenConfigJson`](#class-onopenconfigjson)
  - [Method `execute`](#method-execute-4)
- [Class `OnUvUpdate`](#class-onuvupdate)
  - [Method `execute`](#method-execute-5)
  - [Method `in_thread`](#method-in_thread-2)
  - [Method `thread_after`](#method-thread_after-2)

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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result = self.parent.get_menu()
        self.add_line(result)
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
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnNpmInstallPackages`

```python
class OnNpmInstallPackages(action_base.ActionBase)
```

Install configured NPM packages globally.

This action installs all NPM packages specified in the `config["npm_packages"]`
list as global packages, making them available system-wide for command-line
use and other applications.

<details>
<summary>Code:</summary>

```python
class OnNpmInstallPackages(action_base.ActionBase):

    icon = "📥"
    title = "Install global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Install completed")
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
def in_thread(self) -> None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        return h.dev.run_powershell_script(commands)
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
        self.show_toast("Install completed")
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnNpmUpdatePackages`

```python
class OnNpmUpdatePackages(action_base.ActionBase)
```

Update NPM itself and all globally installed packages.

This action first updates the npm package manager to its latest version,
then updates all globally installed npm packages to their latest versions,
ensuring the development environment has the most current tools available.

<details>
<summary>Code:</summary>

```python
class OnNpmUpdatePackages(action_base.ActionBase):

    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)

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
def in_thread(self) -> None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)
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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        result = h.dev.run_powershell_script(commands)
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
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        result = h.dev.run_powershell_script(commands)
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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_powershell_script(commands)

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
def in_thread(self) -> None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        commands = "uv self update"
        return h.dev.run_powershell_script(commands)
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
