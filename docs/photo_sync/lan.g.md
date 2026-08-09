---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lan.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_likely_virtual_lan_ip`](#-function-is_likely_virtual_lan_ip)
- [🔧 Function `list_lan_ipv4`](#-function-list_lan_ipv4)
- [🔧 Function `new_confirm_code`](#-function-new_confirm_code)
- [🔧 Function `pairing_uri`](#-function-pairing_uri)
- [🔧 Function `sort_lan_ipv4`](#-function-sort_lan_ipv4)

</details>

## 🔧 Function `is_likely_virtual_lan_ip`

```python
def is_likely_virtual_lan_ip(ip: str) -> bool
```

Return `True` for common VM/host-only addresses unsuitable for phone pairing.

<details>
<summary>Code:</summary>

```python
def is_likely_virtual_lan_ip(ip: str) -> bool:
    return any(ip.startswith(prefix) for prefix in _LOW_PRIORITY_PREFIXES)
```

</details>

## 🔧 Function `list_lan_ipv4`

```python
def list_lan_ipv4() -> list[str]
```

Return non-loopback IPv4 addresses, Wi-Fi/LAN preferred over VM adapters.

<details>
<summary>Code:</summary>

```python
def list_lan_ipv4() -> list[str]:
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
```

</details>

## 🔧 Function `new_confirm_code`

```python
def new_confirm_code() -> str
```

Return a two-digit confirmation code shown next to the QR (10-99).

<details>
<summary>Code:</summary>

```python
def new_confirm_code() -> str:
    return f"{secrets.randbelow(90) + 10}"
```

</details>

## 🔧 Function `pairing_uri`

```python
def pairing_uri(*, host: str, port: int, token: str, confirm_code: str) -> str
```

Build the QR pairing URI (host, port, token, and confirm code).

<details>
<summary>Code:</summary>

```python
def pairing_uri(*, host: str, port: int, token: str, confirm_code: str) -> str:
    return f"hsk-photo-sync://{host}:{port}?token={token}&code={confirm_code}"
```

</details>

## 🔧 Function `sort_lan_ipv4`

```python
def sort_lan_ipv4(addresses: list[str], *, preferred: str | None = None) -> list[str]
```

Sort IPs so phones can reach the PC: prefer real LAN, demote VM/host-only.

<details>
<summary>Code:</summary>

```python
def sort_lan_ipv4(addresses: list[str], *, preferred: str | None = None) -> list[str]:

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
```

</details>
