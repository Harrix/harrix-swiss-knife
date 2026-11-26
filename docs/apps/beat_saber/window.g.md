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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Beat Saber tracker", None))
        self.action_sync_pc.setText(QCoreApplication.translate("MainWindow", "Sync from PC", None))
        self.action_sync_quest.setText(QCoreApplication.translate("MainWindow", "Sync from Quest", None))
        self.action_import_backups.setText(QCoreApplication.translate("MainWindow", "Import backups\u2026", None))
        self.action_refresh_catalog.setText(QCoreApplication.translate("MainWindow", "Refresh catalog", None))
        self.action_refresh_views.setText(QCoreApplication.translate("MainWindow", "Refresh views", None))
        self.action_export_pc.setText(QCoreApplication.translate("MainWindow", "Export PC", None))
        self.action_export_quest.setText(QCoreApplication.translate("MainWindow", "Export Quest", None))
        self.action_import_pc.setText(QCoreApplication.translate("MainWindow", "Import PC", None))
        self.action_import_quest.setText(QCoreApplication.translate("MainWindow", "Import Quest", None))
        self.action_backup_db.setText(QCoreApplication.translate("MainWindow", "Backup DB", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About", None))
        self.label_summary.setText(QCoreApplication.translate("MainWindow", "Summary", None))
        self.label_source.setText(QCoreApplication.translate("MainWindow", "Source", None))
        self.combo_source.setItemText(0, QCoreApplication.translate("MainWindow", "Best (PC or Quest)", None))
        self.combo_source.setItemText(1, QCoreApplication.translate("MainWindow", "PC", None))
        self.combo_source.setItemText(2, QCoreApplication.translate("MainWindow", "Quest", None))

        self.label_difficulty.setText(QCoreApplication.translate("MainWindow", "Difficulty", None))
        self.combo_difficulty.setItemText(0, QCoreApplication.translate("MainWindow", "All", None))
        self.combo_difficulty.setItemText(1, QCoreApplication.translate("MainWindow", "Easy", None))
        self.combo_difficulty.setItemText(2, QCoreApplication.translate("MainWindow", "Normal", None))
        self.combo_difficulty.setItemText(3, QCoreApplication.translate("MainWindow", "Hard", None))
        self.combo_difficulty.setItemText(4, QCoreApplication.translate("MainWindow", "Expert", None))
        self.combo_difficulty.setItemText(5, QCoreApplication.translate("MainWindow", "Expert+", None))

        self.line_search.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search song or pack\u2026", None))
        self.check_require_fc.setText(QCoreApplication.translate("MainWindow", "Require full combo", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_missing), QCoreApplication.translate("MainWindow", "Missing", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_compare), QCoreApplication.translate("MainWindow", "Compare", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_clears), QCoreApplication.translate("MainWindow", "Clears", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_history), QCoreApplication.translate("MainWindow", "History", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuSync.setTitle(QCoreApplication.translate("MainWindow", "Sync", None))
        self.menuSaves.setTitle(QCoreApplication.translate("MainWindow", "Saves", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 700)
        self.action_sync_pc = QAction(MainWindow)
        self.action_sync_pc.setObjectName("action_sync_pc")
        self.action_sync_quest = QAction(MainWindow)
        self.action_sync_quest.setObjectName("action_sync_quest")
        self.action_import_backups = QAction(MainWindow)
        self.action_import_backups.setObjectName("action_import_backups")
        self.action_refresh_catalog = QAction(MainWindow)
        self.action_refresh_catalog.setObjectName("action_refresh_catalog")
        self.action_refresh_views = QAction(MainWindow)
        self.action_refresh_views.setObjectName("action_refresh_views")
        self.action_export_pc = QAction(MainWindow)
        self.action_export_pc.setObjectName("action_export_pc")
        self.action_export_quest = QAction(MainWindow)
        self.action_export_quest.setObjectName("action_export_quest")
        self.action_import_pc = QAction(MainWindow)
        self.action_import_pc.setObjectName("action_import_pc")
        self.action_import_quest = QAction(MainWindow)
        self.action_import_quest.setObjectName("action_import_quest")
        self.action_backup_db = QAction(MainWindow)
        self.action_backup_db.setObjectName("action_backup_db")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_root = QVBoxLayout(self.centralWidget)
        self.verticalLayout_root.setSpacing(0)
        self.verticalLayout_root.setObjectName("verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_missing = QWidget()
        self.tab_missing.setObjectName("tab_missing")
        self.verticalLayout_missing = QVBoxLayout(self.tab_missing)
        self.verticalLayout_missing.setObjectName("verticalLayout_missing")
        self.verticalLayout_missing.setContentsMargins(9, 9, 9, 9)
        self.frame_header = QFrame(self.tab_missing)
        self.frame_header.setObjectName("frame_header")
        self.frame_header.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_header = QVBoxLayout(self.frame_header)
        self.verticalLayout_header.setObjectName("verticalLayout_header")
        self.verticalLayout_header.setContentsMargins(0, 0, 0, 0)
        self.label_summary = QLabel(self.frame_header)
        self.label_summary.setObjectName("label_summary")
        self.label_summary.setWordWrap(True)

        self.verticalLayout_header.addWidget(self.label_summary)

        self.horizontalLayout_filters = QHBoxLayout()
        self.horizontalLayout_filters.setObjectName("horizontalLayout_filters")
        self.label_source = QLabel(self.frame_header)
        self.label_source.setObjectName("label_source")

        self.horizontalLayout_filters.addWidget(self.label_source)

        self.combo_source = QComboBox(self.frame_header)
        self.combo_source.addItem("")
        self.combo_source.addItem("")
        self.combo_source.addItem("")
        self.combo_source.setObjectName("combo_source")

        self.horizontalLayout_filters.addWidget(self.combo_source)

        self.label_difficulty = QLabel(self.frame_header)
        self.label_difficulty.setObjectName("label_difficulty")

        self.horizontalLayout_filters.addWidget(self.label_difficulty)

        self.combo_difficulty = QComboBox(self.frame_header)
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.setObjectName("combo_difficulty")

        self.horizontalLayout_filters.addWidget(self.combo_difficulty)

        self.line_search = QLineEdit(self.frame_header)
        self.line_search.setObjectName("line_search")

        self.horizontalLayout_filters.addWidget(self.line_search)

        self.check_require_fc = QCheckBox(self.frame_header)
        self.check_require_fc.setObjectName("check_require_fc")

        self.horizontalLayout_filters.addWidget(self.check_require_fc)

        self.horizontalSpacer_filters = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_filters.addItem(self.horizontalSpacer_filters)

        self.verticalLayout_header.addLayout(self.horizontalLayout_filters)

        self.verticalLayout_missing.addWidget(self.frame_header)

        self.table_missing = QTableWidget(self.tab_missing)
        self.table_missing.setObjectName("table_missing")

        self.verticalLayout_missing.addWidget(self.table_missing)

        self.tabWidget.addTab(self.tab_missing, "")
        self.tab_compare = QWidget()
        self.tab_compare.setObjectName("tab_compare")
        self.verticalLayout_compare = QVBoxLayout(self.tab_compare)
        self.verticalLayout_compare.setObjectName("verticalLayout_compare")
        self.verticalLayout_compare.setContentsMargins(9, 9, 9, 9)
        self.table_compare = QTableWidget(self.tab_compare)
        self.table_compare.setObjectName("table_compare")

        self.verticalLayout_compare.addWidget(self.table_compare)

        self.tabWidget.addTab(self.tab_compare, "")
        self.tab_clears = QWidget()
        self.tab_clears.setObjectName("tab_clears")
        self.verticalLayout_clears = QVBoxLayout(self.tab_clears)
        self.verticalLayout_clears.setObjectName("verticalLayout_clears")
        self.verticalLayout_clears.setContentsMargins(9, 9, 9, 9)
        self.table_clears = QTableWidget(self.tab_clears)
        self.table_clears.setObjectName("table_clears")

        self.verticalLayout_clears.addWidget(self.table_clears)

        self.tabWidget.addTab(self.tab_clears, "")
        self.tab_history = QWidget()
        self.tab_history.setObjectName("tab_history")
        self.verticalLayout_history = QVBoxLayout(self.tab_history)
        self.verticalLayout_history.setObjectName("verticalLayout_history")
        self.verticalLayout_history.setContentsMargins(9, 9, 9, 9)
        self.table_history = QTableWidget(self.tab_history)
        self.table_history.setObjectName("table_history")

        self.verticalLayout_history.addWidget(self.table_history)

        self.tabWidget.addTab(self.tab_history, "")

        self.verticalLayout_root.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1100, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuSync = QMenu(self.menuBar)
        self.menuSync.setObjectName("menuSync")
        self.menuSaves = QMenu(self.menuBar)
        self.menuSaves.setObjectName("menuSaves")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuSync.menuAction())
        self.menuBar.addAction(self.menuSaves.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuSync.addAction(self.action_sync_pc)
        self.menuSync.addAction(self.action_sync_quest)
        self.menuSync.addAction(self.action_import_backups)
        self.menuSync.addAction(self.action_refresh_catalog)
        self.menuSync.addAction(self.action_refresh_views)
        self.menuSaves.addAction(self.action_export_pc)
        self.menuSaves.addAction(self.action_export_quest)
        self.menuSaves.addAction(self.action_import_pc)
        self.menuSaves.addAction(self.action_import_quest)
        self.menuSaves.addAction(self.action_backup_db)
        self.menuHelp.addAction(self.actionAbout)

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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Beat Saber tracker", None))
        self.action_sync_pc.setText(QCoreApplication.translate("MainWindow", "Sync from PC", None))
        self.action_sync_quest.setText(QCoreApplication.translate("MainWindow", "Sync from Quest", None))
        self.action_import_backups.setText(QCoreApplication.translate("MainWindow", "Import backups\u2026", None))
        self.action_refresh_catalog.setText(QCoreApplication.translate("MainWindow", "Refresh catalog", None))
        self.action_refresh_views.setText(QCoreApplication.translate("MainWindow", "Refresh views", None))
        self.action_export_pc.setText(QCoreApplication.translate("MainWindow", "Export PC", None))
        self.action_export_quest.setText(QCoreApplication.translate("MainWindow", "Export Quest", None))
        self.action_import_pc.setText(QCoreApplication.translate("MainWindow", "Import PC", None))
        self.action_import_quest.setText(QCoreApplication.translate("MainWindow", "Import Quest", None))
        self.action_backup_db.setText(QCoreApplication.translate("MainWindow", "Backup DB", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About", None))
        self.label_summary.setText(QCoreApplication.translate("MainWindow", "Summary", None))
        self.label_source.setText(QCoreApplication.translate("MainWindow", "Source", None))
        self.combo_source.setItemText(0, QCoreApplication.translate("MainWindow", "Best (PC or Quest)", None))
        self.combo_source.setItemText(1, QCoreApplication.translate("MainWindow", "PC", None))
        self.combo_source.setItemText(2, QCoreApplication.translate("MainWindow", "Quest", None))

        self.label_difficulty.setText(QCoreApplication.translate("MainWindow", "Difficulty", None))
        self.combo_difficulty.setItemText(0, QCoreApplication.translate("MainWindow", "All", None))
        self.combo_difficulty.setItemText(1, QCoreApplication.translate("MainWindow", "Easy", None))
        self.combo_difficulty.setItemText(2, QCoreApplication.translate("MainWindow", "Normal", None))
        self.combo_difficulty.setItemText(3, QCoreApplication.translate("MainWindow", "Hard", None))
        self.combo_difficulty.setItemText(4, QCoreApplication.translate("MainWindow", "Expert", None))
        self.combo_difficulty.setItemText(5, QCoreApplication.translate("MainWindow", "Expert+", None))

        self.line_search.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search song or pack\u2026", None))
        self.check_require_fc.setText(QCoreApplication.translate("MainWindow", "Require full combo", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_missing), QCoreApplication.translate("MainWindow", "Missing", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_compare), QCoreApplication.translate("MainWindow", "Compare", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_clears), QCoreApplication.translate("MainWindow", "Clears", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_history), QCoreApplication.translate("MainWindow", "History", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuSync.setTitle(QCoreApplication.translate("MainWindow", "Sync", None))
        self.menuSaves.setTitle(QCoreApplication.translate("MainWindow", "Saves", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))
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
        MainWindow.resize(1100, 700)
        self.action_sync_pc = QAction(MainWindow)
        self.action_sync_pc.setObjectName("action_sync_pc")
        self.action_sync_quest = QAction(MainWindow)
        self.action_sync_quest.setObjectName("action_sync_quest")
        self.action_import_backups = QAction(MainWindow)
        self.action_import_backups.setObjectName("action_import_backups")
        self.action_refresh_catalog = QAction(MainWindow)
        self.action_refresh_catalog.setObjectName("action_refresh_catalog")
        self.action_refresh_views = QAction(MainWindow)
        self.action_refresh_views.setObjectName("action_refresh_views")
        self.action_export_pc = QAction(MainWindow)
        self.action_export_pc.setObjectName("action_export_pc")
        self.action_export_quest = QAction(MainWindow)
        self.action_export_quest.setObjectName("action_export_quest")
        self.action_import_pc = QAction(MainWindow)
        self.action_import_pc.setObjectName("action_import_pc")
        self.action_import_quest = QAction(MainWindow)
        self.action_import_quest.setObjectName("action_import_quest")
        self.action_backup_db = QAction(MainWindow)
        self.action_backup_db.setObjectName("action_backup_db")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_root = QVBoxLayout(self.centralWidget)
        self.verticalLayout_root.setSpacing(0)
        self.verticalLayout_root.setObjectName("verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_missing = QWidget()
        self.tab_missing.setObjectName("tab_missing")
        self.verticalLayout_missing = QVBoxLayout(self.tab_missing)
        self.verticalLayout_missing.setObjectName("verticalLayout_missing")
        self.verticalLayout_missing.setContentsMargins(9, 9, 9, 9)
        self.frame_header = QFrame(self.tab_missing)
        self.frame_header.setObjectName("frame_header")
        self.frame_header.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_header = QVBoxLayout(self.frame_header)
        self.verticalLayout_header.setObjectName("verticalLayout_header")
        self.verticalLayout_header.setContentsMargins(0, 0, 0, 0)
        self.label_summary = QLabel(self.frame_header)
        self.label_summary.setObjectName("label_summary")
        self.label_summary.setWordWrap(True)

        self.verticalLayout_header.addWidget(self.label_summary)

        self.horizontalLayout_filters = QHBoxLayout()
        self.horizontalLayout_filters.setObjectName("horizontalLayout_filters")
        self.label_source = QLabel(self.frame_header)
        self.label_source.setObjectName("label_source")

        self.horizontalLayout_filters.addWidget(self.label_source)

        self.combo_source = QComboBox(self.frame_header)
        self.combo_source.addItem("")
        self.combo_source.addItem("")
        self.combo_source.addItem("")
        self.combo_source.setObjectName("combo_source")

        self.horizontalLayout_filters.addWidget(self.combo_source)

        self.label_difficulty = QLabel(self.frame_header)
        self.label_difficulty.setObjectName("label_difficulty")

        self.horizontalLayout_filters.addWidget(self.label_difficulty)

        self.combo_difficulty = QComboBox(self.frame_header)
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.addItem("")
        self.combo_difficulty.setObjectName("combo_difficulty")

        self.horizontalLayout_filters.addWidget(self.combo_difficulty)

        self.line_search = QLineEdit(self.frame_header)
        self.line_search.setObjectName("line_search")

        self.horizontalLayout_filters.addWidget(self.line_search)

        self.check_require_fc = QCheckBox(self.frame_header)
        self.check_require_fc.setObjectName("check_require_fc")

        self.horizontalLayout_filters.addWidget(self.check_require_fc)

        self.horizontalSpacer_filters = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_filters.addItem(self.horizontalSpacer_filters)

        self.verticalLayout_header.addLayout(self.horizontalLayout_filters)

        self.verticalLayout_missing.addWidget(self.frame_header)

        self.table_missing = QTableWidget(self.tab_missing)
        self.table_missing.setObjectName("table_missing")

        self.verticalLayout_missing.addWidget(self.table_missing)

        self.tabWidget.addTab(self.tab_missing, "")
        self.tab_compare = QWidget()
        self.tab_compare.setObjectName("tab_compare")
        self.verticalLayout_compare = QVBoxLayout(self.tab_compare)
        self.verticalLayout_compare.setObjectName("verticalLayout_compare")
        self.verticalLayout_compare.setContentsMargins(9, 9, 9, 9)
        self.table_compare = QTableWidget(self.tab_compare)
        self.table_compare.setObjectName("table_compare")

        self.verticalLayout_compare.addWidget(self.table_compare)

        self.tabWidget.addTab(self.tab_compare, "")
        self.tab_clears = QWidget()
        self.tab_clears.setObjectName("tab_clears")
        self.verticalLayout_clears = QVBoxLayout(self.tab_clears)
        self.verticalLayout_clears.setObjectName("verticalLayout_clears")
        self.verticalLayout_clears.setContentsMargins(9, 9, 9, 9)
        self.table_clears = QTableWidget(self.tab_clears)
        self.table_clears.setObjectName("table_clears")

        self.verticalLayout_clears.addWidget(self.table_clears)

        self.tabWidget.addTab(self.tab_clears, "")
        self.tab_history = QWidget()
        self.tab_history.setObjectName("tab_history")
        self.verticalLayout_history = QVBoxLayout(self.tab_history)
        self.verticalLayout_history.setObjectName("verticalLayout_history")
        self.verticalLayout_history.setContentsMargins(9, 9, 9, 9)
        self.table_history = QTableWidget(self.tab_history)
        self.table_history.setObjectName("table_history")

        self.verticalLayout_history.addWidget(self.table_history)

        self.tabWidget.addTab(self.tab_history, "")

        self.verticalLayout_root.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1100, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuSync = QMenu(self.menuBar)
        self.menuSync.setObjectName("menuSync")
        self.menuSaves = QMenu(self.menuBar)
        self.menuSaves.setObjectName("menuSaves")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuSync.menuAction())
        self.menuBar.addAction(self.menuSaves.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuSync.addAction(self.action_sync_pc)
        self.menuSync.addAction(self.action_sync_quest)
        self.menuSync.addAction(self.action_import_backups)
        self.menuSync.addAction(self.action_refresh_catalog)
        self.menuSync.addAction(self.action_refresh_views)
        self.menuSaves.addAction(self.action_export_pc)
        self.menuSaves.addAction(self.action_export_quest)
        self.menuSaves.addAction(self.action_import_pc)
        self.menuSaves.addAction(self.action_import_quest)
        self.menuSaves.addAction(self.action_backup_db)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
```

</details>
