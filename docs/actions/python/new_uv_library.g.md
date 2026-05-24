---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `new_uv_library.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnNewUvLibrary`](#%EF%B8%8F-class-onnewuvlibrary)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnNewUvLibrary`

```python
class OnNewUvLibrary(ActionBase)
```

Create a new Python library with uv package manager.

This action creates a new Python library using the uv package manager in a selected directory.
The user can choose from predefined project creation directories or browse for a custom location.
The action prompts for a library name with auto-generation option and automatically sets up
the library structure, virtual environment, and dependencies using uv.

The uv package manager (<https://github.com/astral-sh/uv>) is used to set up the library
structure with the --lib flag, which creates a packaged project with src layout and py.typed
marker for type hints. The library is then opened in the configured editor specified in
the application settings.

Libraries are intended to be built and distributed, e.g., by uploading them to PyPI.

<details>
<summary>Code:</summary>

```python
class OnNewUvLibrary(ActionBase):

    icon = "🐍"
    title = "New uv library"

    @ActionBase.handle_exceptions("creating new uv library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create a new Python library with uv package manager."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        # Create auto-generator function that uses the selected folder
        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_py_projects"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.library_name = self.dialogs.get_text_input_with_auto(
            "Library name",
            "Enter the name of the library (English, without spaces):",
            auto_generator=generate_auto_name,
        )
        if not self.library_name:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("creating uv library thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.library_name is None or self.folder_path is None:
            return

        library_name_clean = self.library_name.replace(" ", "-")

        # Create library using uv init --lib
        commands = f"""
            cd {self.folder_path}
            uv init --lib {library_name_clean}
            cd {library_name_clean}
            {self.config["editor"]} .
        """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating uv library thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Create a new Python library with uv package manager.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        # Create auto-generator function that uses the selected folder
        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_py_projects"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.library_name = self.dialogs.get_text_input_with_auto(
            "Library name",
            "Enter the name of the library (English, without spaces):",
            auto_generator=generate_auto_name,
        )
        if not self.library_name:
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
        if self.library_name is None or self.folder_path is None:
            return

        library_name_clean = self.library_name.replace(" ", "-")

        # Create library using uv init --lib
        commands = f"""
            cd {self.folder_path}
            uv init --lib {library_name_clean}
            cd {library_name_clean}
            {self.config["editor"]} .
        """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)
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
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
