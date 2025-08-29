# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableView,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Finance Tracker", None))
        self.groupBox_transaction.setTitle(QCoreApplication.translate("MainWindow", "Transaction Details", None))
        self.label_category_now.setText(QCoreApplication.translate("MainWindow", "TextLabel", None))
        self.lineEdit_description.setPlaceholderText(QCoreApplication.translate("MainWindow", "Description", None))
        self.pushButton_description_clear.setText("")
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add Transaction", None))
        self.label_tag.setText(QCoreApplication.translate("MainWindow", "Tag:", None))
        self.lineEdit_tag.setPlaceholderText(QCoreApplication.translate("MainWindow", "Optional", None))
        self.groupBox_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_show_all_records.setText(QCoreApplication.translate("MainWindow", "Show All Records", None))
        self.pushButton_add_as_text.setText(QCoreApplication.translate("MainWindow", "Add As Text", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", "Filter", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", "All", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", "Expense", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", "Income", None))
        self.label_filter_description.setText(QCoreApplication.translate("MainWindow", "Description:", None))
        self.label_filter_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_filter_currency.setText(QCoreApplication.translate("MainWindow", "Currency:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", "Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", "Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", "Apply Filter", None))
        self.groupBox_today_expense.setTitle(QCoreApplication.translate("MainWindow", "Today's Expenses", None))
        self.label_today_expense.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.label_categories.setText(QCoreApplication.translate("MainWindow", "Categories:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_transactions),
            QCoreApplication.translate("MainWindow", "Transactions", None),
        )
        self.groupBox_add_account.setTitle(QCoreApplication.translate("MainWindow", "Add New Account", None))
        self.label_account_name.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.label_account_currency.setText(QCoreApplication.translate("MainWindow", "Currency:", None))
        self.label_account_balance.setText(QCoreApplication.translate("MainWindow", "Balance:", None))
        self.checkBox_is_liquid.setText(QCoreApplication.translate("MainWindow", "Liquid", None))
        self.checkBox_is_cash.setText(QCoreApplication.translate("MainWindow", "Cash", None))
        self.pushButton_account_add.setText(QCoreApplication.translate("MainWindow", "Add Account", None))
        self.groupBox_account_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_accounts_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_accounts_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.groupBox_balance_accounts.setTitle(QCoreApplication.translate("MainWindow", "Balance", None))
        self.label_balance_accounts.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.label_balance_account_details.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_accounts), QCoreApplication.translate("MainWindow", "Accounts", None)
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Category", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.lineEdit_category_name.setPlaceholderText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_category_type.setItemText(0, QCoreApplication.translate("MainWindow", "Expense", None))
        self.comboBox_category_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))

        self.pushButton_category_add.setText(QCoreApplication.translate("MainWindow", "Add Category", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_categories_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_categories_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.pushButton_copy_categories_as_text.setText(
            QCoreApplication.translate("MainWindow", "Copy Categories As Text", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_categories), QCoreApplication.translate("MainWindow", "Categories", None)
        )
        self.groupBox_exchange_operation.setTitle(QCoreApplication.translate("MainWindow", "Currency Exchange", None))
        self.label_exchange_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.label_exchange_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.label_exchange_rate.setText(QCoreApplication.translate("MainWindow", "Rate:", None))
        self.pushButton_calculate_exchange.setText(QCoreApplication.translate("MainWindow", "Calculate", None))
        self.label_exchange_fee.setText(QCoreApplication.translate("MainWindow", "Fee:", None))
        self.label_exchange_description.setText(QCoreApplication.translate("MainWindow", "Description:", None))
        self.lineEdit_exchange_description.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Exchange description (optional)", None)
        )
        self.label_exchange_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_exchange.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_exchange_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_exchange_add.setText(QCoreApplication.translate("MainWindow", "Add Exchange", None))
        self.groupBox_exchange_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_exchange_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_exchange_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.groupBox_add_currency.setTitle(QCoreApplication.translate("MainWindow", "Add New Currency", None))
        self.label_currency_code.setText(QCoreApplication.translate("MainWindow", "Code:", None))
        self.lineEdit_currency_code.setPlaceholderText(QCoreApplication.translate("MainWindow", "USD, EUR, RUB", None))
        self.label_currency_name.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.lineEdit_currency_name.setPlaceholderText(QCoreApplication.translate("MainWindow", "US Dollar", None))
        self.label_currency_symbol.setText(QCoreApplication.translate("MainWindow", "Symbol:", None))
        self.lineEdit_currency_symbol.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "$, \u20ac, \u20bd", None)
        )
        self.label_subdivision.setText(QCoreApplication.translate("MainWindow", "Subdivision:", None))
        self.pushButton_currency_add.setText(QCoreApplication.translate("MainWindow", "Add Currency", None))
        self.groupBox_default_currency.setTitle(QCoreApplication.translate("MainWindow", "Default Currency", None))
        self.pushButton_set_default_currency.setText(QCoreApplication.translate("MainWindow", "Set Default", None))
        self.groupBox_currency_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_currencies_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_currencies_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_currencies), QCoreApplication.translate("MainWindow", "Currencies", None)
        )
        self.groupBox_rate_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_exchange_update.setText(QCoreApplication.translate("MainWindow", "Update", None))
        self.pushButton_rates_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.label.setText(QCoreApplication.translate("MainWindow", "Delete the last", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", "days", None))
        self.pushButton_rates_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.label_exchange_item_update.setText(QCoreApplication.translate("MainWindow", "For", None))
        self.dateEdit_exchange_item_update.setDisplayFormat(
            QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None)
        )
        self.label_exchange_item_update_2.setText(QCoreApplication.translate("MainWindow", "new rate", None))
        self.pushButton_exchange_item_update.setText(QCoreApplication.translate("MainWindow", "Update Rate", None))
        self.groupBox_filter_2.setTitle(QCoreApplication.translate("MainWindow", "Filter For Table", None))
        self.label_filter_currency_2.setText(QCoreApplication.translate("MainWindow", "Currency:", None))
        self.label_filter_date_2.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_exchange_rates_from.setDisplayFormat(
            QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None)
        )
        self.label_filter_to_2.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_exchange_rates_to.setDisplayFormat(
            QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None)
        )
        self.pushButton_filter_exchange_rates_clear.setText(
            QCoreApplication.translate("MainWindow", "Clear Filter", None)
        )
        self.pushButton_filter_exchange_rates_apply.setText(
            QCoreApplication.translate("MainWindow", "Apply Filter", None)
        )
        self.label_exchange_rates_currency.setText(QCoreApplication.translate("MainWindow", "Currency", None))
        self.label_exchange_rates_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_exchange_rates_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_exchange_rates_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_exchange_rates_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_exchange_rates_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_exchange_rates_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_exchange_rates_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_exchange_rates),
            QCoreApplication.translate("MainWindow", "Exchange Rates", None),
        )
        self.label_chart_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_chart_type.setItemText(0, QCoreApplication.translate("MainWindow", "All", None))
        self.comboBox_chart_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))
        self.comboBox_chart_type.setItemText(2, QCoreApplication.translate("MainWindow", "Expense", None))

        self.label_chart_period.setText(QCoreApplication.translate("MainWindow", "Period:", None))
        self.comboBox_chart_period.setItemText(0, QCoreApplication.translate("MainWindow", "Days", None))
        self.comboBox_chart_period.setItemText(1, QCoreApplication.translate("MainWindow", "Months", None))
        self.comboBox_chart_period.setItemText(2, QCoreApplication.translate("MainWindow", "Years", None))

        self.pushButton_update_chart.setText(QCoreApplication.translate("MainWindow", "Update Chart", None))
        self.pushButton_pie_chart.setText(QCoreApplication.translate("MainWindow", "Pie Chart", None))
        self.pushButton_balance_chart.setText(QCoreApplication.translate("MainWindow", "Balance Chart", None))
        self.label_chart_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_chart_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_chart_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_chart_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_chart_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_chart_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_chart_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_charts), QCoreApplication.translate("MainWindow", "Charts", None)
        )
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", "Generate Report", None))
        self.comboBox_report_type.setItemText(0, QCoreApplication.translate("MainWindow", "Monthly Summary", None))
        self.comboBox_report_type.setItemText(1, QCoreApplication.translate("MainWindow", "Category Analysis", None))
        self.comboBox_report_type.setItemText(2, QCoreApplication.translate("MainWindow", "Currency Analysis", None))
        self.comboBox_report_type.setItemText(3, QCoreApplication.translate("MainWindow", "Account Balances", None))
        self.comboBox_report_type.setItemText(4, QCoreApplication.translate("MainWindow", "Income vs Expenses", None))

        self.pushButton_generate_report.setText(QCoreApplication.translate("MainWindow", "Generate Report", None))
        self.groupBox_summary.setTitle(QCoreApplication.translate("MainWindow", "Quick Summary", None))
        self.label_total_income.setText(QCoreApplication.translate("MainWindow", "Total Income: 0.00\u20bd", None))
        self.label_total_expenses.setText(QCoreApplication.translate("MainWindow", "Total Expenses: 0.00\u20bd", None))
        self.groupBox_daily_balance.setTitle(QCoreApplication.translate("MainWindow", "Today's Balance", None))
        self.label_daily_balance.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MainWindow", "Reports", None)
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1360, 908)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_transactions = QWidget()
        self.tab_transactions.setObjectName("tab_transactions")
        self.horizontalLayout_main = QHBoxLayout(self.tab_transactions)
        self.horizontalLayout_main.setObjectName("horizontalLayout_main")
        self.splitter = QSplitter(self.tab_transactions)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(380, 0))
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_transaction = QGroupBox(self.frame)
        self.groupBox_transaction.setObjectName("groupBox_transaction")
        self.groupBox_transaction.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_transaction)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_category_now = QLabel(self.groupBox_transaction)
        self.label_category_now.setObjectName("label_category_now")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_category_now.setFont(font)
        self.label_category_now.setFocusPolicy(Qt.NoFocus)

        self.verticalLayout_3.addWidget(self.label_category_now)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_description = QLineEdit(self.groupBox_transaction)
        self.lineEdit_description.setObjectName("lineEdit_description")
        font1 = QFont()
        font1.setPointSize(12)
        self.lineEdit_description.setFont(font1)

        self.horizontalLayout_2.addWidget(self.lineEdit_description)

        self.pushButton_description_clear = QPushButton(self.groupBox_transaction)
        self.pushButton_description_clear.setObjectName("pushButton_description_clear")
        self.pushButton_description_clear.setMaximumSize(QSize(32, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_description_clear)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_amount = QHBoxLayout()
        self.horizontalLayout_amount.setObjectName("horizontalLayout_amount")
        self.doubleSpinBox_amount = QDoubleSpinBox(self.groupBox_transaction)
        self.doubleSpinBox_amount.setObjectName("doubleSpinBox_amount")
        self.doubleSpinBox_amount.setFont(font)
        self.doubleSpinBox_amount.setStyleSheet(
            "QDoubleSpinBox {\n"
            "                                          background-color: #C1ECDD;\n"
            "                                          }"
        )
        self.doubleSpinBox_amount.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.doubleSpinBox_amount.setMaximum(999999.989999999990687)
        self.doubleSpinBox_amount.setValue(100.000000000000000)

        self.horizontalLayout_amount.addWidget(self.doubleSpinBox_amount)

        self.comboBox_currency = QComboBox(self.groupBox_transaction)
        self.comboBox_currency.setObjectName("comboBox_currency")
        self.comboBox_currency.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_amount.addWidget(self.comboBox_currency)

        self.verticalLayout_3.addLayout(self.horizontalLayout_amount)

        self.horizontalLayout_date = QHBoxLayout()
        self.horizontalLayout_date.setObjectName("horizontalLayout_date")
        self.dateEdit = QDateEdit(self.groupBox_transaction)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setMinimumSize(QSize(191, 0))
        self.dateEdit.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_date.addWidget(self.dateEdit)

        self.pushButton_yesterday = QPushButton(self.groupBox_transaction)
        self.pushButton_yesterday.setObjectName("pushButton_yesterday")
        self.pushButton_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_date.addWidget(self.pushButton_yesterday)

        self.verticalLayout_3.addLayout(self.horizontalLayout_date)

        self.pushButton_add = QPushButton(self.groupBox_transaction)
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 41))
        self.pushButton_add.setFont(font)
        self.pushButton_add.setStyleSheet(
            "QPushButton {\n"
            "                                      background-color: #C1ECDD;\n"
            "                                      border: 1px solid #7DB68A;\n"
            "                                      border-radius: 4px;\n"
            "                                      }\n"
            "                                      QPushButton:hover {\n"
            "                                      background-color: #D1F5E8;\n"
            "                                      }\n"
            "                                      QPushButton:pressed {\n"
            "                                      background-color: #A8E0C7;\n"
            "                                      }"
        )

        self.verticalLayout_3.addWidget(self.pushButton_add)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_tag = QLabel(self.groupBox_transaction)
        self.label_tag.setObjectName("label_tag")
        self.label_tag.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.label_tag)

        self.lineEdit_tag = QLineEdit(self.groupBox_transaction)
        self.lineEdit_tag.setObjectName("lineEdit_tag")

        self.horizontalLayout_3.addWidget(self.lineEdit_tag)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalLayout_5.addWidget(self.groupBox_transaction)

        self.groupBox_commands = QGroupBox(self.frame)
        self.groupBox_commands.setObjectName("groupBox_commands")
        self.groupBox_commands.setMinimumSize(QSize(0, 1))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_commands)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_commands)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_show_all_records = QPushButton(self.groupBox_commands)
        self.pushButton_show_all_records.setObjectName("pushButton_show_all_records")

        self.horizontalLayout_8.addWidget(self.pushButton_show_all_records)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.pushButton_add_as_text = QPushButton(self.groupBox_commands)
        self.pushButton_add_as_text.setObjectName("pushButton_add_as_text")

        self.horizontalLayout_26.addWidget(self.pushButton_add_as_text)

        self.pushButton_refresh = QPushButton(self.groupBox_commands)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_26.addWidget(self.pushButton_refresh)

        self.verticalLayout_2.addLayout(self.horizontalLayout_26)

        self.verticalLayout_5.addWidget(self.groupBox_commands)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 1))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.radioButton = QRadioButton(self.groupBox_filter)
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setChecked(True)

        self.horizontalLayout_5.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.groupBox_filter)
        self.radioButton_2.setObjectName("radioButton_2")

        self.horizontalLayout_5.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.groupBox_filter)
        self.radioButton_3.setObjectName("radioButton_3")

        self.horizontalLayout_5.addWidget(self.radioButton_3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.label_filter_description = QLabel(self.groupBox_filter)
        self.label_filter_description.setObjectName("label_filter_description")
        self.label_filter_description.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_27.addWidget(self.label_filter_description)

        self.lineEdit_filter_description = QLineEdit(self.groupBox_filter)
        self.lineEdit_filter_description.setObjectName("lineEdit_filter_description")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_filter_description.sizePolicy().hasHeightForWidth())
        self.lineEdit_filter_description.setSizePolicy(sizePolicy)
        self.lineEdit_filter_description.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_27.addWidget(self.lineEdit_filter_description)

        self.verticalLayout_4.addLayout(self.horizontalLayout_27)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_filter_category = QLabel(self.groupBox_filter)
        self.label_filter_category.setObjectName("label_filter_category")
        self.label_filter_category.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_9.addWidget(self.label_filter_category)

        self.comboBox_filter_category = QComboBox(self.groupBox_filter)
        self.comboBox_filter_category.setObjectName("comboBox_filter_category")
        self.comboBox_filter_category.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_9.addWidget(self.comboBox_filter_category)

        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_currency_filter = QHBoxLayout()
        self.horizontalLayout_currency_filter.setObjectName("horizontalLayout_currency_filter")
        self.label_filter_currency = QLabel(self.groupBox_filter)
        self.label_filter_currency.setObjectName("label_filter_currency")
        self.label_filter_currency.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_filter.addWidget(self.label_filter_currency)

        self.comboBox_filter_currency = QComboBox(self.groupBox_filter)
        self.comboBox_filter_currency.setObjectName("comboBox_filter_currency")
        self.comboBox_filter_currency.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_filter.addWidget(self.comboBox_filter_currency)

        self.verticalLayout_4.addLayout(self.horizontalLayout_currency_filter)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_filter_date = QLabel(self.groupBox_filter)
        self.label_filter_date.setObjectName("label_filter_date")
        self.label_filter_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_11.addWidget(self.label_filter_date)

        self.dateEdit_filter_from = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_from.setObjectName("dateEdit_filter_from")
        self.dateEdit_filter_from.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_from.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_filter_from.setCalendarPopup(True)

        self.horizontalLayout_11.addWidget(self.dateEdit_filter_from)

        self.verticalLayout_4.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_filter_to = QLabel(self.groupBox_filter)
        self.label_filter_to.setObjectName("label_filter_to")
        self.label_filter_to.setMinimumSize(QSize(61, 0))
        self.label_filter_to.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontalLayout_12.addWidget(self.label_filter_to)

        self.dateEdit_filter_to = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_to.setObjectName("dateEdit_filter_to")
        self.dateEdit_filter_to.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_to.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_filter_to.setCalendarPopup(True)

        self.horizontalLayout_12.addWidget(self.dateEdit_filter_to)

        self.verticalLayout_4.addLayout(self.horizontalLayout_12)

        self.checkBox_use_date_filter = QCheckBox(self.groupBox_filter)
        self.checkBox_use_date_filter.setObjectName("checkBox_use_date_filter")

        self.verticalLayout_4.addWidget(self.checkBox_use_date_filter)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.pushButton_clear_filter = QPushButton(self.groupBox_filter)
        self.pushButton_clear_filter.setObjectName("pushButton_clear_filter")
        self.pushButton_clear_filter.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_7.addWidget(self.pushButton_clear_filter)

        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName("pushButton_apply_filter")
        self.pushButton_apply_filter.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_7.addWidget(self.pushButton_apply_filter)

        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.verticalLayout_5.addWidget(self.groupBox_filter)

        self.groupBox_today_expense = QGroupBox(self.frame)
        self.groupBox_today_expense.setObjectName("groupBox_today_expense")
        self.groupBox_today_expense.setMinimumSize(QSize(0, 100))
        self.verticalLayout_20 = QVBoxLayout(self.groupBox_today_expense)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.label_today_expense = QLabel(self.groupBox_today_expense)
        self.label_today_expense.setObjectName("label_today_expense")
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
        self.widget_middle.setObjectName("widget_middle")
        self.verticalLayout = QVBoxLayout(self.widget_middle)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_categories = QLabel(self.widget_middle)
        self.label_categories.setObjectName("label_categories")

        self.verticalLayout.addWidget(self.label_categories)

        self.listView_categories = QListView(self.widget_middle)
        self.listView_categories.setObjectName("listView_categories")
        self.listView_categories.setMaximumSize(QSize(16777215, 16777215))
        self.listView_categories.setStyleSheet(
            "QListView {\n"
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
            "                                }"
        )

        self.verticalLayout.addWidget(self.listView_categories)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_transactions = QTableView(self.splitter)
        self.tableView_transactions.setObjectName("tableView_transactions")
        self.splitter.addWidget(self.tableView_transactions)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_transactions, "")
        self.tab_accounts = QWidget()
        self.tab_accounts.setObjectName("tab_accounts")
        self.verticalLayout_22 = QVBoxLayout(self.tab_accounts)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.splitter_2 = QSplitter(self.tab_accounts)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.frame_accounts = QFrame(self.splitter_2)
        self.frame_accounts.setObjectName("frame_accounts")
        self.frame_accounts.setMinimumSize(QSize(300, 0))
        self.frame_accounts.setMaximumSize(QSize(300, 16777215))
        self.frame_accounts.setFrameShape(QFrame.StyledPanel)
        self.frame_accounts.setFrameShadow(QFrame.Raised)
        self.verticalLayout_21 = QVBoxLayout(self.frame_accounts)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.groupBox_add_account = QGroupBox(self.frame_accounts)
        self.groupBox_add_account.setObjectName("groupBox_add_account")
        self.verticalLayout_add_account = QVBoxLayout(self.groupBox_add_account)
        self.verticalLayout_add_account.setObjectName("verticalLayout_add_account")
        self.horizontalLayout_account_name = QHBoxLayout()
        self.horizontalLayout_account_name.setObjectName("horizontalLayout_account_name")
        self.label_account_name = QLabel(self.groupBox_add_account)
        self.label_account_name.setObjectName("label_account_name")
        self.label_account_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_name.addWidget(self.label_account_name)

        self.lineEdit_account_name = QLineEdit(self.groupBox_add_account)
        self.lineEdit_account_name.setObjectName("lineEdit_account_name")
        self.lineEdit_account_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_account_name.addWidget(self.lineEdit_account_name)

        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_name)

        self.horizontalLayout_account_currency = QHBoxLayout()
        self.horizontalLayout_account_currency.setObjectName("horizontalLayout_account_currency")
        self.label_account_currency = QLabel(self.groupBox_add_account)
        self.label_account_currency.setObjectName("label_account_currency")
        self.label_account_currency.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_currency.addWidget(self.label_account_currency)

        self.comboBox_account_currency = QComboBox(self.groupBox_add_account)
        self.comboBox_account_currency.setObjectName("comboBox_account_currency")
        self.comboBox_account_currency.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_account_currency.addWidget(self.comboBox_account_currency)

        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_currency)

        self.horizontalLayout_account_balance = QHBoxLayout()
        self.horizontalLayout_account_balance.setObjectName("horizontalLayout_account_balance")
        self.label_account_balance = QLabel(self.groupBox_add_account)
        self.label_account_balance.setObjectName("label_account_balance")
        self.label_account_balance.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_account_balance.addWidget(self.label_account_balance)

        self.doubleSpinBox_account_balance = QDoubleSpinBox(self.groupBox_add_account)
        self.doubleSpinBox_account_balance.setObjectName("doubleSpinBox_account_balance")
        self.doubleSpinBox_account_balance.setMinimumSize(QSize(170, 0))
        self.doubleSpinBox_account_balance.setMaximum(999999.989999999990687)
        self.doubleSpinBox_account_balance.setValue(0.000000000000000)

        self.horizontalLayout_account_balance.addWidget(self.doubleSpinBox_account_balance)

        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_balance)

        self.horizontalLayout_account_flags = QHBoxLayout()
        self.horizontalLayout_account_flags.setObjectName("horizontalLayout_account_flags")
        self.checkBox_is_liquid = QCheckBox(self.groupBox_add_account)
        self.checkBox_is_liquid.setObjectName("checkBox_is_liquid")
        self.checkBox_is_liquid.setChecked(True)

        self.horizontalLayout_account_flags.addWidget(self.checkBox_is_liquid)

        self.checkBox_is_cash = QCheckBox(self.groupBox_add_account)
        self.checkBox_is_cash.setObjectName("checkBox_is_cash")

        self.horizontalLayout_account_flags.addWidget(self.checkBox_is_cash)

        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_flags)

        self.horizontalLayout_account_add = QHBoxLayout()
        self.horizontalLayout_account_add.setObjectName("horizontalLayout_account_add")
        self.horizontalSpacer_account = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_account_add.addItem(self.horizontalSpacer_account)

        self.pushButton_account_add = QPushButton(self.groupBox_add_account)
        self.pushButton_account_add.setObjectName("pushButton_account_add")

        self.horizontalLayout_account_add.addWidget(self.pushButton_account_add)

        self.verticalLayout_add_account.addLayout(self.horizontalLayout_account_add)

        self.verticalLayout_21.addWidget(self.groupBox_add_account)

        self.groupBox_account_commands = QGroupBox(self.frame_accounts)
        self.groupBox_account_commands.setObjectName("groupBox_account_commands")
        self.verticalLayout_account_commands = QVBoxLayout(self.groupBox_account_commands)
        self.verticalLayout_account_commands.setObjectName("verticalLayout_account_commands")
        self.horizontalLayout_account_commands = QHBoxLayout()
        self.horizontalLayout_account_commands.setObjectName("horizontalLayout_account_commands")
        self.pushButton_accounts_delete = QPushButton(self.groupBox_account_commands)
        self.pushButton_accounts_delete.setObjectName("pushButton_accounts_delete")

        self.horizontalLayout_account_commands.addWidget(self.pushButton_accounts_delete)

        self.pushButton_accounts_refresh = QPushButton(self.groupBox_account_commands)
        self.pushButton_accounts_refresh.setObjectName("pushButton_accounts_refresh")

        self.horizontalLayout_account_commands.addWidget(self.pushButton_accounts_refresh)

        self.verticalLayout_account_commands.addLayout(self.horizontalLayout_account_commands)

        self.verticalLayout_21.addWidget(self.groupBox_account_commands)

        self.groupBox_balance_accounts = QGroupBox(self.frame_accounts)
        self.groupBox_balance_accounts.setObjectName("groupBox_balance_accounts")
        self.groupBox_balance_accounts.setMinimumSize(QSize(0, 100))
        self.verticalLayout_16 = QVBoxLayout(self.groupBox_balance_accounts)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_balance_accounts = QLabel(self.groupBox_balance_accounts)
        self.label_balance_accounts.setObjectName("label_balance_accounts")
        self.label_balance_accounts.setFont(font2)
        self.label_balance_accounts.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_balance_accounts)

        self.label_balance_account_details = QLabel(self.groupBox_balance_accounts)
        self.label_balance_account_details.setObjectName("label_balance_account_details")

        self.verticalLayout_16.addWidget(self.label_balance_account_details)

        self.verticalLayout_21.addWidget(self.groupBox_balance_accounts)

        self.verticalSpacer_accounts = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_accounts)

        self.splitter_2.addWidget(self.frame_accounts)
        self.tableView_accounts = QTableView(self.splitter_2)
        self.tableView_accounts.setObjectName("tableView_accounts")
        self.splitter_2.addWidget(self.tableView_accounts)

        self.verticalLayout_22.addWidget(self.splitter_2)

        self.tabWidget.addTab(self.tab_accounts, "")
        self.tab_categories = QWidget()
        self.tab_categories.setObjectName("tab_categories")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_categories)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_2 = QFrame(self.tab_categories)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setMinimumSize(QSize(300, 0))
        self.frame_2.setMaximumSize(QSize(300, 16777215))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_2)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_17.addWidget(self.label_5)

        self.lineEdit_category_name = QLineEdit(self.groupBox_2)
        self.lineEdit_category_name.setObjectName("lineEdit_category_name")
        self.lineEdit_category_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_17.addWidget(self.lineEdit_category_name)

        self.verticalLayout_10.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_18.addWidget(self.label_6)

        self.comboBox_category_type = QComboBox(self.groupBox_2)
        self.comboBox_category_type.addItem("")
        self.comboBox_category_type.addItem("")
        self.comboBox_category_type.setObjectName("comboBox_category_type")
        self.comboBox_category_type.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_18.addWidget(self.comboBox_category_type)

        self.verticalLayout_10.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_4)

        self.pushButton_category_add = QPushButton(self.groupBox_2)
        self.pushButton_category_add.setObjectName("pushButton_category_add")

        self.horizontalLayout_19.addWidget(self.pushButton_category_add)

        self.verticalLayout_10.addLayout(self.horizontalLayout_19)

        self.verticalLayout_15.addWidget(self.groupBox_2)

        self.groupBox_7 = QGroupBox(self.frame_2)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.pushButton_categories_delete = QPushButton(self.groupBox_7)
        self.pushButton_categories_delete.setObjectName("pushButton_categories_delete")

        self.horizontalLayout_20.addWidget(self.pushButton_categories_delete)

        self.pushButton_categories_refresh = QPushButton(self.groupBox_7)
        self.pushButton_categories_refresh.setObjectName("pushButton_categories_refresh")

        self.horizontalLayout_20.addWidget(self.pushButton_categories_refresh)

        self.verticalLayout_11.addLayout(self.horizontalLayout_20)

        self.pushButton_copy_categories_as_text = QPushButton(self.groupBox_7)
        self.pushButton_copy_categories_as_text.setObjectName("pushButton_copy_categories_as_text")

        self.verticalLayout_11.addWidget(self.pushButton_copy_categories_as_text)

        self.verticalLayout_15.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_2)

        self.horizontalLayout_4.addWidget(self.frame_2)

        self.tableView_categories = QTableView(self.tab_categories)
        self.tableView_categories.setObjectName("tableView_categories")

        self.horizontalLayout_4.addWidget(self.tableView_categories)

        self.tabWidget.addTab(self.tab_categories, "")
        self.tab_currencies = QWidget()
        self.tab_currencies.setObjectName("tab_currencies")
        self.horizontalLayout_10 = QHBoxLayout(self.tab_currencies)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.frame_exchange = QFrame(self.tab_currencies)
        self.frame_exchange.setObjectName("frame_exchange")
        self.frame_exchange.setMinimumSize(QSize(350, 0))
        self.frame_exchange.setMaximumSize(QSize(350, 16777215))
        self.frame_exchange.setFrameShape(QFrame.StyledPanel)
        self.frame_exchange.setFrameShadow(QFrame.Raised)
        self.verticalLayout_exchange = QVBoxLayout(self.frame_exchange)
        self.verticalLayout_exchange.setObjectName("verticalLayout_exchange")
        self.groupBox_exchange_operation = QGroupBox(self.frame_exchange)
        self.groupBox_exchange_operation.setObjectName("groupBox_exchange_operation")
        self.verticalLayout_exchange_operation = QVBoxLayout(self.groupBox_exchange_operation)
        self.verticalLayout_exchange_operation.setObjectName("verticalLayout_exchange_operation")
        self.horizontalLayout_exchange_from = QHBoxLayout()
        self.horizontalLayout_exchange_from.setObjectName("horizontalLayout_exchange_from")
        self.label_exchange_from = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_from.setObjectName("label_exchange_from")
        self.label_exchange_from.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_from.addWidget(self.label_exchange_from)

        self.comboBox_exchange_from = QComboBox(self.groupBox_exchange_operation)
        self.comboBox_exchange_from.setObjectName("comboBox_exchange_from")
        self.comboBox_exchange_from.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_from.addWidget(self.comboBox_exchange_from)

        self.doubleSpinBox_exchange_from = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_from.setObjectName("doubleSpinBox_exchange_from")
        self.doubleSpinBox_exchange_from.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_from.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_from.setValue(100.000000000000000)

        self.horizontalLayout_exchange_from.addWidget(self.doubleSpinBox_exchange_from)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_from)

        self.horizontalLayout_exchange_to = QHBoxLayout()
        self.horizontalLayout_exchange_to.setObjectName("horizontalLayout_exchange_to")
        self.label_exchange_to = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_to.setObjectName("label_exchange_to")
        self.label_exchange_to.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_to.addWidget(self.label_exchange_to)

        self.comboBox_exchange_to = QComboBox(self.groupBox_exchange_operation)
        self.comboBox_exchange_to.setObjectName("comboBox_exchange_to")
        self.comboBox_exchange_to.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_to.addWidget(self.comboBox_exchange_to)

        self.doubleSpinBox_exchange_to = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_to.setObjectName("doubleSpinBox_exchange_to")
        self.doubleSpinBox_exchange_to.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_to.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_to.setValue(73.500000000000000)

        self.horizontalLayout_exchange_to.addWidget(self.doubleSpinBox_exchange_to)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_to)

        self.horizontalLayout_exchange_rate = QHBoxLayout()
        self.horizontalLayout_exchange_rate.setObjectName("horizontalLayout_exchange_rate")
        self.label_exchange_rate = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_rate.setObjectName("label_exchange_rate")
        self.label_exchange_rate.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_rate.addWidget(self.label_exchange_rate)

        self.doubleSpinBox_exchange_rate = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_rate.setObjectName("doubleSpinBox_exchange_rate")
        self.doubleSpinBox_exchange_rate.setMinimumSize(QSize(120, 0))
        self.doubleSpinBox_exchange_rate.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_rate.setValue(73.500000000000000)

        self.horizontalLayout_exchange_rate.addWidget(self.doubleSpinBox_exchange_rate)

        self.pushButton_calculate_exchange = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_calculate_exchange.setObjectName("pushButton_calculate_exchange")
        self.pushButton_calculate_exchange.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_exchange_rate.addWidget(self.pushButton_calculate_exchange)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_rate)

        self.horizontalLayout_exchange_fee = QHBoxLayout()
        self.horizontalLayout_exchange_fee.setObjectName("horizontalLayout_exchange_fee")
        self.label_exchange_fee = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_fee.setObjectName("label_exchange_fee")
        self.label_exchange_fee.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_fee.addWidget(self.label_exchange_fee)

        self.doubleSpinBox_exchange_fee = QDoubleSpinBox(self.groupBox_exchange_operation)
        self.doubleSpinBox_exchange_fee.setObjectName("doubleSpinBox_exchange_fee")
        self.doubleSpinBox_exchange_fee.setMinimumSize(QSize(260, 0))
        self.doubleSpinBox_exchange_fee.setMaximum(999999.989999999990687)
        self.doubleSpinBox_exchange_fee.setValue(0.000000000000000)

        self.horizontalLayout_exchange_fee.addWidget(self.doubleSpinBox_exchange_fee)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_fee)

        self.horizontalLayout_exchange_description = QHBoxLayout()
        self.horizontalLayout_exchange_description.setObjectName("horizontalLayout_exchange_description")
        self.label_exchange_description = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_description.setObjectName("label_exchange_description")
        self.label_exchange_description.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_description.addWidget(self.label_exchange_description)

        self.lineEdit_exchange_description = QLineEdit(self.groupBox_exchange_operation)
        self.lineEdit_exchange_description.setObjectName("lineEdit_exchange_description")
        self.lineEdit_exchange_description.setMinimumSize(QSize(260, 0))

        self.horizontalLayout_exchange_description.addWidget(self.lineEdit_exchange_description)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_description)

        self.horizontalLayout_exchange_date = QHBoxLayout()
        self.horizontalLayout_exchange_date.setObjectName("horizontalLayout_exchange_date")
        self.label_exchange_date = QLabel(self.groupBox_exchange_operation)
        self.label_exchange_date.setObjectName("label_exchange_date")
        self.label_exchange_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_date.addWidget(self.label_exchange_date)

        self.dateEdit_exchange = QDateEdit(self.groupBox_exchange_operation)
        self.dateEdit_exchange.setObjectName("dateEdit_exchange")
        self.dateEdit_exchange.setMinimumSize(QSize(151, 0))
        self.dateEdit_exchange.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_exchange.setCalendarPopup(True)

        self.horizontalLayout_exchange_date.addWidget(self.dateEdit_exchange)

        self.pushButton_exchange_yesterday = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_exchange_yesterday.setObjectName("pushButton_exchange_yesterday")
        self.pushButton_exchange_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_exchange_date.addWidget(self.pushButton_exchange_yesterday)

        self.verticalLayout_exchange_operation.addLayout(self.horizontalLayout_exchange_date)

        self.pushButton_exchange_add = QPushButton(self.groupBox_exchange_operation)
        self.pushButton_exchange_add.setObjectName("pushButton_exchange_add")
        self.pushButton_exchange_add.setMinimumSize(QSize(0, 41))
        self.pushButton_exchange_add.setFont(font)
        self.pushButton_exchange_add.setStyleSheet(
            "QPushButton {\n"
            "                                    background-color: #C1ECDD;\n"
            "                                    border: 1px solid #7DB68A;\n"
            "                                    border-radius: 4px;\n"
            "                                    }\n"
            "                                    QPushButton:hover {\n"
            "                                    background-color: #D1F5E8;\n"
            "                                    }\n"
            "                                    QPushButton:pressed {\n"
            "                                    background-color: #A8E0C7;\n"
            "                                    }"
        )

        self.verticalLayout_exchange_operation.addWidget(self.pushButton_exchange_add)

        self.verticalLayout_exchange.addWidget(self.groupBox_exchange_operation)

        self.groupBox_exchange_commands = QGroupBox(self.frame_exchange)
        self.groupBox_exchange_commands.setObjectName("groupBox_exchange_commands")
        self.verticalLayout_exchange_commands = QVBoxLayout(self.groupBox_exchange_commands)
        self.verticalLayout_exchange_commands.setObjectName("verticalLayout_exchange_commands")
        self.horizontalLayout_exchange_commands = QHBoxLayout()
        self.horizontalLayout_exchange_commands.setObjectName("horizontalLayout_exchange_commands")
        self.pushButton_exchange_delete = QPushButton(self.groupBox_exchange_commands)
        self.pushButton_exchange_delete.setObjectName("pushButton_exchange_delete")

        self.horizontalLayout_exchange_commands.addWidget(self.pushButton_exchange_delete)

        self.pushButton_exchange_refresh = QPushButton(self.groupBox_exchange_commands)
        self.pushButton_exchange_refresh.setObjectName("pushButton_exchange_refresh")

        self.horizontalLayout_exchange_commands.addWidget(self.pushButton_exchange_refresh)

        self.verticalLayout_exchange_commands.addLayout(self.horizontalLayout_exchange_commands)

        self.verticalLayout_exchange.addWidget(self.groupBox_exchange_commands)

        self.verticalSpacer_exchange = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_exchange.addItem(self.verticalSpacer_exchange)

        self.horizontalLayout_10.addWidget(self.frame_exchange)

        self.tableView_exchange = QTableView(self.tab_currencies)
        self.tableView_exchange.setObjectName("tableView_exchange")

        self.horizontalLayout_10.addWidget(self.tableView_exchange)

        self.frame_currencies = QFrame(self.tab_currencies)
        self.frame_currencies.setObjectName("frame_currencies")
        self.frame_currencies.setMinimumSize(QSize(300, 0))
        self.frame_currencies.setMaximumSize(QSize(300, 16777215))
        self.frame_currencies.setFrameShape(QFrame.StyledPanel)
        self.frame_currencies.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_currencies)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.groupBox_add_currency = QGroupBox(self.frame_currencies)
        self.groupBox_add_currency.setObjectName("groupBox_add_currency")
        self.groupBox_add_currency.setMinimumSize(QSize(0, 0))
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_add_currency)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_currency_code = QHBoxLayout()
        self.horizontalLayout_currency_code.setObjectName("horizontalLayout_currency_code")
        self.label_currency_code = QLabel(self.groupBox_add_currency)
        self.label_currency_code.setObjectName("label_currency_code")
        self.label_currency_code.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_code.addWidget(self.label_currency_code)

        self.lineEdit_currency_code = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_code.setObjectName("lineEdit_currency_code")
        self.lineEdit_currency_code.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_code.addWidget(self.lineEdit_currency_code)

        self.verticalLayout_9.addLayout(self.horizontalLayout_currency_code)

        self.horizontalLayout_currency_name = QHBoxLayout()
        self.horizontalLayout_currency_name.setObjectName("horizontalLayout_currency_name")
        self.label_currency_name = QLabel(self.groupBox_add_currency)
        self.label_currency_name.setObjectName("label_currency_name")
        self.label_currency_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_name.addWidget(self.label_currency_name)

        self.lineEdit_currency_name = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_name.setObjectName("lineEdit_currency_name")
        self.lineEdit_currency_name.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_name.addWidget(self.lineEdit_currency_name)

        self.verticalLayout_9.addLayout(self.horizontalLayout_currency_name)

        self.horizontalLayout_currency_symbol = QHBoxLayout()
        self.horizontalLayout_currency_symbol.setObjectName("horizontalLayout_currency_symbol")
        self.label_currency_symbol = QLabel(self.groupBox_add_currency)
        self.label_currency_symbol.setObjectName("label_currency_symbol")
        self.label_currency_symbol.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.label_currency_symbol)

        self.lineEdit_currency_symbol = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_symbol.setObjectName("lineEdit_currency_symbol")
        self.lineEdit_currency_symbol.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.lineEdit_currency_symbol)

        self.verticalLayout_9.addLayout(self.horizontalLayout_currency_symbol)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_subdivision = QLabel(self.groupBox_add_currency)
        self.label_subdivision.setObjectName("label_subdivision")

        self.horizontalLayout_13.addWidget(self.label_subdivision)

        self.spinBox_subdivision = QSpinBox(self.groupBox_add_currency)
        self.spinBox_subdivision.setObjectName("spinBox_subdivision")
        self.spinBox_subdivision.setMinimumSize(QSize(191, 0))
        self.spinBox_subdivision.setMaximum(1000000000)

        self.horizontalLayout_13.addWidget(self.spinBox_subdivision)

        self.verticalLayout_9.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_currency_add = QHBoxLayout()
        self.horizontalLayout_currency_add.setObjectName("horizontalLayout_currency_add")
        self.horizontalSpacer_currency = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_currency_add.addItem(self.horizontalSpacer_currency)

        self.pushButton_currency_add = QPushButton(self.groupBox_add_currency)
        self.pushButton_currency_add.setObjectName("pushButton_currency_add")

        self.horizontalLayout_currency_add.addWidget(self.pushButton_currency_add)

        self.verticalLayout_9.addLayout(self.horizontalLayout_currency_add)

        self.verticalLayout_8.addWidget(self.groupBox_add_currency)

        self.groupBox_default_currency = QGroupBox(self.frame_currencies)
        self.groupBox_default_currency.setObjectName("groupBox_default_currency")
        self.verticalLayout_default_currency = QVBoxLayout(self.groupBox_default_currency)
        self.verticalLayout_default_currency.setObjectName("verticalLayout_default_currency")
        self.horizontalLayout_default_currency = QHBoxLayout()
        self.horizontalLayout_default_currency.setObjectName("horizontalLayout_default_currency")
        self.comboBox_default_currency = QComboBox(self.groupBox_default_currency)
        self.comboBox_default_currency.setObjectName("comboBox_default_currency")
        self.comboBox_default_currency.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_default_currency.addWidget(self.comboBox_default_currency)

        self.pushButton_set_default_currency = QPushButton(self.groupBox_default_currency)
        self.pushButton_set_default_currency.setObjectName("pushButton_set_default_currency")

        self.horizontalLayout_default_currency.addWidget(self.pushButton_set_default_currency)

        self.verticalLayout_default_currency.addLayout(self.horizontalLayout_default_currency)

        self.verticalLayout_8.addWidget(self.groupBox_default_currency)

        self.groupBox_currency_commands = QGroupBox(self.frame_currencies)
        self.groupBox_currency_commands.setObjectName("groupBox_currency_commands")
        self.verticalLayout_currency_commands = QVBoxLayout(self.groupBox_currency_commands)
        self.verticalLayout_currency_commands.setObjectName("verticalLayout_currency_commands")
        self.horizontalLayout_currency_commands = QHBoxLayout()
        self.horizontalLayout_currency_commands.setObjectName("horizontalLayout_currency_commands")
        self.pushButton_currencies_delete = QPushButton(self.groupBox_currency_commands)
        self.pushButton_currencies_delete.setObjectName("pushButton_currencies_delete")

        self.horizontalLayout_currency_commands.addWidget(self.pushButton_currencies_delete)

        self.pushButton_currencies_refresh = QPushButton(self.groupBox_currency_commands)
        self.pushButton_currencies_refresh.setObjectName("pushButton_currencies_refresh")

        self.horizontalLayout_currency_commands.addWidget(self.pushButton_currencies_refresh)

        self.verticalLayout_currency_commands.addLayout(self.horizontalLayout_currency_commands)

        self.verticalLayout_8.addWidget(self.groupBox_currency_commands)

        self.tableView_currencies = QTableView(self.frame_currencies)
        self.tableView_currencies.setObjectName("tableView_currencies")

        self.verticalLayout_8.addWidget(self.tableView_currencies)

        self.horizontalLayout_10.addWidget(self.frame_currencies)

        self.tabWidget.addTab(self.tab_currencies, "")
        self.tab_exchange_rates = QWidget()
        self.tab_exchange_rates.setObjectName("tab_exchange_rates")
        self.horizontalLayout_14 = QHBoxLayout(self.tab_exchange_rates)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.splitter_exchange_rates = QSplitter(self.tab_exchange_rates)
        self.splitter_exchange_rates.setObjectName("splitter_exchange_rates")
        self.splitter_exchange_rates.setOrientation(Qt.Horizontal)
        self.splitter_exchange_rates.setChildrenCollapsible(False)
        self.frame_rates = QFrame(self.splitter_exchange_rates)
        self.frame_rates.setObjectName("frame_rates")
        self.frame_rates.setMinimumSize(QSize(300, 0))
        self.frame_rates.setMaximumSize(QSize(16777215, 16777215))
        self.frame_rates.setFrameShape(QFrame.StyledPanel)
        self.frame_rates.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frame_rates)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.frame_3 = QFrame(self.frame_rates)
        self.frame_3.setObjectName("frame_3")
        self.frame_3.setMinimumSize(QSize(0, 171))
        self.frame_3.setMaximumSize(QSize(16777215, 150))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_25 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_25.setSpacing(5)
        self.horizontalLayout_25.setObjectName("horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(5, 5, 5, 5)
        self.groupBox_rate_commands = QGroupBox(self.frame_3)
        self.groupBox_rate_commands.setObjectName("groupBox_rate_commands")
        self.groupBox_rate_commands.setMinimumSize(QSize(0, 0))
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_rate_commands)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.pushButton_exchange_update = QPushButton(self.groupBox_rate_commands)
        self.pushButton_exchange_update.setObjectName("pushButton_exchange_update")
        self.pushButton_exchange_update.setMinimumSize(QSize(0, 24))
        font3 = QFont()
        font3.setPointSize(8)
        font3.setBold(True)
        self.pushButton_exchange_update.setFont(font3)
        self.pushButton_exchange_update.setStyleSheet(
            "QPushButton {\n"
            "                                            background-color: #C1ECDD;\n"
            "                                            border: 1px solid #7DB68A;\n"
            "                                            border-radius: 4px;\n"
            "                                            }\n"
            "                                            QPushButton:hover {\n"
            "                                            background-color: #D1F5E8;\n"
            "                                            }\n"
            "                                            QPushButton:pressed {\n"
            "                                            background-color: #A8E0C7;\n"
            "                                            }"
        )

        self.verticalLayout_13.addWidget(self.pushButton_exchange_update)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.pushButton_rates_refresh = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_refresh.setObjectName("pushButton_rates_refresh")

        self.horizontalLayout_21.addWidget(self.pushButton_rates_refresh)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label = QLabel(self.groupBox_rate_commands)
        self.label.setObjectName("label")

        self.horizontalLayout_15.addWidget(self.label)

        self.spinBox_exchange_rate_count_days = QSpinBox(self.groupBox_rate_commands)
        self.spinBox_exchange_rate_count_days.setObjectName("spinBox_exchange_rate_count_days")
        self.spinBox_exchange_rate_count_days.setMaximum(100000)
        self.spinBox_exchange_rate_count_days.setValue(1)

        self.horizontalLayout_15.addWidget(self.spinBox_exchange_rate_count_days)

        self.label_2 = QLabel(self.groupBox_rate_commands)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_15.addWidget(self.label_2)

        self.pushButton_rates_delete = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_delete.setObjectName("pushButton_rates_delete")

        self.horizontalLayout_15.addWidget(self.pushButton_rates_delete)

        self.horizontalLayout_21.addLayout(self.horizontalLayout_15)

        self.verticalLayout_13.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_exchange_item_update = QLabel(self.groupBox_rate_commands)
        self.label_exchange_item_update.setObjectName("label_exchange_item_update")

        self.horizontalLayout_16.addWidget(self.label_exchange_item_update)

        self.comboBox_exchange_item_update = QComboBox(self.groupBox_rate_commands)
        self.comboBox_exchange_item_update.setObjectName("comboBox_exchange_item_update")

        self.horizontalLayout_16.addWidget(self.comboBox_exchange_item_update)

        self.dateEdit_exchange_item_update = QDateEdit(self.groupBox_rate_commands)
        self.dateEdit_exchange_item_update.setObjectName("dateEdit_exchange_item_update")
        self.dateEdit_exchange_item_update.setCalendarPopup(True)

        self.horizontalLayout_16.addWidget(self.dateEdit_exchange_item_update)

        self.label_exchange_item_update_2 = QLabel(self.groupBox_rate_commands)
        self.label_exchange_item_update_2.setObjectName("label_exchange_item_update_2")

        self.horizontalLayout_16.addWidget(self.label_exchange_item_update_2)

        self.doubleSpinBox_exchange_item_update = QDoubleSpinBox(self.groupBox_rate_commands)
        self.doubleSpinBox_exchange_item_update.setObjectName("doubleSpinBox_exchange_item_update")
        self.doubleSpinBox_exchange_item_update.setDecimals(9)
        self.doubleSpinBox_exchange_item_update.setMaximum(10000000.000000000000000)

        self.horizontalLayout_16.addWidget(self.doubleSpinBox_exchange_item_update)

        self.pushButton_exchange_item_update = QPushButton(self.groupBox_rate_commands)
        self.pushButton_exchange_item_update.setObjectName("pushButton_exchange_item_update")

        self.horizontalLayout_16.addWidget(self.pushButton_exchange_item_update)

        self.verticalLayout_13.addLayout(self.horizontalLayout_16)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_3)

        self.horizontalLayout_25.addWidget(self.groupBox_rate_commands)

        self.groupBox_filter_2 = QGroupBox(self.frame_3)
        self.groupBox_filter_2.setObjectName("groupBox_filter_2")
        self.groupBox_filter_2.setMinimumSize(QSize(0, 0))
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_filter_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_currency_filter_2 = QHBoxLayout()
        self.horizontalLayout_currency_filter_2.setObjectName("horizontalLayout_currency_filter_2")
        self.label_filter_currency_2 = QLabel(self.groupBox_filter_2)
        self.label_filter_currency_2.setObjectName("label_filter_currency_2")
        self.label_filter_currency_2.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_filter_2.addWidget(self.label_filter_currency_2)

        self.comboBox_exchange_rates_filter_currency = QComboBox(self.groupBox_filter_2)
        self.comboBox_exchange_rates_filter_currency.setObjectName("comboBox_exchange_rates_filter_currency")
        self.comboBox_exchange_rates_filter_currency.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_currency_filter_2.addWidget(self.comboBox_exchange_rates_filter_currency)

        self.verticalLayout_6.addLayout(self.horizontalLayout_currency_filter_2)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.label_filter_date_2 = QLabel(self.groupBox_filter_2)
        self.label_filter_date_2.setObjectName("label_filter_date_2")
        self.label_filter_date_2.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_22.addWidget(self.label_filter_date_2)

        self.dateEdit_filter_exchange_rates_from = QDateEdit(self.groupBox_filter_2)
        self.dateEdit_filter_exchange_rates_from.setObjectName("dateEdit_filter_exchange_rates_from")
        self.dateEdit_filter_exchange_rates_from.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_exchange_rates_from.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_filter_exchange_rates_from.setCalendarPopup(True)

        self.horizontalLayout_22.addWidget(self.dateEdit_filter_exchange_rates_from)

        self.verticalLayout_6.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.label_filter_to_2 = QLabel(self.groupBox_filter_2)
        self.label_filter_to_2.setObjectName("label_filter_to_2")
        self.label_filter_to_2.setMinimumSize(QSize(61, 0))
        self.label_filter_to_2.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontalLayout_23.addWidget(self.label_filter_to_2)

        self.dateEdit_filter_exchange_rates_to = QDateEdit(self.groupBox_filter_2)
        self.dateEdit_filter_exchange_rates_to.setObjectName("dateEdit_filter_exchange_rates_to")
        self.dateEdit_filter_exchange_rates_to.setMinimumSize(QSize(191, 0))
        self.dateEdit_filter_exchange_rates_to.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_filter_exchange_rates_to.setCalendarPopup(True)

        self.horizontalLayout_23.addWidget(self.dateEdit_filter_exchange_rates_to)

        self.verticalLayout_6.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.pushButton_filter_exchange_rates_clear = QPushButton(self.groupBox_filter_2)
        self.pushButton_filter_exchange_rates_clear.setObjectName("pushButton_filter_exchange_rates_clear")
        self.pushButton_filter_exchange_rates_clear.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_24.addWidget(self.pushButton_filter_exchange_rates_clear)

        self.pushButton_filter_exchange_rates_apply = QPushButton(self.groupBox_filter_2)
        self.pushButton_filter_exchange_rates_apply.setObjectName("pushButton_filter_exchange_rates_apply")
        self.pushButton_filter_exchange_rates_apply.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_24.addWidget(self.pushButton_filter_exchange_rates_apply)

        self.verticalLayout_6.addLayout(self.horizontalLayout_24)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_5)

        self.horizontalLayout_25.addWidget(self.groupBox_filter_2)

        self.verticalLayout_14.addWidget(self.frame_3)

        self.tableView_exchange_rates = QTableView(self.frame_rates)
        self.tableView_exchange_rates.setObjectName("tableView_exchange_rates")

        self.verticalLayout_14.addWidget(self.tableView_exchange_rates)

        self.splitter_exchange_rates.addWidget(self.frame_rates)
        self.widget_exchange_rates_right = QWidget(self.splitter_exchange_rates)
        self.widget_exchange_rates_right.setObjectName("widget_exchange_rates_right")
        self.verticalLayout_12 = QVBoxLayout(self.widget_exchange_rates_right)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.frame_exchange_rates_controls = QFrame(self.widget_exchange_rates_right)
        self.frame_exchange_rates_controls.setObjectName("frame_exchange_rates_controls")
        self.frame_exchange_rates_controls.setMaximumSize(QSize(16777215, 80))
        self.frame_exchange_rates_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_exchange_rates_controls.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_exchange_rates_controls = QHBoxLayout(self.frame_exchange_rates_controls)
        self.horizontalLayout_exchange_rates_controls.setObjectName("horizontalLayout_exchange_rates_controls")
        self.label_exchange_rates_currency = QLabel(self.frame_exchange_rates_controls)
        self.label_exchange_rates_currency.setObjectName("label_exchange_rates_currency")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.label_exchange_rates_currency)

        self.comboBox_exchange_rates_currency = QComboBox(self.frame_exchange_rates_controls)
        self.comboBox_exchange_rates_currency.setObjectName("comboBox_exchange_rates_currency")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.comboBox_exchange_rates_currency)

        self.label_exchange_rates_from = QLabel(self.frame_exchange_rates_controls)
        self.label_exchange_rates_from.setObjectName("label_exchange_rates_from")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.label_exchange_rates_from)

        self.dateEdit_exchange_rates_from = QDateEdit(self.frame_exchange_rates_controls)
        self.dateEdit_exchange_rates_from.setObjectName("dateEdit_exchange_rates_from")
        self.dateEdit_exchange_rates_from.setCalendarPopup(True)

        self.horizontalLayout_exchange_rates_controls.addWidget(self.dateEdit_exchange_rates_from)

        self.label_exchange_rates_to = QLabel(self.frame_exchange_rates_controls)
        self.label_exchange_rates_to.setObjectName("label_exchange_rates_to")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.label_exchange_rates_to)

        self.dateEdit_exchange_rates_to = QDateEdit(self.frame_exchange_rates_controls)
        self.dateEdit_exchange_rates_to.setObjectName("dateEdit_exchange_rates_to")
        self.dateEdit_exchange_rates_to.setCalendarPopup(True)

        self.horizontalLayout_exchange_rates_controls.addWidget(self.dateEdit_exchange_rates_to)

        self.pushButton_exchange_rates_last_month = QPushButton(self.frame_exchange_rates_controls)
        self.pushButton_exchange_rates_last_month.setObjectName("pushButton_exchange_rates_last_month")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.pushButton_exchange_rates_last_month)

        self.pushButton_exchange_rates_last_year = QPushButton(self.frame_exchange_rates_controls)
        self.pushButton_exchange_rates_last_year.setObjectName("pushButton_exchange_rates_last_year")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.pushButton_exchange_rates_last_year)

        self.pushButton_exchange_rates_all_time = QPushButton(self.frame_exchange_rates_controls)
        self.pushButton_exchange_rates_all_time.setObjectName("pushButton_exchange_rates_all_time")

        self.horizontalLayout_exchange_rates_controls.addWidget(self.pushButton_exchange_rates_all_time)

        self.horizontalSpacer_food_stats = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_exchange_rates_controls.addItem(self.horizontalSpacer_food_stats)

        self.verticalLayout_12.addWidget(self.frame_exchange_rates_controls)

        self.scrollArea_xchange_rates = QScrollArea(self.widget_exchange_rates_right)
        self.scrollArea_xchange_rates.setObjectName("scrollArea_xchange_rates")
        self.scrollArea_xchange_rates.setWidgetResizable(True)
        self.scrollAreaWidgetContents_food_stats = QWidget()
        self.scrollAreaWidgetContents_food_stats.setObjectName("scrollAreaWidgetContents_food_stats")
        self.scrollAreaWidgetContents_food_stats.setGeometry(QRect(0, 0, 616, 740))
        self.verticalLayout_exchange_rates_content = QVBoxLayout(self.scrollAreaWidgetContents_food_stats)
        self.verticalLayout_exchange_rates_content.setObjectName("verticalLayout_exchange_rates_content")
        self.scrollArea_xchange_rates.setWidget(self.scrollAreaWidgetContents_food_stats)

        self.verticalLayout_12.addWidget(self.scrollArea_xchange_rates)

        self.splitter_exchange_rates.addWidget(self.widget_exchange_rates_right)

        self.horizontalLayout_14.addWidget(self.splitter_exchange_rates)

        self.tabWidget.addTab(self.tab_exchange_rates, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName("tab_charts")
        self.verticalLayout_18 = QVBoxLayout(self.tab_charts)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.frame_charts_controls = QFrame(self.tab_charts)
        self.frame_charts_controls.setObjectName("frame_charts_controls")
        self.frame_charts_controls.setMaximumSize(QSize(16777215, 120))
        self.frame_charts_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_charts_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_charts_controls = QVBoxLayout(self.frame_charts_controls)
        self.verticalLayout_charts_controls.setObjectName("verticalLayout_charts_controls")
        self.horizontalLayout_charts_controls_1 = QHBoxLayout()
        self.horizontalLayout_charts_controls_1.setObjectName("horizontalLayout_charts_controls_1")
        self.label_chart_category = QLabel(self.frame_charts_controls)
        self.label_chart_category.setObjectName("label_chart_category")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_category)

        self.comboBox_chart_category = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_category.setObjectName("comboBox_chart_category")
        self.comboBox_chart_category.setMinimumSize(QSize(201, 0))

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_category)

        self.label_chart_type = QLabel(self.frame_charts_controls)
        self.label_chart_type.setObjectName("label_chart_type")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_type)

        self.comboBox_chart_type = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.addItem("")
        self.comboBox_chart_type.setObjectName("comboBox_chart_type")
        self.comboBox_chart_type.setMinimumSize(QSize(151, 0))

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_type)

        self.label_chart_period = QLabel(self.frame_charts_controls)
        self.label_chart_period.setObjectName("label_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_period)

        self.comboBox_chart_period = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.addItem("")
        self.comboBox_chart_period.setObjectName("comboBox_chart_period")

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_period)

        self.pushButton_update_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_update_chart.setObjectName("pushButton_update_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_update_chart)

        self.horizontalSpacer_charts = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_1.addItem(self.horizontalSpacer_charts)

        self.pushButton_pie_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_pie_chart.setObjectName("pushButton_pie_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_pie_chart)

        self.pushButton_balance_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_balance_chart.setObjectName("pushButton_balance_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_balance_chart)

        self.verticalLayout_charts_controls.addLayout(self.horizontalLayout_charts_controls_1)

        self.horizontalLayout_charts_controls_2 = QHBoxLayout()
        self.horizontalLayout_charts_controls_2.setObjectName("horizontalLayout_charts_controls_2")
        self.label_chart_from = QLabel(self.frame_charts_controls)
        self.label_chart_from.setObjectName("label_chart_from")

        self.horizontalLayout_charts_controls_2.addWidget(self.label_chart_from)

        self.dateEdit_chart_from = QDateEdit(self.frame_charts_controls)
        self.dateEdit_chart_from.setObjectName("dateEdit_chart_from")
        self.dateEdit_chart_from.setCalendarPopup(True)

        self.horizontalLayout_charts_controls_2.addWidget(self.dateEdit_chart_from)

        self.label_chart_to = QLabel(self.frame_charts_controls)
        self.label_chart_to.setObjectName("label_chart_to")

        self.horizontalLayout_charts_controls_2.addWidget(self.label_chart_to)

        self.dateEdit_chart_to = QDateEdit(self.frame_charts_controls)
        self.dateEdit_chart_to.setObjectName("dateEdit_chart_to")
        self.dateEdit_chart_to.setCalendarPopup(True)

        self.horizontalLayout_charts_controls_2.addWidget(self.dateEdit_chart_to)

        self.pushButton_chart_last_month = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_last_month.setObjectName("pushButton_chart_last_month")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_last_month)

        self.pushButton_chart_last_year = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_last_year.setObjectName("pushButton_chart_last_year")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_last_year)

        self.pushButton_chart_all_time = QPushButton(self.frame_charts_controls)
        self.pushButton_chart_all_time.setObjectName("pushButton_chart_all_time")

        self.horizontalLayout_charts_controls_2.addWidget(self.pushButton_chart_all_time)

        self.horizontalSpacer_charts_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_2.addItem(self.horizontalSpacer_charts_2)

        self.verticalLayout_charts_controls.addLayout(self.horizontalLayout_charts_controls_2)

        self.verticalLayout_18.addWidget(self.frame_charts_controls)

        self.scrollArea_charts = QScrollArea(self.tab_charts)
        self.scrollArea_charts.setObjectName("scrollArea_charts")
        self.scrollArea_charts.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts = QWidget()
        self.scrollAreaWidgetContents_charts.setObjectName("scrollAreaWidgetContents_charts")
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1316, 709))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName("verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_18.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_reports = QWidget()
        self.tab_reports.setObjectName("tab_reports")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_reports)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.frame_5 = QFrame(self.tab_reports)
        self.frame_5.setObjectName("frame_5")
        self.frame_5.setMinimumSize(QSize(300, 0))
        self.frame_5.setMaximumSize(QSize(300, 16777215))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groupBox_10 = QGroupBox(self.frame_5)
        self.groupBox_10.setObjectName("groupBox_10")
        self.groupBox_10.setMinimumSize(QSize(0, 0))
        self.verticalLayout_19 = QVBoxLayout(self.groupBox_10)
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.comboBox_report_type = QComboBox(self.groupBox_10)
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.addItem("")
        self.comboBox_report_type.setObjectName("comboBox_report_type")

        self.verticalLayout_19.addWidget(self.comboBox_report_type)

        self.pushButton_generate_report = QPushButton(self.groupBox_10)
        self.pushButton_generate_report.setObjectName("pushButton_generate_report")

        self.verticalLayout_19.addWidget(self.pushButton_generate_report)

        self.verticalLayout_7.addWidget(self.groupBox_10)

        self.groupBox_summary = QGroupBox(self.frame_5)
        self.groupBox_summary.setObjectName("groupBox_summary")
        self.verticalLayout_summary = QVBoxLayout(self.groupBox_summary)
        self.verticalLayout_summary.setObjectName("verticalLayout_summary")
        self.label_total_income = QLabel(self.groupBox_summary)
        self.label_total_income.setObjectName("label_total_income")
        self.label_total_income.setStyleSheet("color: #4CAF50; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_income)

        self.label_total_expenses = QLabel(self.groupBox_summary)
        self.label_total_expenses.setObjectName("label_total_expenses")
        self.label_total_expenses.setStyleSheet("color: red; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_expenses)

        self.verticalLayout_7.addWidget(self.groupBox_summary)

        self.groupBox_daily_balance = QGroupBox(self.frame_5)
        self.groupBox_daily_balance.setObjectName("groupBox_daily_balance")
        self.groupBox_daily_balance.setMinimumSize(QSize(0, 100))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_daily_balance)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_daily_balance = QLabel(self.groupBox_daily_balance)
        self.label_daily_balance.setObjectName("label_daily_balance")
        self.label_daily_balance.setFont(font2)
        self.label_daily_balance.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_daily_balance)

        self.verticalLayout_7.addWidget(self.groupBox_daily_balance)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_4)

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tableView_reports = QTableView(self.tab_reports)
        self.tableView_reports.setObjectName("tableView_reports")

        self.horizontalLayout_6.addWidget(self.tableView_reports)

        self.tabWidget.addTab(self.tab_reports, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1360, 21))
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
