import sys

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import actions_images, actions_notes, actions_py, actions_windows
from harrix_swiss_knife import functions as f


class MainMenu:
    def __init__(self):
        self.menu = QMenu()

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, actions_py.on_rye_new_project)
        self.add_item(self.menu_python, actions_py.on_rye_new_project_dialog)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, actions_images.on_images_optimize)
        self.add_item(self.menu_images, actions_images.on_images_optimize_quality)
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog)
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog_replace)
        self.add_item(self.menu_images, actions_images.on_image_optimize_file)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, actions_images.on_image_clear_optimized_images)
        self.add_item(self.menu_images, actions_images.on_image_clear_images)
        self.add_item(self.menu_images, actions_images.on_image_open_optimized_images)
        self.add_item(self.menu_images, actions_images.on_image_open_images)

        # Notes
        self.menu_notes = self.new_menu("Notes", "📒")
        self.add_item(self.menu_notes, actions_notes.on_diary_new)
        self.add_item(self.menu_notes, actions_notes.on_diary_new_with_images)
        self.add_item(self.menu_notes, actions_notes.on_diary_new_dream)

        self.menu.addMenu(self.menu_python)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_notes)
        self.add_item(self.menu, actions_windows.on_open_camera_uploads)
        self.add_item(self.menu, actions_windows.on_block_disks)
        self.action_get_menu = QAction(
            self.get_icon("☰"), "Get the list of items from this menu", triggered=lambda: self.get_menu()
        )
        self.menu.addAction(self.action_get_menu)
        self.menu.addSeparator()
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard)
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard_dialog)
        self.menu.addSeparator()
        self.action_exit = QAction(self.get_icon("×"), "Exit", triggered=lambda: QApplication.quit())

        self.menu.addAction(self.action_exit)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)
    tray_icon.setContextMenu(main_menu.menu)
    tray_icon.show()
    sys.exit(app.exec())
