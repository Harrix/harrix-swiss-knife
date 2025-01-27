from PySide6.QtWidgets import QSystemTrayIcon


from harrix_swiss_knife import main_window


class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, menu, parent=None):
        super().__init__(icon, parent)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window = None
        self.menu = menu

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window is None:
                self.main_window = main_window.MainWindow(self.menu)
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
