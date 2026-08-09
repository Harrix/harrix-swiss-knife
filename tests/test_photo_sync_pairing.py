"""Tests for LAN photo sync pairing URI helpers."""

from harrix_swiss_knife.photo_sync.lan import new_confirm_code, pairing_uri


def test_pairing_uri_includes_token_and_code() -> None:
    secret = "abc"  # noqa: S105
    uri = pairing_uri(
        host="192.168.1.10",
        port=17865,
        token=secret,
        confirm_code="42",
    )
    assert uri == f"hsk-photo-sync://192.168.1.10:17865?token={secret}&code=42"


def test_new_confirm_code_is_two_digits() -> None:
    for _ in range(20):
        code = new_confirm_code()
        assert len(code) == 2
        assert code.isdigit()
        assert 10 <= int(code) <= 99
