import os
import re
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.load_config('config.json')
path_py_projects = config['path_py_projects']
path_github = config['path_github']
start_pattern_py_projects = config['start_pattern_py_projects']
cli_commands = config['cli_commands']


class on_rye_new_project:
    icon: str = "rye.svg"
    title: str = "New Rye project in Projects"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        self.path: str = path_py_projects
        max_project_number = find_max_project_number(self.path, start_pattern_py_projects)
        self.name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        result_output = create_rye_new_project(self.name_project, self.path)
        self.__call__.add_line(result_output)


class on_rye_new_project_dialog:
    icon: str = "rye.svg"
    title: str = "New Rye project in  …"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project name"
        label: str = "Enter the name of the project (English, without spaces):"
        project_name, ok = QInputDialog.getText(None, title, label)

        if ok and project_name:
            self.name_project: str = project_name
        else:
            self.__call__.add_line("❌ The name of the project was not entered.")
            return

        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_py_projects)

        if folder_path:
            self.path: str = folder_path
        else:
            self.__call__.add_line("❌ The directory was not selected.")
            return

        result_output = create_rye_new_project(self.name_project, self.path)
        self.__call__.add_line(result_output)


class on_sort_python_code_file:
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in one PY file"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select an Python File",
            path_github,
            "Image Files (*.py);;All Files (*)",
        )

        if not file_path:
            self.__call__.add_line("❌ The file was not selected.")
            return

        try:
            functions.sort_py_code(file_path)
            self.__call__.add_line(f"File {file_path} is applied.")
        except Exception:
            self.__call__.add_line(f"❌ File {file_path} is not applied.")


class on_sort_python_code_folder:
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in PY files"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_github)

        if folder_path:
            self.path: str = folder_path
        else:
            self.__call__.add_line("❌ The directory was not selected.")
            return

        result_output = functions.apply_func_to_files(folder_path, ".py", functions.sort_py_code)

        self.__call__.add_line(result_output)


def create_rye_new_project(name_project: str, path: str) -> str:
    """
    Creates a new Rye project with the specified name and path, initializes it, and sets up necessary files.

    Args:

    - `name_project` (`str`): The name of the new Rye project.
    - `path` (`str`): The directory path where the project will be created.

    Returns:

    - `str`: The output from executing the PowerShell script.
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
        code-insiders {path}/{name_project}
        """

    res = functions.run_powershell_script(commands)

    readme_path = Path(path) / name_project / "README.md"
    try:
        with readme_path.open("a", encoding="utf-8") as file:
            file.write(cli_commands)
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
    Finds the maximum project number within directories matching a specified pattern.

    Args:

    - `base_path` (`str`): The base directory path to search for project folders.
    - `start_pattern` (`str`): The starting pattern to identify relevant directories, followed by a number.

    Returns:

    - `int`: The highest project number found that matches the pattern. Returns `0` if no matching directories are found.
    """
    pattern = re.compile(start_pattern + r"(\d+)$")
    max_number: int = 0
    for item in os.listdir(base_path):
        path = os.path.join(base_path, item)
        if os.path.isdir(path):
            match = pattern.match(item)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    return max_number
