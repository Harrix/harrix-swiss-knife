---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `python_project_checks.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PythonProjectChecksMixin`](#%EF%B8%8F-class-pythonprojectchecksmixin)
  - [⚙️ Method `check_single_python_project`](#%EF%B8%8F-method-check_single_python_project)

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
            ok, output = self._run_project_module(project_path, tool, args)
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
        checker = OnCheckMd()
        checker.folder_path = project_path
        checker.selected_rule_ids = set(h.md_check.MdChecker().all_rules)
        checker.include_g_md = True
        checker.check_md_common()
        return getattr(checker, "last_error_count", 0) == 0

    def _run_harrix_python_check(self, project_path: Path) -> bool:
        checker = OnHarrixCheckPython()
        checker.folder_path = project_path
        checker.harrix_check_python_common()
        return getattr(checker, "last_error_count", 0) == 0

    def _run_project_module(self, project_path: Path, tool: str, args: str) -> tuple[bool, str]:
        """Run `python -m <tool>` from the project's `.venv` without `uv run`.

        `uv run` on Windows often flashes a console. Qt tests also map real
        Windows unless `QT_QPA_PLATFORM=offscreen`.

        Args:

        - `project_path` (`Path`): Project root that contains `.venv`.
        - `tool` (`str`): Module name (`ty`, `ruff`, `pytest`).
        - `args` (`str`): Extra arguments, space-separated.

        Returns:

        - `tuple[bool, str]`: Success flag and combined command output.

        """
        pyproject = project_path / "pyproject.toml"
        if not pyproject.is_file():
            return False, f"❌ Missing pyproject.toml in {project_path}"

        python = venv_python(project_path)
        if not python.is_file():
            return False, f"❌ Missing {python}"

        command = venv_module_argv(project_path, tool, *args.split())
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        if tool == "pytest":
            env.setdefault("QT_QPA_PLATFORM", QT_OFFSCREEN_PLATFORM)
        returncode, output = run_argv_output(command, cwd=project_path, env=env, timeout=_UV_CHECK_TIMEOUT)
        return returncode == 0, output
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
            ok, output = self._run_project_module(project_path, tool, args)
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
