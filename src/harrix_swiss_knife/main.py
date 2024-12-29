import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import (
    actions_python,
    actions_windows,
    actions_images,
    actions_notes,
)

from harrix_swiss_knife import functions as f


class MainMenu:
    def __init__(self):
        self.menu = QMenu()

        # Menu Python
        self.menu_python = QMenu("Python", None)
        self.add_item_menu(self.menu_python, actions_python.on_rye_new_project, "rye.svg")
        self.add_item_menu(self.menu_python, actions_python.on_rye_new_project_dialog, "rye.svg")

        # Menu Images
        self.menu_images = QMenu("Images", None)
        self.add_item_menu(self.menu_images, actions_images.on_images_optimize)
        self.add_item_menu(self.menu_images, actions_images.on_images_optimize_quality)
        self.add_item_menu(self.menu_images, actions_images.on_image_optimize_dialog)
        self.add_item_menu(self.menu_images, actions_images.on_image_optimize_dialog_replace)
        self.add_item_menu(self.menu_images, actions_images.on_image_optimize_file)

        # Notes
        self.menu_notes = QMenu("Notes", None)
        self.add_item_menu(self.menu_notes, actions_notes.on_diary_new)
        self.add_item_menu(self.menu_notes, actions_notes.on_diary_new_with_images)
        self.add_item_menu(self.menu_notes, actions_notes.on_diary_new_dream)

        self.menu.addMenu(self.menu_python)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_notes)
        self.add_item_menu(self.menu, actions_windows.on_open_camera_uploads)
        self.add_item_menu(self.menu, actions_windows.on_block_disks)
        self.menu.addSeparator()
        self.add_item_menu(self.menu, actions_images.on_image_optimize_clipboard)
        self.add_item_menu(self.menu, actions_images.on_image_optimize_clipboard_dialog)
        self.menu.addSeparator()
        self.action_exit = QAction("Exit", triggered=lambda: QApplication.quit())
        self.menu.addAction(self.action_exit)

    def add_item_menu(self, menu, class_action, icon=""):
        action_name = f"action_{class_action.__name__}"
        if ".svg" in icon:
            setattr(
                self,
                action_name,
                QAction(
                    QIcon(f":/assets/{icon}"),
                    class_action().title,
                    triggered=class_action(),
                ),
            )
        elif ".svg" in icon:
            setattr(
                self,
                action_name,
                QAction(
                    f.create_emoji_icon(icon),
                    class_action().title,
                    triggered=class_action(),
                ),
            )
        else:
            setattr(
                self,
                action_name,
                QAction(
                    class_action().title,
                    triggered=class_action(),
                ),
            )
        menu.addAction(getattr(self, action_name))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)
    tray_icon.setContextMenu(main_menu.menu)
    tray_icon.show()
    sys.exit(app.exec())
