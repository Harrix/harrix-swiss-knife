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

    def check_single_python_project(self, project_path: Path, *, only_changed: bool = False) -> list[str]:
        """Run checks for one project. Return list of failed check labels."""
        project_name = project_path.name
        project_failures: list[str] = []
        scope = self._resolve_check_scope(project_path, only_changed=only_changed)
        self._log_check_scope(project_path, scope)

        for tool, args in self._UV_CHECKS:
            label = f"{tool} {args}".strip()
            decision = self._tool_run_decision(tool, scope)
            if decision == "skip":
                self.add_line(f"⚪ [{project_name}] {label}: skipped (`--only-changed`, nothing to check)")
                continue
            self.add_line(f"🔵 [{project_name}] {label}")
            extra_paths = self._tool_extra_paths(tool, scope) if decision == "scoped" else None
            ok, output = self._run_project_module(project_path, tool, args, extra_paths=extra_paths)
            if output:
                self.add_line(output)
            if ok:
                self.add_line(f"✅ {label} passed")
            else:
                self.add_line(f"❌ {label} failed")
                project_failures.append(label)

        if scope.only_changed and scope.py_files is not None and not scope.py_files and not scope.force_full_tools:
            self.add_line(f"⚪ [{project_name}] Harrix python check: skipped (`--only-changed`, no dirty .py)")
        else:
            self.add_line(f"🔵 [{project_name}] Harrix python check")
            py_files = None if (not scope.only_changed or scope.force_full_tools) else scope.py_files
            if self._run_harrix_python_check(project_path, py_files=py_files):
                self.add_line("✅ Harrix python check passed")
            else:
                self.add_line("❌ Harrix python check failed")
                project_failures.append("Harrix python check")

        if scope.only_changed and scope.md_files is not None and not scope.md_files:
            self.add_line(f"⚪ [{project_name}] Harrix markdown check: skipped (`--only-changed`, no dirty .md)")
        else:
            self.add_line(f"🔵 [{project_name}] Harrix markdown check")
            md_files = None if not scope.only_changed else scope.md_files
            if self._run_harrix_markdown_check(project_path, md_files=md_files):
                self.add_line("✅ Harrix markdown check passed")
            else:
                self.add_line("❌ Harrix markdown check failed")
                project_failures.append("Harrix markdown check")

        return project_failures

    @staticmethod
    def _filter_checkable_markdown_files(project_path: Path, md_files: list[Path]) -> list[Path]:
        """Drop Markdown paths that the full Harrix MD walker would ignore."""
        kept: list[Path] = []
        root = project_path.resolve()
        for path in md_files:
            try:
                relative = path.resolve().relative_to(root)
            except ValueError:
                continue
            if h.file.should_ignore_path(relative):
                continue
            kept.append(path)
        return kept

    @staticmethod
    def _is_under(path: Path, folder: Path) -> bool:
        try:
            path.resolve().relative_to(folder.resolve())
        except ValueError:
            return False
        return True

    def _log_check_scope(self, project_path: Path, scope: _CheckScope) -> None:
        if not scope.only_changed:
            return
        if scope.force_full_tools:
            self.add_line("🔵 `--only-changed`: tool/config dirty — full ty/ruff/Harrix PY")
        elif scope.py_files is not None:
            self.add_line(f"🔵 `--only-changed`: {len(scope.py_files)} Python file(s)")
            for path in scope.py_files:
                self.add_line(f"  • {path.relative_to(project_path).as_posix()}")
        if scope.force_full_pytest:
            self.add_line("🔵 `--only-changed`: pytest config/conftest dirty — full suite")
        elif scope.pytest_paths is not None:
            if scope.pytest_paths:
                self.add_line(f"🔵 `--only-changed`: {len(scope.pytest_paths)} pytest path(s)")
                for path in scope.pytest_paths:
                    self.add_line(f"  • {path.relative_to(project_path).as_posix()}")
            else:
                self.add_line("🔵 `--only-changed`: no matching pytest paths")
        if scope.md_files is not None and scope.md_files:
            self.add_line(f"🔵 `--only-changed`: {len(scope.md_files)} Markdown file(s)")
            for path in scope.md_files:
                self.add_line(f"  • {path.relative_to(project_path).as_posix()}")

    @staticmethod
    def _paths_for_tool_argv(project_path: Path, paths: list[Path]) -> list[str]:
        result: list[str] = []
        for path in paths:
            try:
                result.append(path.resolve().relative_to(project_path.resolve()).as_posix())
            except ValueError:
                result.append(str(path.resolve()))
        return result

    def _resolve_check_scope(self, project_path: Path, *, only_changed: bool) -> _CheckScope:
        if not only_changed:
            return _CheckScope(
                only_changed=False,
                force_full_tools=True,
                force_full_pytest=True,
                py_files=None,
                md_files=None,
                pytest_paths=None,
            )

        py_files = list_changed_python_files(project_path)
        md_files = list_changed_markdown_files(project_path)
        if py_files is None or md_files is None:
            self.add_line("⚪ `--only-changed`: not a Git repository; running full checks")
            return _CheckScope(
                only_changed=True,
                force_full_tools=True,
                force_full_pytest=True,
                py_files=None,
                md_files=None,
                pytest_paths=None,
            )

        root = git_repo_root(project_path)
        all_changed = list_git_changed_files(root) if root is not None else []
        under_project = [path for path in all_changed if self._is_under(path, project_path)]
        force_full_tools = any(
            path.name.casefold() in {n.casefold() for n in _FULL_TOOL_BASENAMES} for path in under_project
        )
        force_full_pytest = any(
            path.name.casefold() in {n.casefold() for n in _FULL_PYTEST_BASENAMES} for path in under_project
        )
        pytest_paths = None if force_full_pytest else self._select_pytest_paths(project_path, py_files)
        scoped_md = self._filter_checkable_markdown_files(project_path, md_files)

        return _CheckScope(
            only_changed=True,
            force_full_tools=force_full_tools,
            force_full_pytest=force_full_pytest,
            py_files=py_files,
            md_files=scoped_md,
            pytest_paths=pytest_paths,
        )

    def _run_harrix_markdown_check(
        self,
        project_path: Path,
        *,
        md_files: list[Path] | None = None,
    ) -> bool:
        checker = OnCheckMd()
        checker.folder_path = project_path
        checker.selected_rule_ids = set(h.md_check.MdChecker().all_rules)
        checker.include_g_md = True
        if md_files is not None:
            checker.selected_md_files = md_files
        checker.check_md_common()
        return getattr(checker, "last_error_count", 0) == 0

    def _run_harrix_python_check(
        self,
        project_path: Path,
        *,
        py_files: list[Path] | None = None,
    ) -> bool:
        checker = OnHarrixCheckPython()
        checker.folder_path = project_path
        if py_files is not None:
            checker.selected_python_files = py_files
        checker.harrix_check_python_common()
        return getattr(checker, "last_error_count", 0) == 0

    def _run_project_module(
        self,
        project_path: Path,
        tool: str,
        args: str,
        *,
        extra_paths: list[Path] | None = None,
    ) -> tuple[bool, str]:
        """Run `python -m <tool>` from the project's `.venv` without `uv run`.

        `uv run` on Windows often flashes a console. Pytest always gets
        `QT_QPA_PLATFORM=offscreen`, even if the parent process set `windows`.

        Args:

        - `project_path` (`Path`): Project root that contains `.venv`.
        - `tool` (`str`): Module name (`ty`, `ruff`, `pytest`).
        - `args` (`str`): Extra arguments, space-separated.
        - `extra_paths` (`list[Path] | None`): Optional file/dir paths appended to argv.

        Returns:

        - `tuple[bool, str]`: Success flag and combined command output.

        """
        pyproject = project_path / "pyproject.toml"
        if not pyproject.is_file():
            return False, f"❌ Missing pyproject.toml in {project_path}"

        python = venv_python(project_path)
        if not python.is_file():
            return False, f"❌ Missing {python}"

        module_args = [part for part in args.split() if part]
        if extra_paths:
            module_args.extend(self._paths_for_tool_argv(project_path, extra_paths))
        command = venv_module_argv(project_path, tool, *module_args)
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        if tool == "pytest":
            # Override a parent QT_QPA_PLATFORM=windows so tests cannot open real windows.
            env["QT_QPA_PLATFORM"] = QT_OFFSCREEN_PLATFORM
            env["HSK_MUTE_SOUNDS"] = "1"
        returncode, output = run_argv_output(command, cwd=project_path, env=env, timeout=_UV_CHECK_TIMEOUT)
        return returncode == 0, output

    @staticmethod
    def _select_pytest_paths(project_path: Path, py_files: list[Path]) -> list[Path]:
        """Map dirty Python files to pytest targets; empty means skip pytest."""
        tests_dir = project_path / "tests"
        selected: set[Path] = set()
        for path in py_files:
            try:
                rel = path.relative_to(project_path)
            except ValueError:
                continue
            if rel.parts and rel.parts[0].casefold() == "tests":
                selected.add(path)
                continue
            if path.suffix.casefold() != ".py" or path.stem == "__init__":
                continue
            stem = path.stem
            if stem.startswith("test_"):
                selected.add(path)
                continue
            if not tests_dir.is_dir():
                continue
            for match in tests_dir.rglob(f"test_{stem}.py"):
                if match.is_file():
                    selected.add(match.resolve())
        return sorted(selected, key=lambda item: str(item).casefold())

    @staticmethod
    def _tool_extra_paths(tool: str, scope: _CheckScope) -> list[Path]:
        if tool == "pytest":
            return list(scope.pytest_paths or [])
        return list(scope.py_files or [])

    @staticmethod
    def _tool_run_decision(tool: str, scope: _CheckScope) -> str:
        """Return `full`, `scoped`, or `skip` for a uv tool."""
        if not scope.only_changed:
            return "full"
        if tool == "pytest":
            if scope.force_full_pytest:
                return "full"
            if scope.pytest_paths is None:
                return "full"
            if not scope.pytest_paths:
                return "skip"
            return "scoped"
        if scope.force_full_tools:
            return "full"
        if scope.py_files is None:
            return "full"
        if not scope.py_files:
            return "skip"
        return "scoped"
