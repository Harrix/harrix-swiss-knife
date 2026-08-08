---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lan.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `list_lan_ipv4`](#-function-list_lan_ipv4)
- [🔧 Function `pairing_uri`](#-function-pairing_uri)

</details>

## 🔧 Function `list_lan_ipv4`

```python
def list_lan_ipv4() -> list[str]
```

Return non-loopback IPv4 addresses for this machine (best-effort).

<details>
<summary>Code:</summary>

```python
def list_lan_ipv4() -> list[str]:
    addresses: list[str] = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM):
            ip = info[4][0]
            if ip and not ip.startswith("127.") and ip not in addresses:
                addresses.append(ip)
    except OSError:
        pass

    # Fallback: UDP connect trick (does not send packets) to learn the preferred outbound IP.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127.") and ip not in addresses:
                addresses.insert(0, ip)
    except OSError:
        pass

    return addresses
```

</details>

## 🔧 Function `pairing_uri`

```python
def pairing_uri(*, host: str, port: int, token: str) -> str
```

Build the QR / paste pairing URI.

<details>
<summary>Code:</summary>

```python
def pairing_uri(*, host: str, port: int, token: str) -> str:
    return f"hsk-photo-sync://{host}:{port}?token={token}"
```

</details>
