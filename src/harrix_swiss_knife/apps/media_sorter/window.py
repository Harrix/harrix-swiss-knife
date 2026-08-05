# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Media Sorter", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About", None))
        self.label_folder_title.setText(QCoreApplication.translate("MainWindow", "Working folder", None))
        self.lineEdit_folder.setPlaceholderText(QCoreApplication.translate("MainWindow", "Select a folder\u2026", None))
        self.pushButton_browse.setText(QCoreApplication.translate("MainWindow", "Browse\u2026", None))
        self.pushButton_reload.setText(QCoreApplication.translate("MainWindow", "Reload", None))
        self.label_mode_title.setText(QCoreApplication.translate("MainWindow", "Mode", None))
        self.radioButton_random.setText(QCoreApplication.translate("MainWindow", "Random", None))
        self.radioButton_explorer.setText(QCoreApplication.translate("MainWindow", "Explorer", None))
        self.checkBox_unreviewed_only.setText(QCoreApplication.translate("MainWindow", "Unreviewed only", None))
        self.label_stats.setText(QCoreApplication.translate("MainWindow", "Reviewed: 0 \u00b7 Remaining: 0", None))
        self.label_status.setText("")
        self.pushButton_next.setText(QCoreApplication.translate("MainWindow", "Next (skip)", None))
        self.pushButton_mark_reviewed.setText(QCoreApplication.translate("MainWindow", "Mark reviewed", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete (Recycle Bin)", None))
        self.label_random_name.setText(QCoreApplication.translate("MainWindow", "No media", None))
        self.label_random_preview.setText(QCoreApplication.translate("MainWindow", "Select a folder to begin", None))
        ___qtreewidgetitem = self.treeWidget_folders.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", "Folders", None))
        self.label_bins_title.setText(QCoreApplication.translate("MainWindow", "Bins", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_root = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_root.setObjectName("horizontalLayout_root")
        self.splitter_main = QSplitter(self.centralwidget)
        self.splitter_main.setObjectName("splitter_main")
        self.splitter_main.setOrientation(Qt.Orientation.Horizontal)
        self.leftPanel = QWidget(self.splitter_main)
        self.leftPanel.setObjectName("leftPanel")
        self.leftPanel.setMinimumSize(QSize(220, 0))
        self.leftPanel.setMaximumSize(QSize(320, 16777215))
        self.verticalLayout_left = QVBoxLayout(self.leftPanel)
        self.verticalLayout_left.setObjectName("verticalLayout_left")
        self.label_folder_title = QLabel(self.leftPanel)
        self.label_folder_title.setObjectName("label_folder_title")

        self.verticalLayout_left.addWidget(self.label_folder_title)

        self.lineEdit_folder = QLineEdit(self.leftPanel)
        self.lineEdit_folder.setObjectName("lineEdit_folder")
        self.lineEdit_folder.setReadOnly(True)

        self.verticalLayout_left.addWidget(self.lineEdit_folder)

        self.horizontalLayout_folder_buttons = QHBoxLayout()
        self.horizontalLayout_folder_buttons.setObjectName("horizontalLayout_folder_buttons")
        self.pushButton_browse = QPushButton(self.leftPanel)
        self.pushButton_browse.setObjectName("pushButton_browse")

        self.horizontalLayout_folder_buttons.addWidget(self.pushButton_browse)

        self.pushButton_reload = QPushButton(self.leftPanel)
        self.pushButton_reload.setObjectName("pushButton_reload")

        self.horizontalLayout_folder_buttons.addWidget(self.pushButton_reload)

        self.verticalLayout_left.addLayout(self.horizontalLayout_folder_buttons)

        self.label_mode_title = QLabel(self.leftPanel)
        self.label_mode_title.setObjectName("label_mode_title")

        self.verticalLayout_left.addWidget(self.label_mode_title)

        self.radioButton_random = QRadioButton(self.leftPanel)
        self.radioButton_random.setObjectName("radioButton_random")
        self.radioButton_random.setChecked(True)

        self.verticalLayout_left.addWidget(self.radioButton_random)

        self.radioButton_explorer = QRadioButton(self.leftPanel)
        self.radioButton_explorer.setObjectName("radioButton_explorer")

        self.verticalLayout_left.addWidget(self.radioButton_explorer)

        self.checkBox_unreviewed_only = QCheckBox(self.leftPanel)
        self.checkBox_unreviewed_only.setObjectName("checkBox_unreviewed_only")
        self.checkBox_unreviewed_only.setChecked(True)

        self.verticalLayout_left.addWidget(self.checkBox_unreviewed_only)

        self.label_stats = QLabel(self.leftPanel)
        self.label_stats.setObjectName("label_stats")
        self.label_stats.setWordWrap(True)

        self.verticalLayout_left.addWidget(self.label_stats)

        self.label_status = QLabel(self.leftPanel)
        self.label_status.setObjectName("label_status")
        self.label_status.setWordWrap(True)

        self.verticalLayout_left.addWidget(self.label_status)

        self.verticalSpacer_left = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_left.addItem(self.verticalSpacer_left)

        self.pushButton_next = QPushButton(self.leftPanel)
        self.pushButton_next.setObjectName("pushButton_next")

        self.verticalLayout_left.addWidget(self.pushButton_next)

        self.pushButton_mark_reviewed = QPushButton(self.leftPanel)
        self.pushButton_mark_reviewed.setObjectName("pushButton_mark_reviewed")

        self.verticalLayout_left.addWidget(self.pushButton_mark_reviewed)

        self.pushButton_delete = QPushButton(self.leftPanel)
        self.pushButton_delete.setObjectName("pushButton_delete")

        self.verticalLayout_left.addWidget(self.pushButton_delete)

        self.splitter_main.addWidget(self.leftPanel)
        self.centerPanel = QWidget(self.splitter_main)
        self.centerPanel.setObjectName("centerPanel")
        self.verticalLayout_center = QVBoxLayout(self.centerPanel)
        self.verticalLayout_center.setObjectName("verticalLayout_center")
        self.verticalLayout_center.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_center = QStackedWidget(self.centerPanel)
        self.stackedWidget_center.setObjectName("stackedWidget_center")
        self.page_random = QWidget()
        self.page_random.setObjectName("page_random")
        self.verticalLayout_random = QVBoxLayout(self.page_random)
        self.verticalLayout_random.setObjectName("verticalLayout_random")
        self.label_random_name = QLabel(self.page_random)
        self.label_random_name.setObjectName("label_random_name")
        self.label_random_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_random.addWidget(self.label_random_name)

        self.label_random_preview = QLabel(self.page_random)
        self.label_random_preview.setObjectName("label_random_preview")
        self.label_random_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_random_preview.setMinimumSize(QSize(200, 200))

        self.verticalLayout_random.addWidget(self.label_random_preview)

        self.stackedWidget_center.addWidget(self.page_random)
        self.page_explorer = QWidget()
        self.page_explorer.setObjectName("page_explorer")
        self.horizontalLayout_explorer = QHBoxLayout(self.page_explorer)
        self.horizontalLayout_explorer.setObjectName("horizontalLayout_explorer")
        self.horizontalLayout_explorer.setContentsMargins(0, 0, 0, 0)
        self.treeWidget_folders = QTreeWidget(self.page_explorer)
        self.treeWidget_folders.setObjectName("treeWidget_folders")
        self.treeWidget_folders.setMinimumSize(QSize(160, 0))
        self.treeWidget_folders.setMaximumSize(QSize(280, 16777215))
        self.treeWidget_folders.setHeaderHidden(True)

        self.horizontalLayout_explorer.addWidget(self.treeWidget_folders)

        self.listWidget_files = QListWidget(self.page_explorer)
        self.listWidget_files.setObjectName("listWidget_files")
        self.listWidget_files.setViewMode(QListView.ViewMode.IconMode)
        self.listWidget_files.setResizeMode(QListView.ResizeMode.Adjust)
        self.listWidget_files.setMovement(QListView.Movement.Static)
        self.listWidget_files.setSpacing(8)
        self.listWidget_files.setUniformItemSizes(True)

        self.horizontalLayout_explorer.addWidget(self.listWidget_files)

        self.stackedWidget_center.addWidget(self.page_explorer)

        self.verticalLayout_center.addWidget(self.stackedWidget_center)

        self.splitter_main.addWidget(self.centerPanel)
        self.rightPanel = QWidget(self.splitter_main)
        self.rightPanel.setObjectName("rightPanel")
        self.rightPanel.setMinimumSize(QSize(200, 0))
        self.rightPanel.setMaximumSize(QSize(360, 16777215))
        self.verticalLayout_right = QVBoxLayout(self.rightPanel)
        self.verticalLayout_right.setObjectName("verticalLayout_right")
        self.label_bins_title = QLabel(self.rightPanel)
        self.label_bins_title.setObjectName("label_bins_title")

        self.verticalLayout_right.addWidget(self.label_bins_title)

        self.scrollArea_bins = QScrollArea(self.rightPanel)
        self.scrollArea_bins.setObjectName("scrollArea_bins")
        self.scrollArea_bins.setWidgetResizable(True)
        self.scrollArea_bins.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollAreaWidgetContents_bins = QWidget()
        self.scrollAreaWidgetContents_bins.setObjectName("scrollAreaWidgetContents_bins")
        self.scrollAreaWidgetContents_bins.setGeometry(QRect(0, 0, 180, 400))
        self.verticalLayout_bins = QVBoxLayout(self.scrollAreaWidgetContents_bins)
        self.verticalLayout_bins.setObjectName("verticalLayout_bins")
        self.verticalSpacer_bins = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_bins.addItem(self.verticalSpacer_bins)

        self.scrollArea_bins.setWidget(self.scrollAreaWidgetContents_bins)

        self.verticalLayout_right.addWidget(self.scrollArea_bins)

        self.splitter_main.addWidget(self.rightPanel)

        self.horizontalLayout_root.addWidget(self.splitter_main)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1280, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.stackedWidget_center.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
