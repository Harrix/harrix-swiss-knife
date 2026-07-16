---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_python_project.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckPythonProject`](#️-class-oncheckpythonproject)
  - [⚙️ Method `check_python_project_common`](#️-method-check_python_project_common)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnCheckPythonProject`

```python
class OnCheckPythonProject(PythonProjectChecksMixin)
```

Run ty, ruff, pytest, Harrix PY and MD checks for one project folder.

<details>
<summary>Code:</summary>

```python
class OnCheckPythonProject(PythonProjectChecksMixin):

    icon = "🚧"
    title = "Full PY check in …"
    cli_available = True
    cli_hint = "py check"

    def check_python_project_common(self) -> None:
        """Run ty, ruff, pytest, and Harrix Python/Markdown checks for ``folder_path``."""
        if self.folder_path is None:
            return

        project_path = Path(self.folder_path).resolve()
        if not project_path.is_dir():
            self.add_line(f"❌ Not a directory: {project_path}")
            return

        self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
        project_failures = self.check_single_python_project(project_path)

        if not project_failures:
            self.add_line(f"\n✅ All checks passed for {project_path.name}.")
            return

        self.add_line(f"\n❌ Checks failed for {project_path.name}: {', '.join(project_failures)}")

    @ActionBase.handle_exceptions("checking Python project")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Run full Python checks for one project folder."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting full PY check for path: {self.folder_path}")
            self.check_python_project_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking Python project thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_python_project_common()

    @ActionBase.handle_exceptions("checking Python project thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `check_python_project_common`

```python
def check_python_project_common(self) -> None
```

Run ty, ruff, pytest, and Harrix Python/Markdown checks for `folder_path`.

<details>
<summary>Code:</summary>

```python
def check_python_project_common(self) -> None:
        if self.folder_path is None:
            return

        project_path = Path(self.folder_path).resolve()
        if not project_path.is_dir():
            self.add_line(f"❌ Not a directory: {project_path}")
            return

        self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
        project_failures = self.check_single_python_project(project_path)

        if not project_failures:
            self.add_line(f"\n✅ All checks passed for {project_path.name}.")
            return

        self.add_line(f"\n❌ Checks failed for {project_path.name}: {', '.join(project_failures)}")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Run full Python checks for one project folder.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting full PY check for path: {self.folder_path}")
            self.check_python_project_common()
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
        self.check_python_project_common()
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
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>
