import os
import re
import subprocess

from harrix_swiss_knife import functions


def find_max_project_number(base_path):
    pattern = re.compile(r"python_project_(\d+)$")
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


class on_rye_new_project_projects:
    title = "Создать Rye проект в Projects"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_rye_new_project_projects.__call__

        path = "C:/Users/sergi/OneDrive/Projects/Python"
        name_project = f"python_project_{f"{(find_max_project_number(path) + 1):02}"}"

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
        output, error = process.stdout, process.stderr
        if output:
            f.add_line(output)
        if error:
            f.add_line(error)
