"""Tests for BotHub toast pin-chain helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from harrix_swiss_knife.integrations.bothub.qt_runner import (
    BothubRequestState,
    chain_toast_start_kwargs,
    remember_toast_pin,
)


def test_chain_toast_start_kwargs_only_when_chain_was_pinned() -> None:
    assert chain_toast_start_kwargs(None) == {}
    assert chain_toast_start_kwargs(BothubRequestState()) == {}
    assert chain_toast_start_kwargs(BothubRequestState(toast_pin_chain=True)) == {}
    assert chain_toast_start_kwargs(BothubRequestState(toast_pin_chain=True, toast_pinned=False)) == {}
    assert chain_toast_start_kwargs(BothubRequestState(toast_pin_chain=False, toast_pinned=True)) == {}
    assert chain_toast_start_kwargs(BothubRequestState(toast_pin_chain=True, toast_pinned=True)) == {
        "pinned": True,
        "activate": False,
    }


def test_remember_toast_pin_only_for_chain() -> None:
    toast = MagicMock()
    toast.is_pinned = True

    plain = BothubRequestState()
    remember_toast_pin(plain, toast)
    assert plain.toast_pinned is None

    chain = BothubRequestState(toast_pin_chain=True)
    remember_toast_pin(chain, toast)
    assert chain.toast_pinned is True

    toast.is_pinned = False
    remember_toast_pin(chain, toast)
    assert chain.toast_pinned is False

    remember_toast_pin(None, toast)
    remember_toast_pin(chain, None)
    assert chain.toast_pinned is False
