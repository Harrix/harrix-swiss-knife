import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc

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


    action_create_rye_projects = QAction("Создать Rye проект в Projects")
    python_menu.addAction(action_create_rye_projects)

    action_create_rye_github = QAction("Создать Rye проект в Github")
    python_menu.addAction(action_create_rye_github)


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
