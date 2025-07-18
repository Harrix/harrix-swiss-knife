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
    QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
    QStatusBar, QTabWidget, QTableView, QToolBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 950)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_transactions = QWidget()
        self.tab_transactions.setObjectName(u"tab_transactions")
        self.horizontalLayout_main = QHBoxLayout(self.tab_transactions)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.splitter = QSplitter(self.tab_transactions)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(380, 0))
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_transaction = QGroupBox(self.frame)
        self.groupBox_transaction.setObjectName(u"groupBox_transaction")
        self.groupBox_transaction.setMinimumSize(QSize(0, 280))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_transaction)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_category = QLabel(self.groupBox_transaction)
        self.label_category.setObjectName(u"label_category")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_category.setFont(font)

        self.verticalLayout_5.addWidget(self.label_category)

        self.horizontalLayout_type = QHBoxLayout()
        self.horizontalLayout_type.setObjectName(u"horizontalLayout_type")
        self.radioButton_income = QRadioButton(self.groupBox_transaction)
        self.radioButton_income.setObjectName(u"radioButton_income")
        self.radioButton_income.setStyleSheet(u"QRadioButton {\n"
"                                          color: green;\n"
"                                          font-weight: bold;\n"
"                                          }")

        self.horizontalLayout_type.addWidget(self.radioButton_income)

        self.radioButton_expense = QRadioButton(self.groupBox_transaction)
        self.radioButton_expense.setObjectName(u"radioButton_expense")
        self.radioButton_expense.setChecked(True)
        self.radioButton_expense.setStyleSheet(u"QRadioButton {\n"
"                                          color: red;\n"
"                                          font-weight: bold;\n"
"                                          }")

        self.horizontalLayout_type.addWidget(self.radioButton_expense)


        self.verticalLayout_5.addLayout(self.horizontalLayout_type)

        self.horizontalLayout_amount = QHBoxLayout()
        self.horizontalLayout_amount.setObjectName(u"horizontalLayout_amount")
        self.doubleSpinBox_amount = QDoubleSpinBox(self.groupBox_transaction)
        self.doubleSpinBox_amount.setObjectName(u"doubleSpinBox_amount")
        self.doubleSpinBox_amount.setFont(font)
        self.doubleSpinBox_amount.setStyleSheet(u"QDoubleSpinBox {\n"
"                                          background-color: lightblue;\n"
"                                          }")
        self.doubleSpinBox_amount.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_amount.setMaximum(999999.989999999990687)
        self.doubleSpinBox_amount.setValue(100.000000000000000)

        self.horizontalLayout_amount.addWidget(self.doubleSpinBox_amount)

        self.label_currency = QLabel(self.groupBox_transaction)
        self.label_currency.setObjectName(u"label_currency")
        self.label_currency.setMaximumSize(QSize(61, 16777215))

        self.horizontalLayout_amount.addWidget(self.label_currency)


        self.verticalLayout_5.addLayout(self.horizontalLayout_amount)

        self.comboBox_category = QComboBox(self.groupBox_transaction)
        self.comboBox_category.setObjectName(u"comboBox_category")

        self.verticalLayout_5.addWidget(self.comboBox_category)

        self.lineEdit_description = QLineEdit(self.groupBox_transaction)
        self.lineEdit_description.setObjectName(u"lineEdit_description")

        self.verticalLayout_5.addWidget(self.lineEdit_description)

        self.horizontalLayout_date = QHBoxLayout()
        self.horizontalLayout_date.setObjectName(u"horizontalLayout_date")
        self.dateEdit = QDateEdit(self.groupBox_transaction)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setMinimumSize(QSize(191, 0))
        self.dateEdit.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_date.addWidget(self.dateEdit)

        self.pushButton_yesterday = QPushButton(self.groupBox_transaction)
        self.pushButton_yesterday.setObjectName(u"pushButton_yesterday")
        self.pushButton_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_date.addWidget(self.pushButton_yesterday)


        self.verticalLayout_5.addLayout(self.horizontalLayout_date)

        self.pushButton_add = QPushButton(self.groupBox_transaction)
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


        self.verticalLayout_3.addWidget(self.groupBox_transaction)

        self.groupBox_commands = QGroupBox(self.frame)
        self.groupBox_commands.setObjectName(u"groupBox_commands")
        self.groupBox_commands.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_commands)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_commands)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_refresh = QPushButton(self.groupBox_commands)
        self.pushButton_refresh.setObjectName(u"pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)

        self.pushButton_export_csv = QPushButton(self.groupBox_commands)
        self.pushButton_export_csv.setObjectName(u"pushButton_export_csv")
        self.pushButton_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_export_csv)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)


        self.verticalLayout_3.addWidget(self.groupBox_commands)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName(u"groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 201))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_filter_category = QLabel(self.groupBox_filter)
        self.label_filter_category.setObjectName(u"label_filter_category")
        self.label_filter_category.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_9.addWidget(self.label_filter_category)

        self.comboBox_filter_category = QComboBox(self.groupBox_filter)
        self.comboBox_filter_category.setObjectName(u"comboBox_filter_category")
        self.comboBox_filter_category.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_9.addWidget(self.comboBox_filter_category)


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

        self.groupBox_daily_balance = QGroupBox(self.frame)
        self.groupBox_daily_balance.setObjectName(u"groupBox_daily_balance")
        self.groupBox_daily_balance.setMinimumSize(QSize(0, 100))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_daily_balance)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_daily_balance = QLabel(self.groupBox_daily_balance)
        self.label_daily_balance.setObjectName(u"label_daily_balance")
        font1 = QFont()
        font1.setPointSize(24)
        font1.setBold(True)
        self.label_daily_balance.setFont(font1)
        self.label_daily_balance.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_daily_balance)


        self.verticalLayout_3.addWidget(self.groupBox_daily_balance)

        self.verticalSpacer = QSpacerItem(20, 143, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.frame)
        self.widget_middle = QWidget(self.splitter)
        self.widget_middle.setObjectName(u"widget_middle")
        self.verticalLayout = QVBoxLayout(self.widget_middle)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_categories = QLabel(self.widget_middle)
        self.label_categories.setObjectName(u"label_categories")

        self.verticalLayout.addWidget(self.label_categories)

        self.listView_categories = QListView(self.widget_middle)
        self.listView_categories.setObjectName(u"listView_categories")
        self.listView_categories.setMaximumSize(QSize(16777215, 16777215))
        self.listView_categories.setStyleSheet(u"QListView {\n"
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

        self.verticalLayout.addWidget(self.listView_categories)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_transactions = QTableView(self.splitter)
        self.tableView_transactions.setObjectName(u"tableView_transactions")
        self.splitter.addWidget(self.tableView_transactions)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_transactions, "")
        self.tab_categories = QWidget()
        self.tab_categories.setObjectName(u"tab_categories")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_categories)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.tableView_categories = QTableView(self.tab_categories)
        self.tableView_categories.setObjectName(u"tableView_categories")

        self.horizontalLayout_4.addWidget(self.tableView_categories)

        self.frame_2 = QFrame(self.tab_categories)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(300, 0))
        self.frame_2.setMaximumSize(QSize(300, 16777215))
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
        self.label_5.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_17.addWidget(self.label_5)

        self.lineEdit_category_name = QLineEdit(self.groupBox_2)
        self.lineEdit_category_name.setObjectName(u"lineEdit_category_name")
        self.lineEdit_category_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_17.addWidget(self.lineEdit_category_name)


        self.verticalLayout_10.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_18.addWidget(self.label_6)

        self.comboBox_category_type = QComboBox(self.groupBox_2)
        self.comboBox_category_type.addItem("")
        self.comboBox_category_type.addItem("")
        self.comboBox_category_type.setObjectName(u"comboBox_category_type")
        self.comboBox_category_type.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_18.addWidget(self.comboBox_category_type)


        self.verticalLayout_10.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_color = QHBoxLayout()
        self.horizontalLayout_color.setObjectName(u"horizontalLayout_color")
        self.label_color = QLabel(self.groupBox_2)
        self.label_color.setObjectName(u"label_color")
        self.label_color.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_color.addWidget(self.label_color)

        self.pushButton_color_picker = QPushButton(self.groupBox_2)
        self.pushButton_color_picker.setObjectName(u"pushButton_color_picker")
        self.pushButton_color_picker.setMinimumSize(QSize(170, 30))
        self.pushButton_color_picker.setStyleSheet(u"background-color: #4CAF50;")

        self.horizontalLayout_color.addWidget(self.pushButton_color_picker)


        self.verticalLayout_10.addLayout(self.horizontalLayout_color)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_4)

        self.pushButton_category_add = QPushButton(self.groupBox_2)
        self.pushButton_category_add.setObjectName(u"pushButton_category_add")

        self.horizontalLayout_19.addWidget(self.pushButton_category_add)


        self.verticalLayout_10.addLayout(self.horizontalLayout_19)


        self.verticalLayout_15.addWidget(self.groupBox_2)

        self.groupBox_7 = QGroupBox(self.frame_2)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.pushButton_categories_delete = QPushButton(self.groupBox_7)
        self.pushButton_categories_delete.setObjectName(u"pushButton_categories_delete")

        self.horizontalLayout_20.addWidget(self.pushButton_categories_delete)

        self.pushButton_categories_refresh = QPushButton(self.groupBox_7)
        self.pushButton_categories_refresh.setObjectName(u"pushButton_categories_refresh")

        self.horizontalLayout_20.addWidget(self.pushButton_categories_refresh)


        self.verticalLayout_11.addLayout(self.horizontalLayout_20)


        self.verticalLayout_15.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_2)


        self.horizontalLayout_4.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_categories, "")
        self.tab_budget = QWidget()
        self.tab_budget.setObjectName(u"tab_budget")
        self.horizontalLayout_budget = QHBoxLayout(self.tab_budget)
        self.horizontalLayout_budget.setObjectName(u"horizontalLayout_budget")
        self.tableView_budget = QTableView(self.tab_budget)
        self.tableView_budget.setObjectName(u"tableView_budget")

        self.horizontalLayout_budget.addWidget(self.tableView_budget)

        self.frame_budget = QFrame(self.tab_budget)
        self.frame_budget.setObjectName(u"frame_budget")
        self.frame_budget.setMinimumSize(QSize(300, 0))
        self.frame_budget.setMaximumSize(QSize(300, 16777215))
        self.frame_budget.setFrameShape(QFrame.StyledPanel)
        self.frame_budget.setFrameShadow(QFrame.Raised)
        self.verticalLayout_budget = QVBoxLayout(self.frame_budget)
        self.verticalLayout_budget.setObjectName(u"verticalLayout_budget")
        self.groupBox_budget_add = QGroupBox(self.frame_budget)
        self.groupBox_budget_add.setObjectName(u"groupBox_budget_add")
        self.verticalLayout_budget_add = QVBoxLayout(self.groupBox_budget_add)
        self.verticalLayout_budget_add.setObjectName(u"verticalLayout_budget_add")
        self.comboBox_budget_category = QComboBox(self.groupBox_budget_add)
        self.comboBox_budget_category.setObjectName(u"comboBox_budget_category")

        self.verticalLayout_budget_add.addWidget(self.comboBox_budget_category)

        self.doubleSpinBox_budget_amount = QDoubleSpinBox(self.groupBox_budget_add)
        self.doubleSpinBox_budget_amount.setObjectName(u"doubleSpinBox_budget_amount")
        self.doubleSpinBox_budget_amount.setMaximum(999999.989999999990687)
        self.doubleSpinBox_budget_amount.setValue(1000.000000000000000)

        self.verticalLayout_budget_add.addWidget(self.doubleSpinBox_budget_amount)

        self.comboBox_budget_period = QComboBox(self.groupBox_budget_add)
        self.comboBox_budget_period.addItem("")
        self.comboBox_budget_period.addItem("")
        self.comboBox_budget_period.addItem("")
        self.comboBox_budget_period.setObjectName(u"comboBox_budget_period")

        self.verticalLayout_budget_add.addWidget(self.comboBox_budget_period)

        self.pushButton_budget_add = QPushButton(self.groupBox_budget_add)
        self.pushButton_budget_add.setObjectName(u"pushButton_budget_add")

        self.verticalLayout_budget_add.addWidget(self.pushButton_budget_add)


        self.verticalLayout_budget.addWidget(self.groupBox_budget_add)

        self.groupBox_budget_commands = QGroupBox(self.frame_budget)
        self.groupBox_budget_commands.setObjectName(u"groupBox_budget_commands")
        self.verticalLayout_budget_commands = QVBoxLayout(self.groupBox_budget_commands)
        self.verticalLayout_budget_commands.setObjectName(u"verticalLayout_budget_commands")
        self.horizontalLayout_budget_commands = QHBoxLayout()
        self.horizontalLayout_budget_commands.setObjectName(u"horizontalLayout_budget_commands")
        self.pushButton_budget_delete = QPushButton(self.groupBox_budget_commands)
        self.pushButton_budget_delete.setObjectName(u"pushButton_budget_delete")

        self.horizontalLayout_budget_commands.addWidget(self.pushButton_budget_delete)

        self.pushButton_budget_refresh = QPushButton(self.groupBox_budget_commands)
        self.pushButton_budget_refresh.setObjectName(u"pushButton_budget_refresh")

        self.horizontalLayout_budget_commands.addWidget(self.pushButton_budget_refresh)


        self.verticalLayout_budget_commands.addLayout(self.horizontalLayout_budget_commands)


        self.verticalLayout_budget.addWidget(self.groupBox_budget_commands)

        self.verticalSpacer_budget = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_budget.addItem(self.verticalSpacer_budget)


        self.horizontalLayout_budget.addWidget(self.frame_budget)

        self.tabWidget.addTab(self.tab_budget, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName(u"tab_charts")
        self.verticalLayout_18 = QVBoxLayout(self.tab_charts)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.frame_charts_controls = QFrame(self.tab_charts)
        self.frame_charts_controls.setObjectName(u"frame_charts_controls")
        self.frame_charts_controls.setMaximumSize(QSize(16777215, 120))
        self.frame_charts_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_charts_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_charts_controls = QVBoxLayout(self.frame_charts_controls)
        self.verticalLayout_charts_controls.setObjectName(u"verticalLayout_charts_controls")
        self.horizontalLayout_charts_controls_1 = QHBoxLayout()
        self.horizontalLayout_charts_controls_1.setObjectName(u"horizontalLayout_charts_controls_1")
        self.label_chart_category = QLabel(self.frame_charts_controls)
        self.label_chart_category.setObjectName(u"label_chart_category")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_category)

        self.comboBox_chart_category = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_category.setObjectName(u"comboBox_chart_category")
        self.comboBox_chart_category.setMinimumSize(QSize(201, 0))

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_category)

        self.label_chart_type = QLabel(self.frame_charts_controls)
        self.label_chart_type.setObjectName(u"label_chart_type")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_type)

        self.comboBox_chart_type = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.setObjectName(u"comboBox_chart_type")
        self.comboBox_chart_type.setMinimumSize(QSize(151, 0))

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_type)

        self.label_chart_period = QLabel(self.frame_charts_controls)
        self.label_chart_period.setObjectName(u"label_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_period)

        self.comboBox_chart_period = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.setObjectName(u"comboBox_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_period)

        self.pushButton_update_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_update_chart.setObjectName(u"pushButton_update_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_update_chart)

        self.horizontalSpacer_charts = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_1.addItem(self.horizontalSpacer_charts)

        self.pushButton_pie_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_pie_chart.setObjectName(u"pushButton_pie_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_pie_chart)

        self.pushButton_balance_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_balance_chart.setObjectName(u"pushButton_balance_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_balance_chart)


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


        self.verticalLayout_charts_controls.addLayout(self.horizontalLayout_charts_controls_2)


        self.verticalLayout_18.addWidget(self.frame_charts_controls)

        self.scrollArea_charts = QScrollArea(self.tab_charts)
        self.scrollArea_charts.setObjectName(u"scrollArea_charts")
        self.scrollArea_charts.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts = QWidget()
        self.scrollAreaWidgetContents_charts.setObjectName(u"scrollAreaWidgetContents_charts")
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1356, 775))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName(u"verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_18.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_reports = QWidget()
        self.tab_reports.setObjectName(u"tab_reports")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_reports)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.tableView_reports = QTableView(self.tab_reports)
        self.tableView_reports.setObjectName(u"tableView_reports")

        self.horizontalLayout_6.addWidget(self.tableView_reports)

        self.frame_5 = QFrame(self.tab_reports)
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
        self.comboBox_report_type = QComboBox(self.groupBox_10)
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.setObjectName(u"comboBox_report_type")

        self.verticalLayout_19.addWidget(self.comboBox_report_type)

        self.pushButton_generate_report = QPushButton(self.groupBox_10)
        self.pushButton_generate_report.setObjectName(u"pushButton_generate_report")

        self.verticalLayout_19.addWidget(self.pushButton_generate_report)


        self.verticalLayout_16.addWidget(self.groupBox_10)

        self.groupBox_summary = QGroupBox(self.frame_5)
        self.groupBox_summary.setObjectName(u"groupBox_summary")
        self.verticalLayout_summary = QVBoxLayout(self.groupBox_summary)
        self.verticalLayout_summary.setObjectName(u"verticalLayout_summary")
        self.label_total_income = QLabel(self.groupBox_summary)
        self.label_total_income.setObjectName(u"label_total_income")
        self.label_total_income.setStyleSheet(u"color: green; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_income)

        self.label_total_expenses = QLabel(self.groupBox_summary)
        self.label_total_expenses.setObjectName(u"label_total_expenses")
        self.label_total_expenses.setStyleSheet(u"color: red; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_expenses)

        self.label_net_balance = QLabel(self.groupBox_summary)
        self.label_net_balance.setObjectName(u"label_net_balance")
        self.label_net_balance.setStyleSheet(u"font-weight: bold; font-size: 14px;")

        self.verticalLayout_summary.addWidget(self.label_net_balance)


        self.verticalLayout_16.addWidget(self.groupBox_summary)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)


        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_reports, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1400, 21))
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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Finance Tracker", None))
        self.groupBox_transaction.setTitle(QCoreApplication.translate("MainWindow", u"Transaction Details", None))
        self.label_category.setText(QCoreApplication.translate("MainWindow", u"Select Category", None))
        self.radioButton_income.setText(QCoreApplication.translate("MainWindow", u"Income", None))
        self.radioButton_expense.setText(QCoreApplication.translate("MainWindow", u"Expense", None))
        self.label_currency.setText(QCoreApplication.translate("MainWindow", u"USD", None))
        self.lineEdit_description.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Description (optional)", None))
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", u"Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", u"Add Transaction", None))
        self.groupBox_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", u"Export CSV", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.label_filter_category.setText(QCoreApplication.translate("MainWindow", u"Category:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", u"to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", u"Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", u"Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", u"Apply Filter", None))
        self.groupBox_daily_balance.setTitle(QCoreApplication.translate("MainWindow", u"Today's Balance", None))
        self.label_daily_balance.setText(QCoreApplication.translate("MainWindow", u"$0.00", None))
        self.label_categories.setText(QCoreApplication.translate("MainWindow", u"Categories:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_transactions), QCoreApplication.translate("MainWindow", u"Transactions", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Add New Category", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.comboBox_category_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Expense", None))
        self.comboBox_category_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Income", None))

        self.label_color.setText(QCoreApplication.translate("MainWindow", u"Color:", None))
        self.pushButton_color_picker.setText(QCoreApplication.translate("MainWindow", u"Choose Color", None))
        self.pushButton_category_add.setText(QCoreApplication.translate("MainWindow", u"Add Category", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_categories_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_categories_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_categories), QCoreApplication.translate("MainWindow", u"Categories", None))
        self.groupBox_budget_add.setTitle(QCoreApplication.translate("MainWindow", u"Set Budget", None))
        self.comboBox_budget_period.setItemText(0, QCoreApplication.translate("MainWindow", u"Monthly", None))
        self.comboBox_budget_period.setItemText(1, QCoreApplication.translate("MainWindow", u"Weekly", None))
        self.comboBox_budget_period.setItemText(2, QCoreApplication.translate("MainWindow", u"Daily", None))

        self.pushButton_budget_add.setText(QCoreApplication.translate("MainWindow", u"Set Budget", None))
        self.groupBox_budget_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_budget_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_budget_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_budget), QCoreApplication.translate("MainWindow", u"Budget", None))
        self.label_chart_category.setText(QCoreApplication.translate("MainWindow", u"Category:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.comboBox_chart_type.setItemText(0, QCoreApplication.translate("MainWindow", u"All", None))
        self.comboBox_chart_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Income", None))
        self.comboBox_chart_type.setItemText(2, QCoreApplication.translate("MainWindow", u"Expense", None))

        self.label_chart_period.setText(QCoreApplication.translate("MainWindow", u"Period:", None))
        self.comboBox_chart_period.setItemText(0, QCoreApplication.translate("MainWindow", u"Days", None))
        self.comboBox_chart_period.setItemText(1, QCoreApplication.translate("MainWindow", u"Months", None))
        self.comboBox_chart_period.setItemText(2, QCoreApplication.translate("MainWindow", u"Years", None))

        self.pushButton_update_chart.setText(QCoreApplication.translate("MainWindow", u"Update Chart", None))
        self.pushButton_pie_chart.setText(QCoreApplication.translate("MainWindow", u"Pie Chart", None))
        self.pushButton_balance_chart.setText(QCoreApplication.translate("MainWindow", u"Balance Chart", None))
        self.label_chart_from.setText(QCoreApplication.translate("MainWindow", u"From:", None))
        self.dateEdit_chart_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_chart_to.setText(QCoreApplication.translate("MainWindow", u"To:", None))
        self.dateEdit_chart_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_chart_last_month.setText(QCoreApplication.translate("MainWindow", u"Last Month", None))
        self.pushButton_chart_last_year.setText(QCoreApplication.translate("MainWindow", u"Last Year", None))
        self.pushButton_chart_all_time.setText(QCoreApplication.translate("MainWindow", u"All Time", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_charts), QCoreApplication.translate("MainWindow", u"Charts", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"Generate Report", None))
        self.comboBox_report_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Monthly Summary", None))
        self.comboBox_report_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Category Analysis", None))
        self.comboBox_report_type.setItemText(2, QCoreApplication.translate("MainWindow", u"Budget vs Actual", None))
        self.comboBox_report_type.setItemText(3, QCoreApplication.translate("MainWindow", u"Income vs Expenses", None))

        self.pushButton_generate_report.setText(QCoreApplication.translate("MainWindow", u"Generate Report", None))
        self.groupBox_summary.setTitle(QCoreApplication.translate("MainWindow", u"Quick Summary", None))
        self.label_total_income.setText(QCoreApplication.translate("MainWindow", u"Total Income: $0.00", None))
        self.label_total_expenses.setText(QCoreApplication.translate("MainWindow", u"Total Expenses: $0.00", None))
        self.label_net_balance.setText(QCoreApplication.translate("MainWindow", u"Net Balance: $0.00", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MainWindow", u"Reports", None))
    # retranslateUi

