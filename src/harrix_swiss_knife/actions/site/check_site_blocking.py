"""Check where a website is blocked from this computer."""

from __future__ import annotations

import http.client
import ipaddress
import json
import os
import re
import shutil
import socket
import ssl
import struct
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, ClassVar

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.subprocess_run import hidden_subprocess_kwargs
from harrix_swiss_knife.integrations.bothub import (
    build_prompt,
    run_bothub_request,
    run_bothub_request_blocking,
)

_PROMPT_KEY = "site_blocking_check"
_DEFAULT_URL = "https://harrix.dev/"
_CONTROL_HOST = "example.com"
_HTTPS_PORT = 443
_HTTP_PORT = 80
_DNS_PORT = 53
_DNS_TIMEOUT = 2.0
_DOH_TIMEOUT = 4.0
_TCP_TIMEOUT = 3.5
_HTTP_TIMEOUT = 4.0
_HTTP_READ_LIMIT = 8192
_HTTP_CHUNK = 2048
_STATUS_OK = 200
_STATUS_REDIRECT = 400
_CF_ORIGIN_MIN = 520
_CF_ORIGIN_MAX = 526
_CF_FETCH_TIMEOUT = 4.0
_CF_READ_LIMIT = 65536
_TRACE_HOPS = 8
_TRACE_WAIT_MS = 400
_TRACE_TIMEOUT = 20.0
_MAX_PROBE_IPS = 4
_HEADER_LEN = 12
_QTYPE_A = 1
_QTYPE_NS = 2
_QTYPE_AAAA = 28
_RCODE_MASK = 0xF
_POINTER_MASK = 0xC0
_LABEL_LENGTH_MASK = 0x3F
_MAX_NAME_DEPTH = 10
_MAX_HOST_LENGTH = 253
_MIN_HOSTS_FIELDS = 2
_IPV4_LEN = 4
_IPV6_LEN = 16
_IPV4_DOTS = 3
_IPV6_MIN_COLONS = 2
_HOP_PAST_ROUTER = 2
_SYSTEM_RESOLVER = "System"
_DOH_RESOLVER = "dns.google DoH"
_PUBLIC_RESOLVERS = ("8.8.8.8", "1.1.1.1", "9.9.9.9")
_DECOY_SNI = "example.com"
_TLS_BREAKS = frozenset({"timeout", "reset", "protocol"})
_RESET_WINERRORS = frozenset({10054})
_REFUSED_WINERRORS = frozenset({10061})
_UNREACHABLE_WINERRORS = frozenset({10049, 10050, 10051, 10065})
_TIMEOUT_WINERRORS = frozenset({10060})
_RESET_ERRNOS = frozenset({54, 104})
_REFUSED_ERRNOS = frozenset({61, 111})
_UNREACHABLE_ERRNOS = frozenset({51, 65, 101, 113})
_TIMEOUT_ERRNOS = frozenset({60, 110})
_NOT_FOUND_WINERRORS = frozenset({11001})
_RCODES = ("NOERROR", "FORMERR", "SERVFAIL", "NXDOMAIN", "NOTIMP", "REFUSED")
_CF_POLICY = frozenset({"1003", "1006", "1007", "1008", "1010", "1015", "1020"})
_CF_ORIGIN = frozenset({"520", "521", "522", "523", "524", "525", "526"})
_BLOCK_PAGE_MARKERS = (
    "\u0440\u043e\u0441\u043a\u043e\u043c\u043d\u0430\u0434\u0437\u043e\u0440",
    "\u0434\u043e\u0441\u0442\u0443\u043f \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d",
    "\u0441\u0430\u0439\u0442 \u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d",
)
_STATUS_RE = re.compile(r"^HTTP/\d+(?:\.\d+)?\s+(\d{3})")
_CF_CODE_RE = re.compile(r"error\s*(?:code)?[:\s]+(\d{3,4})", re.IGNORECASE)
_HOP_RE = re.compile(r"^\s*(\d+)\s+(.*)$")
_FALLBACK_CF_CIDRS = (
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22",
    "2400:cb00::/32",
    "2606:4700::/32",
    "2803:f800::/32",
    "2405:b500::/32",
    "2405:8100::/32",
    "2a06:98c0::/29",
    "2c0f:f248::/32",
)


