import os
import re
from PySide6.QtWidgets import QInputDialog, QFileDialog
from harrix_swiss_knife import functions

path_default: str = "C:/Users/sergi/OneDrive/Projects/Python"
start_pattern: str = "python_project_"


class on_rye_new_project:
    title: str = "New Rye project in Projects"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        self.path: str = path_default
        self.name_project: str = f"python_project_{f'{(find_max_project_number(self.path, start_pattern) + 1):02}'}"

        result_output = create_rye_new_project(self.name_project, self.path)
        self.__call__.add_line(result_output)


class on_rye_new_project_dialog:
    title: str = "New Rye project in  …"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project name"
        label: str = "Enter the name of the project (English, without spaces):"
        project_name, ok = QInputDialog.getText(None, title, label)

        if ok and project_name:
            self.name_project: str = project_name
        else:
            self.__call__.add_line("The name of the project was not entered.")
            return

        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_default)

        if folder_path:
            self.path: str = folder_path
        else:
            self.__call__.add_line("The directory was not selected.")
            return

        result_output = create_rye_new_project(self.name_project, self.path)
        self.__call__.add_line(result_output)


def find_max_project_number(base_path: str, start_pattern: str) -> int:
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


def create_rye_new_project(name_project: str, path: str) -> str:
    commands: str = f"""
        cd {path}
        rye init {name_project}
        code-insiders {path}/{name_project}
        cd {name_project}
        rye sync
        "" | Out-File -FilePath src/{name_project}/main.py -Encoding utf8
        Set-Content -Path src/{name_project}/__init__.py -Value $null
        """

    return functions.run_powershell_script(commands)
