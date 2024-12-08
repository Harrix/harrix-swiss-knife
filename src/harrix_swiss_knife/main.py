import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from harrix_swiss_knife import resources_rc

def on_quit():
    QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Создаем иконку для трея
    tray_icon = QSystemTrayIcon(QIcon(":/assets/logo.svg"), parent=app)

    # Создаем меню
    menu = QMenu()

    action1 = QAction("Пункт 1")
    action2 = QAction("Пункт 2")
    exit_action = QAction("Выход", triggered=on_quit)

    menu.addAction(action1)
    menu.addAction(action2)
    menu.addSeparator()
    menu.addAction(exit_action)

    # Устанавливаем меню в иконке трея
    tray_icon.setContextMenu(menu)

    # Показать иконку в трее
    tray_icon.show()
    sys.exit(app.exec())
