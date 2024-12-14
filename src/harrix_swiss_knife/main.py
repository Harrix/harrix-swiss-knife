import os
import re
import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc


def write_in_output_txt(func):
    output_lines = []

    def wrapper():
        output_lines.clear()
        func()
        file = Path("output.txt")
        file.write_text("\n".join(output_lines) + "\n", encoding="utf8")
        print("\n".join(output_lines))
        os.startfile(file)

    def add_line(line):
        output_lines.append(line)

    wrapper.add_line = add_line
    return wrapper


def find_max_project_number(base_path):
    pattern = re.compile(r"pythonProject(\d+)$")
    max_number = 0

    # Обход всех элементов в указанной директории
    for item in os.listdir(base_path):
        path = os.path.join(base_path, item)
        if os.path.isdir(path):
            match = pattern.match(item)
            if match:
                # Извлечение числа из имени папки
                number = int(match.group(1))
                # Определение максимального числа
                if number > max_number:
                    max_number = number

    return max_number


@write_in_output_txt
def on_rye_new_project_projects():
    f = on_rye_new_project_projects

    path = "C:/Users/sergi/OneDrive/Projects/Python"
    name_project = f"pythonProject{find_max_project_number(path) + 1}"

    commands = [
        f"cd {path}",
        f"rye init {name_project}",
        f"code-insiders {path}/{name_project}",
        f"cd {name_project}",
        f"rye sync",
        f'"" | Out-File -FilePath src/{name_project}/main.py -Encoding utf8',
        f"Set-Content -Path src/{name_project}/__init__.py -Value $null",
    ]

    command = ";".join(commands)
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

    f.add_line("end")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    # Создаем иконку для трея
    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)

    # Создаем меню
    menu = QMenu()

    python_menu = QMenu("Python", None)
    menu.addMenu(python_menu)
    action_rye_new_project_projects = QAction(
        "Создать Rye проект в Projects", triggered=on_rye_new_project_projects
    )
    python_menu.addAction(action_rye_new_project_projects)
    action_rye_new_project = QAction("Создать Rye проект в …")
    python_menu.addAction(action_rye_new_project)

    action2 = QAction("Пункт 2")
    exit_action = QAction("Выход", triggered=lambda: QApplication.quit())

    menu.addAction(action2)
    menu.addSeparator()
    menu.addAction(exit_action)

    # Устанавливаем меню в иконке трея
    tray_icon.setContextMenu(menu)

    # Показать иконку в трее
    tray_icon.show()
    sys.exit(app.exec())
