"""Tests for LAN IP ranking used in photo sync pairing."""

from harrix_swiss_knife.photo_sync.lan import is_likely_virtual_lan_ip, sort_lan_ipv4


def test_sort_prefers_wifi_over_virtualbox() -> None:
    ordered = sort_lan_ipv4(
        ["192.168.56.1", "192.168.1.42"],
        preferred="192.168.1.42",
    )
    assert ordered[0] == "192.168.1.42"
    assert ordered[-1] == "192.168.56.1"


def test_sort_demotes_virtual_even_without_preferred() -> None:
    ordered = sort_lan_ipv4(["192.168.56.1", "10.0.0.5"])
    assert ordered[0] == "10.0.0.5"


def test_virtualbox_host_only_detected() -> None:
    assert is_likely_virtual_lan_ip("192.168.56.1")
    assert not is_likely_virtual_lan_ip("192.168.1.10")
