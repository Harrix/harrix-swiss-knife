# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitness_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QTableView,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QWidget,
)


class Ui_MainWindow(object):
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Fitness tracker", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", "Add Exercise", None))
        self.pushButton_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.pushButton_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.label.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", "Export Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", "List", None)
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Name", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Unit of Measurement", None))
        self.pushButton_exercise_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_exercise_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_exercise_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_exercise_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", "Exercises", None)
        )
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", "Add New Exercise Type", None))
        self.pushButton_type_add.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", "With the selected row:", None))
        self.pushButton_type_delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.pushButton_type_update.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.pushButton_type_refresh.setText(QCoreApplication.translate("MainWindow", "Refresh Table", None))
        self.pushButton_17.setText(QCoreApplication.translate("MainWindow", "PushButton", None))
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
        self.pushButton_statistics_refresh.setText(QCoreApplication.translate("MainWindow", "Records", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", "Analytics", None)
        )

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1191, 822)
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
        self.horizontalLayout_2 = QHBoxLayout(self.tab)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tableView = QTableView(self.tab)
        self.tableView.setObjectName("tableView")

        self.horizontalLayout_2.addWidget(self.tableView)

        self.frame = QFrame(self.tab)
        self.frame.setObjectName("frame")
        self.frame.setMinimumSize(QSize(301, 0))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 281, 211))
        self.pushButton_add = QPushButton(self.groupBox)
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_add.setGeometry(QRect(200, 180, 75, 23))
        self.comboBox = QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(10, 20, 261, 22))
        self.comboBox_2 = QComboBox(self.groupBox)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setGeometry(QRect(10, 60, 261, 22))
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(10, 140, 261, 20))
        self.spinBox = QSpinBox(self.groupBox)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setGeometry(QRect(10, 100, 261, 22))
        self.spinBox.setMaximum(1000000)
        self.spinBox.setValue(100)
        self.pushButton_delete = QPushButton(self.frame)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.pushButton_delete.setGeometry(QRect(10, 260, 75, 23))
        self.label = QLabel(self.frame)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 230, 131, 16))
        self.pushButton_update = QPushButton(self.frame)
        self.pushButton_update.setObjectName("pushButton_update")
        self.pushButton_update.setGeometry(QRect(100, 260, 75, 23))
        self.pushButton_refresh = QPushButton(self.frame)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.pushButton_refresh.setGeometry(QRect(10, 310, 161, 23))
        self.pushButton_export_csv = QPushButton(self.frame)
        self.pushButton_export_csv.setObjectName("pushButton_export_csv")
        self.pushButton_export_csv.setGeometry(QRect(10, 340, 161, 23))

        self.horizontalLayout_2.addWidget(self.frame)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableView_2 = QTableView(self.tab_2)
        self.tableView_2.setObjectName("tableView_2")

        self.horizontalLayout_3.addWidget(self.tableView_2)

        self.frame_2 = QFrame(self.tab_2)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setMinimumSize(QSize(300, 0))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 10, 281, 151))
        self.lineEdit_4 = QLineEdit(self.groupBox_2)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_4.setGeometry(QRect(10, 20, 113, 20))
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(160, 20, 47, 13))
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(160, 50, 111, 16))
        self.lineEdit_5 = QLineEdit(self.groupBox_2)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_5.setGeometry(QRect(10, 50, 113, 20))
        self.pushButton_exercise_add = QPushButton(self.groupBox_2)
        self.pushButton_exercise_add.setObjectName("pushButton_exercise_add")
        self.pushButton_exercise_add.setGeometry(QRect(190, 120, 75, 23))
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(10, 170, 141, 16))
        self.pushButton_exercise_delete = QPushButton(self.frame_2)
        self.pushButton_exercise_delete.setObjectName("pushButton_exercise_delete")
        self.pushButton_exercise_delete.setGeometry(QRect(10, 200, 75, 23))
        self.pushButton_exercise_update = QPushButton(self.frame_2)
        self.pushButton_exercise_update.setObjectName("pushButton_exercise_update")
        self.pushButton_exercise_update.setGeometry(QRect(90, 200, 75, 23))
        self.pushButton_exercise_refresh = QPushButton(self.frame_2)
        self.pushButton_exercise_refresh.setObjectName("pushButton_exercise_refresh")
        self.pushButton_exercise_refresh.setGeometry(QRect(10, 230, 151, 23))

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView_3 = QTableView(self.tab_3)
        self.tableView_3.setObjectName("tableView_3")

        self.horizontalLayout_4.addWidget(self.tableView_3)

        self.frame_3 = QFrame(self.tab_3)
        self.frame_3.setObjectName("frame_3")
        self.frame_3.setMinimumSize(QSize(300, 0))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.groupBox_3 = QGroupBox(self.frame_3)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 10, 291, 161))
        self.comboBox_3 = QComboBox(self.groupBox_3)
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.setGeometry(QRect(20, 30, 241, 22))
        self.lineEdit_6 = QLineEdit(self.groupBox_3)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setGeometry(QRect(20, 70, 241, 20))
        self.pushButton_type_add = QPushButton(self.groupBox_3)
        self.pushButton_type_add.setObjectName("pushButton_type_add")
        self.pushButton_type_add.setGeometry(QRect(190, 110, 75, 23))
        self.label_4 = QLabel(self.frame_3)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(10, 180, 141, 16))
        self.pushButton_type_delete = QPushButton(self.frame_3)
        self.pushButton_type_delete.setObjectName("pushButton_type_delete")
        self.pushButton_type_delete.setGeometry(QRect(10, 220, 75, 23))
        self.pushButton_type_update = QPushButton(self.frame_3)
        self.pushButton_type_update.setObjectName("pushButton_type_update")
        self.pushButton_type_update.setGeometry(QRect(100, 220, 75, 23))
        self.pushButton_type_refresh = QPushButton(self.frame_3)
        self.pushButton_type_refresh.setObjectName("pushButton_type_refresh")
        self.pushButton_type_refresh.setGeometry(QRect(10, 260, 151, 23))
        self.pushButton_17 = QPushButton(self.frame_3)
        self.pushButton_17.setObjectName("pushButton_17")
        self.pushButton_17.setGeometry(QRect(230, 330, 61, 21))
        font = QFont()
        font.setPointSize(20)
        self.pushButton_17.setFont(font)

        self.horizontalLayout_4.addWidget(self.frame_3)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_5)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tableView_4 = QTableView(self.tab_5)
        self.tableView_4.setObjectName("tableView_4")

        self.horizontalLayout_5.addWidget(self.tableView_4)

        self.frame_4 = QFrame(self.tab_5)
        self.frame_4.setObjectName("frame_4")
        self.frame_4.setMinimumSize(QSize(300, 0))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.groupBox_4 = QGroupBox(self.frame_4)
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setGeometry(QRect(10, 10, 281, 131))
        self.lineEdit_3 = QLineEdit(self.groupBox_4)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(10, 50, 261, 20))
        self.pushButton_weight_add = QPushButton(self.groupBox_4)
        self.pushButton_weight_add.setObjectName("pushButton_weight_add")
        self.pushButton_weight_add.setGeometry(QRect(190, 90, 75, 23))
        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(10, 20, 261, 22))
        self.doubleSpinBox.setMaximum(300.000000000000000)
        self.doubleSpinBox.setValue(89.000000000000000)
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
        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.textEdit = QTextEdit(self.tab_4)
        self.textEdit.setObjectName("textEdit")
        font1 = QFont()
        font1.setFamilies(["Roboto Mono"])
        font1.setPointSize(10)
        self.textEdit.setFont(font1)

        self.horizontalLayout_6.addWidget(self.textEdit)

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
        self.menuBar.setGeometry(QRect(0, 0, 1191, 21))
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
