import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc
from harrix_swiss_knife import actions_python


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainMenu:
    def __init__(self):
        self.menu = QMenu()

        self.python_menu = QMenu("Python", None)
        self.action_rye_new_project_projects = QAction(
            actions_python.on_rye_new_project_projects.title,
            triggered=actions_python.on_rye_new_project_projects(),
        )
        self.python_menu.addAction(self.action_rye_new_project_projects)
        self.action_rye_new_project = QAction("Создать Rye проект в …")
        self.python_menu.addAction(self.action_rye_new_project)

        self.exit_action = QAction("Выход", triggered=lambda: QApplication.quit())

        self.menu.addMenu(self.python_menu)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)
    tray_icon.setContextMenu(main_menu.menu)
    tray_icon.show()

    sys.excepthook = except_hook
    sys.exit(app.exec())
