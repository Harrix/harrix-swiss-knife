from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu

from harrix_swiss_knife import functions as f


class MainMenuBase:
    def __init__(self):
        self.menu = QMenu()

    def add_item(self, menu, class_action, icon=""):
        if icon:
            action = QAction(self.get_icon(icon), class_action().title, triggered=class_action())
        elif class_action().icon:
            action = QAction(self.get_icon(class_action().icon), class_action().title, triggered=class_action())
        else:
            action = QAction(class_action().title, triggered=class_action())
        setattr(self, f"action_{class_action.__name__}", action)
        menu.addAction(action)

    def get_icon(self, icon):
        return QIcon(f":/assets/{icon}") if ".svg" in icon else f.pyside_create_emoji_icon(icon)

    @f.write_in_output_txt(is_show_output=True)
    def get_menu(self):
        filename = f.get_project_root() / "README.md"
        list_of_menu = "\n".join(f.pyside_generate_markdown_from_qmenu(self.menu))

        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        start_index = None
        end_index = None
        for i, line in enumerate(lines):
            if line.startswith("## List of commands"):
                start_index = i
            elif start_index is not None and line.startswith("##") and i != start_index:
                end_index = i
                break

        if start_index is not None and end_index is not None:
            new_lines = "".join(lines[: start_index + 1]) + "\n" + list_of_menu + "\n\n" + "".join(lines[end_index:])
            with open(filename, "w", encoding="utf-8") as file:
                file.writelines(new_lines)

        self.get_menu.add_line(list_of_menu)

    def new_menu(self, title, icon):
        menu = QMenu(title, None)
        menu.setIcon(self.get_icon(icon))
        return menu