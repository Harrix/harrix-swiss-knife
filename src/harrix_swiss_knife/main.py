import sys

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from harrix_swiss_knife import actions_os, resources_rc  # noqa
from harrix_swiss_knife import actions_images, actions_dev, actions_notes, actions_py, main_menu_base


class MainMenu(main_menu_base.MainMenuBase):
    def __init__(self):
        super().__init__()

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "💻")
        self.action_get_menu = QAction(
            self.get_icon("☰"), "Get the list of items from this menu", triggered=lambda: self.get_menu()
        )
        self.menu_dev.addAction(self.action_get_menu)
        self.add_item(self.menu_dev, actions_dev.on_open_config_json)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, actions_images.on_images_optimize)
        self.add_item(self.menu_images, actions_images.on_images_optimize_quality)
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog_replace)
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog)
        self.add_item(self.menu_images, actions_images.on_image_optimize_file)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, actions_images.on_image_clear_images)
        self.add_item(self.menu_images, actions_images.on_image_clear_optimized_images)
        self.add_item(self.menu_images, actions_images.on_image_open_images)
        self.add_item(self.menu_images, actions_images.on_image_open_optimized_images)

        # Notes
        self.menu_notes = self.new_menu("Notes", "📓")
        self.add_item(self.menu_notes, actions_notes.on_diary_new_dream)
        self.add_item(self.menu_notes, actions_notes.on_diary_new_with_images)
        self.add_item(self.menu_notes, actions_notes.on_diary_new)
        self.add_item(self.menu_notes, actions_notes.on_new_article)
        self.add_item(self.menu_notes, actions_notes.on_new_note_dialog_with_images)
        self.add_item(self.menu_notes, actions_notes.on_new_note_dialog)

        # Menu OS
        self.menu_os = self.new_menu("OS", "🪟")
        self.add_item(self.menu_os, actions_os.on_block_disks)
        self.add_item(self.menu_os, actions_os.on_open_camera_uploads)

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, actions_py.on_rye_new_project_dialog)
        self.add_item(self.menu_python, actions_py.on_rye_new_project)
        self.add_item(self.menu_python, actions_py.on_sort_isort_fmt_python_code_folder)
        self.add_item(self.menu_python, actions_py.on_sort_python_code_file)
        self.add_item(self.menu_python, actions_py.on_sort_python_code_folder)

        # MainMenu
        self.menu.addMenu(self.menu_dev)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_notes)
        self.menu.addMenu(self.menu_os)
        self.menu.addMenu(self.menu_python)

        self.menu.addSeparator()
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard)
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard_dialog)
        self.menu.addSeparator()
        self.action_exit = QAction(self.get_icon("×"), "Exit", triggered=lambda: QApplication.quit())

        self.menu.addAction(self.action_exit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)
    tray_icon.setContextMenu(main_menu.menu)
    tray_icon.show()
    sys.exit(app.exec())
