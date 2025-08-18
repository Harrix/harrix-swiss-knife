# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                               QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QListView,
                               QMainWindow, QMenuBar, QPushButton,
                               QRadioButton, QScrollArea, QSizePolicy,
                               QSpacerItem, QSpinBox, QSplitter, QStatusBar,
                               QTableView, QTabWidget, QToolBar, QVBoxLayout,
                               QWidget)


class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Food tracker", None))
        self.groupBox_food_add.setTitle(QCoreApplication.translate("MainWindow", "Add Food Entry", None))
        self.lineEdit_food_manual_name.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Enter food name", None)
        )
        self.pushButton_food_manual_name_clear.setText("")
        self.label_food_weight_unit.setText(QCoreApplication.translate("MainWindow", "g", None))
        self.label_food_calories.setText(QCoreApplication.translate("MainWindow", "kcal", None))
        self.checkBox_food_is_drink.setText(QCoreApplication.translate("MainWindow", "Drink", None))
        self.radioButton_use_weight.setText(QCoreApplication.translate("MainWindow", "Calculate by weight", None))
        self.radioButton_use_calories.setText(QCoreApplication.translate("MainWindow", "Enter calories directly", None))
        self.label_food_calories_calc.setText(QCoreApplication.translate("MainWindow", "Calculated calories: 0", None))
        self.dateEdit_food.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_food_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_food_add.setText(QCoreApplication.translate("MainWindow", "Add Food", None))
        self.groupBox_food_items.setTitle(QCoreApplication.translate("MainWindow", "Add Food Item", None))
        self.label_food_name.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.label_food_name_en.setText(QCoreApplication.translate("MainWindow", "Name EN:", None))
        self.checkBox_is_drink.setText(QCoreApplication.translate("MainWindow", "Is drink", None))
        self.label_food_cal100.setText(QCoreApplication.translate("MainWindow", "Cal/100g:", None))
        self.label_food_default_weight.setText(QCoreApplication.translate("MainWindow", "Default weight:", None))
        self.label_food_default_cal.setText(QCoreApplication.translate("MainWindow", "Default portion calories:", None))
        self.pushButton_food_item_add.setText(QCoreApplication.translate("MainWindow", "Add Item", None))
        self.groupBox_food_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_food_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_food_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.pushButton_add_as_text.setText(QCoreApplication.translate("MainWindow", "Add As Text", None))
        self.pushButton_show_all_records.setText(QCoreApplication.translate("MainWindow", "Show All Records", None))
        self.pushButton_check.setText(QCoreApplication.translate("MainWindow", "Check", None))
        self.groupBox_food_today.setTitle(QCoreApplication.translate("MainWindow", "Today", None))
        self.label_food_today.setText(QCoreApplication.translate("MainWindow", "0", None))
        self.label_food_items.setText(QCoreApplication.translate("MainWindow", "Food Items:", None))
        self.label_favorite_food_items.setText(QCoreApplication.translate("MainWindow", "Food Favorite Items:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_food), QCoreApplication.translate("MainWindow", "Food", None)
        )
        self.label.setText(QCoreApplication.translate("MainWindow", "Kcal per day:", None))
        self.label_food_stats_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_food_stats_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_food_stats_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_food_stats_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_food_stats_last_week.setText(QCoreApplication.translate("MainWindow", "Last Week", None))
        self.pushButton_food_stats_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_food_stats_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_food_stats_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.pushButton_food_stats_update.setText(QCoreApplication.translate("MainWindow", "Update Chart", None))
        self.comboBox_food_stats_period.setItemText(0, QCoreApplication.translate("MainWindow", "Days", None))
        self.comboBox_food_stats_period.setItemText(1, QCoreApplication.translate("MainWindow", "Months", None))
        self.comboBox_food_stats_period.setItemText(2, QCoreApplication.translate("MainWindow", "Years", None))

        self.pushButton_food_stats_food_weight.setText(
            QCoreApplication.translate("MainWindow", "Food Weight Chart", None)
        )
        self.pushButton_food_stats_drink.setText(QCoreApplication.translate("MainWindow", "Drinks Chart", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_food_stats),
            QCoreApplication.translate("MainWindow", "Food Statistics", None),
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1375, 926)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_food = QWidget()
        self.tab_food.setObjectName("tab_food")
        self.horizontalLayout_food = QHBoxLayout(self.tab_food)
        self.horizontalLayout_food.setObjectName("horizontalLayout_food")
        self.splitter_food = QSplitter(self.tab_food)
        self.splitter_food.setObjectName("splitter_food")
        self.splitter_food.setOrientation(Qt.Horizontal)
        self.splitter_food.setChildrenCollapsible(False)
        self.frame_food_controls = QFrame(self.splitter_food)
        self.frame_food_controls.setObjectName("frame_food_controls")
        self.frame_food_controls.setMinimumSize(QSize(350, 0))
        self.frame_food_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_food_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_food_controls = QVBoxLayout(self.frame_food_controls)
        self.verticalLayout_food_controls.setObjectName("verticalLayout_food_controls")
        self.groupBox_food_add = QGroupBox(self.frame_food_controls)
        self.groupBox_food_add.setObjectName("groupBox_food_add")
        self.verticalLayout = QVBoxLayout(self.groupBox_food_add)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_food_manual_name = QHBoxLayout()
        self.horizontalLayout_food_manual_name.setObjectName("horizontalLayout_food_manual_name")
        self.lineEdit_food_manual_name = QLineEdit(self.groupBox_food_add)
        self.lineEdit_food_manual_name.setObjectName("lineEdit_food_manual_name")
        font = QFont()
        font.setPointSize(12)
        self.lineEdit_food_manual_name.setFont(font)

        self.horizontalLayout_food_manual_name.addWidget(self.lineEdit_food_manual_name)

        self.pushButton_food_manual_name_clear = QPushButton(self.groupBox_food_add)
        self.pushButton_food_manual_name_clear.setObjectName("pushButton_food_manual_name_clear")
        self.pushButton_food_manual_name_clear.setMaximumSize(QSize(32, 16777215))

        self.horizontalLayout_food_manual_name.addWidget(self.pushButton_food_manual_name_clear)

        self.verticalLayout.addLayout(self.horizontalLayout_food_manual_name)

        self.horizontalLayout_food_weight = QHBoxLayout()
        self.horizontalLayout_food_weight.setObjectName("horizontalLayout_food_weight")
        self.spinBox_food_weight = QSpinBox(self.groupBox_food_add)
        self.spinBox_food_weight.setObjectName("spinBox_food_weight")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.spinBox_food_weight.setFont(font1)
        self.spinBox_food_weight.setStyleSheet(
            "QSpinBox {\n"
            "                                          background-color: #e3f2fd;\n"
            "                                          }"
        )
        self.spinBox_food_weight.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.spinBox_food_weight.setMaximum(10000)
        self.spinBox_food_weight.setValue(100)

        self.horizontalLayout_food_weight.addWidget(self.spinBox_food_weight)

        self.label_food_weight_unit = QLabel(self.groupBox_food_add)
        self.label_food_weight_unit.setObjectName("label_food_weight_unit")

        self.horizontalLayout_food_weight.addWidget(self.label_food_weight_unit)

        self.doubleSpinBox_food_calories = QDoubleSpinBox(self.groupBox_food_add)
        self.doubleSpinBox_food_calories.setObjectName("doubleSpinBox_food_calories")
        self.doubleSpinBox_food_calories.setFont(font1)
        self.doubleSpinBox_food_calories.setStyleSheet(
            "QDoubleSpinBox {\n"
            "                                          background-color: #e3f2fd;\n"
            "                                          }"
        )
        self.doubleSpinBox_food_calories.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.doubleSpinBox_food_calories.setMaximum(10000.000000000000000)

        self.horizontalLayout_food_weight.addWidget(self.doubleSpinBox_food_calories)

        self.label_food_calories = QLabel(self.groupBox_food_add)
        self.label_food_calories.setObjectName("label_food_calories")

        self.horizontalLayout_food_weight.addWidget(self.label_food_calories)

        self.checkBox_food_is_drink = QCheckBox(self.groupBox_food_add)
        self.checkBox_food_is_drink.setObjectName("checkBox_food_is_drink")

        self.horizontalLayout_food_weight.addWidget(self.checkBox_food_is_drink)

        self.verticalLayout.addLayout(self.horizontalLayout_food_weight)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButton_use_weight = QRadioButton(self.groupBox_food_add)
        self.radioButton_use_weight.setObjectName("radioButton_use_weight")
        self.radioButton_use_weight.setChecked(True)

        self.horizontalLayout_2.addWidget(self.radioButton_use_weight)

        self.radioButton_use_calories = QRadioButton(self.groupBox_food_add)
        self.radioButton_use_calories.setObjectName("radioButton_use_calories")

        self.horizontalLayout_2.addWidget(self.radioButton_use_calories)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.label_food_calories_calc = QLabel(self.groupBox_food_add)
        self.label_food_calories_calc.setObjectName("label_food_calories_calc")
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.label_food_calories_calc.setFont(font2)

        self.verticalLayout.addWidget(self.label_food_calories_calc)

        self.horizontalLayout_food_date = QHBoxLayout()
        self.horizontalLayout_food_date.setObjectName("horizontalLayout_food_date")
        self.dateEdit_food = QDateEdit(self.groupBox_food_add)
        self.dateEdit_food.setObjectName("dateEdit_food")
        self.dateEdit_food.setMinimumSize(QSize(191, 0))
        self.dateEdit_food.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_food.setCalendarPopup(True)

        self.horizontalLayout_food_date.addWidget(self.dateEdit_food)

        self.pushButton_food_yesterday = QPushButton(self.groupBox_food_add)
        self.pushButton_food_yesterday.setObjectName("pushButton_food_yesterday")
        self.pushButton_food_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_food_date.addWidget(self.pushButton_food_yesterday)

        self.verticalLayout.addLayout(self.horizontalLayout_food_date)

        self.pushButton_food_add = QPushButton(self.groupBox_food_add)
        self.pushButton_food_add.setObjectName("pushButton_food_add")
        self.pushButton_food_add.setMinimumSize(QSize(0, 41))
        self.pushButton_food_add.setFont(font1)
        self.pushButton_food_add.setStyleSheet(
            "QPushButton {\n"
            "                                      background-color: #e3f2fd;\n"
            "                                      border: 1px solid #2196F3;\n"
            "                                      border-radius: 4px;\n"
            "                                      }\n"
            "                                      QPushButton:hover {\n"
            "                                      background-color: #bbdefb;\n"
            "                                      }\n"
            "                                      QPushButton:pressed {\n"
            "                                      background-color: #90caf9;\n"
            "                                      }"
        )

        self.verticalLayout.addWidget(self.pushButton_food_add)

        self.verticalLayout_food_controls.addWidget(self.groupBox_food_add)

        self.groupBox_food_items = QGroupBox(self.frame_food_controls)
        self.groupBox_food_items.setObjectName("groupBox_food_items")
        self.verticalLayout_food_items = QVBoxLayout(self.groupBox_food_items)
        self.verticalLayout_food_items.setObjectName("verticalLayout_food_items")
        self.horizontalLayout_food_name = QHBoxLayout()
        self.horizontalLayout_food_name.setObjectName("horizontalLayout_food_name")
        self.label_food_name = QLabel(self.groupBox_food_items)
        self.label_food_name.setObjectName("label_food_name")

        self.horizontalLayout_food_name.addWidget(self.label_food_name)

        self.lineEdit_food_name = QLineEdit(self.groupBox_food_items)
        self.lineEdit_food_name.setObjectName("lineEdit_food_name")

        self.horizontalLayout_food_name.addWidget(self.lineEdit_food_name)

        self.verticalLayout_food_items.addLayout(self.horizontalLayout_food_name)

        self.horizontalLayout_food_name_en = QHBoxLayout()
        self.horizontalLayout_food_name_en.setObjectName("horizontalLayout_food_name_en")
        self.label_food_name_en = QLabel(self.groupBox_food_items)
        self.label_food_name_en.setObjectName("label_food_name_en")

        self.horizontalLayout_food_name_en.addWidget(self.label_food_name_en)

        self.lineEdit_food_name_en = QLineEdit(self.groupBox_food_items)
        self.lineEdit_food_name_en.setObjectName("lineEdit_food_name_en")

        self.horizontalLayout_food_name_en.addWidget(self.lineEdit_food_name_en)

        self.verticalLayout_food_items.addLayout(self.horizontalLayout_food_name_en)

        self.checkBox_is_drink = QCheckBox(self.groupBox_food_items)
        self.checkBox_is_drink.setObjectName("checkBox_is_drink")

        self.verticalLayout_food_items.addWidget(self.checkBox_is_drink)

        self.horizontalLayout_food_cal100 = QHBoxLayout()
        self.horizontalLayout_food_cal100.setObjectName("horizontalLayout_food_cal100")
        self.label_food_cal100 = QLabel(self.groupBox_food_items)
        self.label_food_cal100.setObjectName("label_food_cal100")

        self.horizontalLayout_food_cal100.addWidget(self.label_food_cal100)

        self.doubleSpinBox_food_cal100 = QDoubleSpinBox(self.groupBox_food_items)
        self.doubleSpinBox_food_cal100.setObjectName("doubleSpinBox_food_cal100")
        self.doubleSpinBox_food_cal100.setMaximum(9999.000000000000000)

        self.horizontalLayout_food_cal100.addWidget(self.doubleSpinBox_food_cal100)

        self.verticalLayout_food_items.addLayout(self.horizontalLayout_food_cal100)

        self.horizontalLayout_food_default_weight = QHBoxLayout()
        self.horizontalLayout_food_default_weight.setObjectName("horizontalLayout_food_default_weight")
        self.label_food_default_weight = QLabel(self.groupBox_food_items)
        self.label_food_default_weight.setObjectName("label_food_default_weight")

        self.horizontalLayout_food_default_weight.addWidget(self.label_food_default_weight)

        self.spinBox_food_default_weight = QSpinBox(self.groupBox_food_items)
        self.spinBox_food_default_weight.setObjectName("spinBox_food_default_weight")
        self.spinBox_food_default_weight.setMaximum(10000)

        self.horizontalLayout_food_default_weight.addWidget(self.spinBox_food_default_weight)

        self.verticalLayout_food_items.addLayout(self.horizontalLayout_food_default_weight)

        self.horizontalLayout_food_default_cal = QHBoxLayout()
        self.horizontalLayout_food_default_cal.setObjectName("horizontalLayout_food_default_cal")
        self.label_food_default_cal = QLabel(self.groupBox_food_items)
        self.label_food_default_cal.setObjectName("label_food_default_cal")

        self.horizontalLayout_food_default_cal.addWidget(self.label_food_default_cal)

        self.doubleSpinBox_food_default_cal = QDoubleSpinBox(self.groupBox_food_items)
        self.doubleSpinBox_food_default_cal.setObjectName("doubleSpinBox_food_default_cal")
        self.doubleSpinBox_food_default_cal.setMaximum(9999.000000000000000)

        self.horizontalLayout_food_default_cal.addWidget(self.doubleSpinBox_food_default_cal)

        self.verticalLayout_food_items.addLayout(self.horizontalLayout_food_default_cal)

        self.pushButton_food_item_add = QPushButton(self.groupBox_food_items)
        self.pushButton_food_item_add.setObjectName("pushButton_food_item_add")

        self.verticalLayout_food_items.addWidget(self.pushButton_food_item_add)

        self.verticalLayout_food_controls.addWidget(self.groupBox_food_items)

        self.groupBox_food_commands = QGroupBox(self.frame_food_controls)
        self.groupBox_food_commands.setObjectName("groupBox_food_commands")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_food_commands)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_food_commands = QHBoxLayout()
        self.horizontalLayout_food_commands.setObjectName("horizontalLayout_food_commands")
        self.pushButton_food_delete = QPushButton(self.groupBox_food_commands)
        self.pushButton_food_delete.setObjectName("pushButton_food_delete")

        self.horizontalLayout_food_commands.addWidget(self.pushButton_food_delete)

        self.pushButton_food_refresh = QPushButton(self.groupBox_food_commands)
        self.pushButton_food_refresh.setObjectName("pushButton_food_refresh")

        self.horizontalLayout_food_commands.addWidget(self.pushButton_food_refresh)

        self.verticalLayout_2.addLayout(self.horizontalLayout_food_commands)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_add_as_text = QPushButton(self.groupBox_food_commands)
        self.pushButton_add_as_text.setObjectName("pushButton_add_as_text")

        self.horizontalLayout_3.addWidget(self.pushButton_add_as_text)

        self.pushButton_show_all_records = QPushButton(self.groupBox_food_commands)
        self.pushButton_show_all_records.setObjectName("pushButton_show_all_records")

        self.horizontalLayout_3.addWidget(self.pushButton_show_all_records)

        self.pushButton_check = QPushButton(self.groupBox_food_commands)
        self.pushButton_check.setObjectName("pushButton_check")

        self.horizontalLayout_3.addWidget(self.pushButton_check)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalLayout_food_controls.addWidget(self.groupBox_food_commands)

        self.groupBox_food_today = QGroupBox(self.frame_food_controls)
        self.groupBox_food_today.setObjectName("groupBox_food_today")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_food_today)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_food_today = QLabel(self.groupBox_food_today)
        self.label_food_today.setObjectName("label_food_today")
        font3 = QFont()
        font3.setPointSize(30)
        font3.setBold(True)
        self.label_food_today.setFont(font3)
        self.label_food_today.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.label_food_today)

        self.verticalLayout_food_controls.addWidget(self.groupBox_food_today)

        self.verticalSpacer_food = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_food_controls.addItem(self.verticalSpacer_food)

        self.splitter_food.addWidget(self.frame_food_controls)
        self.widget_food_middle = QWidget(self.splitter_food)
        self.widget_food_middle.setObjectName("widget_food_middle")
        self.verticalLayout_food_middle = QVBoxLayout(self.widget_food_middle)
        self.verticalLayout_food_middle.setObjectName("verticalLayout_food_middle")
        self.verticalLayout_food_middle.setContentsMargins(0, 0, 0, 0)
        self.label_food_items = QLabel(self.widget_food_middle)
        self.label_food_items.setObjectName("label_food_items")

        self.verticalLayout_food_middle.addWidget(self.label_food_items)

        self.listView_food_items = QListView(self.widget_food_middle)
        self.listView_food_items.setObjectName("listView_food_items")
        self.listView_food_items.setStyleSheet(
            "QListView {\n"
            "                                border: 2px solid #2196F3;\n"
            "                                border-radius: 4px;\n"
            "                                background-color: white;\n"
            "                                }\n"
            "                                QListView::item {\n"
            "                                padding: 4px;\n"
            "                                border-bottom: 1px solid #e0e0e0;\n"
            "                                }\n"
            "                                QListView::item:selected {\n"
            "                                background-color: #e3f2fd;\n"
            "                                color: black;\n"
            "                                }\n"
            "                                QListView::item:hover {\n"
            "                                background-color: #bbdefb;\n"
            "                                }"
        )

        self.verticalLayout_food_middle.addWidget(self.listView_food_items)

        self.label_favorite_food_items = QLabel(self.widget_food_middle)
        self.label_favorite_food_items.setObjectName("label_favorite_food_items")

        self.verticalLayout_food_middle.addWidget(self.label_favorite_food_items)

        self.listView_favorite_food_items = QListView(self.widget_food_middle)
        self.listView_favorite_food_items.setObjectName("listView_favorite_food_items")
        self.listView_favorite_food_items.setStyleSheet(
            "QListView {\n"
            "                                border: 2px solid #2196F3;\n"
            "                                border-radius: 4px;\n"
            "                                background-color: white;\n"
            "                                }\n"
            "                                QListView::item {\n"
            "                                padding: 4px;\n"
            "                                border-bottom: 1px solid #e0e0e0;\n"
            "                                }\n"
            "                                QListView::item:selected {\n"
            "                                background-color: #e3f2fd;\n"
            "                                color: black;\n"
            "                                }\n"
            "                                QListView::item:hover {\n"
            "                                background-color: #bbdefb;\n"
            "                                }"
        )

        self.verticalLayout_food_middle.addWidget(self.listView_favorite_food_items)

        self.splitter_food.addWidget(self.widget_food_middle)
        self.tableView_food_log = QTableView(self.splitter_food)
        self.tableView_food_log.setObjectName("tableView_food_log")
        self.splitter_food.addWidget(self.tableView_food_log)

        self.horizontalLayout_food.addWidget(self.splitter_food)

        self.tabWidget.addTab(self.tab_food, "")
        self.tab_food_stats = QWidget()
        self.tab_food_stats.setObjectName("tab_food_stats")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_food_stats)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame = QFrame(self.tab_food_stats)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(250, 0))
        self.frame.setMaximumSize(QSize(250, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(self.frame)
        self.label.setObjectName("label")

        self.verticalLayout_3.addWidget(self.label)

        self.tableView_kcal_per_day = QTableView(self.frame)
        self.tableView_kcal_per_day.setObjectName("tableView_kcal_per_day")

        self.verticalLayout_3.addWidget(self.tableView_kcal_per_day)

        self.horizontalLayout_4.addWidget(self.frame)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_food_stats_controls = QFrame(self.tab_food_stats)
        self.frame_food_stats_controls.setObjectName("frame_food_stats_controls")
        self.frame_food_stats_controls.setMaximumSize(QSize(16777215, 80))
        self.frame_food_stats_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_food_stats_controls.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_food_stats_controls = QHBoxLayout(self.frame_food_stats_controls)
        self.horizontalLayout_food_stats_controls.setObjectName("horizontalLayout_food_stats_controls")
        self.label_food_stats_from = QLabel(self.frame_food_stats_controls)
        self.label_food_stats_from.setObjectName("label_food_stats_from")

        self.horizontalLayout_food_stats_controls.addWidget(self.label_food_stats_from)

        self.dateEdit_food_stats_from = QDateEdit(self.frame_food_stats_controls)
        self.dateEdit_food_stats_from.setObjectName("dateEdit_food_stats_from")
        self.dateEdit_food_stats_from.setCalendarPopup(True)

        self.horizontalLayout_food_stats_controls.addWidget(self.dateEdit_food_stats_from)

        self.label_food_stats_to = QLabel(self.frame_food_stats_controls)
        self.label_food_stats_to.setObjectName("label_food_stats_to")

        self.horizontalLayout_food_stats_controls.addWidget(self.label_food_stats_to)

        self.dateEdit_food_stats_to = QDateEdit(self.frame_food_stats_controls)
        self.dateEdit_food_stats_to.setObjectName("dateEdit_food_stats_to")
        self.dateEdit_food_stats_to.setCalendarPopup(True)

        self.horizontalLayout_food_stats_controls.addWidget(self.dateEdit_food_stats_to)

        self.pushButton_food_stats_last_week = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_last_week.setObjectName("pushButton_food_stats_last_week")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_last_week)

        self.pushButton_food_stats_last_month = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_last_month.setObjectName("pushButton_food_stats_last_month")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_last_month)

        self.pushButton_food_stats_last_year = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_last_year.setObjectName("pushButton_food_stats_last_year")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_last_year)

        self.pushButton_food_stats_all_time = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_all_time.setObjectName("pushButton_food_stats_all_time")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_all_time)

        self.pushButton_food_stats_update = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_update.setObjectName("pushButton_food_stats_update")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_update)

        self.comboBox_food_stats_period = QComboBox(self.frame_food_stats_controls)
        self.comboBox_food_stats_period.addItem("")
        self.comboBox_food_stats_period.addItem("")
        self.comboBox_food_stats_period.addItem("")
        self.comboBox_food_stats_period.setObjectName("comboBox_food_stats_period")

        self.horizontalLayout_food_stats_controls.addWidget(self.comboBox_food_stats_period)

        self.pushButton_food_stats_food_weight = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_food_weight.setObjectName("pushButton_food_stats_food_weight")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_food_weight)

        self.pushButton_food_stats_drink = QPushButton(self.frame_food_stats_controls)
        self.pushButton_food_stats_drink.setObjectName("pushButton_food_stats_drink")

        self.horizontalLayout_food_stats_controls.addWidget(self.pushButton_food_stats_drink)

        self.horizontalSpacer_food_stats = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_food_stats_controls.addItem(self.horizontalSpacer_food_stats)

        self.verticalLayout_4.addWidget(self.frame_food_stats_controls)

        self.scrollArea_food_stats = QScrollArea(self.tab_food_stats)
        self.scrollArea_food_stats.setObjectName("scrollArea_food_stats")
        self.scrollArea_food_stats.setWidgetResizable(True)
        self.scrollAreaWidgetContents_food_stats = QWidget()
        self.scrollAreaWidgetContents_food_stats.setObjectName("scrollAreaWidgetContents_food_stats")
        self.scrollAreaWidgetContents_food_stats.setGeometry(QRect(0, 0, 1073, 758))
        self.verticalLayout_food_stats_content = QVBoxLayout(self.scrollAreaWidgetContents_food_stats)
        self.verticalLayout_food_stats_content.setObjectName("verticalLayout_food_stats_content")
        self.scrollArea_food_stats.setWidget(self.scrollAreaWidgetContents_food_stats)

        self.verticalLayout_4.addWidget(self.scrollArea_food_stats)

        self.horizontalLayout_4.addLayout(self.verticalLayout_4)

        self.tabWidget.addTab(self.tab_food_stats, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1375, 21))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
