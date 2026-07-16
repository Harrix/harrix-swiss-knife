---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_python_projects.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckPythonProjects`](#️-class-oncheckpythonprojects)
  - [⚙️ Method `check_all_python_projects_common`](#️-method-check_all_python_projects_common)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnCheckPythonProjects`

```python
class OnCheckPythonProjects(PythonProjectChecksMixin)
```

Run ty, ruff, pytest, Harrix PY and MD checks for all paths_python_projects.

<details>
<summary>Code:</summary>

```python
class OnCheckPythonProjects(PythonProjectChecksMixin):

    icon = "🚧"
    title = "Full PY check all projects"
    cli_available = True
    cli_hint = "py check-all"

    def check_all_python_projects_common(self) -> None:
        """Run ty, ruff, pytest, and Harrix Python/Markdown checks for each configured project."""
        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            return

        project_paths: list[Path] = []
        for entry in raw:
            path = Path(str(entry)).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                self.add_line(f"⚠️ Could not resolve path: {entry}")
                continue
            if not resolved.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {resolved}")
                continue
            project_paths.append(resolved)

        if not project_paths:
            self.add_line("❌ No valid project paths in paths_python_projects.")
            return

        failed_projects: dict[str, list[str]] = {}

        for project_path in project_paths:
            self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
            project_failures = self.check_single_python_project(project_path)
            if project_failures:
                failed_projects[project_path.name] = project_failures

        passed_count = len(project_paths) - len(failed_projects)
        total_count = len(project_paths)
        if not failed_projects:
            self.add_line(f"\n✅ All projects passed all checks ({passed_count}/{total_count}).")
            return

        self.add_line(f"\n❌ Checks failed in {len(failed_projects)} project(s):")
        for name, failures in failed_projects.items():
            self.add_line(f"- {name}: {', '.join(failures)}")

    @ActionBase.handle_exceptions("checking all Python projects")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Run full Python checks for each path in paths_python_projects."""
        if noninteractive:
            self.add_line("🔵 Starting full PY checks for all projects")
            self.check_all_python_projects_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking all Python projects thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_all_python_projects_common()

    @ActionBase.handle_exceptions("checking all Python projects thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `check_all_python_projects_common`

```python
def check_all_python_projects_common(self) -> None
```

Run ty, ruff, pytest, and Harrix Python/Markdown checks for each configured project.

<details>
<summary>Code:</summary>

```python
def check_all_python_projects_common(self) -> None:
        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            return

        project_paths: list[Path] = []
        for entry in raw:
            path = Path(str(entry)).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                self.add_line(f"⚠️ Could not resolve path: {entry}")
                continue
            if not resolved.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {resolved}")
                continue
            project_paths.append(resolved)

        if not project_paths:
            self.add_line("❌ No valid project paths in paths_python_projects.")
            return

        failed_projects: dict[str, list[str]] = {}

        for project_path in project_paths:
            self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
            project_failures = self.check_single_python_project(project_path)
            if project_failures:
                failed_projects[project_path.name] = project_failures

        passed_count = len(project_paths) - len(failed_projects)
        total_count = len(project_paths)
        if not failed_projects:
            self.add_line(f"\n✅ All projects passed all checks ({passed_count}/{total_count}).")
            return

        self.add_line(f"\n❌ Checks failed in {len(failed_projects)} project(s):")
        for name, failures in failed_projects.items():
            self.add_line(f"- {name}: {', '.join(failures)}")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Run full Python checks for each path in paths_python_projects.

<details>
<summary>Code:</summary>

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        if noninteractive:
            self.add_line("🔵 Starting full PY checks for all projects")
            self.check_all_python_projects_common()
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
        self.check_all_python_projects_common()
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
