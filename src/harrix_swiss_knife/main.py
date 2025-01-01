import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import actions_windows, actions_images, actions_notes, actions_py

from harrix_swiss_knife import functions as f


class MainMenu:
    def __init__(self):
        self.menu = QMenu()

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, actions_py.on_rye_new_project, "rye.svg")
        self.add_item(self.menu_python, actions_py.on_rye_new_project_dialog, "rye.svg")

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, actions_images.on_images_optimize, "🚀")
        self.add_item(self.menu_images, actions_images.on_images_optimize_quality, "🔝")
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog, "⬆️")
        self.add_item(self.menu_images, actions_images.on_image_optimize_dialog_replace, "⬆️")
        self.add_item(self.menu_images, actions_images.on_image_optimize_file, "🖼️")
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, actions_images.on_image_clear_optimized_images, "🧹")
        self.add_item(self.menu_images, actions_images.on_image_clear_images, "🧹")
        self.add_item(self.menu_images, actions_images.on_image_open_optimized_images, "📂")
        self.add_item(self.menu_images, actions_images.on_image_open_images, "📂")

        # Notes
        self.menu_notes = self.new_menu("Notes", "📒")
        self.add_item(self.menu_notes, actions_notes.on_diary_new, "📓")
        self.add_item(self.menu_notes, actions_notes.on_diary_new_with_images, "🖼️")
        self.add_item(self.menu_notes, actions_notes.on_diary_new_dream, "💤")

        self.menu.addMenu(self.menu_python)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_notes)
        self.add_item(self.menu, actions_windows.on_open_camera_uploads, "📸")
        self.add_item(self.menu, actions_windows.on_block_disks, "🔒")
        self.menu.addSeparator()
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard, "🚀")
        self.add_item(self.menu, actions_images.on_image_optimize_clipboard_dialog, "🚀")
        self.menu.addSeparator()
        self.action_exit = QAction(self.get_icon("×"), "Exit", triggered=lambda: QApplication.quit())
        self.menu.addAction(self.action_exit)

    def add_item(self, menu, class_action, icon=""):
        if icon:
            action = QAction(self.get_icon(icon), class_action().title, triggered=class_action())
        else:
            action = QAction(class_action().title, triggered=class_action())
        setattr(self, f"action_{class_action.__name__}", action)
        menu.addAction(action)

    def get_icon(self, icon):
        return QIcon(f":/assets/{icon}") if ".svg" in icon else f.create_emoji_icon(icon)

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
