from pathlib import Path
import shutil
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

        from harrix_swiss_knife import funcs_temp

        result = funcs_temp.extract_functions_and_classes(filename)
        self.add_line(result)


class on_generate_markdown_documentation(action_base.ActionBase):
    icon: str = "🏗️"
    title: str = "Generate MD documentation"
    is_show_output = True

    def execute(self, *args, **kwargs):
        projects = ["C:/GitHub/harrix-pylib"]

        for folder_path in projects:
            output = generate_docs_for_project(folder_path, config["beginning_of_md"])
            self.add_line(output)


def generate_docs_for_project(folder: Path | str, beginning_of_md: str) -> str:
    result_lines = []
    folder = Path(folder)

    docs_folder = folder / "docs"
    docs_folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(folder / "README.md", docs_folder / 'index.md')
    result_lines.append(f"File README.md is copied.")

    list_funcs_all = ""

    for filename in (Path(folder) / "src").rglob(f"*.py"):
        if not (filename.is_file() and not filename.stem.startswith("__")):
            continue
        from harrix_swiss_knife import funcs_temp
        list_funcs = funcs_temp.extract_functions_and_classes(filename)
        docs = funcs_temp.generate_markdown_documentation(filename)
        filename_docs = docs_folder / f"{filename.stem}.md"
        Path(filename_docs).write_text(beginning_of_md + "\n" + docs, encoding="utf8")

        list_funcs_all += list_funcs + "\n\n"

        result_lines.append(f"File {filename.name} is processed.")

    if len(list_funcs_all.splitlines()) > 2:
        list_funcs_all = list_funcs_all[:-1]

    h.md.replace_section(folder / "README.md", list_funcs_all, "## List of functions")

    return "\n".join(result_lines)



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
    icon: str = "uv.svg"
    title: str = "New uv project in Projects"

    def execute(self, *args, **kwargs):
        path = config["path_py_projects"]
        max_project_number = h.file.find_max_folder_number(path, config["start_pattern_py_projects"])
        name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.add_line(h.py.create_uv_new_project(name_project, path, config["editor"], config["cli_commands"]))


class on_uv_new_project_dialog(action_base.ActionBase):
    icon: str = "uv.svg"
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
