# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListView,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QSplitter, QStatusBar, QTabWidget, QTableView,
    QToolBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1375, 945)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_main = QHBoxLayout(self.tab)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.splitter = QSplitter(self.tab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(350, 0))
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 225))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_exercise = QLabel(self.groupBox)
        self.label_exercise.setObjectName(u"label_exercise")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_exercise.setFont(font)

        self.verticalLayout_5.addWidget(self.label_exercise)

        self.label_last_date_count_today = QLabel(self.groupBox)
        self.label_last_date_count_today.setObjectName(u"label_last_date_count_today")

        self.verticalLayout_5.addWidget(self.label_last_date_count_today)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.spinBox_count = QSpinBox(self.groupBox)
        self.spinBox_count.setObjectName(u"spinBox_count")
        self.spinBox_count.setFont(font)
        self.spinBox_count.setStyleSheet(u"QSpinBox {\n"
"                                          background-color: lightgreen;\n"
"                                          }")
        self.spinBox_count.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spinBox_count.setMaximum(1000000)
        self.spinBox_count.setValue(100)

        self.horizontalLayout_14.addWidget(self.spinBox_count)

        self.label_unit = QLabel(self.groupBox)
        self.label_unit.setObjectName(u"label_unit")
        self.label_unit.setMaximumSize(QSize(61, 16777215))

        self.horizontalLayout_14.addWidget(self.label_unit)


        self.verticalLayout_5.addLayout(self.horizontalLayout_14)

        self.comboBox_type = QComboBox(self.groupBox)
        self.comboBox_type.setObjectName(u"comboBox_type")

        self.verticalLayout_5.addWidget(self.comboBox_type)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.dateEdit = QDateEdit(self.groupBox)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setMinimumSize(QSize(191, 0))
        self.dateEdit.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_13.addWidget(self.dateEdit)

        self.pushButton_yesterday = QPushButton(self.groupBox)
        self.pushButton_yesterday.setObjectName(u"pushButton_yesterday")
        self.pushButton_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_13.addWidget(self.pushButton_yesterday)


        self.verticalLayout_5.addLayout(self.horizontalLayout_13)

        self.pushButton_add = QPushButton(self.groupBox)
        self.pushButton_add.setObjectName(u"pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 41))
        self.pushButton_add.setFont(font)
        self.pushButton_add.setStyleSheet(u"QPushButton {\n"
"                                      background-color: lightgreen;\n"
"                                      border: 1px solid #4CAF50;\n"
"                                      border-radius: 4px;\n"
"                                      }\n"
"                                      QPushButton:hover {\n"
"                                      background-color: #90EE90;\n"
"                                      }\n"
"                                      QPushButton:pressed {\n"
"                                      background-color: #7FDD7F;\n"
"                                      }")

        self.verticalLayout_5.addWidget(self.pushButton_add)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.label_exercise_avif = QLabel(self.frame)
        self.label_exercise_avif.setObjectName(u"label_exercise_avif")
        self.label_exercise_avif.setMinimumSize(QSize(0, 150))
        self.label_exercise_avif.setStyleSheet(u"border: 1px solid gray;")
        self.label_exercise_avif.setScaledContents(False)
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_exercise_avif)

        self.groupBox_5 = QGroupBox(self.frame)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_5)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_refresh = QPushButton(self.groupBox_5)
        self.pushButton_refresh.setObjectName(u"pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.pushButton_show_all_records = QPushButton(self.groupBox_5)
        self.pushButton_show_all_records.setObjectName(u"pushButton_show_all_records")

        self.horizontalLayout_25.addWidget(self.pushButton_show_all_records)

        self.pushButton_export_csv = QPushButton(self.groupBox_5)
        self.pushButton_export_csv.setObjectName(u"pushButton_export_csv")
        self.pushButton_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_25.addWidget(self.pushButton_export_csv)


        self.verticalLayout_2.addLayout(self.horizontalLayout_25)


        self.verticalLayout_3.addWidget(self.groupBox_5)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName(u"groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 201))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_filter_exercise = QLabel(self.groupBox_filter)
        self.label_filter_exercise.setObjectName(u"label_filter_exercise")
        self.label_filter_exercise.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_9.addWidget(self.label_filter_exercise)

        self.comboBox_filter_exercise = QComboBox(self.groupBox_filter)
        self.comboBox_filter_exercise.setObjectName(u"comboBox_filter_exercise")
        self.comboBox_filter_exercise.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_9.addWidget(self.comboBox_filter_exercise)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_filter_type = QLabel(self.groupBox_filter)
        self.label_filter_type.setObjectName(u"label_filter_type")
        self.label_filter_type.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_10.addWidget(self.label_filter_type)

        self.comboBox_filter_type = QComboBox(self.groupBox_filter)
        self.comboBox_filter_type.setObjectName(u"comboBox_filter_type")
        self.comboBox_filter_type.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_10.addWidget(self.comboBox_filter_type)


        self.verticalLayout_4.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_filter_date = QLabel(self.groupBox_filter)
        self.label_filter_date.setObjectName(u"label_filter_date")
        self.label_filter_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_11.addWidget(self.label_filter_date)

        self.dateEdit_filter_from = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_from.setObjectName(u"dateEdit_filter_from")
        self.dateEdit_filter_from.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_from.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit_filter_from.setCalendarPopup(True)

        self.horizontalLayout_11.addWidget(self.dateEdit_filter_from)


        self.verticalLayout_4.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_filter_to = QLabel(self.groupBox_filter)
        self.label_filter_to.setObjectName(u"label_filter_to")
        self.label_filter_to.setMinimumSize(QSize(61, 0))
        self.label_filter_to.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_12.addWidget(self.label_filter_to)

        self.dateEdit_filter_to = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_to.setObjectName(u"dateEdit_filter_to")
        self.dateEdit_filter_to.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_to.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit_filter_to.setCalendarPopup(True)

        self.horizontalLayout_12.addWidget(self.dateEdit_filter_to)


        self.verticalLayout_4.addLayout(self.horizontalLayout_12)

        self.checkBox_use_date_filter = QCheckBox(self.groupBox_filter)
        self.checkBox_use_date_filter.setObjectName(u"checkBox_use_date_filter")

        self.verticalLayout_4.addWidget(self.checkBox_use_date_filter)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.pushButton_clear_filter = QPushButton(self.groupBox_filter)
        self.pushButton_clear_filter.setObjectName(u"pushButton_clear_filter")

        self.horizontalLayout_7.addWidget(self.pushButton_clear_filter)

        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName(u"pushButton_apply_filter")

        self.horizontalLayout_7.addWidget(self.pushButton_apply_filter)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)


        self.verticalLayout_3.addWidget(self.groupBox_filter)

        self.groupBox_9 = QGroupBox(self.frame)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.groupBox_9.setMinimumSize(QSize(0, 0))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_9)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_count_sets_today = QLabel(self.groupBox_9)
        self.label_count_sets_today.setObjectName(u"label_count_sets_today")
        font1 = QFont()
        font1.setPointSize(50)
        font1.setBold(True)
        self.label_count_sets_today.setFont(font1)
        self.label_count_sets_today.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_count_sets_today)


        self.verticalLayout_3.addWidget(self.groupBox_9)

        self.verticalSpacer = QSpacerItem(20, 143, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.frame)
        self.widget_middle = QWidget(self.splitter)
        self.widget_middle.setObjectName(u"widget_middle")
        self.verticalLayout = QVBoxLayout(self.widget_middle)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.widget_middle)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout.addWidget(self.label_7)

        self.listView_exercises = QListView(self.widget_middle)
        self.listView_exercises.setObjectName(u"listView_exercises")
        self.listView_exercises.setMaximumSize(QSize(16777215, 16777215))
        self.listView_exercises.setStyleSheet(u"QListView {\n"
"                                border: 2px solid #4CAF50;\n"
"                                border-radius: 4px;\n"
"                                background-color: white;\n"
"                                }\n"
"                                QListView::item {\n"
"                                padding: 4px;\n"
"                                border-bottom: 1px solid #e0e0e0;\n"
"                                }\n"
"                                QListView::item:selected {\n"
"                                background-color: #e8f5e8;\n"
"                                color: black;\n"
"                                }\n"
"                                QListView::item:hover {\n"
"                                background-color: #f0f8f0;\n"
"                                }")

        self.verticalLayout.addWidget(self.listView_exercises)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_process = QTableView(self.splitter)
        self.tableView_process.setObjectName(u"tableView_process")
        self.splitter.addWidget(self.tableView_process)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.splitter_2 = QSplitter(self.tab_2)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter_2.setChildrenCollapsible(False)
        self.widget_top = QWidget(self.splitter_2)
        self.widget_top.setObjectName(u"widget_top")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_top)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.widget_top)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(250, 0))
        self.frame_2.setMaximumSize(QSize(250, 16777215))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_2)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_17.addWidget(self.label_5)

        self.lineEdit_exercise_name = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_name.setObjectName(u"lineEdit_exercise_name")
        self.lineEdit_exercise_name.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_17.addWidget(self.lineEdit_exercise_name)


        self.verticalLayout_10.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_18.addWidget(self.label_6)

        self.lineEdit_exercise_unit = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_unit.setObjectName(u"lineEdit_exercise_unit")
        self.lineEdit_exercise_unit.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_18.addWidget(self.lineEdit_exercise_unit)


        self.verticalLayout_10.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_calories_per_unit = QHBoxLayout()
        self.horizontalLayout_calories_per_unit.setObjectName(u"horizontalLayout_calories_per_unit")
        self.label_calories_per_unit = QLabel(self.groupBox_2)
        self.label_calories_per_unit.setObjectName(u"label_calories_per_unit")
        self.label_calories_per_unit.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_calories_per_unit.addWidget(self.label_calories_per_unit)

        self.doubleSpinBox_calories_per_unit = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_calories_per_unit.setObjectName(u"doubleSpinBox_calories_per_unit")
        self.doubleSpinBox_calories_per_unit.setMinimumSize(QSize(70, 0))
        self.doubleSpinBox_calories_per_unit.setDecimals(2)
        self.doubleSpinBox_calories_per_unit.setMaximum(999.990000000000009)
        self.doubleSpinBox_calories_per_unit.setValue(0.000000000000000)

        self.horizontalLayout_calories_per_unit.addWidget(self.doubleSpinBox_calories_per_unit)


        self.verticalLayout_10.addLayout(self.horizontalLayout_calories_per_unit)

        self.check_box_is_type_required = QCheckBox(self.groupBox_2)
        self.check_box_is_type_required.setObjectName(u"check_box_is_type_required")

        self.verticalLayout_10.addWidget(self.check_box_is_type_required)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_4)

        self.pushButton_exercise_add = QPushButton(self.groupBox_2)
        self.pushButton_exercise_add.setObjectName(u"pushButton_exercise_add")

        self.horizontalLayout_19.addWidget(self.pushButton_exercise_add)


        self.verticalLayout_10.addLayout(self.horizontalLayout_19)


        self.verticalLayout_15.addWidget(self.groupBox_2)

        self.groupBox_7 = QGroupBox(self.frame_2)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.pushButton_exercises_delete = QPushButton(self.groupBox_7)
        self.pushButton_exercises_delete.setObjectName(u"pushButton_exercises_delete")

        self.horizontalLayout_20.addWidget(self.pushButton_exercises_delete)

        self.pushButton_exercises_refresh = QPushButton(self.groupBox_7)
        self.pushButton_exercises_refresh.setObjectName(u"pushButton_exercises_refresh")

        self.horizontalLayout_20.addWidget(self.pushButton_exercises_refresh)


        self.verticalLayout_11.addLayout(self.horizontalLayout_20)


        self.verticalLayout_15.addWidget(self.groupBox_7)

        self.label_exercise_avif_2 = QLabel(self.frame_2)
        self.label_exercise_avif_2.setObjectName(u"label_exercise_avif_2")
        self.label_exercise_avif_2.setMinimumSize(QSize(0, 150))
        self.label_exercise_avif_2.setStyleSheet(u"border: 1px solid gray;")
        self.label_exercise_avif_2.setScaledContents(False)
        self.label_exercise_avif_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_exercise_avif_2)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_2)


        self.horizontalLayout_2.addWidget(self.frame_2)

        self.tableView_exercises = QTableView(self.widget_top)
        self.tableView_exercises.setObjectName(u"tableView_exercises")

        self.horizontalLayout_2.addWidget(self.tableView_exercises)

        self.splitter_2.addWidget(self.widget_top)
        self.widget_bottom = QWidget(self.splitter_2)
        self.widget_bottom.setObjectName(u"widget_bottom")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_bottom)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.widget_bottom)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(250, 0))
        self.frame_3.setMaximumSize(QSize(250, 16777215))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_3)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.groupBox_3 = QGroupBox(self.frame_3)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_14 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.comboBox_exercise_name = QComboBox(self.groupBox_3)
        self.comboBox_exercise_name.setObjectName(u"comboBox_exercise_name")

        self.verticalLayout_14.addWidget(self.comboBox_exercise_name)

        self.lineEdit_exercise_type = QLineEdit(self.groupBox_3)
        self.lineEdit_exercise_type.setObjectName(u"lineEdit_exercise_type")

        self.verticalLayout_14.addWidget(self.lineEdit_exercise_type)

        self.horizontalLayout_calories_modifier = QHBoxLayout()
        self.horizontalLayout_calories_modifier.setObjectName(u"horizontalLayout_calories_modifier")
        self.label_calories_modifier = QLabel(self.groupBox_3)
        self.label_calories_modifier.setObjectName(u"label_calories_modifier")

        self.horizontalLayout_calories_modifier.addWidget(self.label_calories_modifier)

        self.doubleSpinBox_calories_modifier = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_calories_modifier.setObjectName(u"doubleSpinBox_calories_modifier")
        self.doubleSpinBox_calories_modifier.setDecimals(2)
        self.doubleSpinBox_calories_modifier.setMinimum(0.010000000000000)
        self.doubleSpinBox_calories_modifier.setMaximum(10.000000000000000)
        self.doubleSpinBox_calories_modifier.setSingleStep(0.100000000000000)
        self.doubleSpinBox_calories_modifier.setValue(1.000000000000000)

        self.horizontalLayout_calories_modifier.addWidget(self.doubleSpinBox_calories_modifier)


        self.verticalLayout_14.addLayout(self.horizontalLayout_calories_modifier)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_5)

        self.pushButton_type_add = QPushButton(self.groupBox_3)
        self.pushButton_type_add.setObjectName(u"pushButton_type_add")

        self.horizontalLayout_22.addWidget(self.pushButton_type_add)


        self.verticalLayout_14.addLayout(self.horizontalLayout_22)


        self.verticalLayout_12.addWidget(self.groupBox_3)

        self.groupBox_8 = QGroupBox(self.frame_3)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.pushButton_types_delete = QPushButton(self.groupBox_8)
        self.pushButton_types_delete.setObjectName(u"pushButton_types_delete")

        self.horizontalLayout_21.addWidget(self.pushButton_types_delete)

        self.pushButton_types_refresh = QPushButton(self.groupBox_8)
        self.pushButton_types_refresh.setObjectName(u"pushButton_types_refresh")

        self.horizontalLayout_21.addWidget(self.pushButton_types_refresh)


        self.verticalLayout_13.addLayout(self.horizontalLayout_21)


        self.verticalLayout_12.addWidget(self.groupBox_8)

        self.label_exercise_avif_3 = QLabel(self.frame_3)
        self.label_exercise_avif_3.setObjectName(u"label_exercise_avif_3")
        self.label_exercise_avif_3.setMinimumSize(QSize(0, 150))
        self.label_exercise_avif_3.setStyleSheet(u"border: 1px solid gray;")
        self.label_exercise_avif_3.setScaledContents(False)
        self.label_exercise_avif_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_12.addWidget(self.label_exercise_avif_3)

        self.verticalSpacer_3 = QSpacerItem(20, 608, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_3)


        self.horizontalLayout_3.addWidget(self.frame_3)

        self.tableView_exercise_types = QTableView(self.widget_bottom)
        self.tableView_exercise_types.setObjectName(u"tableView_exercise_types")

        self.horizontalLayout_3.addWidget(self.tableView_exercise_types)

        self.splitter_2.addWidget(self.widget_bottom)

        self.horizontalLayout_4.addWidget(self.splitter_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.frame_4 = QFrame(self.tab_5)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(250, 0))
        self.frame_4.setMaximumSize(QSize(250, 16777215))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_4)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.groupBox_4 = QGroupBox(self.frame_4)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.doubleSpinBox_weight = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_weight.setObjectName(u"doubleSpinBox_weight")
        self.doubleSpinBox_weight.setMaximum(300.000000000000000)
        self.doubleSpinBox_weight.setValue(89.000000000000000)

        self.verticalLayout_7.addWidget(self.doubleSpinBox_weight)

        self.dateEdit_weight = QDateEdit(self.groupBox_4)
        self.dateEdit_weight.setObjectName(u"dateEdit_weight")
        self.dateEdit_weight.setMinimumSize(QSize(191, 0))
        self.dateEdit_weight.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit_weight.setCalendarPopup(True)

        self.verticalLayout_7.addWidget(self.dateEdit_weight)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_3)

        self.pushButton_weight_add = QPushButton(self.groupBox_4)
        self.pushButton_weight_add.setObjectName(u"pushButton_weight_add")

        self.horizontalLayout_15.addWidget(self.pushButton_weight_add)


        self.verticalLayout_7.addLayout(self.horizontalLayout_15)


        self.verticalLayout_9.addWidget(self.groupBox_4)

        self.groupBox_6 = QGroupBox(self.frame_4)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.pushButton_weight_delete = QPushButton(self.groupBox_6)
        self.pushButton_weight_delete.setObjectName(u"pushButton_weight_delete")

        self.horizontalLayout_16.addWidget(self.pushButton_weight_delete)

        self.pushButton_weight_refresh = QPushButton(self.groupBox_6)
        self.pushButton_weight_refresh.setObjectName(u"pushButton_weight_refresh")

        self.horizontalLayout_16.addWidget(self.pushButton_weight_refresh)


        self.verticalLayout_8.addLayout(self.horizontalLayout_16)


        self.verticalLayout_9.addWidget(self.groupBox_6)

        self.tableView_weight = QTableView(self.frame_4)
        self.tableView_weight.setObjectName(u"tableView_weight")

        self.verticalLayout_9.addWidget(self.tableView_weight)


        self.horizontalLayout_5.addWidget(self.frame_4)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame_weight_controls = QFrame(self.tab_5)
        self.frame_weight_controls.setObjectName(u"frame_weight_controls")
        self.frame_weight_controls.setMaximumSize(QSize(16777215, 80))
        self.frame_weight_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_weight_controls.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_weight_controls = QHBoxLayout(self.frame_weight_controls)
        self.horizontalLayout_weight_controls.setObjectName(u"horizontalLayout_weight_controls")
        self.label_weight_from = QLabel(self.frame_weight_controls)
        self.label_weight_from.setObjectName(u"label_weight_from")

        self.horizontalLayout_weight_controls.addWidget(self.label_weight_from)

        self.dateEdit_weight_from = QDateEdit(self.frame_weight_controls)
        self.dateEdit_weight_from.setObjectName(u"dateEdit_weight_from")
        self.dateEdit_weight_from.setCalendarPopup(True)

        self.horizontalLayout_weight_controls.addWidget(self.dateEdit_weight_from)

        self.label_weight_to = QLabel(self.frame_weight_controls)
        self.label_weight_to.setObjectName(u"label_weight_to")

        self.horizontalLayout_weight_controls.addWidget(self.label_weight_to)

        self.dateEdit_weight_to = QDateEdit(self.frame_weight_controls)
        self.dateEdit_weight_to.setObjectName(u"dateEdit_weight_to")
        self.dateEdit_weight_to.setCalendarPopup(True)

        self.horizontalLayout_weight_controls.addWidget(self.dateEdit_weight_to)

        self.pushButton_weight_last_month = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_last_month.setObjectName(u"pushButton_weight_last_month")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_last_month)

        self.pushButton_weight_last_year = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_last_year.setObjectName(u"pushButton_weight_last_year")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_last_year)

        self.pushButton_weight_all_time = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_all_time.setObjectName(u"pushButton_weight_all_time")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_all_time)

        self.pushButton_update_weight_chart = QPushButton(self.frame_weight_controls)
        self.pushButton_update_weight_chart.setObjectName(u"pushButton_update_weight_chart")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_update_weight_chart)

        self.horizontalSpacer_weight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_weight_controls.addItem(self.horizontalSpacer_weight)


        self.verticalLayout_6.addWidget(self.frame_weight_controls)

        self.scrollArea_weight_chart = QScrollArea(self.tab_5)
        self.scrollArea_weight_chart.setObjectName(u"scrollArea_weight_chart")
        self.scrollArea_weight_chart.setWidgetResizable(True)
        self.scrollAreaWidgetContents_weight_chart = QWidget()
        self.scrollAreaWidgetContents_weight_chart.setObjectName(u"scrollAreaWidgetContents_weight_chart")
        self.scrollAreaWidgetContents_weight_chart.setGeometry(QRect(0, 0, 1073, 777))
        self.verticalLayout_weight_chart_content = QVBoxLayout(self.scrollAreaWidgetContents_weight_chart)
        self.verticalLayout_weight_chart_content.setObjectName(u"verticalLayout_weight_chart_content")
        self.scrollArea_weight_chart.setWidget(self.scrollAreaWidgetContents_weight_chart)

        self.verticalLayout_6.addWidget(self.scrollArea_weight_chart)


        self.horizontalLayout_5.addLayout(self.verticalLayout_6)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName(u"tab_charts")
        self.horizontalLayout_26 = QHBoxLayout(self.tab_charts)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.splitter_charts = QSplitter(self.tab_charts)
        self.splitter_charts.setObjectName(u"splitter_charts")
        self.splitter_charts.setOrientation(Qt.Horizontal)
        self.widget_left_panel = QWidget(self.splitter_charts)
        self.widget_left_panel.setObjectName(u"widget_left_panel")
        self.verticalLayout_18 = QVBoxLayout(self.widget_left_panel)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_chart_exercise = QLabel(self.widget_left_panel)
        self.label_chart_exercise.setObjectName(u"label_chart_exercise")

        self.verticalLayout_18.addWidget(self.label_chart_exercise)

        self.listView_chart_exercise = QListView(self.widget_left_panel)
        self.listView_chart_exercise.setObjectName(u"listView_chart_exercise")
        self.listView_chart_exercise.setMinimumSize(QSize(301, 0))
        self.listView_chart_exercise.setMaximumSize(QSize(16777215, 16777215))
        self.listView_chart_exercise.setStyleSheet(u"QListView {\n"
"                                border: 2px solid #4CAF50;\n"
"                                border-radius: 4px;\n"
"                                background-color: white;\n"
"                                }\n"
"                                QListView::item {\n"
"                                padding: 4px;\n"
"                                border-bottom: 1px solid #e0e0e0;\n"
"                                }\n"
"                                QListView::item:selected {\n"
"                                background-color: #e8f5e8;\n"
"                                color: black;\n"
"                                }\n"
"                                QListView::item:hover {\n"
"                                background-color: #f0f8f0;\n"
"                                }")

        self.verticalLayout_18.addWidget(self.listView_chart_exercise)

        self.label_chart_type = QLabel(self.widget_left_panel)
        self.label_chart_type.setObjectName(u"label_chart_type")

        self.verticalLayout_18.addWidget(self.label_chart_type)

        self.listView_chart_type = QListView(self.widget_left_panel)
        self.listView_chart_type.setObjectName(u"listView_chart_type")
        self.listView_chart_type.setMaximumSize(QSize(16777215, 16777215))
        self.listView_chart_type.setStyleSheet(u"QListView {\n"
"                                border: 2px solid #4CAF50;\n"
"                                border-radius: 4px;\n"
"                                background-color: white;\n"
"                                }\n"
"                                QListView::item {\n"
"                                padding: 4px;\n"
"                                border-bottom: 1px solid #e0e0e0;\n"
"                                }\n"
"                                QListView::item:selected {\n"
"                                background-color: #e8f5e8;\n"
"                                color: black;\n"
"                                }\n"
"                                QListView::item:hover {\n"
"                                background-color: #f0f8f0;\n"
"                                }")

        self.verticalLayout_18.addWidget(self.listView_chart_type)

        self.groupBox_type_of_charts = QGroupBox(self.widget_left_panel)
        self.groupBox_type_of_charts.setObjectName(u"groupBox_type_of_charts")
        self.groupBox_type_of_charts.setMinimumSize(QSize(0, 0))
        self.verticalLayout_21 = QVBoxLayout(self.groupBox_type_of_charts)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.radioButton_type_of_chart_standart = QRadioButton(self.groupBox_type_of_charts)
        self.radioButton_type_of_chart_standart.setObjectName(u"radioButton_type_of_chart_standart")

        self.verticalLayout_21.addWidget(self.radioButton_type_of_chart_standart)

        self.radioButton_type_of_chart_show_sets_chart = QRadioButton(self.groupBox_type_of_charts)
        self.radioButton_type_of_chart_show_sets_chart.setObjectName(u"radioButton_type_of_chart_show_sets_chart")

        self.verticalLayout_21.addWidget(self.radioButton_type_of_chart_show_sets_chart)

        self.radioButton_type_of_chart_kcal = QRadioButton(self.groupBox_type_of_charts)
        self.radioButton_type_of_chart_kcal.setObjectName(u"radioButton_type_of_chart_kcal")

        self.verticalLayout_21.addWidget(self.radioButton_type_of_chart_kcal)

        self.radioButton_type_of_chart_compare_last = QRadioButton(self.groupBox_type_of_charts)
        self.radioButton_type_of_chart_compare_last.setObjectName(u"radioButton_type_of_chart_compare_last")

        self.verticalLayout_21.addWidget(self.radioButton_type_of_chart_compare_last)

        self.radioButton_type_of_chart_compare_same_months = QRadioButton(self.groupBox_type_of_charts)
        self.radioButton_type_of_chart_compare_same_months.setObjectName(u"radioButton_type_of_chart_compare_same_months")

        self.verticalLayout_21.addWidget(self.radioButton_type_of_chart_compare_same_months)


        self.verticalLayout_18.addWidget(self.groupBox_type_of_charts)

        self.splitter_charts.addWidget(self.widget_left_panel)
        self.widget_right_panel = QWidget(self.splitter_charts)
        self.widget_right_panel.setObjectName(u"widget_right_panel")
        self.verticalLayout_20 = QVBoxLayout(self.widget_right_panel)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.frame_charts_controls = QFrame(self.widget_right_panel)
        self.frame_charts_controls.setObjectName(u"frame_charts_controls")
        self.frame_charts_controls.setMaximumSize(QSize(16777215, 120))
        self.frame_charts_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_charts_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_charts_controls = QVBoxLayout(self.frame_charts_controls)
        self.verticalLayout_charts_controls.setObjectName(u"verticalLayout_charts_controls")
        self.horizontalLayout_charts_controls_1 = QHBoxLayout()
        self.horizontalLayout_charts_controls_1.setObjectName(u"horizontalLayout_charts_controls_1")
        self.label_chart_period = QLabel(self.frame_charts_controls)
        self.label_chart_period.setObjectName(u"label_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_period)

        self.comboBox_chart_period = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.setObjectName(u"comboBox_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_period)

        self.checkBox_max_value = QCheckBox(self.frame_charts_controls)
        self.checkBox_max_value.setObjectName(u"checkBox_max_value")

        self.horizontalLayout_charts_controls_1.addWidget(self.checkBox_max_value)

        self.pushButton_update_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_update_chart.setObjectName(u"pushButton_update_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_update_chart)

        self.horizontalSpacer_charts = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_1.addItem(self.horizontalSpacer_charts)


        self.verticalLayout_charts_controls.addLayout(self.horizontalLayout_charts_controls_1)

        self.horizontalLayout_charts_controls_2 = QHBoxLayout()
        self.horizontalLayout_charts_controls_2.setObjectName(u"horizontalLayout_charts_controls_2")
        self.label_chart_from = QLabel(self.frame_charts_controls)
        self.label_chart_from.setObjectName(u"label_chart_from")

        self.horizontalLayout_charts_controls_2.addWidget(self.label_chart_from)

        self.dateEdit_chart_from = QDateEdit(self.frame_charts_controls)
        self.dateEdit_chart_from.setObjectName(u"dateEdit_chart_from")
        self.dateEdit_chart_from.setCalendarPopup(True)

        self.horizontalLayout_charts_controls_2.addWidget(self.dateEdit_chart_from)

        self.label_chart_to = QLabel(self.frame_charts_controls)
        self.label_chart_to.setObjectName(u"label_chart_to")

        self.horizontalLayout_charts_controls_2.addWidget(self.label_chart_to)

        self.dateEdit_chart_to = QDateEdit(self.frame_charts_controls)
        self.dateEdit_chart_to.setObjectName(u"dateEdit_chart_to")
        self.dateEdit_chart_to.setCalendarPopup(True)

        self.horizontalLayout_charts_controls_2.addWidget(self.dateEdit_chart_to)

        self.pushButton_chart_last_month = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_last_month.setObjectName(u"pushButton_chart_last_month")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_last_month)

        self.pushButton_chart_last_year = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_last_year.setObjectName(u"pushButton_chart_last_year")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_last_year)

        self.pushButton_chart_all_time = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_all_time.setObjectName(u"pushButton_chart_all_time")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_all_time)

        self.horizontalSpacer_charts_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_2.addItem(self.horizontalSpacer_charts_2)

        self.label_compare_last = QLabel(self.frame_charts_controls)
        self.label_compare_last.setObjectName(u"label_compare_last")

        self.horizontalLayout_charts_controls_2.addWidget(self.label_compare_last)

        self.spinBox_compare_last = QSpinBox(self.frame_charts_controls)
        self.spinBox_compare_last.setObjectName(u"spinBox_compare_last")
        self.spinBox_compare_last.setValue(3)

        self.horizontalLayout_charts_controls_2.addWidget(self.spinBox_compare_last)

        self.comboBox_compare_same_months = QComboBox(self.frame_charts_controls)
        self.comboBox_compare_same_months.setObjectName(u"comboBox_compare_same_months")

        self.horizontalLayout_charts_controls_2.addWidget(self.comboBox_compare_same_months)


        self.verticalLayout_charts_controls.addLayout(self.horizontalLayout_charts_controls_2)


        self.horizontalLayout_23.addWidget(self.frame_charts_controls)

        self.label_exercise_avif_4 = QLabel(self.widget_right_panel)
        self.label_exercise_avif_4.setObjectName(u"label_exercise_avif_4")
        self.label_exercise_avif_4.setMinimumSize(QSize(150, 76))
        self.label_exercise_avif_4.setStyleSheet(u"border: 1px solid gray;")
        self.label_exercise_avif_4.setScaledContents(False)
        self.label_exercise_avif_4.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_23.addWidget(self.label_exercise_avif_4)


        self.verticalLayout_20.addLayout(self.horizontalLayout_23)

        self.scrollArea_charts = QScrollArea(self.widget_right_panel)
        self.scrollArea_charts.setObjectName(u"scrollArea_charts")
        self.scrollArea_charts.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts = QWidget()
        self.scrollAreaWidgetContents_charts.setObjectName(u"scrollAreaWidgetContents_charts")
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1021, 742))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName(u"verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_20.addWidget(self.scrollArea_charts)

        self.splitter_charts.addWidget(self.widget_right_panel)

        self.horizontalLayout_26.addWidget(self.splitter_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.frame_5 = QFrame(self.tab_4)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(300, 0))
        self.frame_5.setMaximumSize(QSize(300, 16777215))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_5)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.groupBox_10 = QGroupBox(self.frame_5)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.groupBox_10.setMinimumSize(QSize(0, 0))
        self.verticalLayout_19 = QVBoxLayout(self.groupBox_10)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.comboBox_records_select_exercise = QComboBox(self.groupBox_10)
        self.comboBox_records_select_exercise.setObjectName(u"comboBox_records_select_exercise")

        self.verticalLayout_19.addWidget(self.comboBox_records_select_exercise)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_record_count = QLabel(self.groupBox_10)
        self.label_record_count.setObjectName(u"label_record_count")

        self.horizontalLayout_24.addWidget(self.label_record_count)

        self.spinBox_record_count = QSpinBox(self.groupBox_10)
        self.spinBox_record_count.setObjectName(u"spinBox_record_count")
        self.spinBox_record_count.setMinimum(1)
        self.spinBox_record_count.setMaximum(100)
        self.spinBox_record_count.setValue(5)

        self.horizontalLayout_24.addWidget(self.spinBox_record_count)


        self.verticalLayout_19.addLayout(self.horizontalLayout_24)

        self.pushButton_statistics_refresh = QPushButton(self.groupBox_10)
        self.pushButton_statistics_refresh.setObjectName(u"pushButton_statistics_refresh")

        self.verticalLayout_19.addWidget(self.pushButton_statistics_refresh)


        self.verticalLayout_16.addWidget(self.groupBox_10)

        self.pushButton_last_exercises = QPushButton(self.frame_5)
        self.pushButton_last_exercises.setObjectName(u"pushButton_last_exercises")

        self.verticalLayout_16.addWidget(self.pushButton_last_exercises)

        self.pushButton_check_steps = QPushButton(self.frame_5)
        self.pushButton_check_steps.setObjectName(u"pushButton_check_steps")

        self.verticalLayout_16.addWidget(self.pushButton_check_steps)

        self.label_exercise_avif_5 = QLabel(self.frame_5)
        self.label_exercise_avif_5.setObjectName(u"label_exercise_avif_5")
        self.label_exercise_avif_5.setMinimumSize(QSize(0, 150))
        self.label_exercise_avif_5.setStyleSheet(u"border: 1px solid gray;")
        self.label_exercise_avif_5.setScaledContents(False)
        self.label_exercise_avif_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_exercise_avif_5)

        self.verticalSpacer_4 = QSpacerItem(20, 759, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)


        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tableView_statistics = QTableView(self.tab_4)
        self.tableView_statistics.setObjectName(u"tableView_statistics")

        self.horizontalLayout_6.addWidget(self.tableView_statistics)

        self.tabWidget.addTab(self.tab_4, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1375, 21))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Fitness tracker", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Set parameters", None))
        self.label_exercise.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_last_date_count_today.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_unit.setText(QCoreApplication.translate("MainWindow", u"times", None))
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", u"Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.label_exercise_avif.setText(QCoreApplication.translate("MainWindow", u"No exercise selected", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", u"Delete selected", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        self.pushButton_show_all_records.setText(QCoreApplication.translate("MainWindow", u"Show All Records", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", u"Export Table", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.label_filter_exercise.setText(QCoreApplication.translate("MainWindow", u"Exercise:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", u"to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", u"Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", u"Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", u"Apply Filter", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"Count of Sets Today", None))
        self.label_count_sets_today.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Exercise:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Sets", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Add New Exercise", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Unit of Measurement:", None))
        self.label_calories_per_unit.setText(QCoreApplication.translate("MainWindow", u"Calories per unit:", None))
        self.check_box_is_type_required.setText(QCoreApplication.translate("MainWindow", u"Type required", None))
        self.pushButton_exercise_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_exercises_delete.setText(QCoreApplication.translate("MainWindow", u"Delete selected", None))
        self.pushButton_exercises_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        self.label_exercise_avif_2.setText(QCoreApplication.translate("MainWindow", u"No exercise selected", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Add New Exercise Type", None))
        self.label_calories_modifier.setText(QCoreApplication.translate("MainWindow", u"Calories modifier:", None))
        self.pushButton_type_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_types_delete.setText(QCoreApplication.translate("MainWindow", u"Delete selected", None))
        self.pushButton_types_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        self.label_exercise_avif_3.setText(QCoreApplication.translate("MainWindow", u"No exercise selected", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Exercises", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Add New Weight", None))
        self.dateEdit_weight.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_weight_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_weight_delete.setText(QCoreApplication.translate("MainWindow", u"Delete selected", None))
        self.pushButton_weight_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        self.label_weight_from.setText(QCoreApplication.translate("MainWindow", u"From:", None))
        self.dateEdit_weight_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_weight_to.setText(QCoreApplication.translate("MainWindow", u"To:", None))
        self.dateEdit_weight_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_weight_last_month.setText(QCoreApplication.translate("MainWindow", u"Last Month", None))
        self.pushButton_weight_last_year.setText(QCoreApplication.translate("MainWindow", u"Last Year", None))
        self.pushButton_weight_all_time.setText(QCoreApplication.translate("MainWindow", u"All Time", None))
        self.pushButton_update_weight_chart.setText(QCoreApplication.translate("MainWindow", u"Update Chart", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", u"Weight", None))
        self.label_chart_exercise.setText(QCoreApplication.translate("MainWindow", u"Exercise:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.groupBox_type_of_charts.setTitle(QCoreApplication.translate("MainWindow", u"Type Of Chart", None))
        self.radioButton_type_of_chart_standart.setText(QCoreApplication.translate("MainWindow", u"Standart", None))
        self.radioButton_type_of_chart_show_sets_chart.setText(QCoreApplication.translate("MainWindow", u"Show Sets Chart", None))
        self.radioButton_type_of_chart_kcal.setText(QCoreApplication.translate("MainWindow", u"Kcal", None))
        self.radioButton_type_of_chart_compare_last.setText(QCoreApplication.translate("MainWindow", u"Compare last months", None))
        self.radioButton_type_of_chart_compare_same_months.setText(QCoreApplication.translate("MainWindow", u"Compare same months", None))
        self.label_chart_period.setText(QCoreApplication.translate("MainWindow", u"Period:", None))
        self.comboBox_chart_period.setItemText(0, QCoreApplication.translate("MainWindow", u"Days", None))
        self.comboBox_chart_period.setItemText(1, QCoreApplication.translate("MainWindow", u"Months", None))
        self.comboBox_chart_period.setItemText(2, QCoreApplication.translate("MainWindow", u"Years", None))

        self.checkBox_max_value.setText(QCoreApplication.translate("MainWindow", u"Max value, not sum", None))
        self.pushButton_update_chart.setText(QCoreApplication.translate("MainWindow", u"Update Chart", None))
        self.label_chart_from.setText(QCoreApplication.translate("MainWindow", u"From:", None))
        self.dateEdit_chart_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_chart_to.setText(QCoreApplication.translate("MainWindow", u"To:", None))
        self.dateEdit_chart_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_chart_last_month.setText(QCoreApplication.translate("MainWindow", u"Last Month", None))
        self.pushButton_chart_last_year.setText(QCoreApplication.translate("MainWindow", u"Last Year", None))
        self.pushButton_chart_all_time.setText(QCoreApplication.translate("MainWindow", u"All Time", None))
        self.label_compare_last.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_exercise_avif_4.setText(QCoreApplication.translate("MainWindow", u"No exercise selected", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_charts), QCoreApplication.translate("MainWindow", u"Exercise Chart", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"Records", None))
        self.label_record_count.setText(QCoreApplication.translate("MainWindow", u"Record count:", None))
        self.pushButton_statistics_refresh.setText(QCoreApplication.translate("MainWindow", u"Records", None))
        self.pushButton_last_exercises.setText(QCoreApplication.translate("MainWindow", u"Last exercises", None))
        self.pushButton_check_steps.setText(QCoreApplication.translate("MainWindow", u"Check steps", None))
        self.label_exercise_avif_5.setText(QCoreApplication.translate("MainWindow", u"No exercise selected", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Statistics", None))
    # retranslateUi

