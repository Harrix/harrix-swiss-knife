from PySide6.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QTextEdit, QWidget, QHBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, menu):
        super().__init__()

        self.setWindowTitle("Menu")
        self.resize(600, 400)
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Create a QListWidget to display menu items
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        # Add QTextEdit on the right
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit, 2)

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def on_item_clicked(self, item):
        action = item.data(Qt.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()
            # Display information in QTextEdit
            self.text_edit.append(f"Action performed: {action.text()}")

    def populate_list(self, actions, indent_level=0):
        for action in actions:
            item = QListWidgetItem()
            # Add indentation for submenus
            text = ("    " * indent_level) + action.text()
            item.setText(text)
            if not action.icon().isNull():
                item.setIcon(action.icon())
            item.setData(Qt.UserRole, action)

            self.list_widget.addItem(item)

            # Check if the action has a submenu
            if action.menu() is not None:
                # Make the text bold
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                # Recursively add actions from the submenu
                self.populate_list(action.menu().actions(), indent_level + 1)
