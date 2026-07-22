---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `new_uv_notebook.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnNewUvNotebook`](#%EF%B8%8F-class-onnewuvnotebook)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnNewUvNotebook`

```python
class OnNewUvNotebook(ActionBase)
```

Create a new Jupyter notebook project with uv package manager.

This action creates a new flat Python project using the uv package manager in a selected directory.
The user can choose from predefined project creation directories or browse for a custom location.
The action prompts for a notebook name with auto-generation option and automatically sets up
the project structure, virtual environment, Jupyter dependencies, and a starter notebook.

The project is opened in the configured editor specified in the application settings.

<details>
<summary>Code:</summary>

```python
class OnNewUvNotebook(ActionBase):

    icon = "📓"
    title = "New uv notebook in …"

    @ActionBase.handle_exceptions("creating new uv notebook")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create a new Jupyter notebook project with uv package manager."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_jupyter_notebooks"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.notebook_name = self.dialogs.get_text_input_with_auto(
            "Notebook name",
            "Enter the name of the notebook project (English, without spaces):",
            auto_generator=generate_auto_name,
            validator=validate_uv_project_name,
        )
        if not self.notebook_name:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("creating uv notebook thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.notebook_name is None or self.folder_path is None:
            return

        self.add_line(
            h.py.create_uv_new_notebook(
                self.notebook_name.replace(" ", "-"),
                str(self.folder_path),
                self.config["editor"],
                self.config["cli_commands"],
            ),
        )

    @ActionBase.handle_exceptions("creating uv notebook thread completion")
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

Create a new Jupyter notebook project with uv package manager.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_jupyter_notebooks"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.notebook_name = self.dialogs.get_text_input_with_auto(
            "Notebook name",
            "Enter the name of the notebook project (English, without spaces):",
            auto_generator=generate_auto_name,
            validator=validate_uv_project_name,
        )
        if not self.notebook_name:
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
        if self.notebook_name is None or self.folder_path is None:
            return

        self.add_line(
            h.py.create_uv_new_notebook(
                self.notebook_name.replace(" ", "-"),
                str(self.folder_path),
                self.config["editor"],
                self.config["cli_commands"],
            ),
        )
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
