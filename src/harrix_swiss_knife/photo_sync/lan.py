"""LAN interface helpers for photo sync pairing."""

from __future__ import annotations

import socket


def list_lan_ipv4() -> list[str]:
    """Return non-loopback IPv4 addresses for this machine (best-effort)."""
    addresses: list[str] = []
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

    # Fallback: UDP connect trick (does not send packets) to learn the preferred outbound IP.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if isinstance(ip, str) and ip and not ip.startswith("127.") and ip not in addresses:
                addresses.insert(0, ip)
    except OSError:
        pass

    return addresses


def pairing_uri(*, host: str, port: int, token: str) -> str:
    """Build the QR / paste pairing URI."""
    return f"hsk-photo-sync://{host}:{port}?token={token}"
