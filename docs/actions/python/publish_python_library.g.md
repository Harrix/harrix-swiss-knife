---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `publish_python_library.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnPublishPythonLibrary`](#%EF%B8%8F-class-onpublishpythonlibrary)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread_01`](#%EF%B8%8F-method-in_thread_01)
  - [⚙️ Method `thread_after_01`](#%EF%B8%8F-method-thread_after_01)

</details>

## 🏛️ Class `OnPublishPythonLibrary`

```python
class OnPublishPythonLibrary(ActionBase)
```

Publish a new version of a Python library to PyPI.

This action automates the process of updating, building, and publishing a Python
library package to PyPI. The process follows these steps:

1. Select the library to publish from configured paths
2. Bump the minor version number of the selected library
3. Build the package and publish it to PyPI using the provided token
4. Commit the version changes to the library repository

The action requires a PyPI token, which can be provided in the configuration or
entered when prompted. The entire process is executed in background threads to
maintain UI responsiveness.

Note: Since dependent projects now use editable installs (uv add --editable),
they automatically receive updates without needing to update package versions.

<details>
<summary>Code:</summary>

```python
class OnPublishPythonLibrary(ActionBase):

    icon = "⚡"
    title = "Publish Python library to PyPI in …"

    @ActionBase.handle_exceptions("publishing Python library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Publish a new version of a Python library to PyPI."""
        # Select library to publish
        self.library_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_libraries"], self.config["path_github"]
        )
        if not self.library_path:
            return

        # Get PyPI token
        self.token = self.config.get("pypi_token", "")
        if not self.token:
            self.token = self.dialogs.get_text_input(
                "PyPI token", "Enter the token of the project in PyPI:", f"pypi-{'Aa' * 88}"
            )
        if not self.token:
            return

        self.library_name = self.library_path.parts[-1]
        self.start_thread(self.in_thread_01, self.thread_after_01, f"Build and publish {self.library_name}")

    @ActionBase.handle_exceptions("publishing library build thread")
    def in_thread_01(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        library_path = Path(self.library_path)
        cwd = str(library_path)

        version_output = self._run_argv(["uv", "version", "--bump", "minor"], cwd=cwd).strip()
        self.new_version = version_output.split(" => ")[1].splitlines()[0]
        self.add_line(f"New version: {self.new_version}")

        self.add_line(self._run_argv(["uv", "sync", "--upgrade", "--active"], cwd=cwd))

        dist_dir = library_path / "dist"
        if dist_dir.is_dir():
            shutil.rmtree(dist_dir, ignore_errors=True)

        self.add_line(self._run_argv(["uv", "build"], cwd=cwd))

        publish_env = {**os.environ, "UV_PUBLISH_TOKEN": str(self.token)}
        self.add_line(self._run_argv(["uv", "publish"], cwd=cwd, env=publish_env))

        self.add_line(self._run_argv(["git", "add", "pyproject.toml", "uv.lock"], cwd=cwd))
        self.add_line(
            self._run_argv(
                ["git", "commit", "-m", f"🚀 Build version {self.new_version}"],
                cwd=cwd,
            )
        )
        return None

    @ActionBase.handle_exceptions("publishing library thread completion")
    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _run_argv(
        self,
        command: list[str],
        *,
        cwd: str,
        env: dict[str, str] | None = None,
        timeout: float = _DEFAULT_SUBPROCESS_TIMEOUT,
    ) -> str:
        """Run a command as an argv list and return combined output."""
        executable = shutil.which(command[0]) or command[0]
        argv = [executable, *command[1:]]
        try:
            process = subprocess.run(
                argv,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=timeout,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds: {' '.join(command)}"

        output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
        output = "\n".join(filter(None, output_parts))
        if process.returncode != 0:
            self.add_line(f"❌ Command failed ({process.returncode}): {' '.join(command)}")
        return output
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Publish a new version of a Python library to PyPI.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        # Select library to publish
        self.library_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_libraries"], self.config["path_github"]
        )
        if not self.library_path:
            return

        # Get PyPI token
        self.token = self.config.get("pypi_token", "")
        if not self.token:
            self.token = self.dialogs.get_text_input(
                "PyPI token", "Enter the token of the project in PyPI:", f"pypi-{'Aa' * 88}"
            )
        if not self.token:
            return

        self.library_name = self.library_path.parts[-1]
        self.start_thread(self.in_thread_01, self.thread_after_01, f"Build and publish {self.library_name}")
```

</details>

### ⚙️ Method `in_thread_01`

```python
def in_thread_01(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread_01(self) -> str | None:
        library_path = Path(self.library_path)
        cwd = str(library_path)

        version_output = self._run_argv(["uv", "version", "--bump", "minor"], cwd=cwd).strip()
        self.new_version = version_output.split(" => ")[1].splitlines()[0]
        self.add_line(f"New version: {self.new_version}")

        self.add_line(self._run_argv(["uv", "sync", "--upgrade", "--active"], cwd=cwd))

        dist_dir = library_path / "dist"
        if dist_dir.is_dir():
            shutil.rmtree(dist_dir, ignore_errors=True)

        self.add_line(self._run_argv(["uv", "build"], cwd=cwd))

        publish_env = {**os.environ, "UV_PUBLISH_TOKEN": str(self.token)}
        self.add_line(self._run_argv(["uv", "publish"], cwd=cwd, env=publish_env))

        self.add_line(self._run_argv(["git", "add", "pyproject.toml", "uv.lock"], cwd=cwd))
        self.add_line(
            self._run_argv(
                ["git", "commit", "-m", f"🚀 Build version {self.new_version}"],
                cwd=cwd,
            )
        )
        return None
```

</details>

### ⚙️ Method `thread_after_01`

```python
def thread_after_01(self, result: Any) -> None
```

Execute code in the main thread after in_thread_01(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
