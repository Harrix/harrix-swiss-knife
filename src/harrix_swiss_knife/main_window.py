"""Main window module for the harrix-swiss-knife application.

This module provides the MainWindow class that serves as the primary user interface
for the application, displaying menu actions and handling user interactions.
"""

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QSplitter,
    QTextEdit,
    QWidget,
)


class MainWindow(QMainWindow):
    """The main window of the application that displays a menu and handles user interactions.

    Attributes:

    - `list_widget` (`QListWidget`): Widget to display the list of menu actions.
    - `text_edit` (`QTextEdit`): Widget to display information about performed actions.

    """

    def __init__(self, menu: QMenu) -> None:
        """Initialize the `MainWindow` with the given menu.

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

        splitter = QSplitter()
        layout.addWidget(splitter)

        self.list_widget = QListWidget()
        splitter.addWidget(self.list_widget)

        self.text_edit = QTextEdit()
        splitter.addWidget(self.text_edit)

        splitter.setSizes([300, 700])

        # Populate QListWidget with actions from the menu
        self.populate_list(menu.actions())

        # Connect the itemClicked signal to an event handler
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Override the close event to hide the window instead of closing it.

        Args:

        - `event` (`QCloseEvent`): The close event triggered when the window is requested to close.

        Prevents the window from closing and hides it instead.

        """
        event.ignore()
        self.hide()

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle the event when an item in the list widget is clicked.

        Args:

        - `item` (`QListWidgetItem`): The item that was clicked.

        If the associated action is a `QAction`, it triggers the action and logs the action's text
        in the text edit widget.

        Returns:

        - None

        """
        # Check if the item is enabled
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return  # Do nothing if the item is disabled
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            # Trigger the action
            action.trigger()
            # Display information in QTextEdit
            output_txt = (h.dev.get_project_root() / "temp/output.txt").read_text(encoding="utf8")
            self.text_edit.setPlainText(output_txt)

    def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None:
        """Populate the list widget with actions, handling submenus recursively.

        Args:

        - `actions` (`list[QAction]`): A list of actions to add to the list widget.
        - `indent_level` (`int`): The current indentation level for submenu actions. Defaults to `0`.

        For each action, an item is created with appropriate indentation and icon. If the action
        has a submenu, the text is made bold and the submenu actions are added recursively with increased indentation.

        Returns:

        - None

        """
        for action in actions:
            if not action.text():
                continue
            item = QListWidgetItem()
            # Add indentation for submenus
            text = ("    " * indent_level) + action.text()
            item.setText(text)
            if not action.icon().isNull():
                item.setIcon(action.icon())

            if action.menu() is not None and isinstance(action.menu(), QMenu):
                # The action has a submenu
                # Make the text bold
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                # Set the item flags to make it not selectable and disabled
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                # Do not set UserRole data for this item
                self.list_widget.addItem(item)
                # Recursively add actions from the submenu
                self.populate_list(action.menu().actions(), indent_level + 1)  # type: ignore noqa: PGH003
            else:
                # Regular action without submenu
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.list_widget.addItem(item)
