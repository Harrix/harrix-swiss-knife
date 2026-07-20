---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `python_project_checks.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PythonProjectChecksMixin`](#️-class-pythonprojectchecksmixin)
  - [⚙️ Method `check_single_python_project`](#️-method-check_single_python_project)

</details>

## 🏛️ Class `PythonProjectChecksMixin`

```python
class PythonProjectChecksMixin(ActionBase)
```

Mixin with ty/ruff/pytest and Harrix PY/MD checks for one project folder.

<details>
<summary>Code:</summary>

```python
class PythonProjectChecksMixin(ActionBase):

    _UV_CHECKS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("ty", "check"),
        ("ruff", "check"),
        ("pytest", ""),
    )

    def check_single_python_project(self, project_path: Path) -> list[str]:
        """Run full checks for one project. Return list of failed check labels."""
        project_name = project_path.name
        project_failures: list[str] = []

        for tool, args in self._UV_CHECKS:
            label = f"{tool} {args}".strip()
            self.add_line(f"🔵 [{project_name}] {label}")
            ok, output = self._run_uv_command(project_path, tool, args)
            if output:
                self.add_line(output)
            if ok:
                self.add_line(f"✅ {label} passed")
            else:
                self.add_line(f"❌ {label} failed")
                project_failures.append(label)

        self.add_line(f"🔵 [{project_name}] Harrix python check")
        if self._run_harrix_python_check(project_path):
            self.add_line("✅ Harrix python check passed")
        else:
            self.add_line("❌ Harrix python check failed")
            project_failures.append("Harrix python check")

        self.add_line(f"🔵 [{project_name}] Harrix markdown check")
        if self._run_harrix_markdown_check(project_path):
            self.add_line("✅ Harrix markdown check passed")
        else:
            self.add_line("❌ Harrix markdown check failed")
            project_failures.append("Harrix markdown check")

        return project_failures

    def _run_harrix_markdown_check(self, project_path: Path) -> bool:
        checker = OnCheckMdFolder()
        checker.folder_path = project_path
        checker.selected_rule_ids = set(h.md_check.MdChecker().all_rules)
        checker.include_g_md = True
        checker.check_md_folder_common()
        return not any("🔢 Count errors" in line for line in checker.result_lines)

    def _run_harrix_python_check(self, project_path: Path) -> bool:
        checker = OnHarrixCheckPythonFolder()
        checker.folder_path = project_path
        checker.harrix_check_python_folder_common()
        return not any("🔢 Count errors" in line for line in checker.result_lines)

    def _run_uv_command(self, project_path: Path, tool: str, args: str) -> tuple[bool, str]:
        pyproject = project_path / "pyproject.toml"
        if not pyproject.is_file():
            return False, f"❌ Missing pyproject.toml in {project_path}"

        venv_dir = project_path / ".venv"
        if not venv_dir.is_dir():
            return False, f"❌ Missing .venv in {project_path}"

        command = ["uv", "run", tool, *args.split()]
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=project_path,
                env=env,
                check=False,
            )
        except Exception as e:
            return False, f"Error executing command: {e!s}"

        output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
        output = "\n".join(filter(None, output_parts))
        return process.returncode == 0, output
```

</details>

### ⚙️ Method `check_single_python_project`

```python
def check_single_python_project(self, project_path: Path) -> list[str]
```

Run full checks for one project. Return list of failed check labels.

<details>
<summary>Code:</summary>

```python
def check_single_python_project(self, project_path: Path) -> list[str]:
        project_name = project_path.name
        project_failures: list[str] = []

        for tool, args in self._UV_CHECKS:
            label = f"{tool} {args}".strip()
            self.add_line(f"🔵 [{project_name}] {label}")
            ok, output = self._run_uv_command(project_path, tool, args)
            if output:
                self.add_line(output)
            if ok:
                self.add_line(f"✅ {label} passed")
            else:
                self.add_line(f"❌ {label} failed")
                project_failures.append(label)

        self.add_line(f"🔵 [{project_name}] Harrix python check")
        if self._run_harrix_python_check(project_path):
            self.add_line("✅ Harrix python check passed")
        else:
            self.add_line("❌ Harrix python check failed")
            project_failures.append("Harrix python check")

        self.add_line(f"🔵 [{project_name}] Harrix markdown check")
        if self._run_harrix_markdown_check(project_path):
            self.add_line("✅ Harrix markdown check passed")
        else:
            self.add_line("❌ Harrix markdown check failed")
            project_failures.append("Harrix markdown check")

        return project_failures
```

</details>
