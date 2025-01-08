from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.dev_load_config("config/config.json")


class on_py_uv_new_project:
    icon: str = "uv.svg"
    title: str = "New uv project in Projects"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        self.path: str = config["path_py_projects"]
        max_project_number = functions.file_find_max_folder_number(self.path, config["start_pattern_py_projects"])
        self.name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.__call__.add_line(py_create_uv_new_project(self.name_project, self.path))


class on_py_uv_new_project_dialog:
    icon: str = "uv.svg"
    title: str = "New uv project in …"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project name"
        label: str = "Enter the name of the project (English, without spaces):"
        project_name, ok = QInputDialog.getText(None, title, label)

        if ok and project_name:
            self.name_project: str = project_name
        else:
            self.__call__.add_line("❌ The name of the project was not entered.")
            return

        self.name_project = self.name_project.replace(" ", "-")

        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_py_projects"])

        if folder_path:
            self.path: str = folder_path
        else:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        self.__call__.add_line(py_create_uv_new_project(self.name_project, self.path))


class on_py_sort_code:
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in one PY file"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select an Python File",
            config["path_github"],
            "Image Files (*.py);;All Files (*)",
        )

        if not file_path:
            self.__call__.add_line("❌ The file was not selected.")
            return

        try:
            functions.dev_sort_py_code(file_path)
            self.__call__.add_line(f"File {file_path} is applied.")
        except Exception:
            self.__call__.add_line(f"❌ File {file_path} is not applied.")


class on_py_sort_code_folder:
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in PY files"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if folder_path:
            self.path: str = folder_path
        else:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        self.__call__.add_line(functions.file_apply_func(folder_path, ".py", functions.dev_sort_py_code))


class on_py_sort_isort_fmt_python_code_folder:
    icon: str = "🌟"
    title: str = "isort, ruff format, sort in PY files"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not (folder_path):
            self.__call__.add_line("❌ The folder was not selected.")
            return

        commands = f"""
            cd {folder_path}
            isort .
            ruff format
            """

        self.__call__.add_line(functions.dev_run_powershell_script(commands))
        self.__call__.add_line(functions.file_apply_func(folder_path, ".py", functions.dev_sort_py_code))


def py_create_uv_new_project(name_project: str, path: str | Path) -> str:
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
        uv init --package {name_project}
        cd {name_project}
        uv sync
        uv add --dev isort
        uv add --dev ruff
        uv add --dev pytest
        New-Item -ItemType File -Path src/{name_project}/main.py -Force
        New-Item -ItemType File -Path src/{name_project}/__init__.py -Force
        Add-Content -Path pyproject.toml -Value "`n[tool.ruff]"
        Add-Content -Path pyproject.toml -Value "line-length = 120"
        {config["editor"]} {path}/{name_project}
        """

    res = functions.dev_run_powershell_script(commands)

    readme_path = Path(path) / name_project / "README.md"
    try:
        with readme_path.open("a", encoding="utf-8") as file:
            file.write(f"# {name_project}\n\n{config['cli_commands']}")
        res += f"Content successfully added to {readme_path}"
    except FileNotFoundError:
        res += f"File not found: {readme_path}"
    except IOError as e:
        res += f"I/O error: {e}"
    except Exception as e:
        res += f"An unexpected error occurred: {e}"

    return res