class OnCheckSiteBlocking(ActionBase):
    """Find the network layer where a site stops opening from this computer.

    The user enters any URL. The check compares system DNS with public resolvers,
    then TCP, TLS (including a different SNI), HTTP, and, when TCP fails, traceroute.
    Cloudflare addresses and error codes are separated from an origin-server failure.
    A short AI explanation is requested from the same prompt path as other actions.

    """

    icon = "🔍"
    title = "Check why a site is blocked…"
    description = "DNS, router, Cloudflare, or server: where a URL stops opening"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site check-blocking"
    quick_launcher = True
    _cf_networks: ClassVar[tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] | None] = None

    @ActionBase.handle_exceptions("checking why a site is blocked")
    def execute(
        self,
        *_args: Any,
        url: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Ask for a URL, measure where it fails, and explain the result."""
        self._noninteractive = noninteractive
        raw = url
        if raw is None:
            raw = self.get_text_input(
                "Check why a site is blocked",
                "Site URL. The check runs on this computer and only describes this network.",
                _DEFAULT_URL,
            )
        if raw is None:
            return
        try:
            target = self._parse_target(raw)
        except ValueError as exc:
            self.add_line(f"❌ {exc}")
            if not noninteractive:
                self.show_result()
            return
        self._target = target
        if noninteractive:
            self._publish(self._collect(target))
            return
        self.start_thread(self._collect_saved, self._publish, "Checking site…")

    def _add_block(self, text: str) -> None:
        """Append a multi-line block as separate output lines."""
        for line in text.splitlines():
            self.add_line(line)

    @classmethod
    def _classify(cls, facts: BlockingFacts) -> tuple[str, str, str]:
        """Return a verdict ID, an English level name, and an English summary."""
        if facts.hosts_override:
            summary = (
                f"The hosts file maps {facts.host} to {facts.hosts_override}. "
                "The request is intercepted on this computer and does not reach the router."
            )
            return "hosts", "This computer", summary
        if facts.dns_mismatch:
            return cls._dns_mismatch_verdict(facts)
        if not facts.connects:
            return cls._no_address_verdict(facts)
        if not any(probe.tcp_ok for probe in facts.connects):
            return cls._tcp_failed_verdict(facts)
        return cls._tcp_ok_verdict(facts)

    @staticmethod
    def _cloudflare_label(facts: BlockingFacts) -> str:
        """Say whether the name or its addresses belong to Cloudflare."""
        if facts.cloudflare_ns or any(probe.on_cloudflare for probe in facts.connects):
            return "yes"
        if not facts.nameservers and not facts.connects:
            return "unknown"
        return "no"

    @classmethod
    def _cloudflare_networks(cls) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]:
        """Load Cloudflare ranges, refreshing from the public list when it answers."""
        cached = cls._cf_networks
        if cached is not None:
            return cached
        fetched = cls._fetch_cloudflare_cidrs()
        cidrs = fetched or _FALLBACK_CF_CIDRS
        networks = tuple(ipaddress.ip_network(item) for item in cidrs)
        cls._cf_networks = networks
        return networks

    @classmethod
    def _collect(cls, target: Target) -> BlockingFacts:
        """Run DNS, connection, traceroute, and control probes."""
        networks = cls._cloudflare_networks()
        lookups = cls._lookups(target.host)
        nameservers = tuple(dict.fromkeys(name for lookup in lookups for name in lookup.nameservers))
        cloudflare_ns = any(
            name.lower() == "cloudflare.com" or name.lower().endswith(".cloudflare.com") for name in nameservers
        )
        system_ips = next((lookup.ips for lookup in lookups if lookup.resolver == _SYSTEM_RESOLVER), ())
        public_ips = tuple(ip for lookup in lookups if lookup.resolver != _SYSTEM_RESOLVER for ip in lookup.ips)
        mismatch = cls._dns_mismatch(system_ips, public_ips, networks)
        ips = cls._probe_addresses(system_ips, public_ips)
        connects = cls._connect_all(ips, target, networks)
        trace_ran = False
        hops: tuple[OnCheckSiteBlocking.TraceHop, ...] = ()
        if connects and not any(probe.tcp_ok for probe in connects):
            trace_ip = next((ip for ip in ips if cls._is_global(ip)), "")
            if trace_ip:
                trace_ran = True
                hops = cls._traceroute(trace_ip)
        control_dns: bool | None = None
        control_tcp: bool | None = None
        if not any(probe.tcp_ok for probe in connects):
            control_dns, control_tcp = cls._control()
        return cls.BlockingFacts(
            url=target.url,
            host=target.host,
            port=target.port,
            hosts_override=cls._hosts_override(cls._hosts_text(), target.host),
            lookups=lookups,
            nameservers=nameservers,
            cloudflare_ns=cloudflare_ns,
            dns_mismatch=mismatch,
            connects=connects,
            hops=hops,
            trace_ran=trace_ran,
            control_dns_ok=control_dns,
            control_tcp_ok=control_tcp,
        )

    def _collect_saved(self) -> BlockingFacts:
        """Measure the URL chosen in `execute`."""
        return self._collect(self._target)

    @classmethod
    def _connect_all(
        cls,
        ips: tuple[str, ...],
        target: Target,
        networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
    ) -> tuple[ConnectProbe, ...]:
        """Open TCP, TLS, and HTTP to each selected address."""
        if not ips:
            return ()
        worker = partial(
            cls._connect_one,
            host=target.host,
            port=target.port,
            scheme=target.scheme,
            networks=networks,
        )
        with ThreadPoolExecutor(max_workers=min(_MAX_PROBE_IPS, len(ips))) as pool:
            return tuple(pool.map(worker, ips))

    @classmethod
    def _connect_one(
        cls,
        ip: str,
        *,
        host: str,
        port: int,
        scheme: str,
        networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
    ) -> ConnectProbe:
        """Probe one address: TCP, then TLS and HTTP when the port is HTTPS."""
        on_cloudflare = cls._ip_on_cloudflare(ip, networks)
        use_tls = scheme == "https" and port == _HTTPS_PORT
        try:
            sock = socket.create_connection((ip, port), _TCP_TIMEOUT)
        except (TimeoutError, OSError) as exc:
            return cls.ConnectProbe(
                ip=ip,
                on_cloudflare=on_cloudflare,
                tcp_error=cls._tcp_error(exc),
                checked_tls=use_tls,
            )
        try:
            if not use_tls:
                status, server, cf_ray, cf_error = cls._read_http(sock, host)
                return cls.ConnectProbe(
                    ip=ip,
                    on_cloudflare=on_cloudflare,
                    tcp_ok=True,
                    checked_tls=False,
                    http_status=status,
                    cf_ray=cf_ray,
                    cf_error=cf_error,
                    server=server,
                )
            tls_ok, tls_error, status, server, cf_ray, cf_error = cls._tls_and_http(ip, port, host, sock)
        finally:
            sock.close()
        decoy: bool | None = None
        if use_tls and not tls_ok and tls_error in _TLS_BREAKS:
            decoy = cls._decoy_tls(ip, port)
        return cls.ConnectProbe(
            ip=ip,
            on_cloudflare=on_cloudflare,
            tcp_ok=True,
            checked_tls=True,
            tls_ok=tls_ok,
            tls_error=tls_error,
            decoy_tls_ok=decoy,
            http_status=status,
            cf_ray=cf_ray,
            cf_error=cf_error,
            server=server,
        )

    @classmethod
    def _control(cls) -> tuple[bool, bool]:
        """Check whether example.com resolves and accepts TCP/443."""
        ips: tuple[str, ...] = ()
        try:
            infos = socket.getaddrinfo(_CONTROL_HOST, _HTTPS_PORT, type=socket.SOCK_STREAM)
            hosts: list[str] = []
            for item in infos:
                host_addr = item[4][0]
                if isinstance(host_addr, str):
                    hosts.append(host_addr)
            ips = tuple(dict.fromkeys(hosts))
        except OSError:
            ips = ()
        if not any(cls._is_global(ip) for ip in ips):
            try:
                packet = cls._exchange_udp(_CONTROL_HOST, "8.8.8.8", _QTYPE_A)
                _rcode, resolved, _ns = cls._parse_dns_message(packet)
                ips = resolved
            except (OSError, TimeoutError):
                ips = ()
        dns_ok = any(cls._is_global(ip) for ip in ips)
        tcp_ok = False
        for ip in ips:
            if not cls._is_global(ip):
                continue
            try:
                with socket.create_connection((ip, _HTTPS_PORT), _TCP_TIMEOUT):
                    tcp_ok = True
            except (TimeoutError, OSError):
                continue
            break
        return dns_ok, tcp_ok

    @classmethod
    def _decoy_tls(cls, ip: str, port: int) -> bool:
        """Return whether TLS to `ip` completes with a different server name."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        bare: socket.socket | None = None
        try:
            bare = socket.create_connection((ip, port), _TCP_TIMEOUT)
            with context.wrap_socket(bare, server_hostname=_DECOY_SNI):
                return True
        except (TimeoutError, ssl.SSLError, OSError):
            return False
        finally:
            if bare is not None:
                bare.close()

    @classmethod
    def _dns_mismatch(
        cls,
        system_ips: tuple[str, ...],
        public_ips: tuple[str, ...],
        networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
    ) -> bool:
        """Return whether system DNS disagrees with public resolvers.

        Different Cloudflare edge addresses are treated as the same answer.

        """
        system_global = {ip for ip in system_ips if cls._is_global(ip)}
        public_global = {ip for ip in public_ips if cls._is_global(ip)}
        if not system_global and system_ips and not public_global:
            return True
        if public_global and not system_global:
            return True
        if system_global and public_global and system_global.isdisjoint(public_global):
            combined = system_global | public_global
            return not all(cls._ip_on_cloudflare(ip, networks) for ip in combined)
        return False

    @classmethod
    def _dns_mismatch_verdict(cls, facts: BlockingFacts) -> tuple[str, str, str]:
        """Explain a system resolver that disagrees with public DNS."""
        opened = any(
            probe.tcp_ok and probe.http_status is not None and _STATUS_OK <= probe.http_status < _STATUS_REDIRECT
            for probe in facts.connects
        )
        if opened:
            summary = (
                "System DNS returned a different address from the public resolvers. "
                "The site answers on the public address, so the server and Cloudflare are reachable "
                "from this network. Name resolution on this computer or the router is what fails."
            )
        else:
            summary = (
                "System DNS does not match the public resolvers. "
                "A browser that uses system DNS never asks the real address of the site."
            )
        return "dns", "DNS", summary

    @staticmethod
    def _dns_query(host: str, qtype: int) -> tuple[bytes, int]:
        """Build a recursive DNS query and return the packet plus its ID."""
        tid = int.from_bytes(os.urandom(2), "big")
        header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 0)
        qname = b""
        for label in host.rstrip(".").split("."):
            raw = label.encode("ascii")
            qname += bytes((len(raw),)) + raw
        qname += b"\x00"
        return header + qname + struct.pack("!HH", qtype, 1), tid

    @staticmethod
    def _exchange_udp(host: str, resolver: str, qtype: int) -> bytes:
        """Send one DNS query and return the raw response."""
        query, tid = OnCheckSiteBlocking._dns_query(host, qtype)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(_DNS_TIMEOUT)
            sock.sendto(query, (resolver, _DNS_PORT))
            data, _source = sock.recvfrom(_HTTP_CHUNK)
        if len(data) < _HEADER_LEN or struct.unpack_from("!H", data, 0)[0] != tid:
            msg = "DNS response did not match the query"
            raise OSError(msg)
        return data

    def _explain(self, report: str) -> None:
        """Send the report to the configured AI prompt, then show it."""
        try:
            prompt = build_prompt(
                self.config,
                _PROMPT_KEY,
                {"REPORT": report},
                prompt_display_name=_PROMPT_KEY,
            )
        except ValueError as exc:
            self.add_line("")
            self.add_line(f"AI: {exc}")
            if not self._noninteractive:
                self.show_result()
            return
        if self._noninteractive:
            answer = run_bothub_request_blocking(
                None,
                self.config,
                prompt,
                toast_message="Explaining the block…",
                offer_retry=False,
            )
            if answer:
                self.add_line("")
                self._add_block(answer)
            return

        def on_success(answer: str) -> None:
            if answer.strip():
                self.add_line("")
                self._add_block(answer)
            self.show_result()

        def on_error(message: str) -> None:
            self.add_line("")
            self.add_line(f"AI: {message}")
            self.show_result()

        run_bothub_request(
            None,
            self.config,
            prompt,
            on_success,
            on_error=on_error,
            toast_message="Explaining the block…",
        )

    @staticmethod
    def _extract_cf_error(body: str) -> str | None:
        """Pull a Cloudflare error code or a block-page hint out of an HTTP body."""
        match = _CF_CODE_RE.search(body)
        if match is not None:
            return match.group(1)
        lowered = body.lower()
        if "just a moment" in lowered or "attention required" in lowered or "cf-browser-verification" in lowered:
            return "challenge"
        if "sorry, you have been blocked" in lowered or "access denied" in lowered:
            return "blocked"
        if any(marker in lowered for marker in _BLOCK_PAGE_MARKERS):
            return "blockpage"
        return None

    @staticmethod
    def _fetch_cloudflare_cidrs() -> tuple[str, ...]:
        """Download current Cloudflare IP ranges. Empty when the download fails."""
        lines: list[str] = []
        for path in ("/ips-v4", "/ips-v6"):
            text = OnCheckSiteBlocking._http_get("www.cloudflare.com", path, _CF_FETCH_TIMEOUT)
            for line in text.splitlines():
                item = line.strip()
                if not item or item.startswith("#"):
                    continue
                try:
                    ipaddress.ip_network(item)
                except ValueError:
                    continue
                lines.append(item)
        return tuple(lines)

    @staticmethod
    def _format_lookup(lookup: DnsLookup) -> str:
        """Format one resolver line."""
        if lookup.ips:
            text = ", ".join(lookup.ips)
            if lookup.error:
                return f"{text} ({lookup.error})"
            return text
        if lookup.rcode:
            return lookup.rcode if not lookup.error else f"{lookup.rcode} ({lookup.error})"
        return lookup.error or "no answer"

    @staticmethod
    def _format_probe(probe: ConnectProbe) -> str:
        """Format one connection probe."""
        parts = [probe.ip]
        if probe.on_cloudflare:
            parts.append("Cloudflare")
        parts.append("TCP ok" if probe.tcp_ok else f"TCP {probe.tcp_error or 'fail'}")
        if probe.checked_tls:
            if probe.tls_ok:
                parts.append("TLS ok")
            elif probe.tls_error == "certificate":
                parts.append("TLS certificate replaced")
            elif probe.tls_error:
                parts.append(f"TLS {probe.tls_error}")
            if probe.decoy_tls_ok is True:
                parts.append("other SNI succeeds")
            elif probe.decoy_tls_ok is False:
                parts.append("other SNI fails")
        if probe.http_status is not None:
            parts.append(f"HTTP {probe.http_status}")
        if probe.cf_ray:
            parts.append("cf-ray")
        if probe.cf_error:
            parts.append(f"hint {probe.cf_error}")
        if probe.server:
            parts.append(f"server {probe.server}")
        return ", ".join(parts)

    @classmethod
    def _format_report(cls, facts: BlockingFacts, verdict: tuple[str, str, str]) -> str:
        """Render measurements and the verdict as plain text."""
        _code, title, summary = verdict
        lines = [
            "Check from this computer. It describes blocking only on this network.",
            f"Address: {facts.url}",
            f"Name: {facts.host}, port {facts.port}",
            "",
            f"Level: {title}",
            summary,
            "",
            "DNS",
        ]
        if facts.hosts_override:
            lines.append(f"- hosts file: {facts.host} -> {facts.hosts_override}")
        if not facts.lookups:
            lines.append("- No answers")
        lines.extend(f"- {lookup.resolver}: {cls._format_lookup(lookup)}" for lookup in facts.lookups)
        if facts.nameservers:
            lines.append("NS: " + ", ".join(facts.nameservers))
        lines.append("Cloudflare: " + cls._cloudflare_label(facts))
        lines.append("")
        lines.append("Connections")
        if not facts.connects:
            lines.append("- Not run")
        lines.extend("- " + cls._format_probe(probe) for probe in facts.connects)
        lines.append("")
        lines.append("Route")
        if not facts.trace_ran:
            lines.append("- Not run")
        elif not facts.hops:
            lines.append(
                "- Traceroute returned no hops. ICMP is often filtered, so this does not prove packets stopped."
            )
        else:
            lines.extend(f"- {hop.index}. {hop.ip or 'timeout'}" for hop in facts.hops)
        lines.append("")
        lines.append("Control example.com")
        if facts.control_dns_ok is None and facts.control_tcp_ok is None:
            lines.append("- Not needed")
        else:
            dns_label = cls._yes_no(value=facts.control_dns_ok)
            tcp_label = cls._yes_no(value=facts.control_tcp_ok)
            lines.append(f"- DNS: {dns_label}, TCP 443: {tcp_label}")
        return "\n".join(lines)

    @staticmethod
    def _header_value(headers: str, name: str) -> str:
        """Return one HTTP header value, or an empty string."""
        prefix = name.lower() + ":"
        for line in headers.split("\r\n"):
            if line.lower().startswith(prefix):
                return line.split(":", 1)[1].strip()
        return ""

    @staticmethod
    def _hosts_override(text: str, host: str) -> str | None:
        """Return the hosts-file address for `host`, if the name is overridden."""
        wanted = host.lower().rstrip(".")
        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < _MIN_HOSTS_FIELDS:
                continue
            address, names = parts[0], parts[1:]
            if any(name.lower().rstrip(".") == wanted for name in names):
                return address
        return None

    @staticmethod
    def _hosts_text() -> str:
        """Read the system hosts file. Missing file yields an empty string."""
        if sys.platform == "win32":
            root = os.environ.get("SYSTEMROOT", r"C:\Windows")
            path = Path(root) / "System32" / "drivers" / "etc" / "hosts"
        else:
            path = Path("/etc/hosts")
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    @staticmethod
    def _http_get(host: str, path: str, timeout: float) -> str:
        """GET `path` over HTTPS and return a short body, or an empty string."""
        connection = http.client.HTTPSConnection(host, timeout=timeout)
        try:
            connection.request("GET", path, headers={"User-Agent": "harrix-swiss-knife", "Accept": "*/*"})
            response = connection.getresponse()
            if response.status != _STATUS_OK:
                return ""
            return response.read(_CF_READ_LIMIT).decode("utf-8", "replace")
        except (OSError, http.client.HTTPException, TimeoutError):
            return ""
        finally:
            connection.close()

    @staticmethod
    def _http_ok(probe: ConnectProbe) -> bool:
        """Return whether the probe received a success or redirect status."""
        return probe.http_status is not None and _STATUS_OK <= probe.http_status < _STATUS_REDIRECT

    @staticmethod
    def _ip_on_cloudflare(ip: str, networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]) -> bool:
        """Return whether `ip` falls in a Cloudflare range."""
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(address in network for network in networks)

    @staticmethod
    def _is_global(ip: str) -> bool:
        """Return whether `ip` is a public unicast address."""
        try:
            return bool(ipaddress.ip_address(ip).is_global)
        except ValueError:
            return False

    @staticmethod
    def _last_answering_hop(hops: tuple[TraceHop, ...]) -> TraceHop | None:
        """Return the last hop that sent an address back."""
        answered = [hop for hop in hops if hop.ip]
        if not answered:
            return None
        return answered[-1]

    @classmethod
    def _lookup_doh(cls, host: str) -> DnsLookup:
        """Resolve A, AAAA, and NS through dns.google JSON."""
        ips: list[str] = []
        found_ns: list[str] = []
        rcode = ""
        error = ""
        quoted = urllib.parse.quote(host)
        for qtype in (_QTYPE_A, _QTYPE_AAAA, _QTYPE_NS):
            body = cls._http_get("dns.google", f"/resolve?name={quoted}&type={qtype}", _DOH_TIMEOUT)
            if not body:
                error = error or "no response"
                continue
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                error = error or "bad JSON"
                continue
            if not isinstance(payload, dict):
                continue
            status = payload.get("Status")
            if isinstance(status, int) and not isinstance(status, bool):
                rcode = cls._rcode_name(status)
            answers = payload.get("Answer", [])
            if not isinstance(answers, list):
                continue
            for answer in answers:
                if not isinstance(answer, dict):
                    continue
                data = str(answer.get("data", "")).rstrip(".")
                atype = answer.get("type")
                if atype in {_QTYPE_A, _QTYPE_AAAA} and data:
                    ips.append(data)
                elif atype == _QTYPE_NS and data:
                    found_ns.append(data)
        return cls.DnsLookup(_DOH_RESOLVER, tuple(dict.fromkeys(ips)), tuple(dict.fromkeys(found_ns)), rcode, error)

    @classmethod
    def _lookup_system(cls, host: str) -> DnsLookup:
        """Resolve `host` with the operating-system resolver."""
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            winerror = getattr(exc, "winerror", None)
            if exc.errno == socket.EAI_NONAME or winerror in _NOT_FOUND_WINERRORS:
                return cls.DnsLookup(_SYSTEM_RESOLVER, (), (), "NXDOMAIN", "")
            return cls.DnsLookup(_SYSTEM_RESOLVER, (), (), "", str(exc))
        except OSError as exc:
            return cls.DnsLookup(_SYSTEM_RESOLVER, (), (), "", str(exc))
        hosts: list[str] = []
        for item in infos:
            host_addr = item[4][0]
            if isinstance(host_addr, str):
                hosts.append(host_addr)
        ips = tuple(dict.fromkeys(hosts))
        rcode = "NOERROR" if ips else "NXDOMAIN"
        return cls.DnsLookup(_SYSTEM_RESOLVER, ips, (), rcode, "")

    @classmethod
    def _lookup_udp(cls, host: str, resolver: str, *, nameservers: bool) -> DnsLookup:
        """Resolve A, AAAA, and optionally NS via DNS over UDP."""
        ips: list[str] = []
        found_ns: list[str] = []
        rcode = ""
        error = ""
        queries = ((_QTYPE_A, False), (_QTYPE_AAAA, False))
        if nameservers:
            queries = (*queries, (_QTYPE_NS, True))
        for qtype, collect_ns in queries:
            try:
                packet = cls._exchange_udp(host, resolver, qtype)
            except TimeoutError:
                error = error or "timeout"
                continue
            except OSError as exc:
                error = error or str(exc)
                continue
            parsed_rcode, parsed_ips, parsed_ns = cls._parse_dns_message(packet)
            rcode = parsed_rcode or rcode
            if collect_ns:
                found_ns.extend(parsed_ns)
            else:
                ips.extend(parsed_ips)
        return cls.DnsLookup(resolver, tuple(dict.fromkeys(ips)), tuple(dict.fromkeys(found_ns)), rcode, error)

    @classmethod
    def _lookups(cls, host: str) -> tuple[DnsLookup, ...]:
        """Query the system resolver, three public UDP resolvers, and DoH."""
        tasks = [partial(cls._lookup_system, host)]
        tasks.extend(
            partial(cls._lookup_udp, host, resolver, nameservers=resolver == "8.8.8.8")
            for resolver in _PUBLIC_RESOLVERS
        )
        tasks.append(partial(cls._lookup_doh, host))
        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            futures = [pool.submit(task) for task in tasks]
        return tuple(future.result() for future in futures)

    @classmethod
    def _no_address_verdict(cls, facts: BlockingFacts) -> tuple[str, str, str]:
        """Explain a name that produced no address to connect to."""
        responded = [lookup for lookup in facts.lookups if lookup.rcode or lookup.ips]
        nxdomain = bool(responded) and all(lookup.rcode == "NXDOMAIN" and not lookup.ips for lookup in responded)
        if facts.control_dns_ok is False and facts.control_tcp_ok is False:
            summary = (
                f"Neither {facts.host} nor the control name {_CONTROL_HOST} resolves, "
                "and the control TCP connection does not open. This computer has no normal internet path."
            )
            return "offline", "No internet", summary
        if nxdomain and facts.control_dns_ok:
            summary = (
                f"Resolvers agree on NXDOMAIN for {facts.host}, while {_CONTROL_HOST} still resolves. "
                "The name likely does not exist. This is not a block."
            )
            return "nxdomain", "Name does not exist", summary
        summary = (
            "Neither system DNS nor the public resolvers returned an address. "
            "The failure is DNS. The check never reached the router path, Cloudflare, or the server."
        )
        return "dns_down", "DNS unavailable", summary

    @staticmethod
    def _parse_dns_message(data: bytes) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        """Return rcode, address records, and NS names from a DNS message."""
        if len(data) < _HEADER_LEN:
            return "FORMERR", (), ()
        _tid, flags, questions, answers, authorities, _extra = struct.unpack_from("!HHHHHH", data, 0)
        rcode = OnCheckSiteBlocking._rcode_name(flags & _RCODE_MASK)
        offset = _HEADER_LEN
        ips: list[str] = []
        nameservers: list[str] = []
        try:
            for _index in range(questions):
                _name, offset = OnCheckSiteBlocking._read_name(data, offset)
                offset += 4
            for section, count in ((True, answers), (False, authorities)):
                for _index in range(count):
                    _name, offset = OnCheckSiteBlocking._read_name(data, offset)
                    rtype, _rclass, _ttl, rdlen = struct.unpack_from("!HHIH", data, offset)
                    offset += 10
                    rdata_at = offset
                    offset += rdlen
                    if section and rtype == _QTYPE_A and rdlen == _IPV4_LEN:
                        ips.append(socket.inet_ntoa(data[rdata_at : rdata_at + _IPV4_LEN]))
                    elif section and rtype == _QTYPE_AAAA and rdlen == _IPV6_LEN:
                        ips.append(str(ipaddress.IPv6Address(data[rdata_at : rdata_at + _IPV6_LEN])))
                    elif rtype == _QTYPE_NS:
                        ns_name, _end = OnCheckSiteBlocking._read_name(data, rdata_at)
                        if ns_name:
                            nameservers.append(ns_name.rstrip("."))
        except (struct.error, ValueError, IndexError):
            return rcode or "FORMERR", tuple(ips), tuple(nameservers)
        return rcode, tuple(dict.fromkeys(ips)), tuple(dict.fromkeys(nameservers))

    @staticmethod
    def _parse_target(raw: str) -> Target:
        """Normalize a user-entered site into host, port, and scheme."""
        text = raw.strip()
        if not text or any(char in text for char in "\r\n\t "):
            msg = "Enter one site address, for example https://harrix.dev/"
            raise ValueError(msg)
        if "://" not in text:
            text = "https://" + text
        parts = urllib.parse.urlsplit(text)
        scheme = (parts.scheme or "https").lower()
        if scheme not in {"http", "https"}:
            msg = "Only http and https addresses can be checked"
            raise ValueError(msg)
        host = parts.hostname or ""
        try:
            host = host.encode("idna").decode("ascii").rstrip(".")
        except UnicodeError as exc:
            msg = "The site name is not a valid host"
            raise ValueError(msg) from exc
        if not host or len(host) > _MAX_HOST_LENGTH:
            msg = "Enter one site address, for example https://harrix.dev/"
            raise ValueError(msg)
        port = parts.port
        if port is None:
            port = _HTTPS_PORT if scheme == "https" else _HTTP_PORT
        path = parts.path or "/"
        default_port = (scheme == "https" and port == _HTTPS_PORT) or (scheme == "http" and port == _HTTP_PORT)
        netloc = host if default_port else f"{host}:{port}"
        url = urllib.parse.urlunsplit((scheme, netloc, path, "", ""))
        return OnCheckSiteBlocking.Target(url=url, host=host, port=port, scheme=scheme)

    @staticmethod
    def _parse_tracert(text: str) -> tuple[TraceHop, ...]:
        """Parse Windows or Unix traceroute text into hops."""
        hops: list[OnCheckSiteBlocking.TraceHop] = []
        for line in text.splitlines():
            match = _HOP_RE.match(line)
            if match is None:
                continue
            found = ""
            for token in re.findall(r"[0-9A-Fa-f:.]+", match.group(2)):
                if token.count(".") != _IPV4_DOTS and token.count(":") < _IPV6_MIN_COLONS:
                    continue
                try:
                    found = str(ipaddress.ip_address(token))
                except ValueError:
                    continue
                break
            hops.append(OnCheckSiteBlocking.TraceHop(int(match.group(1)), found or None))
        return tuple(hops)

    @classmethod
    def _probe_addresses(cls, system_ips: tuple[str, ...], public_ips: tuple[str, ...]) -> tuple[str, ...]:
        """Prefer global system addresses, then public-resolver addresses, capped."""
        ordered: list[str] = []
        global_ips = [ip for ip in (*system_ips, *public_ips) if cls._is_global(ip)]
        local_ips = [ip for ip in system_ips if not cls._is_global(ip)]
        for ip in (*global_ips, *local_ips):
            if ip in ordered:
                continue
            ordered.append(ip)
            if len(ordered) >= _MAX_PROBE_IPS:
                break
        return tuple(ordered)

    def _publish(self, facts: BlockingFacts) -> None:
        """Write the report and request an AI explanation."""
        verdict = self._classify(facts)
        report = self._format_report(facts, verdict)
        self._add_block(report)
        self._explain(report)

    @staticmethod
    def _rcode_name(rcode: int) -> str:
        """Map a DNS rcode number to its mnemonic."""
        if 0 <= rcode < len(_RCODES):
            return _RCODES[rcode]
        return str(rcode)

    @classmethod
    def _read_http(cls, sock: socket.socket | ssl.SSLSocket, host: str) -> tuple[int | None, str, bool, str | None]:
        """Send `GET /` and return status, server header, cf-ray flag, and a body hint."""
        request = (
            "GET / HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "User-Agent: harrix-swiss-knife\r\n"
            "Accept: */*\r\n"
            "Connection: close\r\n\r\n"
        ).encode("ascii", "replace")
        try:
            sock.settimeout(_HTTP_TIMEOUT)
            sock.sendall(request)
            chunks: list[bytes] = []
            total = 0
            while total < _HTTP_READ_LIMIT:
                try:
                    chunk = sock.recv(_HTTP_CHUNK)
                except TimeoutError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
        except OSError:
            return None, "", False, None
        text = b"".join(chunks).decode("utf-8", "replace")
        head, _, body = text.partition("\r\n\r\n")
        match = _STATUS_RE.match(head)
        if match is None:
            return None, "", False, cls._extract_cf_error(text)
        status = int(match.group(1))
        server = cls._header_value(head, "server")
        cf_ray = bool(cls._header_value(head, "cf-ray"))
        cf_error = cls._extract_cf_error(body)
        if cf_error is None and _CF_ORIGIN_MIN <= status <= _CF_ORIGIN_MAX:
            cf_error = str(status)
        return status, server, cf_ray, cf_error

    @staticmethod
    def _read_name(data: bytes, offset: int, depth: int = 0) -> tuple[str, int]:
        """Read a possibly compressed DNS name. Return the name and the next offset."""
        if depth > _MAX_NAME_DEPTH:
            msg = "DNS name is too deeply compressed"
            raise ValueError(msg)
        labels: list[str] = []
        jumped = False
        end = offset
        while True:
            if offset >= len(data):
                msg = "DNS name is truncated"
                raise ValueError(msg)
            length = data[offset]
            if length == 0:
                offset += 1
                if not jumped:
                    end = offset
                break
            if length & _POINTER_MASK == _POINTER_MASK:
                if offset + 1 >= len(data):
                    msg = "DNS name is truncated"
                    raise ValueError(msg)
                pointer = ((length & _LABEL_LENGTH_MASK) << 8) | data[offset + 1]
                if not jumped:
                    end = offset + 2
                pointed, _pointed_end = OnCheckSiteBlocking._read_name(data, pointer, depth + 1)
                if pointed:
                    labels.append(pointed)
                jumped = True
                break
            offset += 1
            label = data[offset : offset + length]
            if len(label) != length:
                msg = "DNS name is truncated"
                raise ValueError(msg)
            labels.append(label.decode("ascii", "replace"))
            offset += length
            if not jumped:
                end = offset
        return ".".join(labels), end

    @staticmethod
    def _sni_filtered(probe: ConnectProbe) -> bool:
        """Return whether TLS failed for the site name and succeeded for another name."""
        return bool(
            probe.checked_tls
            and probe.tcp_ok
            and not probe.tls_ok
            and probe.tls_error in _TLS_BREAKS
            and probe.decoy_tls_ok
        )

    @staticmethod
    def _tcp_error(exc: BaseException) -> str:
        """Classify a failed TCP connect as timeout, reset, refused, unreachable, or other."""
        if isinstance(exc, TimeoutError):
            return "timeout"
        winerror = getattr(exc, "winerror", None)
        errno = getattr(exc, "errno", None)
        if winerror in _RESET_WINERRORS or errno in _RESET_ERRNOS:
            return "reset"
        if winerror in _REFUSED_WINERRORS or errno in _REFUSED_ERRNOS:
            return "refused"
        if winerror in _UNREACHABLE_WINERRORS or errno in _UNREACHABLE_ERRNOS:
            return "unreachable"
        if winerror in _TIMEOUT_WINERRORS or errno in _TIMEOUT_ERRNOS:
            return "timeout"
        text = str(exc).lower()
        if "timed out" in text or "timeout" in text:
            return "timeout"
        return "other"

    @classmethod
    def _tcp_failed_verdict(cls, facts: BlockingFacts) -> tuple[str, str, str]:
        """Explain addresses that never accepted TCP."""
        if facts.control_tcp_ok is False:
            summary = (
                f"TCP to {facts.host} and to the control host {_CONTROL_HOST} does not open. "
                "This is a general loss of internet, not a block of one site."
            )
            return "offline", "No internet", summary
        errors = {probe.tcp_error for probe in facts.connects}
        if errors == {"refused"}:
            summary = (
                "The address resolves and the host immediately refuses the connection. "
                "The packet reached a machine. The port is closed on the server or on a filter in front of it."
            )
            return "refused", "Port closed", summary
        if errors <= {"unreachable"}:
            summary = (
                "The operating system reports that there is no route to the address. "
                "The request does not leave this computer or the router."
            )
            return "router", "Router", summary
        last = cls._last_answering_hop(facts.hops)
        cloudflare = any(probe.on_cloudflare for probe in facts.connects)
        if last is not None and last.index == 1 and last.ip is not None and not cls._is_global(last.ip):
            summary = (
                f"Traceroute stops at the first hop {last.ip}. "
                "Port 443 to the site does not open. The request most likely does not leave the router. "
                "Traceroute uses ICMP, so this is a strong sign, not proof."
            )
            return "router", "Router", summary
        if last is not None and last.index >= _HOP_PAST_ROUTER:
            where = last.ip or "no address"
            summary = (
                f"Packets pass the router and stop arriving around hop {last.index} ({where}). "
                "The block is on the path after the router."
            )
            if cloudflare:
                summary += " The address belongs to Cloudflare. The origin server is not visible from this machine."
            return "path", "Path after the router", summary
        summary = (
            "The name resolves the same way, but TCP to the address does not open, and the control site is reachable. "
            "This looks like filtering of the IP or of port 443."
        )
        if cloudflare:
            summary += (
                " The addresses are in the Cloudflare network: the path to Cloudflare is cut, "
                "not the origin server by itself. The origin is not published outside."
            )
        return "ip", "Address network", summary

    @classmethod
    def _tcp_ok_verdict(cls, facts: BlockingFacts) -> tuple[str, str, str]:
        """Explain a host that accepted TCP."""
        probes = facts.connects
        if any(probe.tls_error == "certificate" and cls._http_ok(probe) for probe in probes):
            summary = (
                "The site certificate did not match, but the page still arrived over unverified TLS. "
                "A local HTTPS intercept is on the path: antivirus, AdGuard, or a corporate proxy."
            )
            return "intercept", "Local HTTPS intercept", summary
        if any(probe.tls_ok and cls._http_ok(probe) and probe.cf_error != "blockpage" for probe in probes):
            where = "through Cloudflare" if any(probe.on_cloudflare or probe.cf_ray for probe in probes) else "directly"
            summary = f"The site opens from this computer {where}. No block is visible on this network."
            return "reachable", "Site opens", summary
        if any(not probe.checked_tls and probe.tcp_ok and cls._http_ok(probe) for probe in probes):
            return (
                "reachable",
                "Site opens",
                "An HTTP 2xx or 3xx response arrived. No block is visible on this network.",
            )
        if any(probe.tls_ok and probe.cf_error == "blockpage" for probe in probes):
            summary = "The response body is a block page. It came from the node that finished TLS."
            return "block_page", "Block page", summary
        if any(cls._sni_filtered(probe) for probe in probes):
            summary = (
                "TCP to the address opens, TLS with the site name breaks, and TLS with a different name "
                "to the same IP succeeds. This is a filter on the TLS name (SNI), not a dead server "
                "and not a Cloudflare policy."
            )
            return "sni", "TLS name filter", summary
        if any(probe.cf_error in _CF_ORIGIN for probe in probes):
            summary = (
                "The connection reaches Cloudflare, and a 520-526 code means Cloudflare could not reach "
                "the origin server. The Cloudflare edge is up. The origin is not."
            )
            return "origin", "Origin server", summary
        if any(probe.cf_error in _CF_POLICY or probe.cf_error in {"challenge", "blocked"} for probe in probes):
            summary = (
                "The request reached Cloudflare, and Cloudflare itself refused it or showed a challenge. "
                "This is policy or a challenge at the edge, not a silent origin."
            )
            return "cloudflare", "Cloudflare policy", summary
        if any(
            probe.tls_ok and probe.http_status is not None and probe.http_status >= _STATUS_REDIRECT for probe in probes
        ):
            summary = (
                "TLS completed, and the response was an HTTP error without a Cloudflare block code. "
                "The refusal was produced by whoever finished the handshake."
            )
            return "http", "HTTP response", summary
        if any(
            probe.checked_tls and probe.tcp_ok and not probe.tls_ok and probe.tls_error == "reset" for probe in probes
        ):
            summary = (
                "TCP opens, but TLS is reset both for the site name and for a different name. "
                "This looks like a middlebox on port 443."
            )
            return "tls_reset", "TLS reset", summary
        if any(probe.checked_tls and probe.tcp_ok and not probe.tls_ok for probe in probes):
            summary = (
                "TCP to the address exists, but the TLS handshake does not finish. "
                "The break is on TLS, not on DNS and not on the router."
            )
            return "tls", "TLS break", summary
        return "unknown", "Could not tell", "The measurements were not enough to name one level."

    @classmethod
    def _tls_and_http(
        cls,
        ip: str,
        port: int,
        host: str,
        sock: socket.socket,
    ) -> tuple[bool, str, int | None, str, bool, str | None]:
        """Handshake TLS on an open socket and read one HTTP response."""
        context = ssl.create_default_context()
        try:
            with context.wrap_socket(sock, server_hostname=host) as tls:
                status, server, cf_ray, cf_error = cls._read_http(tls, host)
        except ssl.SSLCertVerificationError:
            return cls._unverified_http(ip, port, host)
        except (TimeoutError, ssl.SSLError, OSError) as exc:
            return False, cls._tls_error(exc), None, "", False, None
        else:
            return True, "", status, server, cf_ray, cf_error

    @staticmethod
    def _tls_error(exc: BaseException) -> str:
        """Classify a failed TLS handshake."""
        if isinstance(exc, ssl.SSLCertVerificationError) or "certificate" in str(exc).lower():
            return "certificate"
        if isinstance(exc, TimeoutError):
            return "timeout"
        if isinstance(exc, ConnectionResetError):
            return "reset"
        text = str(exc).lower()
        if "reset" in text or "eof" in text or "broken pipe" in text:
            return "reset"
        if "timed out" in text or "timeout" in text:
            return "timeout"
        return "protocol"

    @staticmethod
    def _trace_command(ip: str) -> list[str] | None:
        """Build a traceroute command that does not resolve hop names."""
        if sys.platform == "win32":
            root = os.environ.get("SYSTEMROOT", r"C:\Windows")
            executable = str(Path(root) / "System32" / "tracert.exe")
            return [executable, "-d", "-h", str(_TRACE_HOPS), "-w", str(_TRACE_WAIT_MS), ip]
        executable = shutil.which("traceroute")
        if executable is None:
            return None
        return [executable, "-n", "-m", str(_TRACE_HOPS), "-w", "1", ip]

    @staticmethod
    def _traceroute(ip: str) -> tuple[TraceHop, ...]:
        """Run traceroute to a single IP and parse the hops."""
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return ()
        command = OnCheckSiteBlocking._trace_command(ip)
        if command is None:
            return ()
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=_TRACE_TIMEOUT,
                check=False,
                **hidden_subprocess_kwargs(),
            )
        except (OSError, subprocess.TimeoutExpired):
            return ()
        return OnCheckSiteBlocking._parse_tracert(completed.stdout)

    @classmethod
    def _unverified_http(
        cls,
        ip: str,
        port: int,
        host: str,
    ) -> tuple[bool, str, int | None, str, bool, str | None]:
        """Retry HTTP without certificate checks after a verify failure."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        try:
            bare = socket.create_connection((ip, port), _TCP_TIMEOUT)
        except (TimeoutError, OSError) as exc:
            return False, cls._tls_error(exc), None, "", False, None
        try:
            with context.wrap_socket(bare, server_hostname=host) as tls:
                status, server, cf_ray, cf_error = cls._read_http(tls, host)
        except (TimeoutError, ssl.SSLError, OSError) as exc:
            return False, cls._tls_error(exc), None, "", False, None
        finally:
            bare.close()
        return False, "certificate", status, server, cf_ray, cf_error

    @staticmethod
    def _yes_no(*, value: bool | None) -> str:
        """Format a tri-state flag."""
        if value is None:
            return "not checked"
        return "yes" if value else "no"

    @dataclass(frozen=True)
    class Target:
        """Normalized URL, host, port, and scheme."""

        url: str
        host: str
        port: int
        scheme: str

    @dataclass(frozen=True)
    class DnsLookup:
        """One resolver answer."""

        resolver: str
        ips: tuple[str, ...]
        nameservers: tuple[str, ...]
        rcode: str
        error: str

    @dataclass(frozen=True)
    class ConnectProbe:
        """TCP, TLS, and HTTP result for one address."""

        ip: str
        on_cloudflare: bool = False
        tcp_ok: bool = False
        tcp_error: str = ""
        checked_tls: bool = True
        tls_ok: bool = False
        tls_error: str = ""
        decoy_tls_ok: bool | None = None
        http_status: int | None = None
        cf_ray: bool = False
        cf_error: str | None = None
        server: str = ""

    @dataclass(frozen=True)
    class TraceHop:
        """One traceroute hop. `ip` is empty when the hop timed out."""

        index: int
        ip: str | None

    @dataclass(frozen=True)
    class BlockingFacts:
        """Everything measured before the verdict."""

        url: str = _DEFAULT_URL
        host: str = "harrix.dev"
        port: int = _HTTPS_PORT
        hosts_override: str | None = None
        lookups: tuple[OnCheckSiteBlocking.DnsLookup, ...] = ()
        nameservers: tuple[str, ...] = ()
        cloudflare_ns: bool = False
        dns_mismatch: bool = False
        connects: tuple[OnCheckSiteBlocking.ConnectProbe, ...] = ()
        hops: tuple[OnCheckSiteBlocking.TraceHop, ...] = ()
        trace_ran: bool = False
        control_dns_ok: bool | None = None
        control_tcp_ok: bool | None = None
