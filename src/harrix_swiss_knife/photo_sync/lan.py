"""LAN interface helpers for photo sync pairing."""

from __future__ import annotations

import secrets
import socket

# Host-only / VM / container ranges that phones on home Wi-Fi usually cannot reach.
_LOW_PRIORITY_PREFIXES: tuple[str, ...] = (
    "192.168.56.",  # VirtualBox Host-Only
    "192.168.57.",  # VirtualBox Host-Only (alt)
    "192.168.59.",  # VirtualBox
    "192.168.137.",  # Windows Internet Connection Sharing / hotspot bridge
    "169.254.",  # APIPA / link-local
    "172.17.",  # Docker default bridge
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
)


def is_likely_virtual_lan_ip(ip: str) -> bool:
    """Return `True` for common VM/host-only addresses unsuitable for phone pairing."""
    return any(ip.startswith(prefix) for prefix in _LOW_PRIORITY_PREFIXES)


def list_lan_ipv4() -> list[str]:
    """Return non-loopback IPv4 addresses, Wi-Fi/LAN preferred over VM adapters."""
    addresses: list[str] = []
    preferred: str | None = None

    # Preferred outbound interface (usually the real Wi-Fi / Ethernet used for LAN).
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if isinstance(ip, str) and ip and not ip.startswith("127."):
                preferred = ip
                addresses.append(ip)
    except OSError:
        pass

    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM):
            sockaddr = info[4]
            ip = sockaddr[0]
            if not isinstance(ip, str):
                continue
            if ip and not ip.startswith("127.") and ip not in addresses:
                addresses.append(ip)
    except OSError:
        pass

    return sort_lan_ipv4(addresses, preferred=preferred)


def new_confirm_code() -> str:
    """Return a two-digit confirmation code shown next to the QR (10-99)."""
    return f"{secrets.randbelow(90) + 10}"


def pairing_uri(*, host: str, port: int, token: str, confirm_code: str) -> str:
    """Build the QR pairing URI (host, port, token, and confirm code)."""
    return f"hsk-photo-sync://{host}:{port}?token={token}&code={confirm_code}"


def sort_lan_ipv4(addresses: list[str], *, preferred: str | None = None) -> list[str]:
    """Sort IPs so phones can reach the PC: prefer real LAN, demote VM/host-only."""

    def rank(ip: str) -> tuple[int, int, str]:
        if preferred is not None and ip == preferred and not is_likely_virtual_lan_ip(ip):
            return (0, 0, ip)
        if is_likely_virtual_lan_ip(ip):
            return (2, 0, ip)
        if preferred is not None and ip == preferred:
            return (1, 0, ip)
        return (1, 1, ip)

    # Stable unique order by rank.
    return sorted(dict.fromkeys(addresses), key=rank)
