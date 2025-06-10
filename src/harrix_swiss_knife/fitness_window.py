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
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_yesterday.setText(QCoreApplication.translate("MainWindow", "Yesterday", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.label.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", "Export Table", None))
        self.groupBox_filter.setTitle(QCoreApplication.translate("MainWindow", "Filter", None))
        self.label_filter_exercise.setText(QCoreApplication.translate("MainWindow", "Exercise:", None))
        self.label_filter_type.setText(QCoreApplication.translate("MainWindow", "Type:", None))
        self.label_filter_date.setText(QCoreApplication.translate("MainWindow", "Date:", None))
        self.dateEdit_filter_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_filter_to.setText(QCoreApplication.translate("MainWindow", "to", None))
        self.dateEdit_filter_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_apply_filter.setText(QCoreApplication.translate("MainWindow", "Apply Filter", None))
        self.pushButton_clear_filter.setText(QCoreApplication.translate("MainWindow", "Clear Filter", None))
        self.checkBox_use_date_filter.setText(QCoreApplication.translate("MainWindow", "Use date filter", None))
        self.label_exercise_avif.setText(QCoreApplication.translate("MainWindow", "No exercise selected", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", "Sets", None)
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Unit of Measurement", None))
        self.pushButton_exercise_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.check_box_is_type_required.setText(QCoreApplication.translate("MainWindow", "Type required", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_exercises_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_exercises_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_exercises_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", "Exercises", None)
        )
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise Type", None))
        self.pushButton_type_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_types_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_types_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_types_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", "Exercise Types", None)
        )
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", "Add New Data", None))
        self.pushButton_weight_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.pushButton_weight_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_weight_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_weight_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
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
        self.label_weight_from.setText(QCoreApplication.translate("MainWindow", "From:", None))
        self.dateEdit_weight_from.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.label_weight_to.setText(QCoreApplication.translate("MainWindow", "To:", None))
        self.dateEdit_weight_to.setDisplayFormat(QCoreApplication.translate("MainWindow", "yyyy-MM-dd", None))
        self.pushButton_weight_last_month.setText(QCoreApplication.translate("MainWindow", "Last Month", None))
        self.pushButton_weight_last_year.setText(QCoreApplication.translate("MainWindow", "Last Year", None))
        self.pushButton_weight_all_time.setText(QCoreApplication.translate("MainWindow", "All Time", None))
        self.pushButton_update_weight_chart.setText(QCoreApplication.translate("MainWindow", "Update Chart", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_weight_chart),
            QCoreApplication.translate("MainWindow", "Weight Chart", None),
        )
        self.pushButton_statistics_refresh.setText(QCoreApplication.translate("MainWindow", "Records", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", "Statistics", None)
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1260, 926)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_main = QHBoxLayout(self.tab)
        self.horizontalLayout_main.setSpacing(6)
        self.horizontalLayout_main.setContentsMargins(11, 11, 11, 11)
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
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.widget_middle)
        self.label_7.setObjectName("label_7")

        self.verticalLayout.addWidget(self.label_7)

        self.listView_exercises = QListView(self.widget_middle)
        self.listView_exercises.setObjectName("listView_exercises")
        self.listView_exercises.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout.addWidget(self.listView_exercises)

        self.splitter.addWidget(self.widget_middle)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(301, 0))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 281, 191))
        self.pushButton_add = QPushButton(self.groupBox)
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_add.setGeometry(QRect(4, 150, 271, 31))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.pushButton_add.setFont(font)
        self.comboBox_type = QComboBox(self.groupBox)
        self.comboBox_type.setObjectName("comboBox_type")
        self.comboBox_type.setGeometry(QRect(10, 30, 261, 22))
        self.spinBox_count = QSpinBox(self.groupBox)
        self.spinBox_count.setObjectName("spinBox_count")
        self.spinBox_count.setGeometry(QRect(10, 70, 261, 22))
        self.spinBox_count.setMaximum(1000000)
        self.spinBox_count.setValue(100)
        self.dateEdit = QDateEdit(self.groupBox)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setGeometry(QRect(10, 110, 191, 22))
        self.dateEdit.setCalendarPopup(True)
        self.pushButton_yesterday = QPushButton(self.groupBox)
        self.pushButton_yesterday.setObjectName("pushButton_yesterday")
        self.pushButton_yesterday.setGeometry(QRect(210, 110, 61, 22))
        self.pushButton_delete = QPushButton(self.frame)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setGeometry(QRect(10, 240, 75, 23))
        self.label = QLabel(self.frame)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 210, 131, 16))
        self.pushButton_update = QPushButton(self.frame)
        self.pushButton_update.setObjectName("pushButton_update")
        self.pushButton_update.setGeometry(QRect(100, 240, 75, 23))
        self.pushButton_refresh = QPushButton(self.frame)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setGeometry(QRect(10, 290, 161, 23))
        self.pushButton_export_csv = QPushButton(self.frame)
        self.pushButton_export_csv.setObjectName("pushButton_export_csv")
        self.pushButton_export_csv.setGeometry(QRect(10, 320, 161, 23))
        self.groupBox_filter = QGroupBox(self.frame)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.groupBox_filter.setGeometry(QRect(10, 360, 281, 221))
        self.label_filter_exercise = QLabel(self.groupBox_filter)
        self.label_filter_exercise.setObjectName("label_filter_exercise")
        self.label_filter_exercise.setGeometry(QRect(10, 20, 61, 16))
        self.comboBox_filter_exercise = QComboBox(self.groupBox_filter)
        self.comboBox_filter_exercise.setObjectName("comboBox_filter_exercise")
        self.comboBox_filter_exercise.setGeometry(QRect(80, 20, 191, 22))
        self.label_filter_type = QLabel(self.groupBox_filter)
        self.label_filter_type.setObjectName("label_filter_type")
        self.label_filter_type.setGeometry(QRect(10, 50, 61, 16))
        self.comboBox_filter_type = QComboBox(self.groupBox_filter)
        self.comboBox_filter_type.setObjectName("comboBox_filter_type")
        self.comboBox_filter_type.setGeometry(QRect(80, 50, 191, 22))
        self.label_filter_date = QLabel(self.groupBox_filter)
        self.label_filter_date.setObjectName("label_filter_date")
        self.label_filter_date.setGeometry(QRect(10, 80, 61, 16))
        self.dateEdit_filter_from = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_from.setObjectName("dateEdit_filter_from")
        self.dateEdit_filter_from.setGeometry(QRect(80, 80, 191, 22))
        self.dateEdit_filter_from.setCalendarPopup(True)
        self.label_filter_to = QLabel(self.groupBox_filter)
        self.label_filter_to.setObjectName("label_filter_to")
        self.label_filter_to.setGeometry(QRect(20, 110, 21, 16))
        self.label_filter_to.setAlignment(Qt.AlignCenter)
        self.dateEdit_filter_to = QDateEdit(self.groupBox_filter)
        self.dateEdit_filter_to.setObjectName("dateEdit_filter_to")
        self.dateEdit_filter_to.setGeometry(QRect(80, 110, 191, 22))
        self.dateEdit_filter_to.setCalendarPopup(True)
        self.pushButton_apply_filter = QPushButton(self.groupBox_filter)
        self.pushButton_apply_filter.setObjectName("pushButton_apply_filter")
        self.pushButton_apply_filter.setGeometry(QRect(190, 180, 81, 23))
        self.pushButton_clear_filter = QPushButton(self.groupBox_filter)
        self.pushButton_clear_filter.setObjectName("pushButton_clear_filter")
        self.pushButton_clear_filter.setGeometry(QRect(100, 180, 81, 23))
        self.checkBox_use_date_filter = QCheckBox(self.groupBox_filter)
        self.checkBox_use_date_filter.setObjectName("checkBox_use_date_filter")
        self.checkBox_use_date_filter.setGeometry(QRect(10, 160, 131, 17))
        self.label_exercise_avif = QLabel(self.frame)
        self.label_exercise_avif.setObjectName("label_exercise_avif")
        self.label_exercise_avif.setGeometry(QRect(10, 590, 281, 150))
        self.label_exercise_avif.setStyleSheet("border: 1px solid gray;")
        self.label_exercise_avif.setScaledContents(False)
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)
        self.splitter.addWidget(self.frame)

        self.horizontalLayout_main.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableView_exercises = QTableView(self.tab_2)
        self.tableView_exercises.setObjectName("tableView_exercises")

        self.horizontalLayout_3.addWidget(self.tableView_exercises)

        self.frame_2 = QFrame(self.tab_2)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setMinimumSize(QSize(300, 0))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 10, 281, 151))
        self.lineEdit_exercise_name = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_name.setObjectName("lineEdit_exercise_name")
        self.lineEdit_exercise_name.setGeometry(QRect(10, 20, 113, 20))
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(160, 20, 47, 13))
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(160, 50, 111, 16))
        self.lineEdit_exercise_unit = QLineEdit(self.groupBox_2)
        self.lineEdit_exercise_unit.setObjectName("lineEdit_exercise_unit")
        self.lineEdit_exercise_unit.setGeometry(QRect(10, 50, 113, 20))
        self.pushButton_exercise_add = QPushButton(self.groupBox_2)
        self.pushButton_exercise_add.setObjectName("pushButton_exercise_add")
        self.pushButton_exercise_add.setGeometry(QRect(190, 120, 75, 23))
        self.check_box_is_type_required = QCheckBox(self.groupBox_2)
        self.check_box_is_type_required.setObjectName("check_box_is_type_required")
        self.check_box_is_type_required.setGeometry(QRect(10, 80, 251, 17))
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(10, 170, 141, 16))
        self.pushButton_exercises_delete = QPushButton(self.frame_2)
        self.pushButton_exercises_delete.setObjectName("pushButton_exercises_delete")
        self.pushButton_exercises_delete.setGeometry(QRect(10, 200, 75, 23))
        self.pushButton_exercises_update = QPushButton(self.frame_2)
        self.pushButton_exercises_update.setObjectName("pushButton_exercises_update")
        self.pushButton_exercises_update.setGeometry(QRect(90, 200, 75, 23))
        self.pushButton_exercises_refresh = QPushButton(self.frame_2)
        self.pushButton_exercises_refresh.setObjectName("pushButton_exercises_refresh")
        self.pushButton_exercises_refresh.setGeometry(QRect(10, 230, 151, 23))

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView_exercise_types = QTableView(self.tab_3)
        self.tableView_exercise_types.setObjectName("tableView_exercise_types")

        self.horizontalLayout_4.addWidget(self.tableView_exercise_types)

        self.frame_3 = QFrame(self.tab_3)
        self.frame_3.setObjectName("frame_3")
        self.frame_3.setMinimumSize(QSize(300, 0))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.groupBox_3 = QGroupBox(self.frame_3)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 10, 291, 161))
        self.comboBox_exercise_name = QComboBox(self.groupBox_3)
        self.comboBox_exercise_name.setObjectName("comboBox_exercise_name")
        self.comboBox_exercise_name.setGeometry(QRect(20, 30, 241, 22))
        self.lineEdit_exercise_type = QLineEdit(self.groupBox_3)
        self.lineEdit_exercise_type.setObjectName("lineEdit_exercise_type")
        self.lineEdit_exercise_type.setGeometry(QRect(20, 70, 241, 20))
        self.pushButton_type_add = QPushButton(self.groupBox_3)
        self.pushButton_type_add.setObjectName("pushButton_type_add")
        self.pushButton_type_add.setGeometry(QRect(190, 110, 75, 23))
        self.label_4 = QLabel(self.frame_3)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(10, 180, 141, 16))
        self.pushButton_types_delete = QPushButton(self.frame_3)
        self.pushButton_types_delete.setObjectName("pushButton_types_delete")
        self.pushButton_types_delete.setGeometry(QRect(10, 220, 75, 23))
        self.pushButton_types_update = QPushButton(self.frame_3)
        self.pushButton_types_update.setObjectName("pushButton_types_update")
        self.pushButton_types_update.setGeometry(QRect(100, 220, 75, 23))
        self.pushButton_types_refresh = QPushButton(self.frame_3)
        self.pushButton_types_refresh.setObjectName("pushButton_types_refresh")
        self.pushButton_types_refresh.setGeometry(QRect(10, 260, 151, 23))

        self.horizontalLayout_4.addWidget(self.frame_3)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_5)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tableView_weight = QTableView(self.tab_5)
        self.tableView_weight.setObjectName("tableView_weight")

        self.horizontalLayout_5.addWidget(self.tableView_weight)

        self.frame_4 = QFrame(self.tab_5)
        self.frame_4.setObjectName("frame_4")
        self.frame_4.setMinimumSize(QSize(300, 0))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.groupBox_4 = QGroupBox(self.frame_4)
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setGeometry(QRect(10, 10, 281, 131))
        self.lineEdit_weight_date = QLineEdit(self.groupBox_4)
        self.lineEdit_weight_date.setObjectName("lineEdit_weight_date")
        self.lineEdit_weight_date.setGeometry(QRect(10, 50, 261, 20))
        self.pushButton_weight_add = QPushButton(self.groupBox_4)
        self.pushButton_weight_add.setObjectName("pushButton_weight_add")
        self.pushButton_weight_add.setGeometry(QRect(190, 90, 75, 23))
        self.doubleSpinBox_weight = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_weight.setObjectName("doubleSpinBox_weight")
        self.doubleSpinBox_weight.setGeometry(QRect(10, 20, 261, 22))
        self.doubleSpinBox_weight.setMaximum(300.000000000000000)
        self.doubleSpinBox_weight.setValue(89.000000000000000)
        self.pushButton_weight_delete = QPushButton(self.frame_4)
        self.pushButton_weight_delete.setObjectName("pushButton_weight_delete")
        self.pushButton_weight_delete.setGeometry(QRect(10, 170, 75, 23))
        self.pushButton_weight_update = QPushButton(self.frame_4)
        self.pushButton_weight_update.setObjectName("pushButton_weight_update")
        self.pushButton_weight_update.setGeometry(QRect(90, 170, 75, 23))
        self.pushButton_weight_refresh = QPushButton(self.frame_4)
        self.pushButton_weight_refresh.setObjectName("pushButton_weight_refresh")
        self.pushButton_weight_refresh.setGeometry(QRect(10, 210, 151, 23))
        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(10, 150, 141, 16))

        self.horizontalLayout_5.addWidget(self.frame_4)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_charts = QWidget()
        self.tab_charts.setObjectName("tab_charts")
        self.verticalLayout_charts = QVBoxLayout(self.tab_charts)
        self.verticalLayout_charts.setSpacing(6)
        self.verticalLayout_charts.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_charts.setObjectName("verticalLayout_charts")
        self.frame_charts_controls = QFrame(self.tab_charts)
        self.frame_charts_controls.setObjectName("frame_charts_controls")
        self.frame_charts_controls.setMaximumSize(QSize(16777215, 120))
        self.frame_charts_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_charts_controls.setFrameShadow(QFrame.Raised)
        self.verticalLayout_charts_controls = QVBoxLayout(self.frame_charts_controls)
        self.verticalLayout_charts_controls.setSpacing(6)
        self.verticalLayout_charts_controls.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_charts_controls.setObjectName("verticalLayout_charts_controls")
        self.horizontalLayout_charts_controls_1 = QHBoxLayout()
        self.horizontalLayout_charts_controls_1.setSpacing(6)
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
        self.horizontalLayout_charts_controls_2.setSpacing(6)
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
        self.scrollAreaWidgetContents_charts.setGeometry(QRect(0, 0, 1216, 727))
        self.verticalLayout_charts_content = QVBoxLayout(self.scrollAreaWidgetContents_charts)
        self.verticalLayout_charts_content.setSpacing(6)
        self.verticalLayout_charts_content.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_charts_content.setObjectName("verticalLayout_charts_content")
        self.scrollArea_charts.setWidget(self.scrollAreaWidgetContents_charts)

        self.verticalLayout_charts.addWidget(self.scrollArea_charts)

        self.tabWidget.addTab(self.tab_charts, "")
        self.tab_weight_chart = QWidget()
        self.tab_weight_chart.setObjectName("tab_weight_chart")
        self.verticalLayout_weight_chart = QVBoxLayout(self.tab_weight_chart)
        self.verticalLayout_weight_chart.setSpacing(6)
        self.verticalLayout_weight_chart.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_weight_chart.setObjectName("verticalLayout_weight_chart")
        self.frame_weight_controls = QFrame(self.tab_weight_chart)
        self.frame_weight_controls.setObjectName("frame_weight_controls")
        self.frame_weight_controls.setMaximumSize(QSize(16777215, 80))
        self.frame_weight_controls.setFrameShape(QFrame.StyledPanel)
        self.frame_weight_controls.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_weight_controls = QHBoxLayout(self.frame_weight_controls)
        self.horizontalLayout_weight_controls.setSpacing(6)
        self.horizontalLayout_weight_controls.setContentsMargins(11, 11, 11, 11)
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

        self.verticalLayout_weight_chart.addWidget(self.frame_weight_controls)

        self.scrollArea_weight_chart = QScrollArea(self.tab_weight_chart)
        self.scrollArea_weight_chart.setObjectName("scrollArea_weight_chart")
        self.scrollArea_weight_chart.setWidgetResizable(True)
        self.scrollAreaWidgetContents_weight_chart = QWidget()
        self.scrollAreaWidgetContents_weight_chart.setObjectName("scrollAreaWidgetContents_weight_chart")
        self.scrollAreaWidgetContents_weight_chart.setGeometry(QRect(0, 0, 1216, 760))
        self.verticalLayout_weight_chart_content = QVBoxLayout(self.scrollAreaWidgetContents_weight_chart)
        self.verticalLayout_weight_chart_content.setSpacing(6)
        self.verticalLayout_weight_chart_content.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_weight_chart_content.setObjectName("verticalLayout_weight_chart_content")
        self.scrollArea_weight_chart.setWidget(self.scrollAreaWidgetContents_weight_chart)

        self.verticalLayout_weight_chart.addWidget(self.scrollArea_weight_chart)

        self.tabWidget.addTab(self.tab_weight_chart, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setContentsMargins(11, 11, 11, 11)
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
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.pushButton_statistics_refresh = QPushButton(self.frame_5)
        self.pushButton_statistics_refresh.setObjectName("pushButton_statistics_refresh")
        self.pushButton_statistics_refresh.setGeometry(QRect(20, 20, 75, 23))

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_4, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1260, 21))
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
