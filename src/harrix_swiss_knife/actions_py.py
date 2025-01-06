import re
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.dev_load_config("config.json")


class on_rye_new_project:
    icon: str = "rye.svg"
    title: str = "New Rye project in Projects"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        self.path: str = config["path_py_projects"]
        max_project_number = find_max_project_number(self.path, config["start_pattern_py_projects"])
        self.name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.__call__.add_line(create_rye_new_project(self.name_project, self.path))


class on_rye_new_project_dialog:
    icon: str = "rye.svg"
    title: str = "New Rye project in …"

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

        self.__call__.add_line(create_rye_new_project(self.name_project, self.path))


class on_sort_isort_fmt_python_code_folder:
    icon: str = "🌟"
    title: str = "isort, rye fmt, sort in PY files"

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
            rye fmt
            """

        self.__call__.add_line(functions.dev_run_powershell_script(commands))
        self.__call__.add_line(functions.file_apply_func(folder_path, ".py", functions.dev_sort_py_code))


class on_sort_python_code_file:
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


class on_sort_python_code_folder:
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


def create_rye_new_project(name_project: str, path: str | Path) -> str:
    """
    Creates a new project using Rye, initializes it, and sets up necessary files.

    Args:

    - `name_project` (`str`): The name of the new project.
    - `path` (`str` | `Path`): The folder path where the project will be created.

    Returns:

    - `str`: A string containing the result of the operations performed.
    """
    commands = f"""
        cd {path}
        rye init {name_project}
        cd {name_project}
        rye sync
        rye add --dev isort
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
            file.write(config["cli_commands"])
        res += f"Content successfully added to {readme_path}"
    except FileNotFoundError:
        res += f"File not found: {readme_path}"
    except IOError as e:
        res += f"I/O error: {e}"
    except Exception as e:
        res += f"An unexpected error occurred: {e}"

    return res


def find_max_project_number(base_path: str, start_pattern: str) -> int:
    """
    Finds the highest project number in a given folder based on a pattern.

    Args:

    - `base_path` (`str`): The base folder path to search for projects.
    - `start_pattern` (`str`): A regex pattern for matching project names.

    Returns:

    - `int`: The maximum project number found, or 0 if no matches are found.
    """
    pattern = re.compile(start_pattern + r"(\d+)$")
    max_number: int = 0
    base_path = Path(base_path)

    for item in base_path.iterdir():
        if item.is_dir():
            match = pattern.match(item.name)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    return max_number
