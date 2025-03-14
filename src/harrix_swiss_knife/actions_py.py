from pathlib import Path
import re
import time
from PySide6.QtWidgets import QMessageBox

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_extract_functions_and_classes(action_base.ActionBase):
    icon: str = "⬇️"
    title: str = "Extracts list of funcs to a MD list from one PY file"
    is_show_output = True

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Python File", config["path_github"], "Python Files (*.py);;All Files (*)"
        )
        if not filename:
            return

        result = h.py.extract_functions_and_classes(filename)
        self.add_line(result)


class on_generate_md_docs(action_base.ActionBase):
    icon: str = "🏗️"
    title: str = "Generate MD documentation in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if not folder_path:
            return

        folder_path = Path(folder_path)
        domain = f"https://github.com/{config['github_user']}/{folder_path.parts[-1]}"

        output = h.py.generate_md_docs(folder_path, config["beginning_of_md_docs"], domain)
        self.add_line(output)

        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)


class on_harrix_pylib_01_prepare(action_base.ActionBase):
    icon: str = "👩🏻‍🍳"
    title: str = "01 Prepare harrix-pylib"

    def execute(self, *args, **kwargs):
        folder_path = Path(config["path_github"]) / "harrix-pylib"

        commands = f"cd {folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))

        domain = f"https://github.com/{config['github_user']}/{folder_path.parts[-1]}"
        output = h.py.generate_md_docs(folder_path, config["beginning_of_md_docs"], domain)
        self.add_line(output)
        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)

        output = h.dev.run_powershell_script(f"github {folder_path} ")
        self.add_line(output)


class on_harrix_pylib_02_publish(action_base.ActionBase):
    icon: str = "👷‍♂️"
    title: str = "02 Publish and update harrix-pylib"
    is_show_output = True

    def execute(self, *args, **kwargs):
        token = self.get_text_input("PyPi token", "Enter the token of the project in PyPi:")
        if not token:
            return

        path_library = Path(config["path_github"]) / "harrix-pylib"
        projects = [Path(config["path_github"]) / "harrix-swiss-knife"]

        # Increase version of library
        path_toml = path_library / "pyproject.toml"
        content = path_toml.read_text(encoding="utf8")
        pattern = r'version = "(\d+)\.(\d+)"'
        find = re.search(pattern, content, re.DOTALL)
        new_version = f"{find.group(1)}.{int(find.group(2)) + 1}"
        new_content = re.sub(pattern, lambda m: f'version = "{m.group(1)}.{int(m.group(2)) + 1}"', content)
        path_toml.write_text(new_content)
        self.add_line(f"New version {new_version}")

        commands = f"""
            cd {path_library}
            uv sync --upgrade
            Remove-Item -Path "{path_library}/dist/*" -Recurse -Force
            uv build
            uv publish --token {token}
            git add pyproject.toml
            git add uv.lock
            git commit -m "🚀 Build version {new_version}" """
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)

        time_waiting_seconds = 20
        QMessageBox.information(None, "Copy", f"Wait {time_waiting_seconds} seconds for the package to be published.")
        time.sleep(time_waiting_seconds)

        for project in projects:
            project = Path(project)

            commands = f"""
                cd {project}
                uv sync --upgrade
                uv sync --upgrade """
            output = h.dev.run_powershell_script(commands)
            self.add_line(output)

            # Increase version of library
            path_toml = project / "pyproject.toml"
            content = path_toml.read_text(encoding="utf8")
            pattern = path_library.parts[-1] + r'>=(\d+)\.(\d+)'
            new_content = re.sub(pattern, lambda m: f'{path_library.parts[-1]}>={new_version}', content)
            path_toml.write_text(new_content)

            commands = f"""
                cd {project}
                uv sync --upgrade
                git add pyproject.toml
                git add uv.lock
                git commit -m "⬆️ Update {path_library.parts[-1]}" """
            output = h.dev.run_powershell_script(commands)
            self.add_line(output)


class on_sort_code(action_base.ActionBase):
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in one PY file"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Python File", config["path_github"], "Python Files (*.py);;All Files (*)"
        )
        if not filename:
            return

        try:
            h.py.sort_py_code(filename)
            self.add_line(f"File {filename} is applied.")
        except Exception:
            self.add_line(f"❌ File {filename} is not applied.")


class on_sort_code_folder(action_base.ActionBase):
    icon: str = "📶"
    title: str = "Sort classes, methods, functions in PY files"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_sort_isort_fmt_python_code_folder(action_base.ActionBase):
    icon: str = "🌟"
    title: str = "isort, ruff format, sort in PY files"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if not folder_path:
            return

        commands = f"cd {folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))


class on_uv_new_project(action_base.ActionBase):
    icon: str = "🐍"
    title: str = "New uv project in Projects"

    def execute(self, *args, **kwargs):
        path = config["path_py_projects"]
        max_project_number = h.file.find_max_folder_number(path, config["start_pattern_py_projects"])
        name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.add_line(h.py.create_uv_new_project(name_project, path, config["editor"], config["cli_commands"]))


class on_uv_new_project_dialog(action_base.ActionBase):
    icon: str = "🐍"
    title: str = "New uv project in …"

    def execute(self, *args, **kwargs):
        project_name = self.get_text_input("Project name", "Enter the name of the project (English, without spaces):")
        if not project_name:
            return

        folder_path = self.get_existing_directory("Select a Project folder", config["path_py_projects"])
        if not folder_path:
            return

        self.add_line(
            h.py.create_uv_new_project(
                project_name.replace(" ", "-"), folder_path, config["editor"], config["cli_commands"]
            )
        )
