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
- [🔧 Function `new_confirm_code`](#-function-new_confirm_code)
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
