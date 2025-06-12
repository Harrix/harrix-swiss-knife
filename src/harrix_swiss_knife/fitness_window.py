# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitness_window.ui'
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
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableView,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Fitness tracker", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", "Exercise:", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", "Set parameters", None))
        self.label_exercise.setText(QCoreApplication.translate("MainWindow", "TextLabel", None))
        self.label_unit.setText(QCoreApplication.translate("MainWindow", "times", None))
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.label_exercise_avif.setText(QCoreApplication.translate("MainWindow", "No exercise selected", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", "Export Table", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", "Filter", None))
        self.label_filter_exercise.setText(QCoreApplication.translate("MainWindow", "Exercise:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", "Use date filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", "Clear Filter", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", "Apply Filter", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", "Sets", None)
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Unit of Measurement", None))
        self.check_box_is_type_required.setText(QCoreApplication.translate("MainWindow", "Type required", None))
        self.pushButton_exercise_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_exercises_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_exercises_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", "Exercises", None)
        )
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise Type", None))
        self.pushButton_type_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_types_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_types_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", "Exercise Types", None)
        )
        self.label_weight_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_weight_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_weight_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_weight_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_weight_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_weight_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_weight_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.pushButton_update_weight_chart.setText(QCoreApplication.translate("MainWindow", "Update Chart", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", "Add New Weight", None))
        self.dateEdit_weight.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_weight_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", "Commands", None))
        self.pushButton_weight_delete.setText(QCoreApplication.translate("MainWindow", "Delete selected", None))
        self.pushButton_weight_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", "Weight", None)
        )
        self.label_chart_exercise.setText(QCoreApplication.translate("MainWindow", "Exercise:", None))
        self.label_chart_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.label_chart_period.setText(QCoreApplication.translate("MainWindow", "Period:", None))
        self.comboBox_chart_period.setItemText(0, QCoreApplication.translate("MainWindow", "Days", None))
        self.comboBox_chart_period.setItemText(1, QCoreApplication.translate("MainWindow", "Months", None))
        self.comboBox_chart_period.setItemText(2, QCoreApplication.translate("MainWindow", "Years", None))

        self.pushButton_update_chart.setText(QCoreApplication.translate("MainWindow", "Update Chart", None))
        self.pushButton_show_sets_chart.setText(QCoreApplication.translate("MainWindow", "Show Sets Chart", None))
        self.label_chart_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_chart_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_chart_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_chart_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_chart_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_chart_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_chart_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_charts), QCoreApplication.translate("MainWindow", "Exercise Chart", None)
        )
        self.pushButton_statistics_refresh.setText(QCoreApplication.translate("MainWindow", "Records", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", "Statistics", None)
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
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_main = QHBoxLayout(self.tab)
        self.horizontalLayout_main.setObjectName("horizontalLayout_main")
        self.splitter = QSplitter(self.tab)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.tableView_process = QTableView(self.splitter)
        self.tableView_process.setObjectName("tableView_process")
        self.splitter.addWidget(self.tableView_process)
        self.widget_middle = QWidget(self.splitter)
        self.widget_middle.setObjectName("widget_middle")
        self.verticalLayout = QVBoxLayout(self.widget_middle)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.widget_middle)
        self.label_7.setObjectName("label_7")

        self.verticalLayout.addWidget(self.label_7)

        self.listView_exercises = QListView(self.widget_middle)
        self.listView_exercises.setObjectName("listView_exercises")
        self.listView_exercises.setMaximumSize(QSize(16777215, 16777215))
        self.listView_exercises.setStyleSheet(
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

        self.verticalLayout.addWidget(self.listView_exercises)

        self.splitter.addWidget(self.widget_middle)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(350, 0))
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setMinimumSize(QSize(0, 50))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_exercise = QLabel(self.groupBox)
        self.label_exercise.setObjectName("label_exercise")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_exercise.setFont(font)

        self.verticalLayout_5.addWidget(self.label_exercise)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.spinBox_count = QSpinBox(self.groupBox)
        self.spinBox_count.setObjectName("spinBox_count")
        self.spinBox_count.setFont(font)
        self.spinBox_count.setStyleSheet(
            "QSpinBox {\n"
            "                                          background-color: lightgreen;\n"
            "                                          }"
        )
        self.spinBox_count.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.spinBox_count.setMaximum(1000000)
        self.spinBox_count.setValue(100)

        self.horizontalLayout_14.addWidget(self.spinBox_count)

        self.label_unit = QLabel(self.groupBox)
        self.label_unit.setObjectName("label_unit")
        self.label_unit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_14.addWidget(self.label_unit)

        self.verticalLayout_5.addLayout(self.horizontalLayout_14)

        self.comboBox_type = QComboBox(self.groupBox)
        self.comboBox_type.setObjectName("comboBox_type")

        self.verticalLayout_5.addWidget(self.comboBox_type)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.dateEdit = QDateEdit(self.groupBox)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setMinimumSize(QSize(191, 0))
        self.dateEdit.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit.setCalendarPopup(True)

        self.horizontalLayout_13.addWidget(self.dateEdit)

        self.pushButton_yesterday = QPushButton(self.groupBox)
        self.pushButton_yesterday.setObjectName("pushButton_yesterday")
        self.pushButton_yesterday.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_13.addWidget(self.pushButton_yesterday)

        self.verticalLayout_5.addLayout(self.horizontalLayout_13)

        self.pushButton_add = QPushButton(self.groupBox)
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

        self.verticalLayout_3.addWidget(self.groupBox)

        self.label_exercise_avif = QLabel(self.frame)
        self.label_exercise_avif.setObjectName("label_exercise_avif")
        self.label_exercise_avif.setMinimumSize(QSize(0, 150))
        self.label_exercise_avif.setStyleSheet("border: 1px solid gray;")
        self.label_exercise_avif.setScaledContents(False)
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_exercise_avif)

        self.groupBox_5 = QGroupBox(self.frame)
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_delete = QPushButton(self.groupBox_5)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_delete)

        self.pushButton_refresh = QPushButton(self.groupBox_5)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_refresh)

        self.pushButton_export_csv = QPushButton(self.groupBox_5)
        self.pushButton_export_csv.setObjectName("pushButton_export_csv")
        self.pushButton_export_csv.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_8.addWidget(self.pushButton_export_csv)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3.addWidget(self.groupBox_5)

        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setMinimumSize(QSize(0, 201))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_filter)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_filter_exercise = QLabel(self.groupBox_filter)
        self.label_filter_exercise.setObjectName("label_filter_exercise")
        self.label_filter_exercise.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_9.addWidget(self.label_filter_exercise)

        self.comboBox_filter_exercise = QComboBox(self.groupBox_filter)
        self.comboBox_filter_exercise.setObjectName("comboBox_filter_exercise")
        self.comboBox_filter_exercise.setMinimumSize(QSize(191, 0))

        self.horizontalLayout_9.addWidget(self.comboBox_filter_exercise)

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

        self.verticalSpacer = QSpacerItem(20, 143, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.frame)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableView_exercises = QTableView(self.tab_2)
        self.tableView_exercises.setObjectName("tableView_exercises")

        self.horizontalLayout_3.addWidget(self.tableView_exercises)

        self.frame_2 = QFrame(self.tab_2)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setMinimumSize(QSize(300, 0))
        self.frame_2.setMaximumSize(QSize(301, 16777215))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_2)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.lineEdit_exercise_name = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_name.setObjectName("lineEdit_exercise_name")
        self.lineEdit_exercise_name.setMinimumSize(QSize(113, 0))

        self.horizontalLayout_17.addWidget(self.lineEdit_exercise_name)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_17.addWidget(self.label_5)

        self.verticalLayout_10.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.lineEdit_exercise_unit = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_unit.setObjectName("lineEdit_exercise_unit")
        self.lineEdit_exercise_unit.setMinimumSize(QSize(113, 0))

        self.horizontalLayout_18.addWidget(self.lineEdit_exercise_unit)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_18.addWidget(self.label_6)

        self.verticalLayout_10.addLayout(self.horizontalLayout_18)

        self.check_box_is_type_required = QCheckBox(self.groupBox_2)
        self.check_box_is_type_required.setObjectName("check_box_is_type_required")

        self.verticalLayout_10.addWidget(self.check_box_is_type_required)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_4)

        self.pushButton_exercise_add = QPushButton(self.groupBox_2)
        self.pushButton_exercise_add.setObjectName("pushButton_exercise_add")

        self.horizontalLayout_19.addWidget(self.pushButton_exercise_add)

        self.verticalLayout_10.addLayout(self.horizontalLayout_19)

        self.verticalLayout_12.addWidget(self.groupBox_2)

        self.groupBox_7 = QGroupBox(self.frame_2)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.pushButton_exercises_delete = QPushButton(self.groupBox_7)
        self.pushButton_exercises_delete.setObjectName("pushButton_exercises_delete")

        self.horizontalLayout_20.addWidget(self.pushButton_exercises_delete)

        self.pushButton_exercises_refresh = QPushButton(self.groupBox_7)
        self.pushButton_exercises_refresh.setObjectName("pushButton_exercises_refresh")

        self.horizontalLayout_20.addWidget(self.pushButton_exercises_refresh)

        self.verticalLayout_11.addLayout(self.horizontalLayout_20)

        self.verticalLayout_12.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 581, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_2)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView_exercise_types = QTableView(self.tab_3)
        self.tableView_exercise_types.setObjectName("tableView_exercise_types")

        self.horizontalLayout_4.addWidget(self.tableView_exercise_types)

        self.frame_3 = QFrame(self.tab_3)
        self.frame_3.setObjectName("frame_3")
        self.frame_3.setMinimumSize(QSize(300, 0))
        self.frame_3.setMaximumSize(QSize(300, 16777215))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_3)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.groupBox_3 = QGroupBox(self.frame_3)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_14 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.comboBox_exercise_name = QComboBox(self.groupBox_3)
        self.comboBox_exercise_name.setObjectName("comboBox_exercise_name")

        self.verticalLayout_14.addWidget(self.comboBox_exercise_name)

        self.lineEdit_exercise_type = QLineEdit(self.groupBox_3)
        self.lineEdit_exercise_type.setObjectName("lineEdit_exercise_type")

        self.verticalLayout_14.addWidget(self.lineEdit_exercise_type)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_5)

        self.pushButton_type_add = QPushButton(self.groupBox_3)
        self.pushButton_type_add.setObjectName("pushButton_type_add")

        self.horizontalLayout_22.addWidget(self.pushButton_type_add)

        self.verticalLayout_14.addLayout(self.horizontalLayout_22)

        self.verticalLayout_15.addWidget(self.groupBox_3)

        self.groupBox_8 = QGroupBox(self.frame_3)
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.pushButton_types_delete = QPushButton(self.groupBox_8)
        self.pushButton_types_delete.setObjectName("pushButton_types_delete")

        self.horizontalLayout_21.addWidget(self.pushButton_types_delete)

        self.pushButton_types_refresh = QPushButton(self.groupBox_8)
        self.pushButton_types_refresh.setObjectName("pushButton_types_refresh")

        self.horizontalLayout_21.addWidget(self.pushButton_types_refresh)

        self.verticalLayout_13.addLayout(self.horizontalLayout_21)

        self.verticalLayout_15.addWidget(self.groupBox_8)

        self.verticalSpacer_3 = QSpacerItem(20, 608, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_3)

        self.horizontalLayout_4.addWidget(self.frame_3)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_5)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_weight_controls = QFrame(self.tab_5)
        self.frame_weight_controls.setObjectName("frame_weight_controls")
        self.frame_weight_controls.setMaximumSize(QSize(16777215, 80))
        self.frame_weight_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_weight_controls.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_weight_controls = QHBoxLayout(self.frame_weight_controls)
        self.horizontalLayout_weight_controls.setObjectName("horizontalLayout_weight_controls")
        self.label_weight_from = QLabel(self.frame_weight_controls)
        self.label_weight_from.setObjectName("label_weight_from")

        self.horizontalLayout_weight_controls.addWidget(self.label_weight_from)

        self.dateEdit_weight_from = QDateEdit(self.frame_weight_controls)
        self.dateEdit_weight_from.setObjectName("dateEdit_weight_from")
        self.dateEdit_weight_from.setCalendarPopup(True)

        self.horizontalLayout_weight_controls.addWidget(self.dateEdit_weight_from)

        self.label_weight_to = QLabel(self.frame_weight_controls)
        self.label_weight_to.setObjectName("label_weight_to")

        self.horizontalLayout_weight_controls.addWidget(self.label_weight_to)

        self.dateEdit_weight_to = QDateEdit(self.frame_weight_controls)
        self.dateEdit_weight_to.setObjectName("dateEdit_weight_to")
        self.dateEdit_weight_to.setCalendarPopup(True)

        self.horizontalLayout_weight_controls.addWidget(self.dateEdit_weight_to)

        self.pushButton_weight_last_month = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_last_month.setObjectName("pushButton_weight_last_month")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_last_month)

        self.pushButton_weight_last_year = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_last_year.setObjectName("pushButton_weight_last_year")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_last_year)

        self.pushButton_weight_all_time = QPushButton(self.frame_weight_controls)
        self.pushButton_weight_all_time.setObjectName("pushButton_weight_all_time")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_weight_all_time)

        self.pushButton_update_weight_chart = QPushButton(self.frame_weight_controls)
        self.pushButton_update_weight_chart.setObjectName("pushButton_update_weight_chart")

        self.horizontalLayout_weight_controls.addWidget(self.pushButton_update_weight_chart)

        self.horizontalSpacer_weight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_weight_controls.addItem(self.horizontalSpacer_weight)

        self.verticalLayout_6.addWidget(self.frame_weight_controls)

        self.scrollArea_weight_chart = QScrollArea(self.tab_5)
        self.scrollArea_weight_chart.setObjectName("scrollArea_weight_chart")
        self.scrollArea_weight_chart.setWidgetResizable(True)
        self.scrollAreaWidgetContents_weight_chart = QWidget()
        self.scrollAreaWidgetContents_weight_chart.setObjectName("scrollAreaWidgetContents_weight_chart")
        self.scrollAreaWidgetContents_weight_chart.setGeometry(QRect(0, 0, 1073, 758))
        self.verticalLayout_weight_chart_content = QVBoxLayout(self.scrollAreaWidgetContents_weight_chart)
        self.verticalLayout_weight_chart_content.setObjectName("verticalLayout_weight_chart_content")
        self.scrollArea_weight_chart.setWidget(self.scrollAreaWidgetContents_weight_chart)

        self.verticalLayout_6.addWidget(self.scrollArea_weight_chart)

        self.horizontalLayout_5.addLayout(self.verticalLayout_6)

        self.frame_4 = QFrame(self.tab_5)
        self.frame_4.setObjectName("frame_4")
        self.frame_4.setMinimumSize(QSize(250, 0))
        self.frame_4.setMaximumSize(QSize(250, 16777215))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_4)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.groupBox_4 = QGroupBox(self.frame_4)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.doubleSpinBox_weight = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_weight.setObjectName("doubleSpinBox_weight")
        self.doubleSpinBox_weight.setMaximum(300.000000000000000)
        self.doubleSpinBox_weight.setValue(89.000000000000000)

        self.verticalLayout_7.addWidget(self.doubleSpinBox_weight)

        self.dateEdit_weight = QDateEdit(self.groupBox_4)
        self.dateEdit_weight.setObjectName("dateEdit_weight")
        self.dateEdit_weight.setMinimumSize(QSize(191, 0))
        self.dateEdit_weight.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.dateEdit_weight.setCalendarPopup(True)

        self.verticalLayout_7.addWidget(self.dateEdit_weight)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_3)

        self.pushButton_weight_add = QPushButton(self.groupBox_4)
        self.pushButton_weight_add.setObjectName("pushButton_weight_add")

        self.horizontalLayout_15.addWidget(self.pushButton_weight_add)

        self.verticalLayout_7.addLayout(self.horizontalLayout_15)

        self.verticalLayout_9.addWidget(self.groupBox_4)

        self.groupBox_6 = QGroupBox(self.frame_4)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.pushButton_weight_delete = QPushButton(self.groupBox_6)
        self.pushButton_weight_delete.setObjectName("pushButton_weight_delete")

        self.horizontalLayout_16.addWidget(self.pushButton_weight_delete)

        self.pushButton_weight_refresh = QPushButton(self.groupBox_6)
        self.pushButton_weight_refresh.setObjectName("pushButton_weight_refresh")

        self.horizontalLayout_16.addWidget(self.pushButton_weight_refresh)

        self.verticalLayout_8.addLayout(self.horizontalLayout_16)

        self.verticalLayout_9.addWidget(self.groupBox_6)

        self.tableView_weight = QTableView(self.frame_4)
        self.tableView_weight.setObjectName("tableView_weight")

        self.verticalLayout_9.addWidget(self.tableView_weight)

        self.horizontalLayout_5.addWidget(self.frame_4)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName("tab_charts")
        self.verticalLayout_charts = QVBoxLayout(self.tab_charts)
        self.verticalLayout_charts.setObjectName("verticalLayout_charts")
        self.frame_charts_controls = QFrame(self.tab_charts)
        self.frame_charts_controls.setObjectName("frame_charts_controls")
        self.frame_charts_controls.setMaximumSize(QSize(16777215, 120))
        self.frame_charts_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_charts_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_charts_controls = QVBoxLayout(self.frame_charts_controls)
        self.verticalLayout_charts_controls.setObjectName("verticalLayout_charts_controls")
        self.horizontalLayout_charts_controls_1 = QHBoxLayout()
        self.horizontalLayout_charts_controls_1.setObjectName("horizontalLayout_charts_controls_1")
        self.label_chart_exercise = QLabel(self.frame_charts_controls)
        self.label_chart_exercise.setObjectName("label_chart_exercise")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_exercise)

        self.comboBox_chart_exercise = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_exercise.setObjectName("comboBox_chart_exercise")

        self.horizontalLayout_charts_controls_1.addWidget(self.comboBox_chart_exercise)

        self.label_chart_type = QLabel(self.frame_charts_controls)
        self.label_chart_type.setObjectName("label_chart_type")

        self.horizontalLayout_charts_controls_1.addWidget(self.label_chart_type)

        self.comboBox_chart_type = QComboBox(self.frame_charts_controls)
        self.comboBox_chart_type.setObjectName("comboBox_chart_type")

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

        self.pushButton_show_sets_chart = QPushButton(self.frame_charts_controls)
        self.pushButton_show_sets_chart.setObjectName("pushButton_show_sets_chart")

        self.horizontalLayout_charts_controls_1.addWidget(self.pushButton_show_sets_chart)

        self.horizontalSpacer_charts = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_charts_controls_1.addItem(self.horizontalSpacer_charts)

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

        self.verticalLayout_charts.addWidget(self.frame_charts_controls)

        self.scrollArea_charts = QScrollArea(self.tab_charts)
        self.scrollArea_charts.setObjectName("scrollArea_charts")
        self.scrollArea_charts.setWidgetResizable(True)
        self.scrollAreaWidgetContents_charts = QWidget()
        self.scrollAreaWidgetContents_charts.setObjectName("scrollAreaWidgetContents_charts")
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1331, 727))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setObjectName("verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_charts.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.textEdit_statistics = QTextEdit(self.tab_4)
        self.textEdit_statistics.setObjectName("textEdit_statistics")
        font1 = QFont()
        font1.setFamilies(["JetBrains Mono"])
        font1.setPointSize(9)
        self.textEdit_statistics.setFont(font1)

        self.horizontalLayout_6.addWidget(self.textEdit_statistics)

        self.frame_5 = QFrame(self.tab_4)
        self.frame_5.setObjectName("frame_5")
        self.frame_5.setMinimumSize(QSize(300, 0))
        self.frame_5.setMaximumSize(QSize(300, 16777215))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_5)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.pushButton_statistics_refresh = QPushButton(self.frame_5)
        self.pushButton_statistics_refresh.setObjectName("pushButton_statistics_refresh")

        self.verticalLayout_16.addWidget(self.pushButton_statistics_refresh)

        self.verticalSpacer_4 = QSpacerItem(20, 759, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_4, "")

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
