# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSplitter, QTabWidget, QTableView, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(972, 574)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.action_habits_refresh = QAction(MainWindow)
        self.action_habits_refresh.setObjectName(u"action_habits_refresh")
        self.action_habits_delete = QAction(MainWindow)
        self.action_habits_delete.setObjectName(u"action_habits_delete")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_dashboard = QWidget()
        self.tab_dashboard.setObjectName(u"tab_dashboard")
        self.verticalLayout_dashboard = QVBoxLayout(self.tab_dashboard)
        self.verticalLayout_dashboard.setObjectName(u"verticalLayout_dashboard")
        self.verticalLayout_dashboard.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_dashboard, "")
        self.tab_sets_of_habits = QWidget()
        self.tab_sets_of_habits.setObjectName(u"tab_sets_of_habits")
        self.horizontalLayout_27 = QHBoxLayout(self.tab_sets_of_habits)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.splitter_habits = QSplitter(self.tab_sets_of_habits)
        self.splitter_habits.setObjectName(u"splitter_habits")
        self.splitter_habits.setOrientation(Qt.Orientation.Horizontal)
        self.frame_habits = QFrame(self.splitter_habits)
        self.frame_habits.setObjectName(u"frame_habits")
        self.frame_habits.setMinimumSize(QSize(350, 0))
        self.frame_habits.setMaximumSize(QSize(16777215, 16777215))
        self.frame_habits.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_habits.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_habits)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.groupBox_habits_5 = QGroupBox(self.frame_habits)
        self.groupBox_habits_5.setObjectName(u"groupBox_habits_5")
        self.groupBox_habits_5.setMinimumSize(QSize(0, 0))
        self.verticalLayout_22 = QVBoxLayout(self.groupBox_habits_5)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.horizontalLayout_habits_8 = QHBoxLayout()
        self.horizontalLayout_habits_8.setObjectName(u"horizontalLayout_habits_8")
        self.pushButton_habits_delete = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_delete.setObjectName(u"pushButton_habits_delete")
        self.pushButton_habits_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_delete)

        self.pushButton_habits_refresh = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_refresh.setObjectName(u"pushButton_habits_refresh")
        self.pushButton_habits_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_refresh)


        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_8)

        self.horizontalLayout_habits_25 = QHBoxLayout()
        self.horizontalLayout_habits_25.setObjectName(u"horizontalLayout_habits_25")
        self.pushButton_habits_show_all_records = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_show_all_records.setObjectName(u"pushButton_habits_show_all_records")

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_show_all_records)

        self.pushButton_habits_export_csv = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_export_csv.setObjectName(u"pushButton_habits_export_csv")
        self.pushButton_habits_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_export_csv)


        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_25)


        self.verticalLayout_23.addWidget(self.groupBox_habits_5)

        self.groupBox_habits_2 = QGroupBox(self.frame_habits)
        self.groupBox_habits_2.setObjectName(u"groupBox_habits_2")
        self.verticalLayout_habits_10 = QVBoxLayout(self.groupBox_habits_2)
        self.verticalLayout_habits_10.setObjectName(u"verticalLayout_habits_10")
        self.horizontalLayout_habits_17 = QHBoxLayout()
        self.horizontalLayout_habits_17.setObjectName(u"horizontalLayout_habits_17")
        self.label_habits_5 = QLabel(self.groupBox_habits_2)
        self.label_habits_5.setObjectName(u"label_habits_5")
        self.label_habits_5.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_habits_17.addWidget(self.label_habits_5)

        self.lineEdit_habit_name = QLineEdit(self.groupBox_habits_2)
        self.lineEdit_habit_name.setObjectName(u"lineEdit_habit_name")
        self.lineEdit_habit_name.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_habits_17.addWidget(self.lineEdit_habit_name)


        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_17)

        self.horizontalLayout_habit_emoji = QHBoxLayout()
        self.horizontalLayout_habit_emoji.setObjectName(u"horizontalLayout_habit_emoji")
        self.label_habit_emoji = QLabel(self.groupBox_habits_2)
        self.label_habit_emoji.setObjectName(u"label_habit_emoji")
        self.label_habit_emoji.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_habit_emoji.addWidget(self.label_habit_emoji)

        self.lineEdit_habit_emoji = QLineEdit(self.groupBox_habits_2)
        self.lineEdit_habit_emoji.setObjectName(u"lineEdit_habit_emoji")
        self.lineEdit_habit_emoji.setMaximumSize(QSize(80, 16777215))
        self.lineEdit_habit_emoji.setMaxLength(16)

        self.horizontalLayout_habit_emoji.addWidget(self.lineEdit_habit_emoji)

        self.pushButton_habit_choose_emoji = QPushButton(self.groupBox_habits_2)
        self.pushButton_habit_choose_emoji.setObjectName(u"pushButton_habit_choose_emoji")

        self.horizontalLayout_habit_emoji.addWidget(self.pushButton_habit_choose_emoji)

        self.horizontalSpacer_habit_emoji = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_habit_emoji.addItem(self.horizontalSpacer_habit_emoji)


        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habit_emoji)

        self.checkBox_habit_is_bool = QCheckBox(self.groupBox_habits_2)
        self.checkBox_habit_is_bool.setObjectName(u"checkBox_habit_is_bool")

        self.verticalLayout_habits_10.addWidget(self.checkBox_habit_is_bool)

        self.horizontalLayout_habits_19 = QHBoxLayout()
        self.horizontalLayout_habits_19.setObjectName(u"horizontalLayout_habits_19")
        self.horizontalSpacer_habits_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_habits_19.addItem(self.horizontalSpacer_habits_4)

        self.pushButton_habit_add_new = QPushButton(self.groupBox_habits_2)
        self.pushButton_habit_add_new.setObjectName(u"pushButton_habit_add_new")

        self.horizontalLayout_habits_19.addWidget(self.pushButton_habit_add_new)


        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_19)


        self.verticalLayout_23.addWidget(self.groupBox_habits_2)

        self.tableView_habits = QTableView(self.frame_habits)
        self.tableView_habits.setObjectName(u"tableView_habits")

        self.verticalLayout_23.addWidget(self.tableView_habits)

        self.splitter_habits.addWidget(self.frame_habits)
        self.tableView_process_habits = QTableView(self.splitter_habits)
        self.tableView_process_habits.setObjectName(u"tableView_process_habits")
        self.splitter_habits.addWidget(self.tableView_process_habits)

        self.horizontalLayout_27.addWidget(self.splitter_habits)

        self.tabWidget.addTab(self.tab_sets_of_habits, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName(u"tab_charts")
        self.horizontalLayout_charts = QHBoxLayout(self.tab_charts)
        self.horizontalLayout_charts.setObjectName(u"horizontalLayout_charts")
        self.splitter_charts = QSplitter(self.tab_charts)
        self.splitter_charts.setObjectName(u"splitter_charts")
        self.splitter_charts.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter_charts)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setMinimumSize(QSize(150, 0))
        self.verticalLayout_24 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.label_filter_habit = QLabel(self.layoutWidget)
        self.label_filter_habit.setObjectName(u"label_filter_habit")

        self.verticalLayout_24.addWidget(self.label_filter_habit)

        self.listView_filter_habit = QListView(self.layoutWidget)
        self.listView_filter_habit.setObjectName(u"listView_filter_habit")

        self.verticalLayout_24.addWidget(self.listView_filter_habit)

        self.label_filter_habit_year = QLabel(self.layoutWidget)
        self.label_filter_habit_year.setObjectName(u"label_filter_habit_year")

        self.verticalLayout_24.addWidget(self.label_filter_habit_year)

        self.listView_filter_habit_year = QListView(self.layoutWidget)
        self.listView_filter_habit_year.setObjectName(u"listView_filter_habit_year")

        self.verticalLayout_24.addWidget(self.listView_filter_habit_year)

        self.splitter_charts.addWidget(self.layoutWidget)
        self.widget_charts_heatmap = QWidget(self.splitter_charts)
        self.widget_charts_heatmap.setObjectName(u"widget_charts_heatmap")
        self.verticalLayout_charts_heatmap = QVBoxLayout(self.widget_charts_heatmap)
        self.verticalLayout_charts_heatmap.setSpacing(8)
        self.verticalLayout_charts_heatmap.setObjectName(u"verticalLayout_charts_heatmap")
        self.verticalLayout_charts_heatmap.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_charts_heatmap_year = QHBoxLayout()
        self.horizontalLayout_charts_heatmap_year.setObjectName(u"horizontalLayout_charts_heatmap_year")
        self.pushButton_charts_heatmap_prev_year = QPushButton(self.widget_charts_heatmap)
        self.pushButton_charts_heatmap_prev_year.setObjectName(u"pushButton_charts_heatmap_prev_year")
        self.pushButton_charts_heatmap_prev_year.setMinimumSize(QSize(34, 34))
        self.pushButton_charts_heatmap_prev_year.setMaximumSize(QSize(34, 34))

        self.horizontalLayout_charts_heatmap_year.addWidget(self.pushButton_charts_heatmap_prev_year)

        self.horizontalSpacer_charts_heatmap_year = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_heatmap_year.addItem(self.horizontalSpacer_charts_heatmap_year)

        self.pushButton_charts_heatmap_next_year = QPushButton(self.widget_charts_heatmap)
        self.pushButton_charts_heatmap_next_year.setObjectName(u"pushButton_charts_heatmap_next_year")
        self.pushButton_charts_heatmap_next_year.setMinimumSize(QSize(34, 34))
        self.pushButton_charts_heatmap_next_year.setMaximumSize(QSize(34, 34))

        self.horizontalLayout_charts_heatmap_year.addWidget(self.pushButton_charts_heatmap_next_year)


        self.verticalLayout_charts_heatmap.addLayout(self.horizontalLayout_charts_heatmap_year)

        self.scrollArea_charts_process_habits = QScrollArea(self.widget_charts_heatmap)
        self.scrollArea_charts_process_habits.setObjectName(u"scrollArea_charts_process_habits")
        self.scrollArea_charts_process_habits.setMinimumSize(QSize(0, 301))
        self.scrollArea_charts_process_habits.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts_process_habits = QWidget()
        self.scrollAreaWidgetContents_charts_process_habits.setObjectName(u"scrollAreaWidgetContents_charts_process_habits")
        self.scrollAreaWidgetContents_charts_process_habits.setGeometry(QRect(0, 0, 294, 425))
        self.verticalLayout_charts_process_habits_content = QVBoxLayout(self.scrollAreaWidgetContents_charts_process_habits)
        self.verticalLayout_charts_process_habits_content.setObjectName(u"verticalLayout_charts_process_habits_content")
        self.scrollArea_charts_process_habits.setWidget(self.scrollAreaWidgetContents_charts_process_habits)

        self.verticalLayout_charts_heatmap.addWidget(self.scrollArea_charts_process_habits)

        self.splitter_charts.addWidget(self.widget_charts_heatmap)

        self.horizontalLayout_charts.addWidget(self.splitter_charts)

        self.tabWidget.addTab(self.tab_charts, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 972, 33))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuCommands = QMenu(self.menuBar)
        self.menuCommands.setObjectName(u"menuCommands")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuCommands.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuCommands.addAction(self.action_habits_refresh)
        self.menuCommands.addAction(self.action_habits_delete)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Habit tracker", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.action_habits_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Habits", None))
        self.action_habits_delete.setText(QCoreApplication.translate("MainWindow", u"Delete Habit", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_dashboard), QCoreApplication.translate("MainWindow", u"Dashboard", None))
        self.groupBox_habits_5.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_habits_delete.setText(QCoreApplication.translate("MainWindow", u"Delete selected", None))
        self.pushButton_habits_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        self.pushButton_habits_show_all_records.setText(QCoreApplication.translate("MainWindow", u"Show All Records", None))
        self.pushButton_habits_export_csv.setText(QCoreApplication.translate("MainWindow", u"Export Table", None))
        self.groupBox_habits_2.setTitle(QCoreApplication.translate("MainWindow", u"Add New Habit", None))
        self.label_habits_5.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.label_habit_emoji.setText(QCoreApplication.translate("MainWindow", u"Emoji:", None))
        self.lineEdit_habit_emoji.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Emoji", None))
        self.pushButton_habit_choose_emoji.setText(QCoreApplication.translate("MainWindow", u"Choose\u2026", None))
        self.checkBox_habit_is_bool.setText(QCoreApplication.translate("MainWindow", u"Boolean (0 or 1 only)", None))
        self.pushButton_habit_add_new.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sets_of_habits), QCoreApplication.translate("MainWindow", u"Habits", None))
        self.label_filter_habit.setText(QCoreApplication.translate("MainWindow", u"Habit:", None))
        self.label_filter_habit_year.setText(QCoreApplication.translate("MainWindow", u"Year:", None))
#if QT_CONFIG(tooltip)
        self.pushButton_charts_heatmap_prev_year.setToolTip(QCoreApplication.translate("MainWindow", u"Previous year", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_charts_heatmap_prev_year.setText(QCoreApplication.translate("MainWindow", u"\u2190", None))
#if QT_CONFIG(tooltip)
        self.pushButton_charts_heatmap_next_year.setToolTip(QCoreApplication.translate("MainWindow", u"Next year", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_charts_heatmap_next_year.setText(QCoreApplication.translate("MainWindow", u"\u2192", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_charts), QCoreApplication.translate("MainWindow", u"Charts", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuCommands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

