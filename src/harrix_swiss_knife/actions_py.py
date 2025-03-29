import re
import time
from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QMessageBox

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_extract_functions_and_classes(action_base.ActionBase):
    icon = "⬇️"
    title = "Extracts list of funcs to a MD list from one PY file"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Python File", config["path_github"], "Python Files (*.py);;All Files (*)"
        )
        if not filename:
            return

        result = h.py.extract_functions_and_classes(filename)
        self.add_line(result)
        self.show_result()


class on_generate_md_docs(action_base.ActionBase):
    icon = "🏗️"
    title = "Generate MD documentation in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not folder_path:
            return

        folder_path = Path(folder_path)
        domain = f"https://github.com/{config['github_user']}/{folder_path.parts[-1]}"

        result = h.py.generate_md_docs(folder_path, config["beginning_of_md_docs"], domain)
        self.add_line(result)

        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)
        self.show_result()


class on_harrix_pylib_01_prepare(action_base.ActionBase):
    icon = "👩🏻‍🍳"
    title = "01 Prepare harrix-pylib"

    def execute(self, *args, **kwargs):
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        folder_path = Path(config["path_github"]) / "harrix-pylib"

        # Beautify the code
        commands = f"cd {folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))

        # Generate Markdown documentation
        domain = f"https://github.com/{config['github_user']}/{folder_path.parts[-1]}"
        result = h.py.generate_md_docs(folder_path, config["beginning_of_md_docs"], domain)
        self.add_line(result)

        # Format Markdown files using Prettier
        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

        # Open GitHub
        result = h.dev.run_powershell_script(f"github {folder_path} ")

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class on_harrix_pylib_02_publish(action_base.ActionBase):
    icon = "👷‍♂️"
    title = "02 Publish and update harrix-pylib"

    def execute(self, *args, **kwargs):
        self.token = self.get_text_input("PyPi token", "Enter the token of the project in PyPi:")
        if not self.token:
            return

        self.start_thread(self.in_thread_01, self.thread_after_01, "Increase version, build and publish")

    def in_thread_01(self):
        self.path_library = Path(config["path_github"]) / "harrix-pylib"
        self.projects = [Path(config["path_github"]) / "harrix-swiss-knife"]

        # Increase version of library
        path_toml = self.path_library / "pyproject.toml"
        content = path_toml.read_text(encoding="utf8")
        pattern = r'version = "(\d+)\.(\d+)"'
        find = re.search(pattern, content, re.DOTALL)
        self.new_version = f"{find.group(1)}.{int(find.group(2)) + 1}"
        new_content = re.sub(pattern, lambda m: f'version = "{m.group(1)}.{int(m.group(2)) + 1}"', content)
        path_toml.write_text(new_content)
        self.add_line(f"🆕 New version {self.new_version}")

        # Build and publish
        commands = f"""
            cd {self.path_library}
            uv sync --upgrade
            Remove-Item -Path "{self.path_library}/dist/*" -Recurse -Force
            uv build
            uv publish --token {self.token}
            git add pyproject.toml
            git add uv.lock
            git commit -m "🚀 Build version {self.new_version}" """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def in_thread_02(self):
        time.sleep(self.time_waiting_seconds)

    def in_thread_03(self):
        # Update harrix-pylib in projects
        for project in self.projects:
            project = Path(project)

            commands = f"""
                cd {project}
                uv sync --upgrade
                uv sync --upgrade """
            result = h.dev.run_powershell_script(commands)
            self.add_line(result)

            # Increase version of harrix-pylib in project
            path_toml = project / "pyproject.toml"
            content = path_toml.read_text(encoding="utf8")
            pattern = self.path_library.parts[-1] + r">=(\d+)\.(\d+)"
            new_content = re.sub(pattern, lambda m: f"{self.path_library.parts[-1]}>={self.new_version}", content)
            path_toml.write_text(new_content)

            commands = f"""
                cd {project}
                uv sync --upgrade
                git add pyproject.toml
                git add uv.lock
                git commit -m "⬆️ Update {self.path_library.parts[-1]}" """
            result = h.dev.run_powershell_script(commands)
            self.add_line(result)

    def thread_after_01(self, result):
        self.time_waiting_seconds = 20
        message = f"Wait {self.time_waiting_seconds} seconds for the package to be published."
        self.start_thread(self.in_thread_02, self.thread_after_02, message)

    def thread_after_02(self, result):
        self.start_thread(self.in_thread_03, self.thread_after_03, "Update harrix-pylib in projects")

    def thread_after_03(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class on_sort_code(action_base.ActionBase):
    icon = "📶"
    title = "Sort classes, methods, functions in one PY file"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Python File", config["path_github"], "Python Files (*.py);;All Files (*)"
        )
        if not filename:
            return

        try:
            h.py.sort_py_code(filename)
            result = f"✅ File {filename} is applied."
        except Exception:
            result = f"❌ File {filename} is not applied."

        self.add_line(result)
        self.show_toast(result)


class on_sort_code_folder(action_base.ActionBase):
    icon = "📶"
    title = "Sort classes, methods, functions in PY files"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".py", h.py.sort_py_code))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class on_sort_isort_fmt_python_code_folder(action_base.ActionBase):
    icon = "🌟"
    title = "isort, ruff format, sort in PY files"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        commands = f"cd {self.folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(self.folder_path, ".py", h.py.sort_py_code))

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class on_uv_new_project(action_base.ActionBase):
    icon = "🐍"
    title = "New uv project in Projects"

    def execute(self, *args, **kwargs):
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        path = config["path_py_projects"]
        max_project_number = h.file.find_max_folder_number(path, config["start_pattern_py_projects"])
        name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.add_line(h.py.create_uv_new_project(name_project, path, config["editor"], config["cli_commands"]))

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class on_uv_new_project_dialog(action_base.ActionBase):
    icon = "🐍"
    title = "New uv project in …"

    def execute(self, *args, **kwargs):
        self.project_name = self.get_text_input("Project name", "Enter the name of the project (English, without spaces):")
        if not self.project_name:
            return

        self.folder_path = self.get_existing_directory("Select Project folder", config["path_py_projects"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        self.add_line(
            h.py.create_uv_new_project(
                self.project_name.replace(" ", "-"), self.folder_path, config["editor"], config["cli_commands"]
            )
        )

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()
