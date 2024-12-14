import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc
from harrix_swiss_knife import actions_python


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)

    menu = QMenu()

    python_menu = QMenu("Python", None)
    menu.addMenu(python_menu)
    action_rye_new_project_projects = QAction(
        actions_python.on_rye_new_project_projects.title,
        triggered=actions_python.on_rye_new_project_projects(),
    )
    python_menu.addAction(action_rye_new_project_projects)
    action_rye_new_project = QAction("Создать Rye проект в …")
    python_menu.addAction(action_rye_new_project)

    exit_action = QAction("Выход", triggered=lambda: QApplication.quit())
    menu.addSeparator()
    menu.addAction(exit_action)
    tray_icon.setContextMenu(menu)

    tray_icon.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
