---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `get_set_variables_from_yaml.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnGetSetVariablesFromYaml`](#%EF%B8%8F-class-ongetsetvariablesfromyaml)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnGetSetVariablesFromYaml`

```python
class OnGetSetVariablesFromYaml(ActionBase)
```

Get a sorted list of all variables from YAML frontmatter in Markdown files.

This action recursively searches through all Markdown files in a selected folder
and extracts all unique variable names from their YAML frontmatter. It:

1. Recursively searches all subfolders for `.md` files
2. Extracts YAML frontmatter from each file
3. Collects all unique variable names (keys) from the YAML
4. Returns a sorted list of all variables found

Files and folders matching common ignore patterns (like `.git`, `__pycache__`,
`node_modules`, etc.) and hidden files/folders are automatically ignored.

Example output: `['categories', 'date', 'tags']`

<details>
<summary>Code:</summary>

```python
class OnGetSetVariablesFromYaml(ActionBase):

    icon = "📋"
    title = "Get set variables from YAML in …"

    @ActionBase.handle_exceptions("getting set variables from YAML")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Get a sorted list of all variables from YAML frontmatter in Markdown files."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("getting set variables from YAML thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Processing folder: {self.folder_path}")
        variables = h.md.get_set_variables_from_yaml(self.folder_path)

        if variables:
            self.add_line(f"\n✅ Found {len(variables)} unique variable(s):\n")
            for variable in variables:
                self.add_line(f"  - {variable}")
        else:
            self.add_line("ℹ️ No variables found in YAML frontmatter.")  # noqa: RUF001

    @ActionBase.handle_exceptions("getting set variables from YAML thread completion")
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

Get a sorted list of all variables from YAML frontmatter in Markdown files.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
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
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Processing folder: {self.folder_path}")
        variables = h.md.get_set_variables_from_yaml(self.folder_path)

        if variables:
            self.add_line(f"\n✅ Found {len(variables)} unique variable(s):\n")
            for variable in variables:
                self.add_line(f"  - {variable}")
        else:
            self.add_line("ℹ️ No variables found in YAML frontmatter.")  # noqa: RUF001
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
