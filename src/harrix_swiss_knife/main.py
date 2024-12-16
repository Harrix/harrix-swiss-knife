import sys
from functools import partial
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import actions_python, actions_windows, actions_images


class MainMenu:
    def __init__(self):
        self.menu = QMenu()

        # Menu Python
        self.menu_python = QMenu("Python", None)

        self.action_rye_new_project_projects = QAction(
            actions_python.on_rye_new_project.title,
            triggered=partial(
                actions_python.on_rye_new_project(), is_need_dialog=False
            ),
        )
        self.menu_python.addAction(self.action_rye_new_project_projects)

        self.action_rye_new_project = QAction(
            actions_python.on_rye_new_project.title_with_dialog,
            triggered=partial(actions_python.on_rye_new_project(), is_need_dialog=True),
        )
        self.menu_python.addAction(self.action_rye_new_project)

        # Menu Images
        self.menu_images = QMenu("Images", None)

        self.action_optimize = QAction(
            actions_images.on_images_optimize.title,
            triggered=actions_images.on_images_optimize(),
        )
        self.menu_images.addAction(self.action_optimize)

        # Main menu
        self.action_block_disks = QAction(
            actions_windows.on_block_disks.title,
            triggered=actions_windows.on_block_disks(),
        )

        self.action_exit = QAction("Exit", triggered=lambda: QApplication.quit())

        self.menu.addMenu(self.menu_python)
        self.menu.addMenu(self.menu_images)
        self.menu.addAction(self.action_block_disks)
        self.menu.addSeparator()
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
