from PySide6.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QTextEdit, QWidget, QHBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import harrix_pylib as h


class MainWindow(QMainWindow):
    """
    The main window of the application that displays a menu and handles user interactions.

    Attributes:

    - `list_widget` (`QListWidget`): Widget to display the list of menu actions.
    - `text_edit` (`QTextEdit`): Widget to display information about performed actions.
    """

    def __init__(self, menu):
        """
        Initializes the `MainWindow` with the given menu.

        Args:

        - `menu` (`QMenu`): The menu whose actions will be displayed in the list widget.

        Sets up the main window layout, initializes widgets, populates the list with menu actions,
        and connects signals to their respective handlers.
        """
        super().__init__()

        self.setWindowTitle("harrix-swiss-knife")
        self.resize(1024, 800)
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
        """
        Overrides the close event to hide the window instead of closing it.

        Args:

        - `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

        Prevents the window from closing and hides it instead.
        """
        event.ignore()
        self.hide()

    def on_item_clicked(self, item):
        """
        Handles the event when an item in the list widget is clicked.

        Args:

        - `item` (`QListWidgetItem`): The item that was clicked.

        If the associated action is a `QAction`, it triggers the action and logs the action's text
        in the text edit widget.

        Returns:

        - None
        """
        action = item.data(Qt.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()
            # Display information in QTextEdit
            output_txt = (h.dev.get_project_root() / "temp/output.txt").read_text(encoding="utf8")
            self.text_edit.setPlainText(output_txt)

    def populate_list(self, actions, indent_level=0):
        """
        Populates the list widget with actions, handling submenus recursively.

        Args:

        - `actions` (`list[QAction]`): A list of actions to add to the list widget.
        - `indent_level` (`int`): The current indentation level for submenu actions. Defaults to `0`.

        For each action, an item is created with appropriate indentation and icon. If the action
        has a submenu, the text is made bold and the submenu actions are added recursively with increased indentation.

        Returns:

        - None
        """
        for action in actions:
            item = QListWidgetItem()
            # Add indentation for submenus
            if not action.text():
                continue
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
