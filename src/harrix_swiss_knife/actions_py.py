from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_py_sort_code(action_base.ActionBase):
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in one PY file"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Python File", config["path_github"], "Image Files (*.py);;All Files (*)"
        )
        if not filename:
            return

        try:
            h.dev.sort_py_code(filename)
            self.add_line(f"File {filename} is applied.")
        except Exception:
            self.add_line(f"❌ File {filename} is not applied.")


class on_py_sort_code_folder(action_base.ActionBase):
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in PY files"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".py", h.dev.sort_py_code))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_py_sort_isort_fmt_python_code_folder(action_base.ActionBase):
    icon: str = "🌟"
    title: str = "isort, ruff format, sort in PY files"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if not folder_path:
            return

        commands = f"cd {folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(folder_path, ".py", h.dev.sort_py_code))


class on_py_uv_new_project(action_base.ActionBase):
    icon: str = "uv.svg"
    title: str = "New uv project in Projects"

    def execute(self, *args, **kwargs):
        path = config["path_py_projects"]
        max_project_number = h.file.find_max_folder_number(path, config["start_pattern_py_projects"])
        name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.add_line(py_create_uv_new_project(name_project, path))


class on_py_uv_new_project_dialog(action_base.ActionBase):
    icon: str = "uv.svg"
    title: str = "New uv project in …"

    def execute(self, *args, **kwargs):
        project_name = self.get_text_input("Project name", "Enter the name of the project (English, without spaces):")
        if not project_name:
            return

        folder_path = self.get_existing_directory("Select a Project folder", config["path_py_projects"])
        if not folder_path:
            return

        self.add_line(py_create_uv_new_project(project_name.replace(" ", "-"), folder_path))


def py_create_uv_new_project(project_name: str, path: str | Path) -> str:
    """
    Creates a new project using uv, initializes it, and sets up necessary files.

    Args:

    - `name_project` (`str`): The name of the new project.
    - `path` (`str` | `Path`): The folder path where the project will be created.

    Returns:

    - `str`: A string containing the result of the operations performed.
    """
    commands = f"""
        cd {path}
        uv init --package {project_name}
        cd {project_name}
        uv sync
        uv add --dev isort
        uv add --dev ruff
        uv add --dev pytest
        New-Item -ItemType File -Path src/{project_name}/main.py -Force
        New-Item -ItemType File -Path src/{project_name}/__init__.py -Force
        Add-Content -Path pyproject.toml -Value "`n[tool.ruff]"
        Add-Content -Path pyproject.toml -Value "line-length = 120"
        {config["editor"]} {path}/{project_name}
        """

    res = h.dev.run_powershell_script(commands)

    readme_path = Path(path) / project_name / "README.md"
    try:
        with readme_path.open("a", encoding="utf-8") as file:
            file.write(f"# {project_name}\n\n{config['cli_commands']}")
        res += f"Content successfully added to {readme_path}"
    except FileNotFoundError:
        res += f"File not found: {readme_path}"
    except IOError as e:
        res += f"I/O error: {e}"
    except Exception as e:
        res += f"An unexpected error occurred: {e}"

    return res
