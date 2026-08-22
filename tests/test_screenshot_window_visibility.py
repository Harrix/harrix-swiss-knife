"""Tests for screenshot window conceal/restore without closing modal dialogs."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QWidget

from harrix_swiss_knife.screenshot.window_visibility import (
    ConcealedWindow,
    _pick_focus_target,
    hide_app_windows,
    restore_app_windows,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_hide_app_windows_keeps_modal_dialog_exec_alive(qapp: QApplication) -> None:  # noqa: ARG001
    """Modal dialogs must stay accepted/open after conceal — hide() would reject exec()."""
    dialog = QDialog()
    dialog.setModal(True)
    dialog.setWindowOpacity(1.0)
    dialog.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    assert any(item.widget is dialog and item.mode == "opacity" for item in concealed)
    assert dialog.isVisible()
    assert dialog.windowOpacity() == 0.0
    assert dialog.result() == 0  # not finished/rejected
    # Invisible modal must not keep ApplicationModal (blocks shutter / beeps).
    assert dialog.windowModality() == Qt.WindowModality.NonModal
    assert not dialog.isModal()
    assert dialog.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    restore_app_windows(concealed)
    assert dialog.windowOpacity() == 1.0
    assert dialog.isVisible()
    assert dialog.result() == 0
    assert dialog.windowModality() == Qt.WindowModality.ApplicationModal
    assert dialog.isModal()
    assert not dialog.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    dialog.close()


def test_hide_app_windows_fades_window_modal_owner_not_hide(qapp: QApplication) -> None:  # noqa: ARG001
    """Owner of a WindowModal dialog must not use hide()/show() (breaks Z-order)."""
    owner = QWidget()
    owner.setWindowTitle("owner-window")
    owner.show()
    dialog = QDialog(owner)
    dialog.setWindowModality(Qt.WindowModality.WindowModal)
    dialog.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    owner_item = next(item for item in concealed if item.widget is owner)
    dialog_item = next(item for item in concealed if item.widget is dialog)
    assert owner_item.mode == "opacity"
    assert dialog_item.mode == "opacity"
    assert owner.isVisible()
    assert dialog.isVisible()
    assert owner.windowOpacity() == 0.0
    assert dialog.windowOpacity() == 0.0

    restore_app_windows(concealed)
    assert owner.windowOpacity() == 1.0
    assert dialog.windowOpacity() == 1.0
    assert dialog.windowModality() == Qt.WindowModality.WindowModal
    assert dialog.isModal()
    assert dialog.isActiveWindow() or dialog.isVisible()

    dialog.close()
    owner.close()


def test_hide_app_windows_hides_non_modal_top_level(qapp: QApplication) -> None:  # noqa: ARG001
    window = QWidget()
    window.setWindowTitle("non-modal-test")
    window.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    match = next(item for item in concealed if item.widget is window)
    assert match.mode == "hide"
    assert not window.isVisible()

    restore_app_windows(concealed)
    assert window.isVisible()
    window.close()


def test_hide_app_windows_fades_sibling_when_modal_exists(qapp: QApplication) -> None:  # noqa: ARG001
    """A later hide()/show() of Fitness must not land above a WindowModal error box."""
    sibling = QWidget()
    sibling.setWindowTitle("sibling-fitness")
    sibling.show()
    owner = QWidget()
    owner.setWindowTitle("owner-window")
    owner.show()
    dialog = QDialog(owner)
    dialog.setWindowModality(Qt.WindowModality.WindowModal)
    dialog.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    sibling_item = next(item for item in concealed if item.widget is sibling)
    assert sibling_item.mode == "opacity"
    assert sibling.isVisible()
    assert sibling.windowOpacity() == 0.0

    restore_app_windows(concealed)
    assert sibling.windowOpacity() == 1.0
    assert dialog.windowModality() == Qt.WindowModality.WindowModal

    dialog.close()
    owner.close()
    sibling.close()


def test_pick_focus_target_prefers_active_window_over_last_visible(qapp: QApplication) -> None:  # noqa: ARG001
    """Return to Finance, not the last top-level widget (command cards)."""
    cards = QWidget()
    cards.show()
    finance = QWidget()
    finance.show()
    QApplication.processEvents()

    widgets = [
        ConcealedWindow(cards, "hide"),
        ConcealedWindow(finance, "hide", was_active=True),
    ]
    assert _pick_focus_target(widgets) is finance

    cards.close()
    finance.close()


def test_hide_app_windows_records_stay_on_top(qapp: QApplication) -> None:  # noqa: ARG001
    """Stay-on-top command cards are remembered so restore can drop the hint."""
    cards = QWidget()
    cards.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    cards.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    match = next(item for item in concealed if item.widget is cards)
    assert match.stay_on_top

    restore_app_windows(concealed)
    cards.close()


def test_pick_focus_target_uses_saved_modality(qapp: QApplication) -> None:  # noqa: ARG001
    """After fade-out the dialog is NonModal; restore must still prefer it."""
    owner = QWidget()
    owner.show()
    dialog = QDialog(owner)
    dialog.setWindowModality(Qt.WindowModality.NonModal)
    dialog.show()
    QApplication.processEvents()

    widgets = [
        ConcealedWindow(owner, "opacity"),
        ConcealedWindow(dialog, "opacity", modality=Qt.WindowModality.WindowModal),
    ]
    assert _pick_focus_target(widgets) is dialog

    dialog.close()
    owner.close()


def test_restore_app_windows_prefers_modal_dialog_for_focus(qapp: QApplication) -> None:  # noqa: ARG001
    plain = QWidget()
    plain.show()
    modal = QDialog()
    modal.setModal(True)
    modal.show()
    QApplication.processEvents()

    widgets = [
        ConcealedWindow(plain, "hide"),
        ConcealedWindow(modal, "opacity", modality=Qt.WindowModality.ApplicationModal),
    ]
    assert _pick_focus_target(widgets) is modal

    plain.close()
    modal.close()


def test_restore_keeps_message_box_reachable(qapp: QApplication) -> None:  # noqa: ARG001
    """WindowModal QMessageBox must stay visible and modal after conceal/restore."""
    owner = QWidget()
    owner.setWindowTitle("fitness-owner")
    owner.show()
    box = QMessageBox(owner)
    box.setWindowTitle("Error")
    box.setText("Database error")
    box.setWindowModality(Qt.WindowModality.WindowModal)
    box.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    restore_app_windows(concealed)
    QApplication.processEvents()

    assert box.isVisible()
    assert box.windowOpacity() == 1.0
    assert box.windowModality() == Qt.WindowModality.WindowModal
    assert box.isModal()
    assert not box.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    box.close()
    owner.close()


def test_restore_clears_stay_on_top_on_sibling_of_focus(qapp: QApplication) -> None:  # noqa: ARG001
    """Command cards stay-on-top must not cover Finance after a screenshot."""
    cards = QWidget()
    cards.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    cards.show()
    finance = QWidget()
    finance.show()
    QApplication.processEvents()

    widgets = [
        ConcealedWindow(cards, "hide", stay_on_top=True),
        ConcealedWindow(finance, "hide", was_active=True),
    ]
    restore_app_windows(widgets)
    QApplication.processEvents()

    assert not (cards.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
    assert cards.isVisible()
    assert finance.isVisible()

    cards.close()
    finance.close()


def test_restore_keeps_stay_on_top_on_focus_window(qapp: QApplication) -> None:  # noqa: ARG001
    """A stay-on-top window that started capture keeps the hint."""
    cards = QWidget()
    cards.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    cards.show()
    QApplication.processEvents()

    widgets = [ConcealedWindow(cards, "hide", was_active=True, stay_on_top=True)]
    restore_app_windows(widgets)
    QApplication.processEvents()

    assert cards.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    assert cards.isVisible()

    cards.close()


def test_restore_without_activate_shows_windows_and_drops_stay_on_top(qapp: QApplication) -> None:  # noqa: ARG001
    """Preview takes the foreground, so restored Windows must not steal focus."""
    cards = QWidget()
    cards.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    cards.show()
    finance = QWidget()
    finance.show()
    QApplication.processEvents()

    widgets = [
        ConcealedWindow(cards, "hide", stay_on_top=True),
        ConcealedWindow(finance, "hide", was_active=True),
    ]
    restore_app_windows(widgets, activate=False)
    QApplication.processEvents()

    assert cards.isVisible()
    assert finance.isVisible()
    assert not (cards.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)

    cards.close()
    finance.close()
