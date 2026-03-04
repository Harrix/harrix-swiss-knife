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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Habit tracker", None))
        self.groupBox_habits_5.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_habits_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_habits_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_habits_show_all_records.setText(
            QCoreApplication.translate("MainWindow", "Show All Records", None)
        )
        self.pushButton_habits_export_csv.setText(QCoreApplication.translate("MainWindow", "Export Table", None))
        self.groupBox_habits_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Habit", None))
        self.label_habits_5.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.checkBox_habit_is_bool.setText(QCoreApplication.translate("MainWindow", "Boolean (0 or 1 only)", None))
        self.pushButton_habit_add_new.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.groupBox_habits_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_habits_delete_selected.setText(
            QCoreApplication.translate("MainWindow", "Delete selected", None)
        )
        self.pushButton_habits_refresh_table.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.label_filter_habit_year.setText(QCoreApplication.translate("MainWindow", "Year:", None))
        self.label_filter_habit.setText(QCoreApplication.translate("MainWindow", "Habit:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_sets_of_habits), QCoreApplication.translate("MainWindow", "Habits", None)
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2332, 1197)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_sets_of_habits = QWidget()
        self.tab_sets_of_habits.setObjectName("tab_sets_of_habits")
        self.horizontalLayout_27 = QHBoxLayout(self.tab_sets_of_habits)
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.splitter_habits = QSplitter(self.tab_sets_of_habits)
        self.splitter_habits.setObjectName("splitter_habits")
        self.splitter_habits.setOrientation(Qt.Orientation.Horizontal)
        self.frame_habits = QFrame(self.splitter_habits)
        self.frame_habits.setObjectName("frame_habits")
        self.frame_habits.setMinimumSize(QSize(350, 0))
        self.frame_habits.setMaximumSize(QSize(16777215, 16777215))
        self.frame_habits.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_habits.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_habits)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.groupBox_habits_5 = QGroupBox(self.frame_habits)
        self.groupBox_habits_5.setObjectName("groupBox_habits_5")
        self.groupBox_habits_5.setMinimumSize(QSize(0, 0))
        self.verticalLayout_22 = QVBoxLayout(self.groupBox_habits_5)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.horizontalLayout_habits_8 = QHBoxLayout()
        self.horizontalLayout_habits_8.setObjectName("horizontalLayout_habits_8")
        self.pushButton_habits_delete = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_delete.setObjectName("pushButton_habits_delete")
        self.pushButton_habits_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_delete)

        self.pushButton_habits_refresh = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_refresh.setObjectName("pushButton_habits_refresh")
        self.pushButton_habits_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_refresh)

        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_8)

        self.horizontalLayout_habits_25 = QHBoxLayout()
        self.horizontalLayout_habits_25.setObjectName("horizontalLayout_habits_25")
        self.pushButton_habits_show_all_records = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_show_all_records.setObjectName("pushButton_habits_show_all_records")

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_show_all_records)

        self.pushButton_habits_export_csv = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_export_csv.setObjectName("pushButton_habits_export_csv")
        self.pushButton_habits_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_export_csv)

        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_25)

        self.verticalLayout_23.addWidget(self.groupBox_habits_5)

        self.groupBox_habits_2 = QGroupBox(self.frame_habits)
        self.groupBox_habits_2.setObjectName("groupBox_habits_2")
        self.verticalLayout_habits_10 = QVBoxLayout(self.groupBox_habits_2)
        self.verticalLayout_habits_10.setObjectName("verticalLayout_habits_10")
        self.horizontalLayout_habits_17 = QHBoxLayout()
        self.horizontalLayout_habits_17.setObjectName("horizontalLayout_habits_17")
        self.label_habits_5 = QLabel(self.groupBox_habits_2)
        self.label_habits_5.setObjectName("label_habits_5")
        self.label_habits_5.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_habits_17.addWidget(self.label_habits_5)

        self.lineEdit_habit_name = QLineEdit(self.groupBox_habits_2)
        self.lineEdit_habit_name.setObjectName("lineEdit_habit_name")
        self.lineEdit_habit_name.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_habits_17.addWidget(self.lineEdit_habit_name)

        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_17)

        self.checkBox_habit_is_bool = QCheckBox(self.groupBox_habits_2)
        self.checkBox_habit_is_bool.setObjectName("checkBox_habit_is_bool")

        self.verticalLayout_habits_10.addWidget(self.checkBox_habit_is_bool)

        self.horizontalLayout_habits_19 = QHBoxLayout()
        self.horizontalLayout_habits_19.setObjectName("horizontalLayout_habits_19")
        self.horizontalSpacer_habits_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_habits_19.addItem(self.horizontalSpacer_habits_4)

        self.pushButton_habit_add_new = QPushButton(self.groupBox_habits_2)
        self.pushButton_habit_add_new.setObjectName("pushButton_habit_add_new")

        self.horizontalLayout_habits_19.addWidget(self.pushButton_habit_add_new)

        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_19)

        self.verticalLayout_23.addWidget(self.groupBox_habits_2)

        self.groupBox_habits_7 = QGroupBox(self.frame_habits)
        self.groupBox_habits_7.setObjectName("groupBox_habits_7")
        self.verticalLayout_habits_11 = QVBoxLayout(self.groupBox_habits_7)
        self.verticalLayout_habits_11.setObjectName("verticalLayout_habits_11")
        self.horizontalLayout_habits_20 = QHBoxLayout()
        self.horizontalLayout_habits_20.setObjectName("horizontalLayout_habits_20")
        self.pushButton_habits_delete_selected = QPushButton(self.groupBox_habits_7)
        self.pushButton_habits_delete_selected.setObjectName("pushButton_habits_delete_selected")

        self.horizontalLayout_habits_20.addWidget(self.pushButton_habits_delete_selected)

        self.pushButton_habits_refresh_table = QPushButton(self.groupBox_habits_7)
        self.pushButton_habits_refresh_table.setObjectName("pushButton_habits_refresh_table")

        self.horizontalLayout_habits_20.addWidget(self.pushButton_habits_refresh_table)

        self.verticalLayout_habits_11.addLayout(self.horizontalLayout_habits_20)

        self.verticalLayout_23.addWidget(self.groupBox_habits_7)

        self.tableView_habits = QTableView(self.frame_habits)
        self.tableView_habits.setObjectName("tableView_habits")

        self.verticalLayout_23.addWidget(self.tableView_habits)

        self.splitter_habits.addWidget(self.frame_habits)
        self.splitter_4 = QSplitter(self.splitter_habits)
        self.splitter_4.setObjectName("splitter_4")
        self.splitter_4.setOrientation(Qt.Orientation.Vertical)
        self.tableView_process_habits = QTableView(self.splitter_4)
        self.tableView_process_habits.setObjectName("tableView_process_habits")
        self.splitter_4.addWidget(self.tableView_process_habits)
        self.splitter_3 = QSplitter(self.splitter_4)
        self.splitter_3.setObjectName("splitter_3")
        self.splitter_3.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter_3)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_24 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.label_filter_habit_year = QLabel(self.layoutWidget)
        self.label_filter_habit_year.setObjectName("label_filter_habit_year")

        self.verticalLayout_24.addWidget(self.label_filter_habit_year)

        self.listView_filter_habit_year = QListView(self.layoutWidget)
        self.listView_filter_habit_year.setObjectName("listView_filter_habit_year")

        self.verticalLayout_24.addWidget(self.listView_filter_habit_year)

        self.label_filter_habit = QLabel(self.layoutWidget)
        self.label_filter_habit.setObjectName("label_filter_habit")

        self.verticalLayout_24.addWidget(self.label_filter_habit)

        self.listView_filter_habit = QListView(self.layoutWidget)
        self.listView_filter_habit.setObjectName("listView_filter_habit")

        self.verticalLayout_24.addWidget(self.listView_filter_habit)

        self.splitter_3.addWidget(self.layoutWidget)
        self.scrollArea_charts_process_habits = QScrollArea(self.splitter_3)
        self.scrollArea_charts_process_habits.setObjectName("scrollArea_charts_process_habits")
        self.scrollArea_charts_process_habits.setMinimumSize(QSize(0, 301))
        self.scrollArea_charts_process_habits.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts_process_habits = QWidget()
        self.scrollAreaWidgetContents_charts_process_habits.setObjectName(
            "scrollAreaWidgetContents_charts_process_habits"
        )
        self.scrollAreaWidgetContents_charts_process_habits.setGeometry(QRect(0, 0, 86, 778))
        self.verticalLayout_charts_process_habits_content = QVBoxLayout(
            self.scrollAreaWidgetContents_charts_process_habits
        )
        self.verticalLayout_charts_process_habits_content.setObjectName("verticalLayout_charts_process_habits_content")
        self.scrollArea_charts_process_habits.setWidget(self.scrollAreaWidgetContents_charts_process_habits)
        self.splitter_3.addWidget(self.scrollArea_charts_process_habits)
        self.splitter_4.addWidget(self.splitter_3)
        self.splitter_habits.addWidget(self.splitter_4)

        self.horizontalLayout_27.addWidget(self.splitter_habits)

        self.tabWidget.addTab(self.tab_sets_of_habits, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)

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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Habit tracker", None))
        self.groupBox_habits_5.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_habits_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_habits_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_habits_show_all_records.setText(
            QCoreApplication.translate("MainWindow", "Show All Records", None)
        )
        self.pushButton_habits_export_csv.setText(QCoreApplication.translate("MainWindow", "Export Table", None))
        self.groupBox_habits_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Habit", None))
        self.label_habits_5.setText(QCoreApplication.translate("MainWindow", "Name:", None))
        self.checkBox_habit_is_bool.setText(QCoreApplication.translate("MainWindow", "Boolean (0 or 1 only)", None))
        self.pushButton_habit_add_new.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.groupBox_habits_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_habits_delete_selected.setText(
            QCoreApplication.translate("MainWindow", "Delete selected", None)
        )
        self.pushButton_habits_refresh_table.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.label_filter_habit_year.setText(QCoreApplication.translate("MainWindow", "Year:", None))
        self.label_filter_habit.setText(QCoreApplication.translate("MainWindow", "Habit:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_sets_of_habits), QCoreApplication.translate("MainWindow", "Habits", None)
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
        MainWindow.resize(2332, 1197)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_sets_of_habits = QWidget()
        self.tab_sets_of_habits.setObjectName("tab_sets_of_habits")
        self.horizontalLayout_27 = QHBoxLayout(self.tab_sets_of_habits)
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.splitter_habits = QSplitter(self.tab_sets_of_habits)
        self.splitter_habits.setObjectName("splitter_habits")
        self.splitter_habits.setOrientation(Qt.Orientation.Horizontal)
        self.frame_habits = QFrame(self.splitter_habits)
        self.frame_habits.setObjectName("frame_habits")
        self.frame_habits.setMinimumSize(QSize(350, 0))
        self.frame_habits.setMaximumSize(QSize(16777215, 16777215))
        self.frame_habits.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_habits.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_habits)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.groupBox_habits_5 = QGroupBox(self.frame_habits)
        self.groupBox_habits_5.setObjectName("groupBox_habits_5")
        self.groupBox_habits_5.setMinimumSize(QSize(0, 0))
        self.verticalLayout_22 = QVBoxLayout(self.groupBox_habits_5)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.horizontalLayout_habits_8 = QHBoxLayout()
        self.horizontalLayout_habits_8.setObjectName("horizontalLayout_habits_8")
        self.pushButton_habits_delete = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_delete.setObjectName("pushButton_habits_delete")
        self.pushButton_habits_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_delete)

        self.pushButton_habits_refresh = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_refresh.setObjectName("pushButton_habits_refresh")
        self.pushButton_habits_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_8.addWidget(self.pushButton_habits_refresh)

        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_8)

        self.horizontalLayout_habits_25 = QHBoxLayout()
        self.horizontalLayout_habits_25.setObjectName("horizontalLayout_habits_25")
        self.pushButton_habits_show_all_records = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_show_all_records.setObjectName("pushButton_habits_show_all_records")

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_show_all_records)

        self.pushButton_habits_export_csv = QPushButton(self.groupBox_habits_5)
        self.pushButton_habits_export_csv.setObjectName("pushButton_habits_export_csv")
        self.pushButton_habits_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_habits_25.addWidget(self.pushButton_habits_export_csv)

        self.verticalLayout_22.addLayout(self.horizontalLayout_habits_25)

        self.verticalLayout_23.addWidget(self.groupBox_habits_5)

        self.groupBox_habits_2 = QGroupBox(self.frame_habits)
        self.groupBox_habits_2.setObjectName("groupBox_habits_2")
        self.verticalLayout_habits_10 = QVBoxLayout(self.groupBox_habits_2)
        self.verticalLayout_habits_10.setObjectName("verticalLayout_habits_10")
        self.horizontalLayout_habits_17 = QHBoxLayout()
        self.horizontalLayout_habits_17.setObjectName("horizontalLayout_habits_17")
        self.label_habits_5 = QLabel(self.groupBox_habits_2)
        self.label_habits_5.setObjectName("label_habits_5")
        self.label_habits_5.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_habits_17.addWidget(self.label_habits_5)

        self.lineEdit_habit_name = QLineEdit(self.groupBox_habits_2)
        self.lineEdit_habit_name.setObjectName("lineEdit_habit_name")
        self.lineEdit_habit_name.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_habits_17.addWidget(self.lineEdit_habit_name)

        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_17)

        self.checkBox_habit_is_bool = QCheckBox(self.groupBox_habits_2)
        self.checkBox_habit_is_bool.setObjectName("checkBox_habit_is_bool")

        self.verticalLayout_habits_10.addWidget(self.checkBox_habit_is_bool)

        self.horizontalLayout_habits_19 = QHBoxLayout()
        self.horizontalLayout_habits_19.setObjectName("horizontalLayout_habits_19")
        self.horizontalSpacer_habits_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_habits_19.addItem(self.horizontalSpacer_habits_4)

        self.pushButton_habit_add_new = QPushButton(self.groupBox_habits_2)
        self.pushButton_habit_add_new.setObjectName("pushButton_habit_add_new")

        self.horizontalLayout_habits_19.addWidget(self.pushButton_habit_add_new)

        self.verticalLayout_habits_10.addLayout(self.horizontalLayout_habits_19)

        self.verticalLayout_23.addWidget(self.groupBox_habits_2)

        self.groupBox_habits_7 = QGroupBox(self.frame_habits)
        self.groupBox_habits_7.setObjectName("groupBox_habits_7")
        self.verticalLayout_habits_11 = QVBoxLayout(self.groupBox_habits_7)
        self.verticalLayout_habits_11.setObjectName("verticalLayout_habits_11")
        self.horizontalLayout_habits_20 = QHBoxLayout()
        self.horizontalLayout_habits_20.setObjectName("horizontalLayout_habits_20")
        self.pushButton_habits_delete_selected = QPushButton(self.groupBox_habits_7)
        self.pushButton_habits_delete_selected.setObjectName("pushButton_habits_delete_selected")

        self.horizontalLayout_habits_20.addWidget(self.pushButton_habits_delete_selected)

        self.pushButton_habits_refresh_table = QPushButton(self.groupBox_habits_7)
        self.pushButton_habits_refresh_table.setObjectName("pushButton_habits_refresh_table")

        self.horizontalLayout_habits_20.addWidget(self.pushButton_habits_refresh_table)

        self.verticalLayout_habits_11.addLayout(self.horizontalLayout_habits_20)

        self.verticalLayout_23.addWidget(self.groupBox_habits_7)

        self.tableView_habits = QTableView(self.frame_habits)
        self.tableView_habits.setObjectName("tableView_habits")

        self.verticalLayout_23.addWidget(self.tableView_habits)

        self.splitter_habits.addWidget(self.frame_habits)
        self.splitter_4 = QSplitter(self.splitter_habits)
        self.splitter_4.setObjectName("splitter_4")
        self.splitter_4.setOrientation(Qt.Orientation.Vertical)
        self.tableView_process_habits = QTableView(self.splitter_4)
        self.tableView_process_habits.setObjectName("tableView_process_habits")
        self.splitter_4.addWidget(self.tableView_process_habits)
        self.splitter_3 = QSplitter(self.splitter_4)
        self.splitter_3.setObjectName("splitter_3")
        self.splitter_3.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter_3)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_24 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.label_filter_habit_year = QLabel(self.layoutWidget)
        self.label_filter_habit_year.setObjectName("label_filter_habit_year")

        self.verticalLayout_24.addWidget(self.label_filter_habit_year)

        self.listView_filter_habit_year = QListView(self.layoutWidget)
        self.listView_filter_habit_year.setObjectName("listView_filter_habit_year")

        self.verticalLayout_24.addWidget(self.listView_filter_habit_year)

        self.label_filter_habit = QLabel(self.layoutWidget)
        self.label_filter_habit.setObjectName("label_filter_habit")

        self.verticalLayout_24.addWidget(self.label_filter_habit)

        self.listView_filter_habit = QListView(self.layoutWidget)
        self.listView_filter_habit.setObjectName("listView_filter_habit")

        self.verticalLayout_24.addWidget(self.listView_filter_habit)

        self.splitter_3.addWidget(self.layoutWidget)
        self.scrollArea_charts_process_habits = QScrollArea(self.splitter_3)
        self.scrollArea_charts_process_habits.setObjectName("scrollArea_charts_process_habits")
        self.scrollArea_charts_process_habits.setMinimumSize(QSize(0, 301))
        self.scrollArea_charts_process_habits.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts_process_habits = QWidget()
        self.scrollAreaWidgetContents_charts_process_habits.setObjectName(
            "scrollAreaWidgetContents_charts_process_habits"
        )
        self.scrollAreaWidgetContents_charts_process_habits.setGeometry(QRect(0, 0, 86, 778))
        self.verticalLayout_charts_process_habits_content = QVBoxLayout(
            self.scrollAreaWidgetContents_charts_process_habits
        )
        self.verticalLayout_charts_process_habits_content.setObjectName("verticalLayout_charts_process_habits_content")
        self.scrollArea_charts_process_habits.setWidget(self.scrollAreaWidgetContents_charts_process_habits)
        self.splitter_3.addWidget(self.scrollArea_charts_process_habits)
        self.splitter_4.addWidget(self.splitter_3)
        self.splitter_habits.addWidget(self.splitter_4)

        self.horizontalLayout_27.addWidget(self.splitter_habits)

        self.tabWidget.addTab(self.tab_sets_of_habits, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
```

</details>
