"""Tests for the Finance dashboard tab and quick-add dialogs."""

from __future__ import annotations

from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QHeaderView, QLabel, QMainWindow, QPushButton, QTableView

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import TextImageSourceDialog
from harrix_swiss_knife.apps.finance.ai_source_dialog import (
    create_finance_dashboard_photo_dialog,
    create_finance_dashboard_text_dialog,
)
from harrix_swiss_knife.apps.finance.finance_dashboard import FinanceDashboardWidget, pick_today_expense_display
from harrix_swiss_knife.apps.finance.main import apply_transactions_table_column_widths
from harrix_swiss_knife.apps.finance.window import Ui_MainWindow


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_pick_today_expense_display_prefers_default_currency() -> None:
    """Default currency amount is the large figure; other currencies stay extra."""
    amount, extra = pick_today_expense_display(
        ["USD: 12₀₀$", "RUB: 1 234₁₂₽"],
        default_code="RUB",
        zero_text="0₀₀₽",
    )
    assert amount == "1 234₁₂₽"
    assert extra == "USD: 12₀₀$"
    zero, extra_zero = pick_today_expense_display([], default_code="RUB", zero_text="0₀₀₽")
    assert zero == "0₀₀₽"
    assert extra_zero == ""


def test_finance_dashboard_widget_shows_actions_and_expense() -> None:
    """Dashboard card has three centered actions and a large spend total."""
    assert _qapp() is not None
    widget = FinanceDashboardWidget()
    photo = widget.findChild(QPushButton, "financeDashAddPhotoButton")
    voice = widget.findChild(QPushButton, "financeDashAddVoiceButton")
    text = widget.findChild(QPushButton, "financeDashAddTextButton")
    assert photo is not None
    assert voice is not None
    assert text is not None
    assert "Add photo" in photo.text()
    assert "Speak" in voice.text()
    assert "Write text" in text.text()

    clicked: list[str] = []
    widget.add_photo_requested.connect(lambda: clicked.append("photo"))
    widget.add_voice_requested.connect(lambda: clicked.append("voice"))
    widget.add_text_requested.connect(lambda: clicked.append("text"))
    photo.click()
    voice.click()
    text.click()
    assert clicked == ["photo", "voice", "text"]

    widget.set_today_expense("1 234₁₂₽", "USD: 12₀₀$")
    amount = widget.findChild(QLabel, "financeDashExpenseValue")
    extra = widget.findChild(QLabel, "financeDashExpenseExtra")
    assert amount is not None
    assert extra is not None
    assert amount.text() == "1 234₁₂₽"
    assert extra.text() == "USD: 12₀₀$"
    assert not extra.isHidden()


def test_apply_transactions_table_column_widths_skips_hidden_view() -> None:
    """Hidden tables keep default resize modes until the view is shown."""
    assert _qapp() is not None
    view = QTableView()
    model = QStandardItemModel(1, 8)
    for column in range(8):
        model.setItem(0, column, QStandardItem("x"))
    view.setModel(model)
    apply_transactions_table_column_widths(view)
    header = view.horizontalHeader()
    assert header.sectionResizeMode(0) != QHeaderView.ResizeMode.Stretch
    view.show()
    apply_transactions_table_column_widths(view)
    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(5) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(6) == QHeaderView.ResizeMode.Fixed
    assert header.sectionResizeMode(7) == QHeaderView.ResizeMode.Fixed
    assert view.columnWidth(6) == 100
    assert view.columnWidth(7) == 120
    view.close()


def test_finance_window_inserts_dashboard_as_first_tab() -> None:
    """Dashboard is tab 0; later tabs keep their object names."""
    assert _qapp() is not None

    class FinanceUiWindow(QMainWindow, Ui_MainWindow):
        pass

    window = FinanceUiWindow()
    window.setupUi(window)
    tabs = window.tabWidget
    assert tabs.widget(0) is window.tab_finance_dashboard
    assert tabs.widget(1) is window.tab_transactions
    assert window.tab_finance_dashboard.objectName() == "tab_finance_dashboard"
    assert window.tab_transactions.objectName() == "tab_transactions"
    assert not hasattr(window, "tab_categories")
    assert window.action_categories.text() == "Categories"
    assert window.action_currencies.text() == "Currencies"
    assert window.tab_exchange_rates.objectName() == "tab_exchange_rates"
    assert window.tab_charts.objectName() == "tab_charts"
    assert window.tab_reports.objectName() == "tab_reports"
    assert tabs.tabText(0) == "Quick"
    assert tabs.tabText(1) == "Transactions"
    assert tabs.currentWidget() is window.tab_finance_dashboard
    window.close()


def test_finance_dashboard_photo_dialog_is_large_photo_only() -> None:
    """Photo dashboard form hides text and uses the large-type layout."""
    assert _qapp() is not None
    dialog = create_finance_dashboard_photo_dialog()
    assert isinstance(dialog, TextImageSourceDialog)
    assert dialog.text_edit is None
    assert dialog.image_widget is not None
    assert dialog.minimumWidth() >= 800
    assert dialog.minimumHeight() >= 680
    dialog.close()


def test_finance_dashboard_text_dialog_is_large_text_only() -> None:
    """Text dashboard form hides images and uses a large editor."""
    assert _qapp() is not None
    dialog = create_finance_dashboard_text_dialog()
    assert dialog.image_widget is None
    assert dialog.text_edit is not None
    assert dialog.text_edit.minimumHeight() >= 260
    assert dialog.minimumWidth() >= 800
    dialog.close()
