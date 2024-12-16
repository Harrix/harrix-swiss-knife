import os
import re
import subprocess
from PySide6.QtWidgets import QInputDialog, QFileDialog

from harrix_swiss_knife import functions


def find_max_project_number(base_path, start_pattern):
    pattern = re.compile(start_pattern + r"(\d+)$")
    max_number = 0
    for item in os.listdir(base_path):
        path = os.path.join(base_path, item)
        if os.path.isdir(path):
            match = pattern.match(item)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    return max_number


def create_rye_new_project(name_project, path):
    commands = f"""
        cd {path}
        rye init {name_project}
        code-insiders {path}/{name_project}
        cd {name_project}
        rye sync
        "" | Out-File -FilePath src/{name_project}/main.py -Encoding utf8
        Set-Content -Path src/{name_project}/__init__.py -Value $null
        """
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    process = subprocess.run(
        [
            "powershell",
            "-Command",
            f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}",
        ],
        capture_output=True,
        text=True,
    )
    result_output = []
    output, error = process.stdout, process.stderr
    if output:
        result_output.append(output)
    if error:
        result_output.append(error)
    return "\n".join(result_output)


class on_rye_new_project_projects:
    title = "Create Rye project in Projects"
    title_with_dialog = "Create Rye project in  …"
    path_default = "C:/Users/sergi/OneDrive/Projects/Python"
    start_pattern = "python_project_"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_rye_new_project_projects.__call__

        if not kwargs["is_need_dialog"]:
            start_pattern = on_rye_new_project_projects.start_pattern
            self.path = on_rye_new_project_projects.path_default
            self.name_project = f"python_project_{f"{(find_max_project_number(self.path, start_pattern) + 1):02}"}"
        else:
            title = "Project name"
            label = "Enter the name of the project (English, without spaces):"
            project_name, ok = QInputDialog.getText(None, title, label)

            if ok and project_name:
                self.name_project = project_name
            else:
                f.add_line("The name of the project was not entered.")
                return

            title = "Project directory"
            folder_path = QFileDialog.getExistingDirectory(
                None, title, on_rye_new_project_projects.path_default
            )

            if folder_path:
                self.path = folder_path
            else:
                f.add_line("The directory was not selected.")
                return

        result_output = create_rye_new_project(self.name_project, self.path)
        f.add_line(result_output)
