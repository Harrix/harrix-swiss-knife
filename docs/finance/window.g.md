---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `Ui_MainWindow`](#%EF%B8%8F-class-ui_mainwindow)
  - [⚙️ Method `retranslateUi`](#%EF%B8%8F-method-retranslateui)
  - [⚙️ Method `setupUi`](#%EF%B8%8F-method-setupui)

</details>

## 🏛️ Class `Ui_MainWindow`

```python
class Ui_MainWindow(object)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Finance Tracker", None))
        self.groupBox_transaction.setTitle(QCoreApplication.translate("MainWindow", "Transaction Details", None))
        self.radioButton_income.setText(QCoreApplication.translate("MainWindow", "Income", None))
        self.radioButton_expense.setText(QCoreApplication.translate("MainWindow", "Expense", None))
        self.radioButton_transfer.setText(QCoreApplication.translate("MainWindow", "Transfer", None))
        # if QT_CONFIG(tooltip)
        self.comboBox_account.setToolTip(QCoreApplication.translate("MainWindow", "Select account (optional)", None))
        # endif // QT_CONFIG(tooltip)
        self.lineEdit_description.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Description (optional)", None)
        )
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add Transaction", None))
        self.groupBox_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", "Filter", None))
        self.label_filter_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.label_filter_currency.setText(QCoreApplication.translate("MainWindow", "Currency:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", "Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", "Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", "Apply Filter", None))
        self.groupBox_daily_balance.setTitle(QCoreApplication.translate("MainWindow", "Today's Balance", None))
        self.label_daily_balance.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.label_categories.setText(QCoreApplication.translate("MainWindow", "Categories:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_transactions),
            QCoreApplication.translate("MainWindow", "Transactions", None),
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Category", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_category_type.setItemText(0, QCoreApplication.translate("MainWindow", "Expense", None))
        self.comboBox_category_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))
        self.comboBox_category_type.setItemText(2, QCoreApplication.translate("MainWindow", "Transfer", None))

        self.pushButton_category_add.setText(QCoreApplication.translate("MainWindow", "Add Category", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_categories_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_categories_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_categories), QCoreApplication.translate("MainWindow", "Categories", None)
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
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_accounts), QCoreApplication.translate("MainWindow", "Accounts", None)
        )
        self.groupBox_add_currency.setTitle(QCoreApplication.translate("MainWindow", "Add New Currency", None))
        self.label_currency_code.setText(QCoreApplication.translate("MainWindow", "Code:", None))
        self.lineEdit_currency_code.setPlaceholderText(QCoreApplication.translate("MainWindow", "USD, EUR, RUB", None))
        self.label_currency_name.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.lineEdit_currency_name.setPlaceholderText(QCoreApplication.translate("MainWindow", "US Dollar", None))
        self.label_currency_symbol.setText(QCoreApplication.translate("MainWindow", "Symbol:", None))
        self.lineEdit_currency_symbol.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "$, \u20ac, \u20bd", None)
        )
        self.pushButton_currency_add.setText(QCoreApplication.translate("MainWindow", "Add Currency", None))
        self.groupBox_default_currency.setTitle(QCoreApplication.translate("MainWindow", "Default Currency", None))
        self.pushButton_set_default_currency.setText(QCoreApplication.translate("MainWindow", "Set Default", None))
        self.groupBox_currency_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_currencies_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_currencies_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_currencies), QCoreApplication.translate("MainWindow", "Currencies", None)
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
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_exchange),
            QCoreApplication.translate("MainWindow", "Currency Exchange", None),
        )
        self.groupBox_add_rate.setTitle(QCoreApplication.translate("MainWindow", "Add Exchange Rate", None))
        self.label_rate_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.label_rate_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.label_rate_value.setText(QCoreApplication.translate("MainWindow", "Rate:", None))
        self.label_rate_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_rate.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_rate_add.setText(QCoreApplication.translate("MainWindow", "Add Rate", None))
        self.groupBox_rate_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_rates_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_rates_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_exchange_rates),
            QCoreApplication.translate("MainWindow", "Exchange Rates", None),
        )
        self.label_chart_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_chart_type.setItemText(0, QCoreApplication.translate("MainWindow", "All", None))
        self.comboBox_chart_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))
        self.comboBox_chart_type.setItemText(2, QCoreApplication.translate("MainWindow", "Expense", None))
        self.comboBox_chart_type.setItemText(3, QCoreApplication.translate("MainWindow", "Transfer", None))

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
        self.label_net_balance.setText(QCoreApplication.translate("MainWindow", "Net Balance: 0.00\u20bd", None))
        self.label_total_accounts.setText(
            QCoreApplication.translate("MainWindow", "Total in Accounts: 0.00\u20bd", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MainWindow", "Reports", None)
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 950)
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
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_transaction = QGroupBox(self.frame)
        self.groupBox_transaction.setObjectName("groupBox_transaction")
        self.groupBox_transaction.setMinimumSize(QSize(0, 350))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_transaction)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_type = QHBoxLayout()
        self.horizontalLayout_type.setObjectName("horizontalLayout_type")
        self.radioButton_income = QRadioButton(self.groupBox_transaction)
        self.radioButton_income.setObjectName("radioButton_income")
        self.radioButton_income.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: green;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )

        self.horizontalLayout_type.addWidget(self.radioButton_income)

        self.radioButton_expense = QRadioButton(self.groupBox_transaction)
        self.radioButton_expense.setObjectName("radioButton_expense")
        self.radioButton_expense.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: red;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )
        self.radioButton_expense.setChecked(True)

        self.horizontalLayout_type.addWidget(self.radioButton_expense)

        self.radioButton_transfer = QRadioButton(self.groupBox_transaction)
        self.radioButton_transfer.setObjectName("radioButton_transfer")
        self.radioButton_transfer.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: blue;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )

        self.horizontalLayout_type.addWidget(self.radioButton_transfer)

        self.verticalLayout_5.addLayout(self.horizontalLayout_type)

        self.horizontalLayout_amount = QHBoxLayout()
        self.horizontalLayout_amount.setObjectName("horizontalLayout_amount")
        self.doubleSpinBox_amount = QDoubleSpinBox(self.groupBox_transaction)
        self.doubleSpinBox_amount.setObjectName("doubleSpinBox_amount")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.doubleSpinBox_amount.setFont(font)
        self.doubleSpinBox_amount.setStyleSheet(
            "QDoubleSpinBox {\n"
            "                                          background-color: lightblue;\n"
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

        self.verticalLayout_5.addLayout(self.horizontalLayout_amount)

        self.comboBox_category = QComboBox(self.groupBox_transaction)
        self.comboBox_category.setObjectName("comboBox_category")

        self.verticalLayout_5.addWidget(self.comboBox_category)

        self.comboBox_account = QComboBox(self.groupBox_transaction)
        self.comboBox_account.setObjectName("comboBox_account")

        self.verticalLayout_5.addWidget(self.comboBox_account)

        self.lineEdit_description = QLineEdit(self.groupBox_transaction)
        self.lineEdit_description.setObjectName("lineEdit_description")

        self.verticalLayout_5.addWidget(self.lineEdit_description)

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

        self.verticalLayout_5.addLayout(self.horizontalLayout_date)

        self.pushButton_add = QPushButton(self.groupBox_transaction)
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 41))
        self.pushButton_add.setFont(font)
        self.pushButton_add.setStyleSheet(
            "QPushButton {\n"
            "                                      background-color: lightgreen;\n"
            "                                      border: 1px solid #4CAF50;\n"
            "                                      border-radius: 4px;\n"
            "                                      }\n"
            "                                      QPushButton:hover {\n"
            "                                      background-color: #90EE90;\n"
            "                                      }\n"
            "                                      QPushButton:pressed {\n"
            "                                      background-color: #7FDD7F;\n"
            "                                      }"
        )

        self.verticalLayout_5.addWidget(self.pushButton_add)

        self.verticalLayout_3.addWidget(self.groupBox_transaction)

        self.groupBox_commands = QGroupBox(self.frame)
        self.groupBox_commands.setObjectName("groupBox_commands")
        self.groupBox_commands.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_commands)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_commands)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_refresh = QPushButton(self.groupBox_commands)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3.addWidget(self.groupBox_commands)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 250))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
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

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_filter_type = QLabel(self.groupBox_filter)
        self.label_filter_type.setObjectName("label_filter_type")
        self.label_filter_type.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_10.addWidget(self.label_filter_type)

        self.comboBox_filter_type = QComboBox(self.groupBox_filter)
        self.comboBox_filter_type.setObjectName("comboBox_filter_type")
        self.comboBox_filter_type.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_10.addWidget(self.comboBox_filter_type)

        self.verticalLayout_4.addLayout(self.horizontalLayout_10)

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

        self.horizontalLayout_7.addWidget(self.pushButton_clear_filter)

        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName("pushButton_apply_filter")

        self.horizontalLayout_7.addWidget(self.pushButton_apply_filter)

        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.verticalLayout_3.addWidget(self.groupBox_filter)

        self.groupBox_daily_balance = QGroupBox(self.frame)
        self.groupBox_daily_balance.setObjectName("groupBox_daily_balance")
        self.groupBox_daily_balance.setMinimumSize(QSize(0, 100))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_daily_balance)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_daily_balance = QLabel(self.groupBox_daily_balance)
        self.label_daily_balance.setObjectName("label_daily_balance")
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        self.label_daily_balance.setFont(font1)
        self.label_daily_balance.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_daily_balance)

        self.verticalLayout_3.addWidget(self.groupBox_daily_balance)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

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
            "                                }"
        )

        self.verticalLayout.addWidget(self.listView_categories)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_transactions = QTableView(self.splitter)
        self.tableView_transactions.setObjectName("tableView_transactions")
        self.splitter.addWidget(self.tableView_transactions)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_transactions, "")
        self.tab_categories = QWidget()
        self.tab_categories.setObjectName("tab_categories")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_categories)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView_categories = QTableView(self.tab_categories)
        self.tableView_categories.setObjectName("tableView_categories")

        self.horizontalLayout_4.addWidget(self.tableView_categories)

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

        self.verticalLayout_15.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_2)

        self.horizontalLayout_4.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_categories, "")
        self.tab_accounts = QWidget()
        self.tab_accounts.setObjectName("tab_accounts")
        self.horizontalLayout_accounts = QHBoxLayout(self.tab_accounts)
        self.horizontalLayout_accounts.setObjectName("horizontalLayout_accounts")
        self.tableView_accounts = QTableView(self.tab_accounts)
        self.tableView_accounts.setObjectName("tableView_accounts")

        self.horizontalLayout_accounts.addWidget(self.tableView_accounts)

        self.frame_accounts = QFrame(self.tab_accounts)
        self.frame_accounts.setObjectName("frame_accounts")
        self.frame_accounts.setMinimumSize(QSize(300, 0))
        self.frame_accounts.setMaximumSize(QSize(300, 16777215))
        self.frame_accounts.setFrameShape(QFrame.StyledPanel)
        self.frame_accounts.setFrameShadow(QFrame.Raised)
        self.verticalLayout_accounts = QVBoxLayout(self.frame_accounts)
        self.verticalLayout_accounts.setObjectName("verticalLayout_accounts")
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

        self.verticalLayout_accounts.addWidget(self.groupBox_add_account)

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

        self.verticalLayout_accounts.addWidget(self.groupBox_account_commands)

        self.verticalSpacer_accounts = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_accounts.addItem(self.verticalSpacer_accounts)

        self.horizontalLayout_accounts.addWidget(self.frame_accounts)

        self.tabWidget.addTab(self.tab_accounts, "")
        self.tab_currencies = QWidget()
        self.tab_currencies.setObjectName("tab_currencies")
        self.horizontalLayout_currencies = QHBoxLayout(self.tab_currencies)
        self.horizontalLayout_currencies.setObjectName("horizontalLayout_currencies")
        self.tableView_currencies = QTableView(self.tab_currencies)
        self.tableView_currencies.setObjectName("tableView_currencies")

        self.horizontalLayout_currencies.addWidget(self.tableView_currencies)

        self.frame_currencies = QFrame(self.tab_currencies)
        self.frame_currencies.setObjectName("frame_currencies")
        self.frame_currencies.setMinimumSize(QSize(300, 0))
        self.frame_currencies.setMaximumSize(QSize(300, 16777215))
        self.frame_currencies.setFrameShape(QFrame.StyledPanel)
        self.frame_currencies.setFrameShadow(QFrame.Raised)
        self.verticalLayout_currencies = QVBoxLayout(self.frame_currencies)
        self.verticalLayout_currencies.setObjectName("verticalLayout_currencies")
        self.groupBox_add_currency = QGroupBox(self.frame_currencies)
        self.groupBox_add_currency.setObjectName("groupBox_add_currency")
        self.verticalLayout_add_currency = QVBoxLayout(self.groupBox_add_currency)
        self.verticalLayout_add_currency.setObjectName("verticalLayout_add_currency")
        self.horizontalLayout_currency_code = QHBoxLayout()
        self.horizontalLayout_currency_code.setObjectName("horizontalLayout_currency_code")
        self.label_currency_code = QLabel(self.groupBox_add_currency)
        self.label_currency_code.setObjectName("label_currency_code")
        self.label_currency_code.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_code.addWidget(self.label_currency_code)

        self.lineEdit_currency_code = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_code.setObjectName("lineEdit_currency_code")
        self.lineEdit_currency_code.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_code.addWidget(self.lineEdit_currency_code)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_code)

        self.horizontalLayout_currency_name = QHBoxLayout()
        self.horizontalLayout_currency_name.setObjectName("horizontalLayout_currency_name")
        self.label_currency_name = QLabel(self.groupBox_add_currency)
        self.label_currency_name.setObjectName("label_currency_name")
        self.label_currency_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_name.addWidget(self.label_currency_name)

        self.lineEdit_currency_name = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_name.setObjectName("lineEdit_currency_name")
        self.lineEdit_currency_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_name.addWidget(self.lineEdit_currency_name)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_name)

        self.horizontalLayout_currency_symbol = QHBoxLayout()
        self.horizontalLayout_currency_symbol.setObjectName("horizontalLayout_currency_symbol")
        self.label_currency_symbol = QLabel(self.groupBox_add_currency)
        self.label_currency_symbol.setObjectName("label_currency_symbol")
        self.label_currency_symbol.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.label_currency_symbol)

        self.lineEdit_currency_symbol = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_symbol.setObjectName("lineEdit_currency_symbol")
        self.lineEdit_currency_symbol.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.lineEdit_currency_symbol)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_symbol)

        self.horizontalLayout_currency_add = QHBoxLayout()
        self.horizontalLayout_currency_add.setObjectName("horizontalLayout_currency_add")
        self.horizontalSpacer_currency = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_currency_add.addItem(self.horizontalSpacer_currency)

        self.pushButton_currency_add = QPushButton(self.groupBox_add_currency)
        self.pushButton_currency_add.setObjectName("pushButton_currency_add")

        self.horizontalLayout_currency_add.addWidget(self.pushButton_currency_add)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_add)

        self.verticalLayout_currencies.addWidget(self.groupBox_add_currency)

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

        self.verticalLayout_currencies.addWidget(self.groupBox_default_currency)

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

        self.verticalLayout_currencies.addWidget(self.groupBox_currency_commands)

        self.verticalSpacer_currencies = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_currencies.addItem(self.verticalSpacer_currencies)

        self.horizontalLayout_currencies.addWidget(self.frame_currencies)

        self.tabWidget.addTab(self.tab_currencies, "")
        self.tab_exchange = QWidget()
        self.tab_exchange.setObjectName("tab_exchange")
        self.horizontalLayout_exchange = QHBoxLayout(self.tab_exchange)
        self.horizontalLayout_exchange.setObjectName("horizontalLayout_exchange")
        self.tableView_exchange = QTableView(self.tab_exchange)
        self.tableView_exchange.setObjectName("tableView_exchange")

        self.horizontalLayout_exchange.addWidget(self.tableView_exchange)

        self.frame_exchange = QFrame(self.tab_exchange)
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
        self.dateEdit_exchange.setMinimumSize(QSize(191, 0))
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
            "                                    background-color: lightblue;\n"
            "                                    border: 1px solid #2196F3;\n"
            "                                    border-radius: 4px;\n"
            "                                    }\n"
            "                                    QPushButton:hover {\n"
            "                                    background-color: #87CEEB;\n"
            "                                    }\n"
            "                                    QPushButton:pressed {\n"
            "                                    background-color: #6BB6FF;\n"
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

        self.horizontalLayout_exchange.addWidget(self.frame_exchange)

        self.tabWidget.addTab(self.tab_exchange, "")
        self.tab_exchange_rates = QWidget()
        self.tab_exchange_rates.setObjectName("tab_exchange_rates")
        self.horizontalLayout_rates = QHBoxLayout(self.tab_exchange_rates)
        self.horizontalLayout_rates.setObjectName("horizontalLayout_rates")
        self.tableView_exchange_rates = QTableView(self.tab_exchange_rates)
        self.tableView_exchange_rates.setObjectName("tableView_exchange_rates")

        self.horizontalLayout_rates.addWidget(self.tableView_exchange_rates)

        self.frame_rates = QFrame(self.tab_exchange_rates)
        self.frame_rates.setObjectName("frame_rates")
        self.frame_rates.setMinimumSize(QSize(300, 0))
        self.frame_rates.setMaximumSize(QSize(300, 16777215))
        self.frame_rates.setFrameShape(QFrame.StyledPanel)
        self.frame_rates.setFrameShadow(QFrame.Raised)
        self.verticalLayout_rates = QVBoxLayout(self.frame_rates)
        self.verticalLayout_rates.setObjectName("verticalLayout_rates")
        self.groupBox_add_rate = QGroupBox(self.frame_rates)
        self.groupBox_add_rate.setObjectName("groupBox_add_rate")
        self.verticalLayout_add_rate = QVBoxLayout(self.groupBox_add_rate)
        self.verticalLayout_add_rate.setObjectName("verticalLayout_add_rate")
        self.horizontalLayout_rate_from = QHBoxLayout()
        self.horizontalLayout_rate_from.setObjectName("horizontalLayout_rate_from")
        self.label_rate_from = QLabel(self.groupBox_add_rate)
        self.label_rate_from.setObjectName("label_rate_from")
        self.label_rate_from.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_from.addWidget(self.label_rate_from)

        self.comboBox_rate_from = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_from.setObjectName("comboBox_rate_from")
        self.comboBox_rate_from.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_from.addWidget(self.comboBox_rate_from)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_from)

        self.horizontalLayout_rate_to = QHBoxLayout()
        self.horizontalLayout_rate_to.setObjectName("horizontalLayout_rate_to")
        self.label_rate_to = QLabel(self.groupBox_add_rate)
        self.label_rate_to.setObjectName("label_rate_to")
        self.label_rate_to.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_to.addWidget(self.label_rate_to)

        self.comboBox_rate_to = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_to.setObjectName("comboBox_rate_to")
        self.comboBox_rate_to.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_to.addWidget(self.comboBox_rate_to)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_to)

        self.horizontalLayout_rate_value = QHBoxLayout()
        self.horizontalLayout_rate_value.setObjectName("horizontalLayout_rate_value")
        self.label_rate_value = QLabel(self.groupBox_add_rate)
        self.label_rate_value.setObjectName("label_rate_value")
        self.label_rate_value.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_value.addWidget(self.label_rate_value)

        self.doubleSpinBox_rate_value = QDoubleSpinBox(self.groupBox_add_rate)
        self.doubleSpinBox_rate_value.setObjectName("doubleSpinBox_rate_value")
        self.doubleSpinBox_rate_value.setMinimumSize(QSize(170, 0))
        self.doubleSpinBox_rate_value.setMaximum(999999.989999999990687)
        self.doubleSpinBox_rate_value.setValue(73.500000000000000)

        self.horizontalLayout_rate_value.addWidget(self.doubleSpinBox_rate_value)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_value)

        self.horizontalLayout_rate_date = QHBoxLayout()
        self.horizontalLayout_rate_date.setObjectName("horizontalLayout_rate_date")
        self.label_rate_date = QLabel(self.groupBox_add_rate)
        self.label_rate_date.setObjectName("label_rate_date")
        self.label_rate_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_date.addWidget(self.label_rate_date)

        self.dateEdit_rate = QDateEdit(self.groupBox_add_rate)
        self.dateEdit_rate.setObjectName("dateEdit_rate")
        self.dateEdit_rate.setMinimumSize(QSize(170, 0))
        self.dateEdit_rate.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_rate.setCalendarPopup(True)

        self.horizontalLayout_rate_date.addWidget(self.dateEdit_rate)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_date)

        self.horizontalLayout_rate_add = QHBoxLayout()
        self.horizontalLayout_rate_add.setObjectName("horizontalLayout_rate_add")
        self.horizontalSpacer_rate = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_rate_add.addItem(self.horizontalSpacer_rate)

        self.pushButton_rate_add = QPushButton(self.groupBox_add_rate)
        self.pushButton_rate_add.setObjectName("pushButton_rate_add")

        self.horizontalLayout_rate_add.addWidget(self.pushButton_rate_add)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_add)

        self.verticalLayout_rates.addWidget(self.groupBox_add_rate)

        self.groupBox_rate_commands = QGroupBox(self.frame_rates)
        self.groupBox_rate_commands.setObjectName("groupBox_rate_commands")
        self.verticalLayout_rate_commands = QVBoxLayout(self.groupBox_rate_commands)
        self.verticalLayout_rate_commands.setObjectName("verticalLayout_rate_commands")
        self.horizontalLayout_rate_commands = QHBoxLayout()
        self.horizontalLayout_rate_commands.setObjectName("horizontalLayout_rate_commands")
        self.pushButton_rates_delete = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_delete.setObjectName("pushButton_rates_delete")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_delete)

        self.pushButton_rates_refresh = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_refresh.setObjectName("pushButton_rates_refresh")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_refresh)

        self.verticalLayout_rate_commands.addLayout(self.horizontalLayout_rate_commands)

        self.verticalLayout_rates.addWidget(self.groupBox_rate_commands)

        self.verticalSpacer_rates = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_rates.addItem(self.verticalSpacer_rates)

        self.horizontalLayout_rates.addWidget(self.frame_rates)

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
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1356, 751))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName("verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_18.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_reports = QWidget()
        self.tab_reports.setObjectName("tab_reports")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_reports)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tableView_reports = QTableView(self.tab_reports)
        self.tableView_reports.setObjectName("tableView_reports")

        self.horizontalLayout_6.addWidget(self.tableView_reports)

        self.frame_5 = QFrame(self.tab_reports)
        self.frame_5.setObjectName("frame_5")
        self.frame_5.setMinimumSize(QSize(300, 0))
        self.frame_5.setMaximumSize(QSize(300, 16777215))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_5)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
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

        self.verticalLayout_16.addWidget(self.groupBox_10)

        self.groupBox_summary = QGroupBox(self.frame_5)
        self.groupBox_summary.setObjectName("groupBox_summary")
        self.verticalLayout_summary = QVBoxLayout(self.groupBox_summary)
        self.verticalLayout_summary.setObjectName("verticalLayout_summary")
        self.label_total_income = QLabel(self.groupBox_summary)
        self.label_total_income.setObjectName("label_total_income")
        self.label_total_income.setStyleSheet("color: green; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_income)

        self.label_total_expenses = QLabel(self.groupBox_summary)
        self.label_total_expenses.setObjectName("label_total_expenses")
        self.label_total_expenses.setStyleSheet("color: red; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_expenses)

        self.label_net_balance = QLabel(self.groupBox_summary)
        self.label_net_balance.setObjectName("label_net_balance")
        self.label_net_balance.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.verticalLayout_summary.addWidget(self.label_net_balance)

        self.label_total_accounts = QLabel(self.groupBox_summary)
        self.label_total_accounts.setObjectName("label_total_accounts")
        self.label_total_accounts.setStyleSheet("color: blue; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_accounts)

        self.verticalLayout_16.addWidget(self.groupBox_summary)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_reports, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1400, 21))
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
```

</details>

### ⚙️ Method `retranslateUi`

```python
def retranslateUi(self, MainWindow)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Finance Tracker", None))
        self.groupBox_transaction.setTitle(QCoreApplication.translate("MainWindow", "Transaction Details", None))
        self.radioButton_income.setText(QCoreApplication.translate("MainWindow", "Income", None))
        self.radioButton_expense.setText(QCoreApplication.translate("MainWindow", "Expense", None))
        self.radioButton_transfer.setText(QCoreApplication.translate("MainWindow", "Transfer", None))
        # if QT_CONFIG(tooltip)
        self.comboBox_account.setToolTip(QCoreApplication.translate("MainWindow", "Select account (optional)", None))
        # endif // QT_CONFIG(tooltip)
        self.lineEdit_description.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Description (optional)", None)
        )
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add Transaction", None))
        self.groupBox_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", "Filter", None))
        self.label_filter_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.label_filter_currency.setText(QCoreApplication.translate("MainWindow", "Currency:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", "Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", "Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", "Apply Filter", None))
        self.groupBox_daily_balance.setTitle(QCoreApplication.translate("MainWindow", "Today's Balance", None))
        self.label_daily_balance.setText(QCoreApplication.translate("MainWindow", "0.00\u20bd", None))
        self.label_categories.setText(QCoreApplication.translate("MainWindow", "Categories:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_transactions),
            QCoreApplication.translate("MainWindow", "Transactions", None),
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Category", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_category_type.setItemText(0, QCoreApplication.translate("MainWindow", "Expense", None))
        self.comboBox_category_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))
        self.comboBox_category_type.setItemText(2, QCoreApplication.translate("MainWindow", "Transfer", None))

        self.pushButton_category_add.setText(QCoreApplication.translate("MainWindow", "Add Category", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_categories_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_categories_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_categories), QCoreApplication.translate("MainWindow", "Categories", None)
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
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_accounts), QCoreApplication.translate("MainWindow", "Accounts", None)
        )
        self.groupBox_add_currency.setTitle(QCoreApplication.translate("MainWindow", "Add New Currency", None))
        self.label_currency_code.setText(QCoreApplication.translate("MainWindow", "Code:", None))
        self.lineEdit_currency_code.setPlaceholderText(QCoreApplication.translate("MainWindow", "USD, EUR, RUB", None))
        self.label_currency_name.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.lineEdit_currency_name.setPlaceholderText(QCoreApplication.translate("MainWindow", "US Dollar", None))
        self.label_currency_symbol.setText(QCoreApplication.translate("MainWindow", "Symbol:", None))
        self.lineEdit_currency_symbol.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "$, \u20ac, \u20bd", None)
        )
        self.pushButton_currency_add.setText(QCoreApplication.translate("MainWindow", "Add Currency", None))
        self.groupBox_default_currency.setTitle(QCoreApplication.translate("MainWindow", "Default Currency", None))
        self.pushButton_set_default_currency.setText(QCoreApplication.translate("MainWindow", "Set Default", None))
        self.groupBox_currency_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_currencies_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_currencies_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_currencies), QCoreApplication.translate("MainWindow", "Currencies", None)
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
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_exchange),
            QCoreApplication.translate("MainWindow", "Currency Exchange", None),
        )
        self.groupBox_add_rate.setTitle(QCoreApplication.translate("MainWindow", "Add Exchange Rate", None))
        self.label_rate_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.label_rate_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.label_rate_value.setText(QCoreApplication.translate("MainWindow", "Rate:", None))
        self.label_rate_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_rate.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_rate_add.setText(QCoreApplication.translate("MainWindow", "Add Rate", None))
        self.groupBox_rate_commands.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_rates_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_rates_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_exchange_rates),
            QCoreApplication.translate("MainWindow", "Exchange Rates", None),
        )
        self.label_chart_category.setText(QCoreApplication.translate("MainWindow", "Category:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.comboBox_chart_type.setItemText(0, QCoreApplication.translate("MainWindow", "All", None))
        self.comboBox_chart_type.setItemText(1, QCoreApplication.translate("MainWindow", "Income", None))
        self.comboBox_chart_type.setItemText(2, QCoreApplication.translate("MainWindow", "Expense", None))
        self.comboBox_chart_type.setItemText(3, QCoreApplication.translate("MainWindow", "Transfer", None))

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
        self.label_net_balance.setText(QCoreApplication.translate("MainWindow", "Net Balance: 0.00\u20bd", None))
        self.label_total_accounts.setText(
            QCoreApplication.translate("MainWindow", "Total in Accounts: 0.00\u20bd", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MainWindow", "Reports", None)
        )
```

</details>

### ⚙️ Method `setupUi`

```python
def setupUi(self, MainWindow)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 950)
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
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_transaction = QGroupBox(self.frame)
        self.groupBox_transaction.setObjectName("groupBox_transaction")
        self.groupBox_transaction.setMinimumSize(QSize(0, 350))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_transaction)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_type = QHBoxLayout()
        self.horizontalLayout_type.setObjectName("horizontalLayout_type")
        self.radioButton_income = QRadioButton(self.groupBox_transaction)
        self.radioButton_income.setObjectName("radioButton_income")
        self.radioButton_income.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: green;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )

        self.horizontalLayout_type.addWidget(self.radioButton_income)

        self.radioButton_expense = QRadioButton(self.groupBox_transaction)
        self.radioButton_expense.setObjectName("radioButton_expense")
        self.radioButton_expense.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: red;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )
        self.radioButton_expense.setChecked(True)

        self.horizontalLayout_type.addWidget(self.radioButton_expense)

        self.radioButton_transfer = QRadioButton(self.groupBox_transaction)
        self.radioButton_transfer.setObjectName("radioButton_transfer")
        self.radioButton_transfer.setStyleSheet(
            "QRadioButton {\n"
            "                                          color: blue;\n"
            "                                          font-weight: bold;\n"
            "                                          }"
        )

        self.horizontalLayout_type.addWidget(self.radioButton_transfer)

        self.verticalLayout_5.addLayout(self.horizontalLayout_type)

        self.horizontalLayout_amount = QHBoxLayout()
        self.horizontalLayout_amount.setObjectName("horizontalLayout_amount")
        self.doubleSpinBox_amount = QDoubleSpinBox(self.groupBox_transaction)
        self.doubleSpinBox_amount.setObjectName("doubleSpinBox_amount")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.doubleSpinBox_amount.setFont(font)
        self.doubleSpinBox_amount.setStyleSheet(
            "QDoubleSpinBox {\n"
            "                                          background-color: lightblue;\n"
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

        self.verticalLayout_5.addLayout(self.horizontalLayout_amount)

        self.comboBox_category = QComboBox(self.groupBox_transaction)
        self.comboBox_category.setObjectName("comboBox_category")

        self.verticalLayout_5.addWidget(self.comboBox_category)

        self.comboBox_account = QComboBox(self.groupBox_transaction)
        self.comboBox_account.setObjectName("comboBox_account")

        self.verticalLayout_5.addWidget(self.comboBox_account)

        self.lineEdit_description = QLineEdit(self.groupBox_transaction)
        self.lineEdit_description.setObjectName("lineEdit_description")

        self.verticalLayout_5.addWidget(self.lineEdit_description)

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

        self.verticalLayout_5.addLayout(self.horizontalLayout_date)

        self.pushButton_add = QPushButton(self.groupBox_transaction)
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 41))
        self.pushButton_add.setFont(font)
        self.pushButton_add.setStyleSheet(
            "QPushButton {\n"
            "                                      background-color: lightgreen;\n"
            "                                      border: 1px solid #4CAF50;\n"
            "                                      border-radius: 4px;\n"
            "                                      }\n"
            "                                      QPushButton:hover {\n"
            "                                      background-color: #90EE90;\n"
            "                                      }\n"
            "                                      QPushButton:pressed {\n"
            "                                      background-color: #7FDD7F;\n"
            "                                      }"
        )

        self.verticalLayout_5.addWidget(self.pushButton_add)

        self.verticalLayout_3.addWidget(self.groupBox_transaction)

        self.groupBox_commands = QGroupBox(self.frame)
        self.groupBox_commands.setObjectName("groupBox_commands")
        self.groupBox_commands.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_commands)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_commands)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_refresh = QPushButton(self.groupBox_commands)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3.addWidget(self.groupBox_commands)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 250))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
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

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_filter_type = QLabel(self.groupBox_filter)
        self.label_filter_type.setObjectName("label_filter_type")
        self.label_filter_type.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_10.addWidget(self.label_filter_type)

        self.comboBox_filter_type = QComboBox(self.groupBox_filter)
        self.comboBox_filter_type.setObjectName("comboBox_filter_type")
        self.comboBox_filter_type.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_10.addWidget(self.comboBox_filter_type)

        self.verticalLayout_4.addLayout(self.horizontalLayout_10)

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

        self.horizontalLayout_7.addWidget(self.pushButton_clear_filter)

        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName("pushButton_apply_filter")

        self.horizontalLayout_7.addWidget(self.pushButton_apply_filter)

        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.verticalLayout_3.addWidget(self.groupBox_filter)

        self.groupBox_daily_balance = QGroupBox(self.frame)
        self.groupBox_daily_balance.setObjectName("groupBox_daily_balance")
        self.groupBox_daily_balance.setMinimumSize(QSize(0, 100))
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_daily_balance)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_daily_balance = QLabel(self.groupBox_daily_balance)
        self.label_daily_balance.setObjectName("label_daily_balance")
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        self.label_daily_balance.setFont(font1)
        self.label_daily_balance.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_daily_balance)

        self.verticalLayout_3.addWidget(self.groupBox_daily_balance)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

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
            "                                }"
        )

        self.verticalLayout.addWidget(self.listView_categories)

        self.splitter.addWidget(self.widget_middle)
        self.tableView_transactions = QTableView(self.splitter)
        self.tableView_transactions.setObjectName("tableView_transactions")
        self.splitter.addWidget(self.tableView_transactions)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_transactions, "")
        self.tab_categories = QWidget()
        self.tab_categories.setObjectName("tab_categories")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_categories)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView_categories = QTableView(self.tab_categories)
        self.tableView_categories.setObjectName("tableView_categories")

        self.horizontalLayout_4.addWidget(self.tableView_categories)

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

        self.verticalLayout_15.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_2)

        self.horizontalLayout_4.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_categories, "")
        self.tab_accounts = QWidget()
        self.tab_accounts.setObjectName("tab_accounts")
        self.horizontalLayout_accounts = QHBoxLayout(self.tab_accounts)
        self.horizontalLayout_accounts.setObjectName("horizontalLayout_accounts")
        self.tableView_accounts = QTableView(self.tab_accounts)
        self.tableView_accounts.setObjectName("tableView_accounts")

        self.horizontalLayout_accounts.addWidget(self.tableView_accounts)

        self.frame_accounts = QFrame(self.tab_accounts)
        self.frame_accounts.setObjectName("frame_accounts")
        self.frame_accounts.setMinimumSize(QSize(300, 0))
        self.frame_accounts.setMaximumSize(QSize(300, 16777215))
        self.frame_accounts.setFrameShape(QFrame.StyledPanel)
        self.frame_accounts.setFrameShadow(QFrame.Raised)
        self.verticalLayout_accounts = QVBoxLayout(self.frame_accounts)
        self.verticalLayout_accounts.setObjectName("verticalLayout_accounts")
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

        self.verticalLayout_accounts.addWidget(self.groupBox_add_account)

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

        self.verticalLayout_accounts.addWidget(self.groupBox_account_commands)

        self.verticalSpacer_accounts = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_accounts.addItem(self.verticalSpacer_accounts)

        self.horizontalLayout_accounts.addWidget(self.frame_accounts)

        self.tabWidget.addTab(self.tab_accounts, "")
        self.tab_currencies = QWidget()
        self.tab_currencies.setObjectName("tab_currencies")
        self.horizontalLayout_currencies = QHBoxLayout(self.tab_currencies)
        self.horizontalLayout_currencies.setObjectName("horizontalLayout_currencies")
        self.tableView_currencies = QTableView(self.tab_currencies)
        self.tableView_currencies.setObjectName("tableView_currencies")

        self.horizontalLayout_currencies.addWidget(self.tableView_currencies)

        self.frame_currencies = QFrame(self.tab_currencies)
        self.frame_currencies.setObjectName("frame_currencies")
        self.frame_currencies.setMinimumSize(QSize(300, 0))
        self.frame_currencies.setMaximumSize(QSize(300, 16777215))
        self.frame_currencies.setFrameShape(QFrame.StyledPanel)
        self.frame_currencies.setFrameShadow(QFrame.Raised)
        self.verticalLayout_currencies = QVBoxLayout(self.frame_currencies)
        self.verticalLayout_currencies.setObjectName("verticalLayout_currencies")
        self.groupBox_add_currency = QGroupBox(self.frame_currencies)
        self.groupBox_add_currency.setObjectName("groupBox_add_currency")
        self.verticalLayout_add_currency = QVBoxLayout(self.groupBox_add_currency)
        self.verticalLayout_add_currency.setObjectName("verticalLayout_add_currency")
        self.horizontalLayout_currency_code = QHBoxLayout()
        self.horizontalLayout_currency_code.setObjectName("horizontalLayout_currency_code")
        self.label_currency_code = QLabel(self.groupBox_add_currency)
        self.label_currency_code.setObjectName("label_currency_code")
        self.label_currency_code.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_code.addWidget(self.label_currency_code)

        self.lineEdit_currency_code = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_code.setObjectName("lineEdit_currency_code")
        self.lineEdit_currency_code.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_code.addWidget(self.lineEdit_currency_code)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_code)

        self.horizontalLayout_currency_name = QHBoxLayout()
        self.horizontalLayout_currency_name.setObjectName("horizontalLayout_currency_name")
        self.label_currency_name = QLabel(self.groupBox_add_currency)
        self.label_currency_name.setObjectName("label_currency_name")
        self.label_currency_name.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_name.addWidget(self.label_currency_name)

        self.lineEdit_currency_name = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_name.setObjectName("lineEdit_currency_name")
        self.lineEdit_currency_name.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_name.addWidget(self.lineEdit_currency_name)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_name)

        self.horizontalLayout_currency_symbol = QHBoxLayout()
        self.horizontalLayout_currency_symbol.setObjectName("horizontalLayout_currency_symbol")
        self.label_currency_symbol = QLabel(self.groupBox_add_currency)
        self.label_currency_symbol.setObjectName("label_currency_symbol")
        self.label_currency_symbol.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.label_currency_symbol)

        self.lineEdit_currency_symbol = QLineEdit(self.groupBox_add_currency)
        self.lineEdit_currency_symbol.setObjectName("lineEdit_currency_symbol")
        self.lineEdit_currency_symbol.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_currency_symbol.addWidget(self.lineEdit_currency_symbol)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_symbol)

        self.horizontalLayout_currency_add = QHBoxLayout()
        self.horizontalLayout_currency_add.setObjectName("horizontalLayout_currency_add")
        self.horizontalSpacer_currency = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_currency_add.addItem(self.horizontalSpacer_currency)

        self.pushButton_currency_add = QPushButton(self.groupBox_add_currency)
        self.pushButton_currency_add.setObjectName("pushButton_currency_add")

        self.horizontalLayout_currency_add.addWidget(self.pushButton_currency_add)

        self.verticalLayout_add_currency.addLayout(self.horizontalLayout_currency_add)

        self.verticalLayout_currencies.addWidget(self.groupBox_add_currency)

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

        self.verticalLayout_currencies.addWidget(self.groupBox_default_currency)

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

        self.verticalLayout_currencies.addWidget(self.groupBox_currency_commands)

        self.verticalSpacer_currencies = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_currencies.addItem(self.verticalSpacer_currencies)

        self.horizontalLayout_currencies.addWidget(self.frame_currencies)

        self.tabWidget.addTab(self.tab_currencies, "")
        self.tab_exchange = QWidget()
        self.tab_exchange.setObjectName("tab_exchange")
        self.horizontalLayout_exchange = QHBoxLayout(self.tab_exchange)
        self.horizontalLayout_exchange.setObjectName("horizontalLayout_exchange")
        self.tableView_exchange = QTableView(self.tab_exchange)
        self.tableView_exchange.setObjectName("tableView_exchange")

        self.horizontalLayout_exchange.addWidget(self.tableView_exchange)

        self.frame_exchange = QFrame(self.tab_exchange)
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
        self.dateEdit_exchange.setMinimumSize(QSize(191, 0))
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
            "                                    background-color: lightblue;\n"
            "                                    border: 1px solid #2196F3;\n"
            "                                    border-radius: 4px;\n"
            "                                    }\n"
            "                                    QPushButton:hover {\n"
            "                                    background-color: #87CEEB;\n"
            "                                    }\n"
            "                                    QPushButton:pressed {\n"
            "                                    background-color: #6BB6FF;\n"
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

        self.horizontalLayout_exchange.addWidget(self.frame_exchange)

        self.tabWidget.addTab(self.tab_exchange, "")
        self.tab_exchange_rates = QWidget()
        self.tab_exchange_rates.setObjectName("tab_exchange_rates")
        self.horizontalLayout_rates = QHBoxLayout(self.tab_exchange_rates)
        self.horizontalLayout_rates.setObjectName("horizontalLayout_rates")
        self.tableView_exchange_rates = QTableView(self.tab_exchange_rates)
        self.tableView_exchange_rates.setObjectName("tableView_exchange_rates")

        self.horizontalLayout_rates.addWidget(self.tableView_exchange_rates)

        self.frame_rates = QFrame(self.tab_exchange_rates)
        self.frame_rates.setObjectName("frame_rates")
        self.frame_rates.setMinimumSize(QSize(300, 0))
        self.frame_rates.setMaximumSize(QSize(300, 16777215))
        self.frame_rates.setFrameShape(QFrame.StyledPanel)
        self.frame_rates.setFrameShadow(QFrame.Raised)
        self.verticalLayout_rates = QVBoxLayout(self.frame_rates)
        self.verticalLayout_rates.setObjectName("verticalLayout_rates")
        self.groupBox_add_rate = QGroupBox(self.frame_rates)
        self.groupBox_add_rate.setObjectName("groupBox_add_rate")
        self.verticalLayout_add_rate = QVBoxLayout(self.groupBox_add_rate)
        self.verticalLayout_add_rate.setObjectName("verticalLayout_add_rate")
        self.horizontalLayout_rate_from = QHBoxLayout()
        self.horizontalLayout_rate_from.setObjectName("horizontalLayout_rate_from")
        self.label_rate_from = QLabel(self.groupBox_add_rate)
        self.label_rate_from.setObjectName("label_rate_from")
        self.label_rate_from.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_from.addWidget(self.label_rate_from)

        self.comboBox_rate_from = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_from.setObjectName("comboBox_rate_from")
        self.comboBox_rate_from.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_from.addWidget(self.comboBox_rate_from)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_from)

        self.horizontalLayout_rate_to = QHBoxLayout()
        self.horizontalLayout_rate_to.setObjectName("horizontalLayout_rate_to")
        self.label_rate_to = QLabel(self.groupBox_add_rate)
        self.label_rate_to.setObjectName("label_rate_to")
        self.label_rate_to.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_to.addWidget(self.label_rate_to)

        self.comboBox_rate_to = QComboBox(self.groupBox_add_rate)
        self.comboBox_rate_to.setObjectName("comboBox_rate_to")
        self.comboBox_rate_to.setMinimumSize(QSize(170, 0))

        self.horizontalLayout_rate_to.addWidget(self.comboBox_rate_to)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_to)

        self.horizontalLayout_rate_value = QHBoxLayout()
        self.horizontalLayout_rate_value.setObjectName("horizontalLayout_rate_value")
        self.label_rate_value = QLabel(self.groupBox_add_rate)
        self.label_rate_value.setObjectName("label_rate_value")
        self.label_rate_value.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_value.addWidget(self.label_rate_value)

        self.doubleSpinBox_rate_value = QDoubleSpinBox(self.groupBox_add_rate)
        self.doubleSpinBox_rate_value.setObjectName("doubleSpinBox_rate_value")
        self.doubleSpinBox_rate_value.setMinimumSize(QSize(170, 0))
        self.doubleSpinBox_rate_value.setMaximum(999999.989999999990687)
        self.doubleSpinBox_rate_value.setValue(73.500000000000000)

        self.horizontalLayout_rate_value.addWidget(self.doubleSpinBox_rate_value)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_value)

        self.horizontalLayout_rate_date = QHBoxLayout()
        self.horizontalLayout_rate_date.setObjectName("horizontalLayout_rate_date")
        self.label_rate_date = QLabel(self.groupBox_add_rate)
        self.label_rate_date.setObjectName("label_rate_date")
        self.label_rate_date.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_rate_date.addWidget(self.label_rate_date)

        self.dateEdit_rate = QDateEdit(self.groupBox_add_rate)
        self.dateEdit_rate.setObjectName("dateEdit_rate")
        self.dateEdit_rate.setMinimumSize(QSize(170, 0))
        self.dateEdit_rate.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_rate.setCalendarPopup(True)

        self.horizontalLayout_rate_date.addWidget(self.dateEdit_rate)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_date)

        self.horizontalLayout_rate_add = QHBoxLayout()
        self.horizontalLayout_rate_add.setObjectName("horizontalLayout_rate_add")
        self.horizontalSpacer_rate = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_rate_add.addItem(self.horizontalSpacer_rate)

        self.pushButton_rate_add = QPushButton(self.groupBox_add_rate)
        self.pushButton_rate_add.setObjectName("pushButton_rate_add")

        self.horizontalLayout_rate_add.addWidget(self.pushButton_rate_add)

        self.verticalLayout_add_rate.addLayout(self.horizontalLayout_rate_add)

        self.verticalLayout_rates.addWidget(self.groupBox_add_rate)

        self.groupBox_rate_commands = QGroupBox(self.frame_rates)
        self.groupBox_rate_commands.setObjectName("groupBox_rate_commands")
        self.verticalLayout_rate_commands = QVBoxLayout(self.groupBox_rate_commands)
        self.verticalLayout_rate_commands.setObjectName("verticalLayout_rate_commands")
        self.horizontalLayout_rate_commands = QHBoxLayout()
        self.horizontalLayout_rate_commands.setObjectName("horizontalLayout_rate_commands")
        self.pushButton_rates_delete = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_delete.setObjectName("pushButton_rates_delete")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_delete)

        self.pushButton_rates_refresh = QPushButton(self.groupBox_rate_commands)
        self.pushButton_rates_refresh.setObjectName("pushButton_rates_refresh")

        self.horizontalLayout_rate_commands.addWidget(self.pushButton_rates_refresh)

        self.verticalLayout_rate_commands.addLayout(self.horizontalLayout_rate_commands)

        self.verticalLayout_rates.addWidget(self.groupBox_rate_commands)

        self.verticalSpacer_rates = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_rates.addItem(self.verticalSpacer_rates)

        self.horizontalLayout_rates.addWidget(self.frame_rates)

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
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1356, 751))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName("verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_18.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_reports = QWidget()
        self.tab_reports.setObjectName("tab_reports")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_reports)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tableView_reports = QTableView(self.tab_reports)
        self.tableView_reports.setObjectName("tableView_reports")

        self.horizontalLayout_6.addWidget(self.tableView_reports)

        self.frame_5 = QFrame(self.tab_reports)
        self.frame_5.setObjectName("frame_5")
        self.frame_5.setMinimumSize(QSize(300, 0))
        self.frame_5.setMaximumSize(QSize(300, 16777215))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_5)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
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

        self.verticalLayout_16.addWidget(self.groupBox_10)

        self.groupBox_summary = QGroupBox(self.frame_5)
        self.groupBox_summary.setObjectName("groupBox_summary")
        self.verticalLayout_summary = QVBoxLayout(self.groupBox_summary)
        self.verticalLayout_summary.setObjectName("verticalLayout_summary")
        self.label_total_income = QLabel(self.groupBox_summary)
        self.label_total_income.setObjectName("label_total_income")
        self.label_total_income.setStyleSheet("color: green; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_income)

        self.label_total_expenses = QLabel(self.groupBox_summary)
        self.label_total_expenses.setObjectName("label_total_expenses")
        self.label_total_expenses.setStyleSheet("color: red; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_expenses)

        self.label_net_balance = QLabel(self.groupBox_summary)
        self.label_net_balance.setObjectName("label_net_balance")
        self.label_net_balance.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.verticalLayout_summary.addWidget(self.label_net_balance)

        self.label_total_accounts = QLabel(self.groupBox_summary)
        self.label_total_accounts.setObjectName("label_total_accounts")
        self.label_total_accounts.setStyleSheet("color: blue; font-weight: bold;")

        self.verticalLayout_summary.addWidget(self.label_total_accounts)

        self.verticalLayout_16.addWidget(self.groupBox_summary)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_reports, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1400, 21))
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
```

</details>