```

</details>

### ⚙️ Method `check_single_python_project`

```python
def check_single_python_project(self, project_path: Path, *, only_changed: bool = False) -> list[str]
```

Run checks for one project. Return list of failed check labels.

<details>
<summary>Code:</summary>

```python
def check_single_python_project(self, project_path: Path, *, only_changed: bool = False) -> list[str]:
        project_name = project_path.name
        project_failures: list[str] = []
        scope = self._resolve_check_scope(project_path, only_changed=only_changed)
        self._log_check_scope(project_path, scope)

        for tool, args in self._UV_CHECKS:
            label = f"{tool} {args}".strip()
            decision = self._tool_run_decision(tool, scope)
            if decision == "skip":
                self.add_line(f"⚪ [{project_name}] {label}: skipped (`--only-changed`, nothing to check)")
                continue
            self.add_line(f"🔵 [{project_name}] {label}")
            extra_paths = self._tool_extra_paths(tool, scope) if decision == "scoped" else None
            ok, output = self._run_project_module(project_path, tool, args, extra_paths=extra_paths)
            if output:
                self.add_line(output)
            if ok:
                self.add_line(f"✅ {label} passed")
            else:
                self.add_line(f"❌ {label} failed")
                project_failures.append(label)

        if scope.only_changed and scope.py_files is not None and not scope.py_files and not scope.force_full_tools:
            self.add_line(f"⚪ [{project_name}] Harrix python check: skipped (`--only-changed`, no dirty .py)")
        else:
            self.add_line(f"🔵 [{project_name}] Harrix python check")
            py_files = None if (not scope.only_changed or scope.force_full_tools) else scope.py_files
            if self._run_harrix_python_check(project_path, py_files=py_files):
                self.add_line("✅ Harrix python check passed")
            else:
                self.add_line("❌ Harrix python check failed")
                project_failures.append("Harrix python check")

        if scope.only_changed and scope.md_files is not None and not scope.md_files:
            self.add_line(f"⚪ [{project_name}] Harrix markdown check: skipped (`--only-changed`, no dirty .md)")
        else:
            self.add_line(f"🔵 [{project_name}] Harrix markdown check")
            md_files = None if not scope.only_changed else scope.md_files
            if self._run_harrix_markdown_check(project_path, md_files=md_files):
                self.add_line("✅ Harrix markdown check passed")
            else:
                self.add_line("❌ Harrix markdown check failed")
                project_failures.append("Harrix markdown check")

        return project_failures
```

</details>
