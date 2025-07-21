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
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_transaction = QGroupBox(self.frame)
        self.groupBox_transaction.setObjectName(u"groupBox_transaction")
        self.groupBox_transaction.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_transaction)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_category_now = QLabel(self.groupBox_transaction)
        self.label_category_now.setObjectName(u"label_category_now")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_category_now.setFont(font)
        self.label_category_now.setFocusPolicy(Qt.NoFocus)

        self.verticalLayout_3.addWidget(self.label_category_now)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEdit_description = QLineEdit(self.groupBox_transaction)
        self.lineEdit_description.setObjectName(u"lineEdit_description")
        font1 = QFont()
        font1.setPointSize(12)
        self.lineEdit_description.setFont(font1)

        self.horizontalLayout_2.addWidget(self.lineEdit_description)

        self.pushButton_description_clear = QPushButton(self.groupBox_transaction)
        self.pushButton_description_clear.setObjectName(u"pushButton_description_clear")
        self.pushButton_description_clear.setMaximumSize(QSize(32, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_description_clear)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_amount = QHBoxLayout()
        self.horizontalLayout_amount.setObjectName(u"horizontalLayout_amount")
        self.doubleSpinBox_amount = QDoubleSpinBox(self.groupBox_transaction)
        self.doubleSpinBox_amount.setObjectName(u"doubleSpinBox_amount")
        self.doubleSpinBox_amount.setFont(font)
        self.doubleSpinBox_amount.setStyleSheet(u"QDoubleSpinBox {\n"
"                                          background-color: #C1ECDD;\n"
"                                          }")
        self.doubleSpinBox_amount.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.doubleSpinBox_amount.setMaximum(999999.989999999990687)
        self.doubleSpinBox_amount.setValue(100.000000000000000)

        self.horizontalLayout_amount.addWidget(self.doubleSpinBox_amount)

        self.comboBox_currency = QComboBox(self.groupBox_transaction)
        self.comboBox_currency.setObjectName(u"comboBox_currency")
        self.comboBox_currency.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_amount.addWidget(self.comboBox_currency)


        self.verticalLayout_3.addLayout(self.horizontalLayout_amount)

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


        self.verticalLayout_3.addLayout(self.horizontalLayout_date)

        self.pushButton_add = QPushButton(self.groupBox_transaction)
        self.pushButton_add.setObjectName(u"pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 41))
        self.pushButton_add.setFont(font)
        self.pushButton_add.setStyleSheet(u"QPushButton {\n"
"                                      background-color: #C1ECDD;\n"
"                                      border: 1px solid #7DB68A;\n"
"                                      border-radius: 4px;\n"
"                                      }\n"
"                                      QPushButton:hover {\n"
"                                      background-color: #D1F5E8;\n"
"                                      }\n"
"                                      QPushButton:pressed {\n"
"                                      background-color: #A8E0C7;\n"
"                                      }")

        self.verticalLayout_3.addWidget(self.pushButton_add)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_tag = QLabel(self.groupBox_transaction)
        self.label_tag.setObjectName(u"label_tag")
        self.label_tag.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.label_tag)

        self.lineEdit_tag = QLineEdit(self.groupBox_transaction)
        self.lineEdit_tag.setObjectName(u"lineEdit_tag")

        self.horizontalLayout_3.addWidget(self.lineEdit_tag)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.verticalLayout_5.addWidget(self.groupBox_transaction)

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

        self.pushButton_show_all_records = QPushButton(self.groupBox_commands)
        self.pushButton_show_all_records.setObjectName(u"pushButton_show_all_records")

        self.horizontalLayout_8.addWidget(self.pushButton_show_all_records)

        self.pushButton_refresh = QPushButton(self.groupBox_commands)
        self.pushButton_refresh.setObjectName(u"pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)


        self.verticalLayout_5.addWidget(self.groupBox_commands)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName(u"groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.radioButton = QRadioButton(self.groupBox_filter)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setChecked(True)

        self.horizontalLayout_5.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.groupBox_filter)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.horizontalLayout_5.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.groupBox_filter)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.horizontalLayout_5.addWidget(self.radioButton_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

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

        self.horizontalLayout_currency_filter = QHBoxLayout()
        self.horizontalLayout_currency_filter.setObjectName(u"horizontalLayout_currency_filter")
        self.label_filter_currency = QLabel(self.groupBox_filter)
        self.label_filter_currency.setObjectName(u"label_filter_currency")
        self.label_filter_currency.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_filter.addWidget(self.label_filter_currency)

        self.comboBox_filter_currency = QComboBox(self.groupBox_filter)
        self.comboBox_filter_currency.setObjectName(u"comboBox_filter_currency")
        self.comboBox_filter_currency.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_filter.addWidget(self.comboBox_filter_currency)


        self.verticalLayout_4.addLayout(self.horizontalLayout_currency_filter)

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
        self.pushButton_clear_filter.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_7.addWidget(self.pushButton_clear_filter)

        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName(u"pushButton_apply_filter")
        self.pushButton_apply_filter.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_7.addWidget(self.pushButton_apply_filter)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)


        self.verticalLayout_5.addWidget(self.groupBox_filter)

        self.groupBox_today_expense = QGroupBox(self.frame)
        self.groupBox_today_expense.setObjectName(u"groupBox_today_expense")
        self.groupBox_today_expense.setMinimumSize(QSize(0, 100))
        self.verticalLayout_20 = QVBoxLayout(self.groupBox_today_expense)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.label_today_expense = QLabel(self.groupBox_today_expense)
        self.label_today_expense.setObjectName(u"label_today_expense")
        font2 = QFont()
        font2.setPointSize(20)
        font2.setBold(True)
        self.label_today_expense.setFont(font2)
        self.label_today_expense.setAlignment(Qt.AlignCenter)

        self.verticalLayout_20.addWidget(self.label_today_expense)


        self.verticalLayout_5.addWidget(self.groupBox_today_expense)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

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
"                                border: 2px solid #7DB68A;\n"
"                                border-radius: 4px;\n"
"                                background-color: white;\n"
"                                }\n"
"                                QListView::item {\n"
"                                padding: 4px;\n"
"                                border-bottom: 1px solid #e0e0e0;\n"
"                                }\n"
"                                QListView::item:selected {\n"
"                                background-color: #E8F5E8;\n"
"                                color: black;\n"
"                                }\n"
"                                QListView::item:hover {\n"
"                                background-color: #F0FAF0;\n"
"                                }")

        self.verticalLayout.addWidget(self.listView_categories)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_transactions = QTableView(self.splitter)
        self.tableView_transactions.setObjectName(u"tableView_transactions")
        self.splitter.addWidget(self.tableView_transactions)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_transactions, "")
        self.tab_accounts = QWidget()
        self.tab_accounts.setObjectName(u"tab_accounts")
        self.horizontalLayout_accounts = QHBoxLayout(self.tab_accounts)
        self.horizontalLayout_accounts.setObjectName(u"horizontalLayout_accounts")
        self.tableView_accounts = QTableView(self.tab_accounts)
        self.tableView_accounts.setObjectName(u"tableView_accounts")

        self.horizontalLayout_accounts.addWidget(self.tableView_accounts)

        self.frame_accounts = QFrame(self.tab_accounts)
        self.frame_accounts.setObjectName(u"frame_accounts")
        self.frame_accounts.setMinimumSize(QSize(300, 0))
        self.frame_accounts.setMaximumSize(QSize(300, 16777215))
        self.frame_accounts.setFrameShape(QFrame.StyledPanel)
        self.frame_accounts.setFrameShadow(QFrame.Raised)
        self.verticalLayout_accounts = QVBoxLayout(self.frame_accounts)
        self.verticalLayout_accounts.setObjectName(u"verticalLayout_accounts")
        self.groupBox_add_account = QGroupBox(self.frame_accounts)
        self.groupBox_add_account.setObjectName(u"groupBox_add_account")
        self.verticalLayout_add_account = QVBoxLayout(self.groupBox_add_account)
        self.verticalLayout_add_account.setObjectName(u"verticalLayout_add_account")
        self.horizontalLayout_account_name = QHBoxLayout()
        self.horizontalLayout_account_name.setObjectName(u"horizontalLayout_account_name")
        self.label_account_name = QLabel(self.groupBox_add_account)
        self.label_account_name.setObjectName(u"label_account_name")
        self.label_account_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_name.addWidget(self.label_account_name)

        self.lineEdit_account_name = QLineEdit(self.groupBox_add_account)
        self.lineEdit_account_name.setObjectName(u"lineEdit_account_name")
        self.lineEdit_account_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_account_name.addWidget(self.lineEdit_account_name)


        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_name)

        self.horizontalLayout_account_currency = QHBoxLayout()
        self.horizontalLayout_account_currency.setObjectName(u"horizontalLayout_account_currency")
        self.label_account_currency = QLabel(self.groupBox_add_account)
        self.label_account_currency.setObjectName(u"label_account_currency")
        self.label_account_currency.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_currency.addWidget(self.label_account_currency)

        self.comboBox_account_currency = QComboBox(self.groupBox_add_account)
        self.comboBox_account_currency.setObjectName(u"comboBox_account_currency")
        self.comboBox_account_currency.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_account_currency.addWidget(self.comboBox_account_currency)


        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_currency)

        self.horizontalLayout_account_balance = QHBoxLayout()
        self.horizontalLayout_account_balance.setObjectName(u"horizontalLayout_account_balance")
        self.label_account_balance = QLabel(self.groupBox_add_account)
        self.label_account_balance.setObjectName(u"label_account_balance")
        self.label_account_balance.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_balance.addWidget(self.label_account_balance)

        self.doubleSpinBox_account_balance = QDoubleSpinBox(self.groupBox_add_account)
        self.doubleSpinBox_account_balance.setObjectName(u"doubleSpinBox_account_balance")
        self.doubleSpinBox_account_balance.setMinimumSize(QSize(170, 0))
        self.doubleSpinBox_account_balance.setMaximum(999999.989999999990687)
        self.doubleSpinBox_account_balance.setValue(0.000000000000000)

        self.horizontalLayout_account_balance.addWidget(self.doubleSpinBox_account_balance)


        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_balance)

        self.horizontalLayout_account_flags = QHBoxLayout()
        self.horizontalLayout_account_flags.setObjectName(u"horizontalLayout_account_flags")
        self.checkBox_is_liquid = QCheckBox(self.groupBox_add_account)
        self.checkBox_is_liquid.setObjectName(u"checkBox_is_liquid")
        self.checkBox_is_liquid.setChecked(True)

        self.horizontalLayout_account_flags.addWidget(self.checkBox_is_liquid)

        self.checkBox_is_cash = QCheckBox(self.groupBox_add_account)
        self.checkBox_is_cash.setObjectName(u"checkBox_is_cash")

        self.horizontalLayout_account_flags.addWidget(self.checkBox_is_cash)


        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_flags)

        self.horizontalLayout_account_add = QHBoxLayout()
        self.horizontalLayout_account_add.setObjectName(u"horizontalLayout_account_add")
        self.horizontalSpacer_account = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_account_add.addItem(self.horizontalSpacer_account)

        self.pushButton_account_add = QPushButton(self.groupBox_add_account)
        self.pushButton_account_add.setObjectName(u"pushButton_account_add")

        self.horizontalLayout_account_add.addWidget(self.pushButton_account_add)


        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_add)


        self.verticalLayout_accounts.addWidget(self.groupBox_add_account)

        self.groupBox_account_commands = QGroupBox(self.frame_accounts)
        self.groupBox_account_commands.setObjectName(u"groupBox_account_commands")
        self.verticalLayout_account_commands = QVBoxLayout(self.groupBox_account_commands)
        self.verticalLayout_account_commands.setObjectName(u"verticalLayout_account_commands")
        self.horizontalLayout_account_commands = QHBoxLayout()
        self.horizontalLayout_account_commands.setObjectName(u"horizontalLayout_account_commands")
        self.pushButton_accounts_delete = QPushButton(self.groupBox_account_commands)
        self.pushButton_accounts_delete.setObjectName(u"pushButton_accounts_delete")

        self.horizontalLayout_account_commands.addWidget(self.pushButton_accounts_delete)

        self.pushButton_accounts_refresh = QPushButton(self.groupBox_account_commands)
        self.pushButton_accounts_refresh.setObjectName(u"pushButton_accounts_refresh")

        self.horizontalLayout_account_commands.addWidget(self.pushButton_accounts_refresh)


        self.verticalLayout_account_commands.addLayout(self.horizontalLayout_account_commands)


        self.verticalLayout_accounts.addWidget(self.groupBox_account_commands)

        self.verticalSpacer_accounts = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_accounts.addItem(self.verticalSpacer_accounts)


        self.horizontalLayout_accounts.addWidget(self.frame_accounts)

        self.tabWidget.addTab(self.tab_accounts, "")
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
        self.tab_currencies = QWidget()
        self.tab_currencies.setObjectName(u"tab_currencies")
        self.horizontalLayout_currencies = QHBoxLayout(self.tab_currencies)
        self.horizontalLayout_currencies.setObjectName(u"horizontalLayout_currencies")
        self.tableView_currencies = QTableView(self.tab_currencies)
        self.tableView_currencies.setObjectName(u"tableView_currencies")

        self.horizontalLayout_currencies.addWidget(self.tableView_currencies)

        self.frame_currencies = QFrame(self.tab_currencies)
        self.frame_currencies.setObjectName(u"frame_currencies")
        self.frame_currencies.setMinimumSize(QSize(300, 0))
        self.frame_currencies.setMaximumSize(QSize(300, 16777215))
        self.frame_currencies.setFrameShape(QFrame.StyledPanel)
        self.frame_currencies.setFrameShadow(QFrame.Raised)
        self.verticalLayout_currencies = QVBoxLayout(self.frame_currencies)
        self.verticalLayout_currencies.setObjectName(u"verticalLayout_currencies")
        self.groupBox_add_currency = QGroupBox(self.frame_currencies)
        self.groupBox_add_currency.setObjectName(u"groupBox_add_currency")
        self.verticalLayout_add_currency = QVBoxLayout(self.groupBox_add_currency)
        self.verticalLayout_add_currency.setObjectName(u"verticalLayout_add_currency")
        self.horizontalLayout_currency_code = QHBoxLayout()
        self.horizontalLayout_currency_code.setObjectName(u"horizontalLayout_currency_code")
        self.label_currency_code = QLabel(self.groupBox_add_currency)
        self.label_currency_code.setObjectName(u"label_currency_code")
        self.label_currency_code.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_code.addWidget(self.label_currency_code)

        self.lineEdit_currency_code = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_code.setObjectName(u"lineEdit_currency_code")
        self.lineEdit_currency_code.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_code.addWidget(self.lineEdit_currency_code)


        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_code)

        self.horizontalLayout_currency_name = QHBoxLayout()
        self.horizontalLayout_currency_name.setObjectName(u"horizontalLayout_currency_name")
        self.label_currency_name = QLabel(self.groupBox_add_currency)
        self.label_currency_name.setObjectName(u"label_currency_name")
        self.label_currency_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_name.addWidget(self.label_currency_name)

        self.lineEdit_currency_name = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_name.setObjectName(u"lineEdit_currency_name")
        self.lineEdit_currency_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_name.addWidget(self.lineEdit_currency_name)


        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_name)

        self.horizontalLayout_currency_symbol = QHBoxLayout()
        self.horizontalLayout_currency_symbol.setObjectName(u"horizontalLayout_currency_symbol")
        self.label_currency_symbol = QLabel(self.groupBox_add_currency)
        self.label_currency_symbol.setObjectName(u"label_currency_symbol")
        self.label_currency_symbol.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.label_currency_symbol)

        self.lineEdit_currency_symbol = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_symbol.setObjectName(u"lineEdit_currency_symbol")
        self.lineEdit_currency_symbol.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.lineEdit_currency_symbol)


        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_symbol)

        self.horizontalLayout_currency_add = QHBoxLayout()
        self.horizontalLayout_currency_add.setObjectName(u"horizontalLayout_currency_add")
        self.horizontalSpacer_currency = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_currency_add.addItem(self.horizontalSpacer_currency)

        self.pushButton_currency_add = QPushButton(self.groupBox_add_currency)
        self.pushButton_currency_add.setObjectName(u"pushButton_currency_add")

        self.horizontalLayout_currency_add.addWidget(self.pushButton_currency_add)


        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_add)


        self.verticalLayout_currencies.addWidget(self.groupBox_add_currency)

        self.groupBox_default_currency = QGroupBox(self.frame_currencies)
        self.groupBox_default_currency.setObjectName(u"groupBox_default_currency")
        self.verticalLayout_default_currency = QVBoxLayout(self.groupBox_default_currency)
        self.verticalLayout_default_currency.setObjectName(u"verticalLayout_default_currency")
        self.horizontalLayout_default_currency = QHBoxLayout()
        self.horizontalLayout_default_currency.setObjectName(u"horizontalLayout_default_currency")
        self.comboBox_default_currency = QComboBox(self.groupBox_default_currency)
        self.comboBox_default_currency.setObjectName(u"comboBox_default_currency")
        self.comboBox_default_currency.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_default_currency.addWidget(self.comboBox_default_currency)

        self.pushButton_set_default_currency = QPushButton(self.groupBox_default_currency)
        self.pushButton_set_default_currency.setObjectName(u"pushButton_set_default_currency")

        self.horizontalLayout_default_currency.addWidget(self.pushButton_set_default_currency)


        self.verticalLayout_default_currency.addLayout(self.horizontalLayout_default_currency)


        self.verticalLayout_currencies.addWidget(self.groupBox_default_currency)

        self.groupBox_currency_commands = QGroupBox(self.frame_currencies)
        self.groupBox_currency_commands.setObjectName(u"groupBox_currency_commands")
        self.verticalLayout_currency_commands = QVBoxLayout(self.groupBox_currency_commands)
        self.verticalLayout_currency_commands.setObjectName(u"verticalLayout_currency_commands")
        self.horizontalLayout_currency_commands = QHBoxLayout()
        self.horizontalLayout_currency_commands.setObjectName(u"horizontalLayout_currency_commands")
        self.pushButton_currencies_delete = QPushButton(self.groupBox_currency_commands)
        self.pushButton_currencies_delete.setObjectName(u"pushButton_currencies_delete")

        self.horizontalLayout_currency_commands.addWidget(self.pushButton_currencies_delete)

        self.pushButton_currencies_refresh = QPushButton(self.groupBox_currency_commands)
        self.pushButton_currencies_refresh.setObjectName(u"pushButton_currencies_refresh")

        self.horizontalLayout_currency_commands.addWidget(self.pushButton_currencies_refresh)


        self.verticalLayout_currency_commands.addLayout(self.horizontalLayout_currency_commands)


        self.verticalLayout_currencies.addWidget(self.groupBox_currency_commands)

        self.verticalSpacer_currencies = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_currencies.addItem(self.verticalSpacer_currencies)


        self.horizontalLayout_currencies.addWidget(self.frame_currencies)

        self.tabWidget.addTab(self.tab_currencies, "")
        self.tab_exchange = QWidget()
        self.tab_exchange.setObjectName(u"tab_exchange")
        self.horizontalLayout_exchange = QHBoxLayout(self.tab_exchange)
        self.horizontalLayout_exchange.setObjectName(u"horizontalLayout_exchange")
        self.tableView_exchange = QTableView(self.tab_exchange)
        self.tableView_exchange.setObjectName(u"tableView_exchange")

        self.horizontalLayout_exchange.addWidget(self.tableView_exchange)

        self.frame_exchange = QFrame(self.tab_exchange)
        self.frame_exchange.setObjectName(u"frame_exchange")
        self.frame_exchange.setMinimumSize(QSize(350, 0))
        self.frame_exchange.setMaximumSize(QSize(350, 16777215))
        self.frame_exchange.setFrameShape(QFrame.StyledPanel)
        self.frame_exchange.setFrameShadow(QFrame.Raised)
        self.verticalLayout_exchange = QVBoxLayout(self.frame_exchange)
        self.verticalLayout_exchange.setObjectName(u"verticalLayout_exchange")
        self.groupBox_exchange_operation = QGroupBox(self.frame_exchange)
        self.groupBox_exchange_operation.setObjectName(u"groupBox_exchange_operation")
        self.verticalLayout_exchange_operation = QVBoxLayout(self.groupBox_exchange_operation)
        self.verticalLayout_exchange_operation.setObjectName(u"verticalLayout_exchange_operation")
        self.horizontalLayout_exchange_from = QHBoxLayout()
        self.horizontalLayout_exchange_from.setObjectName(u"horizontalLayout_exchange_from")
        self.label_exchange_from = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_from.setObjectName(u"label_exchange_from")
        self.label_exchange_from.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_from.addWidget(self.label_exchange_from)

        self.comboBox_exchange_from = QComboBox(self.groupBox_exchange_operation)
        self.comboBox_exchange_from.setObjectName(u"comboBox_exchange_from")
        self.comboBox_exchange_from.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_from.addWidget(self.comboBox_exchange_from)

        self.doubleSpinBox_exchange_from = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_from.setObjectName(u"doubleSpinBox_exchange_from")
        self.doubleSpinBox_exchange_from.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_from.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_from.setValue(100.000000000000000)

        self.horizontalLayout_exchange_from.addWidget(self.doubleSpinBox_exchange_from)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_from)

        self.horizontalLayout_exchange_to = QHBoxLayout()
        self.horizontalLayout_exchange_to.setObjectName(u"horizontalLayout_exchange_to")
        self.label_exchange_to = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_to.setObjectName(u"label_exchange_to")
        self.label_exchange_to.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_to.addWidget(self.label_exchange_to)

        self.comboBox_exchange_to = QComboBox(self.groupBox_exchange_operation)
        self.comboBox_exchange_to.setObjectName(u"comboBox_exchange_to")
        self.comboBox_exchange_to.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_to.addWidget(self.comboBox_exchange_to)

        self.doubleSpinBox_exchange_to = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_to.setObjectName(u"doubleSpinBox_exchange_to")
        self.doubleSpinBox_exchange_to.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_to.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_to.setValue(73.500000000000000)

        self.horizontalLayout_exchange_to.addWidget(self.doubleSpinBox_exchange_to)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_to)

        self.horizontalLayout_exchange_rate = QHBoxLayout()
        self.horizontalLayout_exchange_rate.setObjectName(u"horizontalLayout_exchange_rate")
        self.label_exchange_rate = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_rate.setObjectName(u"label_exchange_rate")
        self.label_exchange_rate.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_rate.addWidget(self.label_exchange_rate)

        self.doubleSpinBox_exchange_rate = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_rate.setObjectName(u"doubleSpinBox_exchange_rate")
        self.doubleSpinBox_exchange_rate.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_rate.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_rate.setValue(73.500000000000000)

        self.horizontalLayout_exchange_rate.addWidget(self.doubleSpinBox_exchange_rate)

        self.pushButton_calculate_exchange = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_calculate_exchange.setObjectName(u"pushButton_calculate_exchange")
        self.pushButton_calculate_exchange.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_rate.addWidget(self.pushButton_calculate_exchange)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_rate)

        self.horizontalLayout_exchange_fee = QHBoxLayout()
        self.horizontalLayout_exchange_fee.setObjectName(u"horizontalLayout_exchange_fee")
        self.label_exchange_fee = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_fee.setObjectName(u"label_exchange_fee")
        self.label_exchange_fee.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_fee.addWidget(self.label_exchange_fee)

        self.doubleSpinBox_exchange_fee = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_fee.setObjectName(u"doubleSpinBox_exchange_fee")
        self.doubleSpinBox_exchange_fee.setMinimumSize(QSize(260, 0))
        self.doubleSpinBox_exchange_fee.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_fee.setValue(0.000000000000000)

        self.horizontalLayout_exchange_fee.addWidget(self.doubleSpinBox_exchange_fee)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_fee)

        self.horizontalLayout_exchange_description = QHBoxLayout()
        self.horizontalLayout_exchange_description.setObjectName(u"horizontalLayout_exchange_description")
        self.label_exchange_description = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_description.setObjectName(u"label_exchange_description")
        self.label_exchange_description.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_description.addWidget(self.label_exchange_description)

        self.lineEdit_exchange_description = QLineEdit(self.groupBox_exchange_operation)
        self.lineEdit_exchange_description.setObjectName(u"lineEdit_exchange_description")
        self.lineEdit_exchange_description.setMinimumSize(QSize(260, 0))

        self.horizontalLayout_exchange_description.addWidget(self.lineEdit_exchange_description)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_description)

        self.horizontalLayout_exchange_date = QHBoxLayout()
        self.horizontalLayout_exchange_date.setObjectName(u"horizontalLayout_exchange_date")
        self.label_exchange_date = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_date.setObjectName(u"label_exchange_date")
        self.label_exchange_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_date.addWidget(self.label_exchange_date)

        self.dateEdit_exchange = QDateEdit(self.groupBox_exchange_operation)
        self.dateEdit_exchange.setObjectName(u"dateEdit_exchange")
        self.dateEdit_exchange.setMinimumSize(QSize(151, 0))
        self.dateEdit_exchange.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit_exchange.setCalendarPopup(True)

        self.horizontalLayout_exchange_date.addWidget(self.dateEdit_exchange)

        self.pushButton_exchange_yesterday = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_exchange_yesterday.setObjectName(u"pushButton_exchange_yesterday")
        self.pushButton_exchange_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_date.addWidget(self.pushButton_exchange_yesterday)


        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_date)

        self.pushButton_exchange_add = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_exchange_add.setObjectName(u"pushButton_exchange_add")
        self.pushButton_exchange_add.setMinimumSize(QSize(0, 41))
        self.pushButton_exchange_add.setFont(font)
        self.pushButton_exchange_add.setStyleSheet(u"QPushButton {\n"
"                                    background-color: #C1ECDD;\n"
"                                    border: 1px solid #7DB68A;\n"
"                                    border-radius: 4px;\n"
"                                    }\n"
"                                    QPushButton:hover {\n"
"                                    background-color: #D1F5E8;\n"
"                                    }\n"
"                                    QPushButton:pressed {\n"
"                                    background-color: #A8E0C7;\n"
"                                    }")

        self.verticalLayout_exchange_operation.addWidget(self.pushButton_exchange_add)


        self.verticalLayout_exchange.addWidget(self.groupBox_exchange_operation)

        self.groupBox_exchange_commands = QGroupBox(self.frame_exchange)
        self.groupBox_exchange_commands.setObjectName(u"groupBox_exchange_commands")
        self.verticalLayout_exchange_commands = QVBoxLayout(self.groupBox_exchange_commands)
        self.verticalLayout_exchange_commands.setObjectName(u"verticalLayout_exchange_commands")
        self.horizontalLayout_exchange_commands = QHBoxLayout()
        self.horizontalLayout_exchange_commands.setObjectName(u"horizontalLayout_exchange_commands")
        self.pushButton_exchange_delete = QPushButton(self.groupBox_exchange_commands)
        self.pushButton_exchange_delete.setObjectName(u"pushButton_exchange_delete")

        self.horizontalLayout_exchange_commands.addWidget(self.pushButton_exchange_delete)

        self.pushButton_exchange_refresh = QPushButton(self.groupBox_exchange_commands)
        self.pushButton_exchange_refresh.setObjectName(u"pushButton_exchange_refresh")

        self.horizontalLayout_exchange_commands.addWidget(self.pushButton_exchange_refresh)


        self.verticalLayout_exchange_commands.addLayout(self.horizontalLayout_exchange_commands)


        self.verticalLayout_exchange.addWidget(self.groupBox_exchange_commands)

        self.verticalSpacer_exchange = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_exchange.addItem(self.verticalSpacer_exchange)


        self.horizontalLayout_exchange.addWidget(self.frame_exchange)

        self.tabWidget.addTab(self.tab_exchange, "")
        self.tab_exchange_rates = QWidget()
        self.tab_exchange_rates.setObjectName(u"tab_exchange_rates")
        self.horizontalLayout_rates = QHBoxLayout(self.tab_exchange_rates)
        self.horizontalLayout_rates.setObjectName(u"horizontalLayout_rates")
        self.tableView_exchange_rates = QTableView(self.tab_exchange_rates)
        self.tableView_exchange_rates.setObjectName(u"tableView_exchange_rates")

        self.horizontalLayout_rates.addWidget(self.tableView_exchange_rates)

        self.frame_rates = QFrame(self.tab_exchange_rates)
        self.frame_rates.setObjectName(u"frame_rates")
        self.frame_rates.setMinimumSize(QSize(300, 0))
        self.frame_rates.setMaximumSize(QSize(300, 16777215))
        self.frame_rates.setFrameShape(QFrame.StyledPanel)
        self.frame_rates.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_rates)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton_exchange_update = QPushButton(self.frame_rates)
        self.pushButton_exchange_update.setObjectName(u"pushButton_exchange_update")
        self.pushButton_exchange_update.setMinimumSize(QSize(0, 41))
        self.pushButton_exchange_update.setFont(font)
        self.pushButton_exchange_update.setStyleSheet(u"QPushButton {\n"
"                              background-color: #C1ECDD;\n"
"                              border: 1px solid #7DB68A;\n"
"                              border-radius: 4px;\n"
"                              }\n"
"                              QPushButton:hover {\n"
"                              background-color: #D1F5E8;\n"
"                              }\n"
"                              QPushButton:pressed {\n"
"                              background-color: #A8E0C7;\n"
"                              }")

        self.verticalLayout_6.addWidget(self.pushButton_exchange_update)

        self.groupBox_add_rate = QGroupBox(self.frame_rates)
        self.groupBox_add_rate.setObjectName(u"groupBox_add_rate")
        self.verticalLayout_add_rate = QVBoxLayout(self.groupBox_add_rate)
        self.verticalLayout_add_rate.setObjectName(u"verticalLayout_add_rate")
        self.horizontalLayout_rate_from = QHBoxLayout()
        self.horizontalLayout_rate_from.setObjectName(u"horizontalLayout_rate_from")
        self.label_rate_from = QLabel(self.groupBox_add_rate)
        self.label_rate_from.setObjectName(u"label_rate_from")
        self.label_rate_from.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_from.addWidget(self.label_rate_from)

        self.comboBox_rate_from = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_from.setObjectName(u"comboBox_rate_from")
        self.comboBox_rate_from.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_from.addWidget(self.comboBox_rate_from)


        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_from)

        self.horizontalLayout_rate_to = QHBoxLayout()
        self.horizontalLayout_rate_to.setObjectName(u"horizontalLayout_rate_to")
        self.label_rate_to = QLabel(self.groupBox_add_rate)
        self.label_rate_to.setObjectName(u"label_rate_to")
        self.label_rate_to.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_to.addWidget(self.label_rate_to)

        self.comboBox_rate_to = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_to.setObjectName(u"comboBox_rate_to")
        self.comboBox_rate_to.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_to.addWidget(self.comboBox_rate_to)


        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_to)

        self.horizontalLayout_rate_value = QHBoxLayout()
        self.horizontalLayout_rate_value.setObjectName(u"horizontalLayout_rate_value")
        self.label_rate_value = QLabel(self.groupBox_add_rate)
        self.label_rate_value.setObjectName(u"label_rate_value")
        self.label_rate_value.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_value.addWidget(self.label_rate_value)

        self.doubleSpinBox_rate_value = QDoubleSpinBox(self.groupBox_add_rate)
        self.doubleSpinBox_rate_value.setObjectName(u"doubleSpinBox_rate_value")
        self.doubleSpinBox_rate_value.setMinimumSize(QSize(170, 0))
        self.doubleSpinBox_rate_value.setMaximum(999999.989999999990687)
        self.doubleSpinBox_rate_value.setValue(73.500000000000000)

        self.horizontalLayout_rate_value.addWidget(self.doubleSpinBox_rate_value)


        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_value)

        self.horizontalLayout_rate_date = QHBoxLayout()
        self.horizontalLayout_rate_date.setObjectName(u"horizontalLayout_rate_date")
        self.label_rate_date = QLabel(self.groupBox_add_rate)
        self.label_rate_date.setObjectName(u"label_rate_date")
        self.label_rate_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_date.addWidget(self.label_rate_date)

        self.dateEdit_rate = QDateEdit(self.groupBox_add_rate)
        self.dateEdit_rate.setObjectName(u"dateEdit_rate")
        self.dateEdit_rate.setMinimumSize(QSize(170, 0))
        self.dateEdit_rate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dateEdit_rate.setCalendarPopup(True)

        self.horizontalLayout_rate_date.addWidget(self.dateEdit_rate)


        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_date)

        self.horizontalLayout_rate_add = QHBoxLayout()
        self.horizontalLayout_rate_add.setObjectName(u"horizontalLayout_rate_add")
        self.horizontalSpacer_rate = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_rate_add.addItem(self.horizontalSpacer_rate)

        self.pushButton_rate_add = QPushButton(self.groupBox_add_rate)
        self.pushButton_rate_add.setObjectName(u"pushButton_rate_add")

        self.horizontalLayout_rate_add.addWidget(self.pushButton_rate_add)


        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_add)


        self.verticalLayout_6.addWidget(self.groupBox_add_rate)

        self.groupBox_rate_commands = QGroupBox(self.frame_rates)
        self.groupBox_rate_commands.setObjectName(u"groupBox_rate_commands")
        self.verticalLayout_rate_commands = QVBoxLayout(self.groupBox_rate_commands)
        self.verticalLayout_rate_commands.setObjectName(u"verticalLayout_rate_commands")
        self.horizontalLayout_rate_commands = QHBoxLayout()
        self.horizontalLayout_rate_commands.setObjectName(u"horizontalLayout_rate_commands")
        self.pushButton_rates_delete = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_delete.setObjectName(u"pushButton_rates_delete")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_delete)

        self.pushButton_rates_refresh = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_refresh.setObjectName(u"pushButton_rates_refresh")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_refresh)


        self.verticalLayout_rate_commands.addLayout(self.horizontalLayout_rate_commands)


        self.verticalLayout_6.addWidget(self.groupBox_rate_commands)

        self.verticalSpacer_rates = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_rates)


        self.horizontalLayout_rates.addWidget(self.frame_rates)

        self.tabWidget.addTab(self.tab_exchange_rates, "")
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
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1356, 751))
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
        self.verticalLayout_7 = QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
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
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.setObjectName(u"comboBox_report_type")

        self.verticalLayout_19.addWidget(self.comboBox_report_type)

        self.pushButton_generate_report = QPushButton(self.groupBox_10)
        self.pushButton_generate_report.setObjectName(u"pushButton_generate_report")

        self.verticalLayout_19.addWidget(self.pushButton_generate_report)


        self.verticalLayout_7.addWidget(self.groupBox_10)

        self.groupBox_summary = QGroupBox(self.frame_5)
        self.groupBox_summary.setObjectName(u"groupBox_summary")
        self.verticalLayout_summary = QVBoxLayout(self.groupBox_summary)
        self.verticalLayout_summary.setObjectName(u"verticalLayout_summary")
        self.label_total_income = QLabel(self.groupBox_summary)
        self.label_total_income.setObjectName(u"label_total_income")
        self.label_total_income.setStyleSheet(u"color: #4CAF50; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_income)

        self.label_total_expenses = QLabel(self.groupBox_summary)
        self.label_total_expenses.setObjectName(u"label_total_expenses")
        self.label_total_expenses.setStyleSheet(u"color: red; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_expenses)


        self.verticalLayout_7.addWidget(self.groupBox_summary)

        self.groupBox_daily_balance = QGroupBox(self.frame_5)
        self.groupBox_daily_balance.setObjectName(u"groupBox_daily_balance")
        self.groupBox_daily_balance.setMinimumSize(QSize(0, 100))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_daily_balance)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_daily_balance = QLabel(self.groupBox_daily_balance)
        self.label_daily_balance.setObjectName(u"label_daily_balance")
        self.label_daily_balance.setFont(font2)
        self.label_daily_balance.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_daily_balance)


        self.verticalLayout_7.addWidget(self.groupBox_daily_balance)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_4)


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
        self.label_category_now.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lineEdit_description.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.pushButton_description_clear.setText("")
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", u"Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", u"Add Transaction", None))
        self.label_tag.setText(QCoreApplication.translate("MainWindow", u"Tag:", None))
        self.lineEdit_tag.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Optional", None))
        self.groupBox_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_show_all_records.setText(QCoreApplication.translate("MainWindow", u"Show All Records", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"All", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"Expense", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"Income", None))
        self.label_filter_category.setText(QCoreApplication.translate("MainWindow", u"Category:", None))
        self.label_filter_currency.setText(QCoreApplication.translate("MainWindow", u"Currency:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", u"to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", u"Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", u"Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", u"Apply Filter", None))
        self.groupBox_today_expense.setTitle(QCoreApplication.translate("MainWindow", u"Today's Expenses", None))
        self.label_today_expense.setText(QCoreApplication.translate("MainWindow", u"0.00\u20bd", None))
        self.label_categories.setText(QCoreApplication.translate("MainWindow", u"Categories:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_transactions), QCoreApplication.translate("MainWindow", u"Transactions", None))
        self.groupBox_add_account.setTitle(QCoreApplication.translate("MainWindow", u"Add New Account", None))
        self.label_account_name.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.label_account_currency.setText(QCoreApplication.translate("MainWindow", u"Currency:", None))
        self.label_account_balance.setText(QCoreApplication.translate("MainWindow", u"Balance:", None))
        self.checkBox_is_liquid.setText(QCoreApplication.translate("MainWindow", u"Liquid", None))
        self.checkBox_is_cash.setText(QCoreApplication.translate("MainWindow", u"Cash", None))
        self.pushButton_account_add.setText(QCoreApplication.translate("MainWindow", u"Add Account", None))
        self.groupBox_account_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_accounts_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_accounts_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_accounts), QCoreApplication.translate("MainWindow", u"Accounts", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Add New Category", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.lineEdit_category_name.setPlaceholderText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Type:", None))
        self.comboBox_category_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Expense", None))
        self.comboBox_category_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Income", None))

        self.pushButton_category_add.setText(QCoreApplication.translate("MainWindow", u"Add Category", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_categories_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_categories_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_categories), QCoreApplication.translate("MainWindow", u"Categories", None))
        self.groupBox_add_currency.setTitle(QCoreApplication.translate("MainWindow", u"Add New Currency", None))
        self.label_currency_code.setText(QCoreApplication.translate("MainWindow", u"Code:", None))
        self.lineEdit_currency_code.setPlaceholderText(QCoreApplication.translate("MainWindow", u"USD, EUR, RUB", None))
        self.label_currency_name.setText(QCoreApplication.translate("MainWindow", u"Name:", None))
        self.lineEdit_currency_name.setPlaceholderText(QCoreApplication.translate("MainWindow", u"US Dollar", None))
        self.label_currency_symbol.setText(QCoreApplication.translate("MainWindow", u"Symbol:", None))
        self.lineEdit_currency_symbol.setPlaceholderText(QCoreApplication.translate("MainWindow", u"$, \u20ac, \u20bd", None))
        self.pushButton_currency_add.setText(QCoreApplication.translate("MainWindow", u"Add Currency", None))
        self.groupBox_default_currency.setTitle(QCoreApplication.translate("MainWindow", u"Default Currency", None))
        self.pushButton_set_default_currency.setText(QCoreApplication.translate("MainWindow", u"Set Default", None))
        self.groupBox_currency_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_currencies_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_currencies_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_currencies), QCoreApplication.translate("MainWindow", u"Currencies", None))
        self.groupBox_exchange_operation.setTitle(QCoreApplication.translate("MainWindow", u"Currency Exchange", None))
        self.label_exchange_from.setText(QCoreApplication.translate("MainWindow", u"From:", None))
        self.label_exchange_to.setText(QCoreApplication.translate("MainWindow", u"To:", None))
        self.label_exchange_rate.setText(QCoreApplication.translate("MainWindow", u"Rate:", None))
        self.pushButton_calculate_exchange.setText(QCoreApplication.translate("MainWindow", u"Calculate", None))
        self.label_exchange_fee.setText(QCoreApplication.translate("MainWindow", u"Fee:", None))
        self.label_exchange_description.setText(QCoreApplication.translate("MainWindow", u"Description:", None))
        self.lineEdit_exchange_description.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Exchange description (optional)", None))
        self.label_exchange_date.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.dateEdit_exchange.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_exchange_yesterday.setText(QCoreApplication.translate("MainWindow", u"Yesterday", None))
        self.pushButton_exchange_add.setText(QCoreApplication.translate("MainWindow", u"Add Exchange", None))
        self.groupBox_exchange_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_exchange_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_exchange_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_exchange), QCoreApplication.translate("MainWindow", u"Currency Exchange", None))
        self.pushButton_exchange_update.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.groupBox_add_rate.setTitle(QCoreApplication.translate("MainWindow", u"Add Exchange Rate", None))
        self.label_rate_from.setText(QCoreApplication.translate("MainWindow", u"From:", None))
        self.label_rate_to.setText(QCoreApplication.translate("MainWindow", u"To:", None))
        self.label_rate_value.setText(QCoreApplication.translate("MainWindow", u"Rate:", None))
        self.label_rate_date.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.dateEdit_rate.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.pushButton_rate_add.setText(QCoreApplication.translate("MainWindow", u"Add Rate", None))
        self.groupBox_rate_commands.setTitle(QCoreApplication.translate("MainWindow", u"Commands", None))
        self.pushButton_rates_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_rates_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_exchange_rates), QCoreApplication.translate("MainWindow", u"Exchange Rates", None))
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
        self.comboBox_report_type.setItemText(2, QCoreApplication.translate("MainWindow", u"Currency Analysis", None))
        self.comboBox_report_type.setItemText(3, QCoreApplication.translate("MainWindow", u"Account Balances", None))
        self.comboBox_report_type.setItemText(4, QCoreApplication.translate("MainWindow", u"Income vs Expenses", None))

        self.pushButton_generate_report.setText(QCoreApplication.translate("MainWindow", u"Generate Report", None))
        self.groupBox_summary.setTitle(QCoreApplication.translate("MainWindow", u"Quick Summary", None))
        self.label_total_income.setText(QCoreApplication.translate("MainWindow", u"Total Income: 0.00\u20bd", None))
        self.label_total_expenses.setText(QCoreApplication.translate("MainWindow", u"Total Expenses: 0.00\u20bd", None))
        self.groupBox_daily_balance.setTitle(QCoreApplication.translate("MainWindow", u"Today's Balance", None))
        self.label_daily_balance.setText(QCoreApplication.translate("MainWindow", u"0.00\u20bd", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MainWindow", u"Reports", None))
    # retranslateUi

